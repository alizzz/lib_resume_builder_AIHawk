import copy
import logging
import os
import os.path
import random
import re
import sys
import tempfile
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Dict, Tuple, Any

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import TokenTextSplitter
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.system import SystemMessage
from langchain_core.messages.base import BaseMessage

from lib_resume_builder_AIHawk.html_doc import HtmlDoc
from lib_resume_builder_AIHawk.OutputParsers import DelimitedListOutputParser
from lib_resume_builder_AIHawk.asset_manager import PromptManager
from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt_resumer_base import LLMResumerBase, clean_html_string, LoggerChatModel
from lib_resume_builder_AIHawk.resume import KeyValue, Skill, Achievement
from lib_resume_builder_AIHawk.resume import WorkExperience
from lib_resume_builder_AIHawk.html_resume import HtmlResume
from lib_resume_builder_AIHawk.html_cover import HtmlCover
from lib_resume_builder_AIHawk.utils import create_driver_selenium
# from lib_resume_builder_AIHawk.resume_template import resume_template_job_experience, resume_template
from lib_resume_builder_AIHawk.utils import printcolor, printred, read_format_string, get_content
from src.job import Job

load_dotenv()
# ToDo: make it read config file

template_file = os.path.join(os.path.dirname(__file__), 'resume_templates',
                             os.environ.get('RESUME_TEMPLATE', 'hawk_resume_template.html'))
css_file = os.path.join(os.path.dirname(__file__), 'resume_style', 'style_hawk.css')
fullresume_file_backup = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_sample.html')

class LLMResumeJobDescription(LLMResumerBase):
    def __init__(self, openai_api_key, strings=None):
        # LLMResumerBase creates the following members
        # self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=tempertature_cheap))
        # self.llm_good = LoggerChatModel(ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, temperature=temperature_good))
        # self.strings = strings
        # self.system_msg = None
        # self.resume: Resume = None
        # self.msg_chain = []
        super().__init__(openai_api_key=openai_api_key, strings=strings)

        self.llm_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.pos_hierarchy_list = None
        self.resume = None
        self.job = None
        self.job_desc = None
        self.job_title = None
        self.job_company_name = None
        self.msg_chain = [] #[('system', PromptManager().load_prompt('hawk_system'))]
        self.injection_prompt = None


        #region setting up logger
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)

        # Define handler and formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler
        file_handler = logging.FileHandler("app_errors.log")
        file_handler.setFormatter(formatter)

        # Add both handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        #endregion

    def set_job(self, job:Job = None):
        self.job = copy.deepcopy(job)
        self.job.job_description_summary = self.summarize_job_description()
        self.job_title = self.job.title
        self.job_desc = self.job.job_description_summary

    def add_system_prompt(self, key='hawk_system', map:Dict[str,Any]={}):
        if not key: return
        print(f'Adding system prompt {key}')
        try:
            job_desc = self.job.get_llm_prompt_info()
            map["job_description"]=job_desc
            sys_prompt = PromptManager().load_prompt(key, map=map)
            if sys_prompt:
                self.msg_chain.append(('system', sys_prompt))
                self.system_msg = sys_prompt
        except Exception as e:
            printred(f'Failed to add system prompt {key}. Error: {e}')
    def get_prompt(self, prompt_key, default_value, map={}):

        p_ = PromptManager().load_prompt(key=prompt_key, map=map)
        if p_ is None or p_.startswith('Warning: unable'):
            return default_value
        else:
            return p_

        #try:
        #     prompt_file = global_config.prompt_dict.get(prompt_key)
        #     if prompt_file is None:
        #          raise FileNotFoundError()
        #
        #     with open(prompt_file, mode='r', encoding='utf-8') as f:
        #         prompt_content = f.read()
        #         if prompt_content is not None:
        #             #print(f'Retrieved prompt from file {prompt_key}')
        #             return prompt_content
        # except Exception as e:
        #     self.logger.info('an exception')
        #
        # print(f'Unable to retrieve prompt from file {prompt_key}. Returning value from strings.py')
        # return default_value

    #@staticmethod
    #def _preprocess_template_string(template: str) -> str:
    #    # Preprocess a template string to remove unnecessary indentation.
    #   return textwrap.dedent(template)

    def set_default_injection_prompt(self, inj_p=None, map={}):
        # if inj_p is None:
        #     self.injection_prompt =  self._default_injection_prompt()
        # if inj_p == 'None':
        #     self.injection_prompt = ''
        # self.injection_prompt = inj_p.format_map(map)
        self.injection_prompt = ''

    def set_resume(self, resume):
        self.resume = copy.deepcopy(resume)
        #printcolor(f'in LLMResumeJobDescription.setresume::self._resume.experience_details[0].position:{self._resume.experience_details[0].position}', "magenta")
        self.pos_hierarchy_list = self.generate_position_hierarchy_ai()
        self.update_positions_automl()
        #printcolor(f"in LLMResumeJobDescription.set_resume::self.resume_.experience_details[0].position:{self.resume_.experience_details[0].position}, self.pos_hierarchy_list:':{self.pos_hierarchy_list}", "magenta")

    def set_job_description_from_url(self, url_job_description):
        printcolor(
            f'in LLMResumeJobDescription.set_job_description_from_url', "blue")

        driver = create_driver_selenium()
        driver.get(url_job_description)
        time.sleep(3)
        body_element = driver.find_element("tag name", "body")
        response = body_element.get_attribute("outerHTML")
        driver.quit()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8") as temp_file:
            temp_file.write(response)
            temp_file_path = temp_file.name
        try:
            loader = TextLoader(temp_file_path, encoding="utf-8", autodetect_encoding=True)
            document = loader.load()
        finally:
            os.remove(temp_file_path)
        text_splitter = TokenTextSplitter(chunk_size=200, chunk_overlap=50)
        all_splits = text_splitter.split_documents(document)
        vectorstore = FAISS.from_documents(documents=all_splits, embedding=self.llm_embeddings)
        _prompt_text = get_content('generic_question_about_job_description.prompts', os.path.join(os.path.dirname(__file__), 'resume_prompt'))
        prompt = PromptTemplate(
            template=_prompt_text,
            input_variables=["question", "context"]
        )

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        context_formatter = vectorstore.as_retriever() | format_docs
        question_passthrough = RunnablePassthrough()
        chain_job_description= prompt | self.llm_cheap | StrOutputParser()
        #reads from prompts\job_description_summary.prompts if available. Otherwise uses self.strings.summarize_prompt_template
        summarize_prompt_template = self._preprocess_template_string(
            PromptManager().load_prompt('job_description_summary'))
        prompt_summarize = ChatPromptTemplate.from_template(summarize_prompt_template)
        chain_summarize = prompt_summarize | self.llm_cheap | StrOutputParser()
        qa_chain = (
            {
                "context": context_formatter,
                "question": question_passthrough,
            }
            | chain_job_description
            | (lambda output: {"text": output})
            | chain_summarize
        )
        result = qa_chain.invoke("Provide, full job description")
        self.job_desc = result
        print(f'Job description:\n{result}')

    def set_job_title(self, job_title:str):
        self.job_title = job_title

    #def summarize_job_description(self, job:Job = None, description:str=None, title:str=None):
    def summarize_job_description(self):
        if self.job.job_description_summary:
            print('LLMResumeJobDesc::summarize_job_description job description summary has already been set. Skipping')
        else:
            print("in LLMResumeJobDesc::summarize_job_description job description summary has not been set yet")
        traceback.print_stack()

        parser = StrOutputParser()
        map={"job_description":self.job.description, "job_title":self.job.title, "job_id":self.job.id, "id":self.job.id}
        prompt = self._load_and_prepare_prompt(prompt_key='job_description_summary', map_data=map,
                                               parser=parser, msg_chain=self.msg_chain, no_system_prompt=True)
        self.job.job_description_summary = self._invoke_chain(prompt, parser, msg_chain=self.msg_chain, llm=self.llm_good)
        print(f"In LLMResumeJobDescription::summarize_job_description: {self.job.job_description_summary[:200]}")
        return self.job.job_description_summary

    def set_job_description_from_text(self, job_description_text: object) -> object:
        self.job_desc = job_description_text
        # summarize_prompt_template = PromptManager().load_prompt('job_description_summary')
        # prompt = ChatPromptTemplate.from_template(summarize_prompt_template)
        # chain = prompt | self.llm_cheap | StrOutputParser()
        # output = chain.invoke({"text": job_description_text})
        # self.job_description = output
        # print("In set_job_description_from_text() executed job_description_summary prompt")
        return job_description_text

    def _generate_header_gpt(self) -> str:
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        header_prompt_template = self._preprocess_template_string(PromptManager().load_prompt('header'))
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "personal_information": self.resume.personal_information,
            "job_description": self.job_description
        })
        return output

    def generate_header(self, header_prompt_template=None) -> str:
        if header_prompt_template is None:
            return self._generate_header_gpt()
        output="""
        """
        return output

    def generate_education_section(self) -> str:
        print("In generate_education_section")
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        education_prompt_template = self._preprocess_template_string(PromptManager().load_prompt('education_history'))

        prompt = ChatPromptTemplate.from_template(education_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "education_details": self.resume.education_details,
            "job_description": self.job.job_description_summary
        })
        return output

    def generate_work_experience_ai(self, work_experience:WorkExperience, k:int=-1):
        print(f'In: generate_work_experience_ai() for {work_experience.position} at {work_experience.company}')
        we:WorkExperience = copy.deepcopy(work_experience)
        msg_history=[]
        we.summary = self.generate_work_experience_summary_ai(k, we, msg_history)
        msg_history.extend([('ai',we.summary)])

        return self.generate_work_experience_key_achievements_ai(k, we)


    def generate_achievements_section_ai(self) -> str:
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        map = self.build_default_map()

        parser = DelimitedListOutputParser('\n')
        prompt = self._load_and_prepare_prompt(prompt_key='achievements', map_data=map,
                                               parser=parser, msg_chain=self.msg_chain)

        a_list = self._invoke_chain(prompt, parser, msg_chain=self.msg_chain, llm = self.llm_good)

        self.resume.achievements = [Achievement(name=a.split(':')[0], description=a.split(":")[1]) for a in a_list if a and len(a.split(":"))>1]

        # achievements_prompt_template = self._preprocess_template_string(
        #     PromptManager().load_prompt('achievements_html'))
        #
        # if self.resume.achievements:
        #     prompt = ChatPromptTemplate.from_template(achievements_prompt_template)
        #     chain = prompt | self.llm_cheap | StrOutputParser()
        #     output = chain.invoke({
        #         "achievements": self.resume.achievements,
        #         "certifications": self.resume.achievements,
        #         "job_description": self.job_description
        #     })
        return '\n'.join(a_list)

    def build_default_map(self, n_lines=0, n_words=0):
        return {
            "job_id": self.job.id,
            "job_title": self.job_title,
            "job_description": self.job.job_description_summary if self.job.job_description_summary else self.job.description,
            "work_history": '\n'.join([we.text() for we in self.resume.work_experiences]),
            "career_summary": ','.join(self.resume.career_summary),
            "career_highlights": ','.join([x.text() for x in self.resume.career_highlights if x]),
            "skills": ','.join([x.text() for x in self.resume.skills if x]),
            "achievements": ','.join([x.text() for x in self.resume.achievements if x]),
            "n_words":n_words,
            "n_lines":n_lines,
            "years_technical_experience": self.resume.personal_information.years_technical_experience,
            "years_leadership_experience": self.resume.personal_information.years_mgmt_experience
        }
    def _default_injection_prompt(self, map={}, default_injection_prompt='_default_injection_prompt'):
        if not map:
            map={
            "job_title": self.job_title,
            "job_description": self.job_desc,
            "work_history":'\n'.join([we.text() for we in self.resume.work_experiences]),
            "career_summary": ','.join(self.resume.career_summary),
            "career_highlights": ','.join([x.text() for x in self.resume.career_highlights if x]),
            "skills": ','.join([x.text() for x in self.resume.skills if x]),
            "achievements": ','.join([x.text() for x in self.resume.achievements if x])
            }


            return PromptManager().load_prompt(default_injection_prompt, map)

    # def _load_and_prepare_prompt(self,  prompt_key: str, map_data: dict= {}, parser=None, msg_chain: List[BaseMessage]=[],
    #                              do_not_use_long_message_chain:bool = True, no_system_prompt:bool=False) -> ChatPromptTemplate:
    #     try:
    #         if not parser:
    #             parser = StrOutputParser()
    #
    #         if isinstance(parser, StrOutputParser):
    #             format_instructions = "Provide a plain text response without any extra formatting"
    #         else:
    #             try:
    #                 format_instructions = parser.get_format_instructions()
    #             except:
    #                 format_instructions = ''
    #
    #         prompt_template = PromptManager().load_prompt(prompt_key, map=map_data)
    #         formatted_prompt = self._preprocess_template_string(
    #             prompt_template, format_instructions=format_instructions
    #         )
    #
    #         #Note: To maintain continuity of responses we need to send msg_chain
    #         #But it is expensive - a lot of tokens in the chain
    #         #Also every requiest is pretty much self-sufficient, and does not depend on previous answers
    #         #therefore here we reduce number of messages in the chain, and pretend that this is the first message
    #         human_message = HumanMessage(formatted_prompt, prompt_key=prompt_key, job_id=map_data.get("job_id"))
    #
    #         msg_chain.append(human_message)
    #         if do_not_use_long_message_chain:
    #             msg = [SystemMessage(self.system_msg)] if (not no_system_prompt and self.system_msg)  else []
    #
    #             msg.append(human_message)
    #         else:
    #             msg = [m for m in msg_chain]
    #
    #         return ChatPromptTemplate(msg)
    #     except Exception as e:
    #         printred(f"Error loading or preparing prompt {prompt_key}: {e}")
    #         self.logger.error(f"Error loading or preparing prompt {prompt_key}: {e}")
    #         raise e

    def _invoke_chain(self, prompt_template, parser, msg_chain: List[BaseMessage]=[], key:str=None, llm:LoggerChatModel=None):
        try:
            if not llm: llm = self.llm_cheap

            chain = prompt_template | llm
            output:AIMessage = chain.invoke({})

            msg_chain.append(output)
            return parser.invoke(output)
        except Exception as e:
            self.logger.error(f"Error invoking chain: {e}")
            raise e

    # def generate_work_experience_section_summary_ai(self, work_experience="", skills="", position_title="", job_desc="") -> str:
    #     # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
    #     work_experience_summary_prompt_template = self._preprocess_template_string(
    #         PromptManager().load_prompt('professional_experience_role_summary'))
    #
    #     prompt = ChatPromptTemplate.from_template(work_experience_summary_prompt_template)
    #     chain = prompt | self.llm_good | StrOutputParser()
    #     raw_output = chain.invoke({
    #         "job_desc": job_desc,
    #         "work_experience": work_experience,
    #         "position_title": position_title,
    #         "skills": skills
    #     })
    #     output = clean_html_string(raw_output)
    #     return output
    #
    # def generate_work_experience_section_ai(self, work_experience="", skills="", position_title="", job_desc="", n_lines = random.choice([3,4,5])) -> str:
    #     # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
    #     work_experience_prompt_template = self._preprocess_template_string(
    #         PromptManager().load_prompt('work_experience'))
    #
    #     prompt = ChatPromptTemplate.from_template(work_experience_prompt_template)
    #     chain = prompt | self.llm_good | StrOutputParser()
    #     raw_output = chain.invoke({
    #         "experience_details": work_experience,
    #         "job_description": job_desc,
    #         "skills": skills,
    #         "position": position_title,
    #         "n_line_items":n_lines
    #     })
    #     output = clean_html_string(raw_output)
    #     return output

    def generate_side_projects_section(self) -> str:
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        side_projects_prompt_template = self._preprocess_template_string(
            PromptManager().load_prompt('side_projects'))

        prompt = ChatPromptTemplate.from_template(side_projects_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "projects": self.resume.projects,
            "job_description": self.job_description
        })
        return output

    def generate_additional_skills_section(self) -> str:


        def split_string(s, sep=','):
            return [x.strip() for x in s.split(sep)]

        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        additional_skills_prompt_template = self._preprocess_template_string(
            PromptManager().load_prompt('additional_skills'))

        skills = set()

        if self.resume.work_experiences:
            for we in self.resume.work_experiences:
                if we.skills_acquired:
                    skills.update(we.skills_acquired)

        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())

        #additional skills
        skill_list = [x.text() for x in self.resume.skills]
        for k in skill_list:
            skills.update([s.strip() for s in k.split(',') if s])

        #skill_elements = 'Programming, Python, SQL, R, C++, Java, Machine learning, deep learning, Tensorflow, Keras, Scikit-Learn, Natural Language Processing (NLP), Data analysis, statistics, Cloud platforms, AWS, Google Cloud, Big data, Hadoop, Spark'
        #skills.update([f'Technical:{x}' for x in split_string(skill_elements)])
        #skills.update(split_string(skill_elements))
        #print(f'after: {len(skills)}, len(skill_elements):{len(skill_elements.split(","))}')
        #print(','.join(skills))
        #for skill_element in skill_elements:
        #    skills.update(f'technical:{skill_element}')
        #for skill_element in f'Strategic thinking, Project management, Team leadership, Talent development, Agile methodologies'.split(','):
        #    skills.update((f'leadership and management:{skill_element.strip()}'))
        #skills.update([x for x in split_string(
        #    'Strategic thinking, Project management, Team leadership, Talent development, Agile methodologies')])
        #skills.update([x for x in split_string(
        #    'Industry-specific expertise, Business acumen, Financial analysis, Understanding AI applications in various sectors')])
        #skills.update([x for x in split_string(
        #    'Critical thinking, Problem-solving, Creativity, Adaptability and resilience, Effective communication, Data storytelling, Executive presence, Stakeholder management, Analytical reasoning, Creative problem-solving')])
        #skills.update([x for x in split_string(
        #    'prompts engineering, AI literacy (understanding concepts and terminology), Human-AI interaction, Ethical AI development and implementation, AI ethics and governance, Generative AI, genAI')])
        #skills.update([x for x in split_string(
        #    'data ethics,
    #    if self.resume_.skills:
    #        for key, value in self.resume_.skills.items():
    #            skill_list = value.split(',')  # Split the comma-delimited string
    #            for skill_element in skill_list:
    #                skills.update(f'{key}:{skill_element.strip()}')

        prompt = ChatPromptTemplate.from_template(additional_skills_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "languages": self.resume.languages,
            "interests": self.resume.interests,
            "skills": skills,
            "job_description": self.job_description
        })

        #print(f"skills output:{output}")
        return output

    # generate static header based on applicant information
    # ToDo: load from configuration
    def generate_applicant_name_header(self, delim = ' | '):
        # use as a default output if unable to read the chunk from file
        output_ = f'<span class="applicant_name_header">{self.resume.personal_information.name} {self.resume.personal_information.surname}</span> • <span class="phone">{self.resume.personal_information.phone_prefix} {self.resume.personal_information.phone}</span> • <span class="email">{self.resume.personal_information.email}</span>'
        output = None
        try:
            # < div id = "header" >< table >< tr >
            # < td class ="left-aligned-column" >
            # < span class ="applicant_name_header" > {name_prefix}{name} {surname}{name_suffix} < /span > < /td >
            # < td class ="right-aligned-column" > < span class ="phone" > {phone_prefix}{phone} < /span >
            # < span class ="table-cell-delimeter" > {delim_1} < /span >
            # < span class ="email" > {email} < /span >
            # < span class ="table-cell-delimeter" > {delim_2} < /span >
            # < span class ="other_contacts" > {other_contacts} < /span > < /td > < / tr >< / table >< / div >
            fmt_params = {
                'name_prefix': self.resume.personal_information.name_prefix,
                'name': self.resume.personal_information.name,
                'surname': self.resume.personal_information.surname,
                'name_suffix': self.resume.personal_information.name_suffix,
                'phone_prefix': self.resume.personal_information.phone_prefix,
                'phone': self.resume.personal_information.phone,
                'delim_1': delim,
                'email': self.resume.personal_information.email
            }
            file_name = os.path.join(global_config.TEMPLATES_DIRECTORY, 'chunks',
                                     global_config.html_template_chunk['name_header'])
            fmt_string = read_format_string(file_name)
            output = fmt_string.format(**fmt_params)
        except Exception as e:
            self.logger.error('EXCEPTION in generate_applicant_name_header. Using default header')
            printred(f'EXCEPTION in generate_applicant_name_header. Using default header Error {e}')
            printred(traceback.format_exc())
        return output if output is not None and len(output) > 0 else output_

    # generate title based on position name
    def generate_application_title_ai(self):
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        application_title_template = self._preprocess_template_string(
            PromptManager().load_prompt('application_title'))

        prompt = ChatPromptTemplate.from_template(application_title_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "job_description": self.job_description
        })
        # removing non-alphanum from the beginning and end of the string
        clean_output = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9)]+$', '', output.split('(')[0])
        return clean_output

    def generate_position_hierarchy_ai(self):
        return 'Sr. Director, Vice President, Sr. Vice President, CTO'

    # Disabled for now. Generates standard Hierarchy
    def _generate_position_hierarchy_ai(self):
        # reads from prompts\[name.prompt] if available. Otherwise uses self.strings.[value]
        gpt_template = self._preprocess_template_string(
            PromptManager().load_prompt('position_hierarchy'))
        prompt = ChatPromptTemplate.from_template(gpt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        hierarchy_string = chain.invoke({
            "job_description": self.job_description
        })

        output = [position.strip() for position in hierarchy_string.split(',')]
        output_str = ','.join(output)
        print(f"generated position hierarchy {output_str}")
        return output

    def update_positions_automl(self):
        def _position_automl(current_position: str, substitute_positions):
            if substitute_positions is None: return current_position
            num_subs = len(substitute_positions)
            case_statements = {
                "L0": substitute_positions[0],
                "L1": substitute_positions[1] if num_subs > 2 else substitute_positions[num_subs - 1],
                "L2": substitute_positions[2] if num_subs > 3 else substitute_positions[num_subs - 1],
                "L3": substitute_positions[3] if num_subs > 4 else substitute_positions[num_subs - 1],
                "L4": substitute_positions[4] if num_subs > 5 else substitute_positions[num_subs - 1]
            }
            return case_statements.get(current_position, current_position)

        for k in range(len(self.resume.work_experiences)):
            position = self.resume.work_experiences[k].position
            if position in ["L0", "L1", "L2", "L3"]:
                new_pos = _position_automl(position, self.pos_hierarchy_list)
                self.resume.work_experiences[k].position = new_pos

      #ToDo: 1. read experience from config
    #ToDo: 2. use genAI. Generate updated experience based on job description
    def generate_professional_experience(self):
        raw_html = "<div>"
        for exp in self.resume.experience_details:
        # --- Position Header
            raw_html+=f"""<div>
                <table width="720" cellpadding="0" cellspacing="0">
                    <col width="140"/>
                    <col width="240"/>
                    <col width="100"/>
                    <col width="75"/>
                    <tr>
                        <td align="left" class="company_name_employment_history_summary">{exp.company}</td>
                        <td align="left" class="position_employment_history_summary>{exp.position}</td>
                        <td align="right" class="location_employment_history">{exp.location}</td>
                        <td align="right" class="employment_period_employment_history">{exp.employment_period}</td>
                </table>"""
            #--- Position summary ---#
            try:
                raw_html += f"""<div align="justify" class="prof-exp-details">{exp.summary}</div>"""
            except Exception as e:
                self.logger.error(f'Experience summary is not set for {exp.position} for {exp.company}')
                print(f'Experience summary is not set for {exp.position} for {exp.company}')

            #--- Position responsibilities ---#

            responsibility_html = ""
            try:
                for responsibility in exp.key_responsibilities:
                    responsibility_html +=f'<li><p align="justify">{responsibility}</p></li>'
            except Exception as e:
                self.logger.error(f"Exception while processing responsibilities for {exp.position} for {exp.company}")
                print(f"Exception while processing responsibilities for {exp.position} for {exp.company}. Exception {e}")

            if len(responsibility_html)>0:
                    raw_html+=f"""<div class="job-responsibility">{responsibility_html}</div>"""

            raw_html += "</div>"
        raw_html+="</div>"
        output = clean_html_string(raw_html)
        return output

    def generate_footer(self):
        output=""
        return output

    def generate_cover_letter_content_ai(self):
        try:
            map_data = self.build_default_map()
            parser = DelimitedListOutputParser('\n')#StrOutputParser()

            map_data=self.build_default_map()
            map_data['name_prefix']=self.resume.personal_information.name_prefix
            map_data['name'] = self.resume.personal_information.name
            map_data['surname'] = self.resume.personal_information.surname
            map_data['name_suffix'] = self.resume.personal_information.name_suffix
            map_data["company_name"] = self.job.company

            prompt_template = self._load_and_prepare_prompt(
                'cover_letter_body', map_data, parser, self.msg_chain)

            cover_content = self._invoke_chain(prompt_template, parser, llm=self.llm_good)

            return cover_content

        except Exception as e:
            printred(f'Exception in generate_cover_letter_content_ai(). Error: {e} {traceback.format_exc()}')
        return ''
    def generate_tailored_skills_section_ai(self):
        try:
            format_instructions = """
            Deliverable:
            A structured and tailored list of skills, categorized as follows:

            Technical: Comma-delimited list of skills.
            Leadership and People Management: Comma-delimited list of skills.
            Business Domain Knowledge: Comma-delimited list of skills.
            Soft Skills: Comma-delimited list of skills.
            AI/ML Skills: Comma-delimited list of skills.
            Ethics and Governance: Comma-delimited list of skills."""
            map_data = self.build_default_map()

            parser = DelimitedListOutputParser('\n')

            prompt_template = self._load_and_prepare_prompt(
                'skills', map_data, parser, self.msg_chain)

            skills_out = self._invoke_chain(prompt_template, parser=parser, llm=self.llm_cheap)
            list_of_skills: List[Skill] = []
            for s in skills_out:
                sk = s.split(':')
                s = Skill(key=sk[0], value=sk[1] if len(sk)>1 else '')
                list_of_skills.append(s)

            self.resume.skills = list_of_skills
        except Exception as e:
            print(f'Exception in generate_tailored_skills_section_ai(). Error {e}')
        return '\n'.join([s.text() for s in self.resume.skills])

    def generate_career_summary_ai(self, n_words=250) -> str:
        print('In: generate_career_summary_ai()')
        try:
            map_data = self.build_default_map()
            map_data["n_words"] = n_words

            parser = DelimitedListOutputParser('\n')

            prompt_template = self._load_and_prepare_prompt(
                'career_summary', map_data, parser, self.msg_chain)

            self.resume.career_summary = self._invoke_chain(prompt_template, parser, llm=self.llm_good)

        except Exception as e:
            printred(f"Error generating career summary: {e}")
            self.logger.error(f"Error generating career summary: {e}")

        return '\n'.join(self.resume.career_summary)

    def generate_work_experience_key_achievements_ai(self, k, we):
        achivements = []
        try:
            map = self.build_default_map()
            map['n_lines'] = max(6 - 1 * k, 2)  # longer description in more recent time
            map["exp_title"]= we.position
            map["work_experience"] = we.text()

            parser = DelimitedListOutputParser('\n')
            prompt = self._load_and_prepare_prompt(prompt_key='work_experience_key_results', map_data=map,
                                                   parser=parser, msg_chain=self.msg_chain)
            we.key_responsibilities = self._invoke_chain(prompt, parser, msg_chain=self.msg_chain, llm=self.llm_cheap)

        except Exception as e:
            self.logger.error(
                f'Exception while processing work experience key achievements for {we.position} at {we.company}')
            printcolor(
                f'Exception while processing work experience key achievements for {we.position} at {we.company}',
                'blue')
        return we.key_responsibilities

    def generate_work_experience_summary_ai(self, k: int, we: WorkExperience, min_words: int = 30,
                                            start_words: int = 100, step_words: int = 15):
        summary = ''
        try:
            # region work summary
            # compute how many words to generate for the summary. As things are getting older, less text is being generated
            map = self.build_default_map()
            map["n_words"] = max(start_words - step_words * k, min_words)  # longer description in more recent time
            map["work_title"] = we.position
            map['work_experience'] = we.text()
            parser = StrOutputParser()

            prompt = self._load_and_prepare_prompt(prompt_key='work_experience_summary', map_data=map,
                                                   parser=parser, msg_chain=self.msg_chain)
            summary = self._invoke_chain(prompt, parser, msg_chain=self.msg_chain, llm=self.llm_good)
        except Exception as e:
            self.logger.error(
                f'Exception while processing work experience summary for {we.position} at {we.company} Error:{e}')
            printcolor(
                f'Exception while processing work experience summary for {we.position} at {we.company} Error:{e}',
                'blue')
        return summary

    def generate_career_highlights_ai(self, msg_chain: List[tuple[str, str]] = [], n_words=40) -> str:
        print('In: generate_career_highlights_ai()')
        try:
            map = self.build_default_map()
            map["n_words"] = n_words

            parser = DelimitedListOutputParser('\n')
            prompt = self._load_and_prepare_prompt(prompt_key='career_highlights', map_data=map,
                                                   parser=parser, msg_chain=self.msg_chain)

            ch = self._invoke_chain(prompt, parser, msg_chain=self.msg_chain, llm = self.llm_good)

            chh = []
            for c in ch:
                if c:
                    # if isinstance(c, CareerHighlights):
                    #     chh.append(ch)
                    if isinstance(c, str):
                        cc = c.split(":")
                        k = cc[0].strip()
                        if len(cc) > 1:
                            v = cc[1].strip()
                        else:
                            v = ""
                        chh.append(KeyValue(key=k, value=v))
            self.resume.career_highlights = chh

        except Exception as e:
            printred(f'Exception in career_highlights. Error {e} {traceback.format_exc()}')
        return '\n'.join([ch.text() for ch in self.resume.career_highlights if ch])

    def generate_html_resume(self, css = None) -> str:
        print(f'In gpt_resume_job_description.generate_html_resume()', flush=True)
        # Define a list of functions to execute in parallel

        #region Generation functions
        def styles_css_fn(css) -> str:
            css_content = ""
            try:
                with open(css, 'r') as f:
                    css_content = clean_html_string(f.read())
            except Exception as e:
                self.logger.error(f"Error during opening css file: {css_file}")
                print(f"Error during opening css file: {css_file}"
                      f"error: {e}")
            return css_content

        def header_fn():
            return self.generate_header()

        def education_fn():
            return self.generate_education_section()

        def work_experience_fn():
            return self.generate_work_experience_section_ai()

        def side_projects_fn():
            return self.generate_side_projects_section()

        def achievements_fn():
            return self.generate_achievements_section_ai()

        def additional_skills_fn():
            return self.generate_additional_skills_section()

        def applicant_name_header_fn():

            return self.generate_applicant_name_header()

        def application_title_fn():
            self.resume.resume_title = self.job_title
            print(f'Setting resume title to {self.job_title}')
            return self.resume.resume_title
            #return self.generate_application_title_ai()

        def career_summary_fn():

            return self.generate_career_summary_ai()

        def career_highlights_fn():
            highlights = self.generate_career_highlights_ai()

            return highlights

        def career_timeline_fn():
            return self.generate_career_timeline()
        def education_summary_fn():
            return self.generate_education_summary()
        def education_x_fn():
            return self.generate_education_summary()
        def professional_experience_fn():
            #return self.generate_professional_experience()
            out = ''
            for k in range(len(self.resume.work_experiences)):
                #self.resume.work_experiences[k] = self.generate_work_experience_ai(self.resume.work_experiences[k],k)
                kr = self.generate_work_experience_key_achievements_ai(k, self.resume.work_experiences[k] )
                self.resume.work_experiences[k].key_responsibilities = kr

            for k in range(len(self.resume.work_experiences)):
                self.resume.work_experiences[k].summary = self.generate_work_experience_summary_ai(k, self.resume.work_experiences[k])

            return '\n\n'.join([we.text() for we in self.resume.work_experiences])
        def academic_appointments_fn():
            return self.generate_academic_appointments()
        def skills_fn():
            return self.generate_tailored_skills_section_ai()
        def languages_fn():
            return self.generate_language_skills_section()
        def footer_fn():
            return self.generate_footer()

        def position_hierarchy_fn():
            return self.position_hierarchy_ai()

        def create_cover_content_fn():
            self.resume.cover_text = """
            I am genuinely excited about the opportunity to contribute to [Company Name] as a [Job Title]. 
            I would welcome the chance to discuss how my skills and experiences align with your needs in more detail. 
            I am available at your earliest convenience for an interview and can provide any additional information you require. 
            Thank you for considering my application. I look forward to the opportunity to contribute to your team
            """
            self.resume.cover_text = self.generate_cover_letter_content_ai()
            return self.resume.cover_text

        def create_filename():
            # Get the current time
            now = datetime.now()
            # Format the time as YYYYMMDD.hh.mm.sss
            formatted_time = now.strftime("%Y%m%d.%H.%M.%f")[:-3]  # Trim the last 3 digits for milliseconds
            # Create the file name
            file_name = f"finalresume.{formatted_time}"
            return file_name

        # endregion

        self.add_system_prompt(map={"job_title":self.job.title, "job_description":self.job.job_description_summary})

        # Create a dictionary to map the function names to their respective callables
        functions = {
            "applicant_name_header": applicant_name_header_fn,
            "application_title":application_title_fn,
            "skills":skills_fn,
            "achievements": achievements_fn,
            "professional_experience": professional_experience_fn,
            "career_highlights": career_highlights_fn,
            "career_summary": career_summary_fn,
            "cover": create_cover_content_fn
            # #"career_timeline":career_timeline_fn,
            # #"education_summary":education_summary_fn,
            # #"education": education_x_fn,
            # #"academic_appointments":academic_appointments_fn,
            # #"languages": languages_fn,
            # #"footer":footer_fn
        }

        results = {}
        USE_THREADPOOL = False
        if USE_THREADPOOL:
            # Use ThreadPoolExecutor to run the functions in parallel
            with ThreadPoolExecutor() as executor:
                future_to_section = {executor.submit(fn): section for section, fn in functions.items()}
                #results = {}
                for future in as_completed(future_to_section):
                    section = future_to_section[future]
                    try:
                        results[section] = future.result()
                    except Exception as exc:
                        self.logger.error(f'{section} generated an error')
                        print(f'{section} generated an exception: {exc}')
        else:
            for section, fn in functions.items():
                if callable(fn):
                    try:
                        print(f'About to execute section: {section}')
                        res = fn()
                        results[section] = res
                    except Exception as e:
                        print(f'Exception while executing {section}. Error {e}, {traceback.format_exc()}')
                        self.logger.error(f'Exception while executing {section}')

                else:
                    results[section] = fn

        fullresume = HtmlResume(self.resume).html_doc(css_file = css, css_inline=True)
        cover = HtmlCover(self.resume).html_doc(css_file = css, css_inline=True)
        if not fullresume:
            fullresume_template=None
            fullresume=None
            try:
                with open(template_file, 'r') as file:
                    fullresume_template = file.read().replace('\n', '')
            except Exception as e:
                self.logger.error(f"Error during opening template file: {template_file}")
                print(f"Error during opening template file: {template_file}"
                      f"error: {e}")

            if fullresume_template is not None:
                fullresume=fullresume_template.format(
                    applicant_name_header = results["applicant_name_header"],
                    application_title = results["application_title"],
                    career_summary = results["career_summary"],
                    career_timeline = results["career_timeline"],
                    education_summary = results["education_summary"],
                    professional_experience = results["professional_experience"],
                    achievements = results["achievements"],
                    education = results["education"],
                    skills = results["skills"],
                    languages = results["languages"]
                )

            else:
                try:
                    with open(fullresume_template, 'r') as file:
                        fullresume = file.read().replace('\n', '')
                except Exception as e:
                    self.logger.error(f"Error during opening template file: {template_file}")
                    print(f"Error during opening template file: {template_file}"
                          f"error: {e}")
                    sys.exit()

            # Construct the final HTML resume from the results

    #        fullresume = (
    #            f"<body>\n"
    #            f"  {results['header']}\n"
    #            f"  <main>\n"
    #            f"    {results['education']}\n"
    #            f"    {results['work_experience']}\n"
    #            f"    {results['side_projects']}\n"
    #            f"    {results['achievements']}\n"
    #            f"    {results['additional_skills']}\n"
    #            f"  </main>\n"
    #            f"</body>"
     #       )
            fname_full = os.path.join(os.path.dirname(__file__),'resume_output', create_filename())
            print(f'constructed final html resume. Saving to the file: {fname_full}')
            try:
                # Save the file with the generated filename
                with open(fname_full, 'w', encoding='utf-8') as file:
                    file.write(fullresume)
            except Exception as e:
                self.logger.error(f"Error during saving html file: {fname_full}")
                print(f"Error during saving html file: {fname_full}"
                          f"error: {e}")

        self.job.save()
        return fullresume, cover

    def llm_pydantic_invoke(self, pydantic_object, prompt_string_template, llm, **kwargs):
        parser = PydanticOutputParser(pydantic_object=pydantic_object)
        prompt_template = self._preprocess_template_string(prompt_string_template, add_format_instructions_template=True )

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=[list(kwargs.keys())],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | llm
        output = chain.invoke(**kwargs)

        obj = parser.invoke(output)

        return obj

