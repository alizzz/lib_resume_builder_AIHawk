import json
import os
import tempfile
import textwrap
import time
import re
import copy
from datetime import datetime
from typing import Dict, List
from langchain_community.document_loaders import TextLoader
from langchain_core.messages.ai import AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from lib_resume_builder_AIHawk.config import global_config
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
#from lib_resume_builder_AIHawk.resume_template import resume_template_job_experience, resume_template
import lib_resume_builder_AIHawk.resume_templates.resume_template
from utils import printcolor
import os
import os.path
import sys



load_dotenv()
#ToDo: make it read config file
template_file = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_template.html')
css_file = os.path.join(os.path.dirname(__file__), 'resume_style', 'style_al_hawk.css')
fullresume_file_backup = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_sample.html')

#removes \n and multiple spaces from a string
def clean_html_string(html_string):
    # Remove newline characters and leading/trailing spaces
    cleaned_string = html_string.replace("\n", " ").strip()

    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)

    return cleaned_string

class LLMLogger:
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    @staticmethod
    def log_request(prompts, parsed_reply: Dict[str, Dict]):
        calls_log = global_config.LOG_OUTPUT_FILE_PATH / "open_ai_calls.json"
        if isinstance(prompts, StringPromptValue):
            prompts = prompts.text
        elif isinstance(prompts, Dict):
            # Convert prompts to a dictionary if they are not in the expected format
            prompts = {
                f"prompt_{i+1}": prompt.content
                for i, prompt in enumerate(prompts.messages)
            }
        else:
            prompts = {
                f"prompt_{i+1}": prompt.content
                for i, prompt in enumerate(prompts.messages)
            }

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Extract token usage details from the response
        token_usage = parsed_reply["usage_metadata"]
        output_tokens = token_usage["output_tokens"]
        input_tokens = token_usage["input_tokens"]
        total_tokens = token_usage["total_tokens"]

        # Extract model details from the response
        model_name = parsed_reply["response_metadata"]["model_name"]
        prompt_price_per_token = 0.00000015
        completion_price_per_token = 0.0000006

        # Calculate the total cost of the API call
        total_cost = (input_tokens * prompt_price_per_token) + (
            output_tokens * completion_price_per_token
        )

        # Create a log entry with all relevant information
        log_entry = {
            "model": model_name,
            "time": current_time,
            "prompts": prompts,
            "replies": parsed_reply["content"],  # Response content
            "total_tokens": total_tokens,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_cost": total_cost,
        }

        # Write the log entry to the log file in JSON format
        with open(calls_log, "a", encoding="utf-8") as f:
            json_string = json.dumps(log_entry, ensure_ascii=False, indent=4)
            f.write(json_string + "\n")


class LoggerChatModel:

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def __call__(self, messages: List[Dict[str, str]]) -> str:
        reply = self.llm(messages)
        parsed_reply = self.parse_llmresult(reply)
        LLMLogger.log_request(prompts=messages, parsed_reply=parsed_reply)
        return reply

    def parse_llmresult(self, llmresult: AIMessage) -> Dict[str, Dict]:
        content = llmresult.content
        response_metadata = llmresult.response_metadata
        id_ = llmresult.id
        usage_metadata = llmresult.usage_metadata
        parsed_result = {
            "content": content,
            "response_metadata": {
                "model_name": response_metadata.get("model_name", ""),
                "system_fingerprint": response_metadata.get("system_fingerprint", ""),
                "finish_reason": response_metadata.get("finish_reason", ""),
                "logprobs": response_metadata.get("logprobs", None),
            },
            "id": id_,
            "usage_metadata": {
                "input_tokens": usage_metadata.get("input_tokens", 0),
                "output_tokens": usage_metadata.get("output_tokens", 0),
                "total_tokens": usage_metadata.get("total_tokens", 0),
            },
        }
        return parsed_result

class LLMResumeJobDescription:
    def __init__(self, openai_api_key, strings):
        self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.8))
        self.llm_embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.strings = strings
        self.pos_hierarchy_list = None
        self.resume_ = None

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        # Preprocess a template string to remove unnecessary indentation.
        return textwrap.dedent(template)

    def set_resume(self, resume):
        self.resume_ = copy.deepcopy(resume)
        #printcolor(f'in LLMResumeJobDescription.setresume::self._resume.experience_details[0].position:{self._resume.experience_details[0].position}', "magenta")
        self.pos_hierarchy_list = self.generate_position_hierarchy_ai()
        self.update_positions_automl()
        #printcolor(f"in LLMResumeJobDescription.set_resume::self.resume_.experience_details[0].position:{self.resume_.experience_details[0].position}, self.pos_hierarchy_list:':{self.pos_hierarchy_list}", "magenta")

    def set_job_description_from_url(self, url_job_description):
        printcolor(
            f'in LLMResumeJobDescription.set_job_description_from_url', "blue")

        from lib_resume_builder_AIHawk.utils import create_driver_selenium
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
        prompt = PromptTemplate(
            template="""
            You are an expert job description analyst. Your role is to meticulously analyze and interpret job descriptions. 
            After analyzing the job description, answer the following question in a clear, and informative manner.
            
            Question: {question}
            Job Description: {context}
            Answer:
            """,
            input_variables=["question", "context"]
        )
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        context_formatter = vectorstore.as_retriever() | format_docs
        question_passthrough = RunnablePassthrough()
        chain_job_description= prompt | self.llm_cheap | StrOutputParser()
        summarize_prompt_template = self._preprocess_template_string(self.strings.summarize_prompt_template)
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
        self.job_description = result
        print(f'Job description:\n{result}')

    def set_job_description_from_text(self, job_description_text):
        prompt = ChatPromptTemplate.from_template(self.strings.summarize_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({"text": job_description_text})
        self.job_description = output



    def _generate_header_gpt(self) -> str:
        header_prompt_template = self._preprocess_template_string(
            self.strings.prompt_header
        )
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "personal_information": self.resume_.personal_information,
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
        education_prompt_template = self._preprocess_template_string(
            self.strings.prompt_education
        )
        prompt = ChatPromptTemplate.from_template(education_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "education_details": self.resume_.education_details,
            "job_description": self.job_description
        })
        return output
    def generate_career_summary_ai(self)->str:
        print('In: generate_career_summary_ai()' )
        career_summary_prompt_template = self._preprocess_template_string(
            self.strings.prompt_career_summary
        )

        prompt = ChatPromptTemplate.from_template(career_summary_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "education_summary": self.resume_.education_details,
            "job_description": self.job_description,
            "experience_details": self.resume_.experience_details,
            "min_tech_experience": self.resume_.personal_information.years_technical_experience,
            "min_mgmt_experience": self.resume_.personal_information.years_mgmt_experience
        })
        return output

    def generate_work_experience_section_summary_ai(self, work_experience="", skills="", position_title="", job_desc="") -> str:
        work_experience_summary_prompt_template = self._preprocess_template_string(
            self.strings.prompt_professional_experience_role_summary
        )
        prompt = ChatPromptTemplate.from_template(work_experience_summary_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        raw_output = chain.invoke({
            "job_desc": job_desc,
            "work_experience": work_experience,
            "position_title": position_title,
            "skills": skills
        })
        output = clean_html_string(raw_output)
        return output

    def generate_work_experience_section_ai(self, work_experience="", skills="", position_title="", job_desc="") -> str:
        work_experience_prompt_template = self._preprocess_template_string(
            self.strings.prompt_work_experience
        )
        prompt = ChatPromptTemplate.from_template(work_experience_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        raw_output = chain.invoke({
            "experience_details": work_experience,
            "job_description": job_desc,
            "skills": skills,
            "position": position_title
        })
        output = clean_html_string(raw_output)
        return output

    def generate_side_projects_section(self) -> str:
        side_projects_prompt_template = self._preprocess_template_string(
            self.strings.prompt_side_projects
        )
        prompt = ChatPromptTemplate.from_template(side_projects_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "projects": self.resume_.projects,
            "job_description": self.job_description
        })
        return output

    def generate_achievements_section(self) -> str:
        achievements_prompt_template = self._preprocess_template_string(
            self.strings.prompt_achievements
        )

        if self.resume_.achievements:
            prompt = ChatPromptTemplate.from_template(achievements_prompt_template)
            chain = prompt | self.llm_cheap | StrOutputParser()
            output = chain.invoke({
                "achievements": self.resume_.achievements,
                "certifications": self.resume_.achievements,
                "job_description": self.job_description
            })
            return output

    def generate_additional_skills_section(self) -> str:

        def split_string(s, sep=','):
            return [x.strip() for x in s.split(sep)]

        additional_skills_prompt_template = self._preprocess_template_string(
            self.strings.prompt_additional_skills
        )
        
        skills = set()

        if self.resume_.experience_details:
            for exp in self.resume_.experience_details:
                if exp.skills_acquired:
                    skills.update(exp.skills_acquired)

        if self.resume_.education_details:
            for edu in self.resume_.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())

        #additional skills
        skill_list = [x.skill_lst for x in self.resume_.skills]
        for k in skill_list:
            skills.update([s.strip() for s in k.split(',')])

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
        #    'prompt engineering, AI literacy (understanding concepts and terminology), Human-AI interaction, Ethical AI development and implementation, AI ethics and governance, Generative AI, genAI')])
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
            "languages": self.resume_.languages,
            "interests": self.resume_.interests,
            "skills": skills,
            "job_description": self.job_description
        })

        #print(f"skills output:{output}")
        return output


    #generate static header based on applicant information
    #ToDo: load from configuration
    def generate_applicant_name_header(self):
        output = f'<span style="font-variant: small-caps"><b>{self.resume_.personal_information.name} {self.resume_.personal_information.surname}</b></span> • {self.resume_.personal_information.phone_prefix} {self.resume_.personal_information.phone} • {self.resume_.personal_information.email}'
        return output

    #generate title based on position name
    def generate_application_title_ai(self):
        application_title_template = self._preprocess_template_string(
            self.strings.prompt_application_title
        )
        prompt = ChatPromptTemplate.from_template(application_title_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "job_description": self.job_description
        })
        return output

    def generate_position_hierarchy_ai(self):
        gpt_template = self._preprocess_template_string(
            self.strings.prompt_position_hierarchy
        )
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
        def _position_automl(current_position:str, substitute_positions):
            if substitute_positions is None: return current_position
            num_subs = len(substitute_positions)
            case_statements = {
                "L0": substitute_positions[0],
                "L1": substitute_positions[1] if num_subs>2 else substitute_positions[num_subs - 1],
                "L2": substitute_positions[2] if num_subs>3 else substitute_positions[num_subs - 1],
                "L3": substitute_positions[3] if num_subs>4 else substitute_positions[num_subs - 1],
                "L4": substitute_positions[4] if num_subs>5 else substitute_positions[num_subs - 1]
            }
            return case_statements.get(current_position, current_position)

        for k in range(len(self.resume_.experience_details)):
            position = self.resume_.experience_details[k].position
            if position in ["L0","L1","L2","L3"]:
                new_pos = _position_automl(position, self.pos_hierarchy_list)
                self.resume_.experience_details[k].position = new_pos


    def generate_application_title(self):
        output=f'Head of Data Science, Analytics, ML Engineering'
        return output

    #ToDo: read from config or build based on job description
    #ToDo: genAI
    def generate_career_summary(self):
        raw_output = """
        <b>I am a seasoned AI/ML executive who drives R&amp;D and innovative solutions
        through visionary leadership, broad technical expertise, and
        strategic collaboration</b>. Known for loyalty, impactful results,
        and a supportive, even-tempered approach for the last two
        dozen years I deliver sustainable growth with adaptability and
        continuous learning, fostering and nurturing high-performing
        internationally distributed teams, extensive collaboration, and
        x-functional alignment. </p>
        <p align="left" class="career-summary">During
        my entire career I’ve been translating business requirements into
        technical definitions, leading advanced R&amp;D projected and
        converting it to ground breaking products. I am proficient in the
        Artificial Intelligence, Machine Learning, Database, Software and
        Networking technology. I have a proven track record in building
        robust product analytics, data science, and developing cutting-edge
        ML algorithms such as computer vision, NLP, classification,
        supervised/unsupervised learning, and anomaly detection to deliver
        business impact by solving customer problems and growing revenue. I
        am skilled in data stewardship,  business analytics, and building AI
        as-a-service in the cloud. I have a proven success in delivering
        impactful, value-adding solutions, overseeing full product
        development cycles, and meeting critical milestones. I have a deep
        passion for research, tolerance for ambiguity, and a positive &quot;can
        do&quot; attitude with a strong business orientation.
        </p>
        <p align="left" class="career-summary">
        As you can see below my track record includes over <b>25 
        years of progressive technical and business experience</b> 
        delivering innovative, business-defining products, and <b>18 years of successful team management and engineering leadership</b> 
        specifically focusing on building and nurturing diverse,
        geographically distributed teams of engineers and scientists. I
        demonstrated ability to build a common culture based on trust,
        ownership and accountability. I excel in team building, resource
        orchestration, and aligning teams with strategic goals to ensure
        seamless execution, building a great value for customers and
        increasing revenue.</p>
        """
        output = clean_html_string(raw_output)
        return output

    #ToDo: read from config
    def generate_career_timeline(self):
        exp_timeline_html = ""
        for exp in self.resume_.experience_details:
            exp_timeline_html+=f"""<tr>
                <td align="left"><b><i>{exp.company}</i></b></td>
                <td align="left"><i>{exp.industry}</i></td>
                <td align="left"><b>{exp.position}</b></td>
                <td align="right">{exp.location}</td>
                <td align="right">{exp.employment_period}</td>
            </tr>"""
        output_html_raw= f"""
        <table width="760" cellpadding="0" cellspacing="0">
            <col width="110"/>
            <col width="140"/>
            <col width="240"/>
            <col width="120"/>
            <col width="150"/>
            {exp_timeline_html}
        </table>
        """
        output = clean_html_string(output_html_raw)
        return output

    def generate_education_summary(self):
        #print("in generate_education_summary")
        edu_timeline_html = '<ul class="education-summary">'
        for edu in self.resume_.education_details:
            edu_timeline_html += f'<li><p align="justify"><b>{edu.degree}</b>,<i> {edu.field_of_study}</i> {edu.university}</p></li>'
        edu_timeline_html+='</ul>'
        output = clean_html_string(edu_timeline_html)
        return output

    def generate_language_skills_section(self):
        #print("in generate_language_skills_section")
        edu_timeline_html = '<ul class="skills">'
        if self.resume_.languages is None or len(self.resume_.languages)==0:
            return clean_html_string(f'{edu_timeline_html}<li><b>"English</b>:Native</li></ul>')

        for l in self.resume_.languages:
            edu_timeline_html+=f"<li><b>{l.language}</b>:{l.proficiency}</li>"

        edu_timeline_html+="</ul>"
        output = clean_html_string(edu_timeline_html)
        return output

    def generate_academic_appointments(self):
        output=""
        return output

    def generate_professional_experience_ai(self):

        raw_html = "<div>"
        for exp in self.resume_.experience_details:
            skills=""
            key_resp = ""
            try:
                if exp.summary is not None:
                    key_resp+=exp.summary + '/n'

                if exp.key_responsibilities is not None:
                    key_resp = ('\n').join(exp.key_responsibilities)
            except Exception as e:
                printcolor(f"Exception while processing key responsibiity for {exp.company}:{exp.position}. Exception: {e}")

            try:
                if exp.skills_acquired is not None:
                    skills += '\n'.join(exp.skills_acquired)

                if self.resume_.skills is not None:
                    for s in self.resume_.skills:
                        skills+=s.skill_lst
            except Exception as e:
                printcolor(f"Exception while processing skills for {exp.company}:{exp.position}. Exception: {e}")

            # --- Position Header
            raw_html += f"""<div>
                        <table width="720" cellpadding="0" cellspacing="0">
                            <col width="140"/>
                            <col width="240"/>
                            <col width="100"/>
                            <col width="75"/>
                            <tr>
                                <td align="left"><b><i>{exp.company}</i></b></td>
                                <td align="left"><b>{exp.position}</b></td>
                                <td align="right">{exp.location}</td>
                                <td align="right">{exp.employment_period}</td>
                        </table>"""
            # --- Position summary ---#
            try:
                try:
                    exp_summary_ai = self.generate_work_experience_section_summary_ai(
                        work_experience=key_resp, skills=skills, position_title=exp.position, job_desc=self.job_description
                    )
                    if exp_summary_ai is not None and len(exp_summary_ai)>0:
                        raw_html+= f"""<div align="justify" class="prof-exp-details">{exp_summary_ai}</div>"""
                except Exception as e:
                    raw_html += f"""<div align="justify" class="prof-exp-details">{exp.summary}</div>"""
                    printcolor(f'Experience section summary thrown an exception for {exp.position} for {exp.company}. Exception {e}', "yellow")

                # --- Position responsibilities ---#
                responsibility_html = self.generate_work_experience_section_ai(
                        work_experience=key_resp, skills=skills, position_title=exp.position, job_desc=self.job_description)

                if len(responsibility_html) > 0:
                    raw_html += f"""<div><ul>{responsibility_html}</ul></div>"""
            except Exception as e:
                printcolor(f"Exception while processing work experience section for {exp.company}:{exp.position}. Exception:{e}")

            raw_html += "</div>"
        raw_html += "</div>"
        output = clean_html_string(raw_html)
        printcolor(f'work experience:{output}', "magenta")
        return output

    #ToDo: 1. read experience from config
    #ToDo: 2. use genAI. Generate updated experience based on job description
    def generate_professional_experience(self):
        raw_html = "<div>"
        for exp in self.resume_.experience_details:
        # --- Position Header
            raw_html+=f"""<div>
                <table width="720" cellpadding="0" cellspacing="0">
                    <col width="140"/>
                    <col width="240"/>
                    <col width="100"/>
                    <col width="75"/>
                    <tr>
                        <td align="left"><b><i>{exp.company}</i></b></td>
                        <td align="left"><b>{exp.position}</b></td>
                        <td align="right">{exp.location}</td>
                        <td align="right">{exp.employment_period}</td>
                </table>"""
            #--- Position summary ---#
            try:
                raw_html += f"""<div align="justify" class="prof-exp-details">{exp.summary}</div>"""
            except Exception as e:
                print(f'Experience summary is not set for {exp.position} for {exp.company}')

            #--- Position responsibilities ---#

            responsibility_html = ""
            try:
                for responsibility in exp.key_responsibilities:
                    responsibility_html +=f'<li><p align="justify">{responsibility}</p></li>'
            except Exception as e:
                print(f"Exception while processing responsibilities for {exp.position} for {exp.company}. Exception {e}")

            if len(responsibility_html)>0:
                    raw_html+=f"""<div><ul>{responsibility_html}</ul></div>"""

            raw_html += "</div>"
        raw_html+="</div>"
        output = clean_html_string(raw_html)
        return output

    def generate_footer(self):
        output=""
        return output

    def generate_html_resume(self) -> str:
        print(f'In gpt_resume_job_description.generate_html_resume()', flush=True)
        # Define a list of functions to execute in parallel

        def styles_css_fn() -> str:
            css = ""
            try:
                with open(css_file, 'r') as f:
                    css = clean_html_string(f.read())
            except Exception as e:
                print(f"Error during opening css file: {css_file}"
                      f"error: {e}")
            return css

        def header_fn():
            return self.generate_header()

        def education_fn():
            return self.generate_education_section()

        def work_experience_fn():
            return self.generate_work_experience_section_ai()

        def side_projects_fn():
            return self.generate_side_projects_section()

        def achievements_fn():
            return self.generate_achievements_section()

        def additional_skills_fn():
            return self.generate_additional_skills_section()

        def applicant_name_header_fn():
            return self.generate_applicant_name_header()

        def application_title_fn():
            return self.generate_application_title_ai()

        def career_summary_fn():
            return self.generate_career_summary_ai()
        def career_timeline_fn():
            return self.generate_career_timeline()
        def education_summary_fn():
            return self.generate_education_summary()
        def education_x_fn():
            return self.generate_education_summary()
        def professional_experience_fn():
            #return self.generate_professional_experience()
            return self.generate_professional_experience_ai()
        def academic_appointments_fn():
            return self.generate_academic_appointments()
        def skills_fn():
            return self.generate_additional_skills_section()
        def languages_fn():
            return self.generate_language_skills_section()
        def footer_fn():
            return self.generate_footer()

        def position_hierarchy_fn():
            return self.position_hierarchy_ai()

        # Create a dictionary to map the function names to their respective callables
        functions = {
            "applicant_name_header": applicant_name_header_fn,
            "application_title":application_title_fn,
            "career_summary": career_summary_fn,
            "career_timeline":career_timeline_fn,
            "education_summary":education_summary_fn,
            "education": education_x_fn,
            "professional_experience":professional_experience_fn,
            "academic_appointments":academic_appointments_fn,
            "achievements":achievements_fn,
            "skills":skills_fn,
            "languages": languages_fn,
            "footer":footer_fn
        }


#        "header": header_fn,
#            "education": education_fn,
#            "work_experience": work_experience_fn,
#            "side_projects": side_projects_fn,
#            "achievements": achievements_fn,
#            "additional_skills": additional_skills_fn
#       }
#
        # Use ThreadPoolExecutor to run the functions in parallel
        with ThreadPoolExecutor() as executor:
            future_to_section = {executor.submit(fn): section for section, fn in functions.items()}
            results = {}
            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    results[section] = future.result()
                except Exception as exc:
                    print(f'{section} generated an exception: {exc}')

        fullresume_template=None
        fullresume=None
        try:
            with open(template_file, 'r') as file:
                fullresume_template = file.read().replace('\n', '')
        except Exception as e:
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

        def create_filename():
            # Get the current time
            now = datetime.now()
            # Format the time as YYYYMMDD.hh.mm.sss
            formatted_time = now.strftime("%Y%m%d.%H.%M.%f")[:-3]  # Trim the last 3 digits for milliseconds
            # Create the file name
            file_name = f"finalresume.{formatted_time}"
            return file_name

        fname_full = os.path.join(os.path.dirname(__file__),'resume_output', create_filename())
        print(f'constructed final html resume. Saving to the file: {fname_full}')
        try:
            # Save the file with the generated filename
            with open(fname_full, 'w') as file:
                file.write(fullresume)
        except Exception as e:
            print(f"Error during saving html file: {fname_full}"
                      f"error: {e}")

        return fullresume