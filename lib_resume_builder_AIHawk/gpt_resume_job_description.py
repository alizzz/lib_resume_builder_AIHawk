import json
import os
import tempfile
import textwrap
import time
import re
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
import os
import os.path
import sys


load_dotenv()
#ToDo: make it read config file
template_file = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_template.html')
css_file = os.path.join(os.path.dirname(__file__), 'resume_style', 'style_al_hawk.css')
full_resume_file_backup = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_sample.html')

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

    @staticmethod
    def _preprocess_template_string(template: str) -> str:
        # Preprocess a template string to remove unnecessary indentation.
        return textwrap.dedent(template)

    def set_resume(self, resume):
        self.resume = resume

    def set_job_description_from_url(self, url_job_description):
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
        text_splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
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
        education_prompt_template = self._preprocess_template_string(
            self.strings.prompt_education
        )
        prompt = ChatPromptTemplate.from_template(education_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "education_details": self.resume.education_details,
            "job_description": self.job_description
        })
        return output
    def generate_career_summary_ai(self)->str:
        career_summary_prompt_template = self._preprocess_template_string(
            self.string.prompt_career_summary
        )
        prompt = ChatPromptTemplate.from_template(career_summary_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "career_summary": self.resume.education_details,
            "job_description": self.job_description
        })
        return output

    def generate_work_experience_section(self) -> str:
        work_experience_prompt_template = self._preprocess_template_string(
            self.strings.prompt_working_experience
        )
        prompt = ChatPromptTemplate.from_template(work_experience_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "experience_details": self.resume.experience_details,
            "job_description": self.job_description
        })
        return output

    def generate_side_projects_section(self) -> str:
        side_projects_prompt_template = self._preprocess_template_string(
            self.strings.prompt_side_projects
        )
        prompt = ChatPromptTemplate.from_template(side_projects_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "projects": self.resume.projects,
            "job_description": self.job_description
        })
        return output

    def generate_achievements_section(self) -> str:
        achievements_prompt_template = self._preprocess_template_string(
            self.strings.prompt_achievements
        )

        if self.resume.achievements: 
            prompt = ChatPromptTemplate.from_template(achievements_prompt_template)
            chain = prompt | self.llm_cheap | StrOutputParser()
            output = chain.invoke({
                "achievements": self.resume.achievements,
                "certifications": self.resume.achievements,
                "job_description": self.job_description
            })
            return output

    def generate_additional_skills_section(self) -> str:
        additional_skills_prompt_template = self._preprocess_template_string(
            self.strings.prompt_additional_skills
        )
        
        skills = set()

        if self.resume.experience_details:
            for exp in self.resume.experience_details:
                if exp.skills_acquired:
                    skills.update(exp.skills_acquired)

        if self.resume.education_details:
            for edu in self.resume.education_details:
                if edu.exam:
                    for exam in edu.exam:
                        skills.update(exam.keys())
        prompt = ChatPromptTemplate.from_template(additional_skills_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "languages": self.resume.languages,
            "interests": self.resume.interests,
            "skills": skills,
            "job_description": self.job_description
        })
        
        return output


    #generate static header based on applicant information
    #ToDo: load from configuration
    def generate_applicant_name_header(self):
    #       applicant = {
    #       name:"Alexander",
    #       surname:"Liss",
    #       suffix:", PhD, MBA",
    #       phone:"(646) 867 0808",
    #       email:"hawk@talkdirect.net"
     #   }
        output = f'<span style="font-variant: small-caps"><b>Alexander Liss</b></span> • +1 (646) 867 0808 • hawk@talkdirect.net'
        return output

    #ToDo: generate based on position name
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
        raw_output="""
        <table width="720" cellpadding="0" cellspacing="0">
            <col width="140"/>
            <col width="140"/>
            <col width="240"/>
            <col width="100"/>
            <col width="75"/>
            <tr>
                <td align="left"><b><i>HyperC</i></b></td>
                <td align="left"><i>AI Strategy and Product, Data Science, ML Engineering</i></td>
                <td align="left"><b>Manager AIML Engineering</b></td>
                <td align="right">San Francisco Bay, CA</td>
                <td align="right">2023-2024</td>
            </tr>
            <tr>
                <td align="left"><b><i>Google</i></b></td>
                <td align="left"><i>Data Science, Engineering</i></td>
                <td align="left"><b>Head of Data Science, CX lab</b></td>
                <td align="right">Mountain View, CA</td>
                <td align="right">2021-2023</td>
            </tr>
            <tr>
                <td align="left"><b><i>Tensorsoft</i></b></td>
                <td align="left"><i>Data Science, AIML, Eng</i></td>
                <td align="left"><b>Co-founder, CTO and Lead Data Science Engineer</b></td>
                <td align="right">Mountain View, CA</td>
                <td align="right">2016-2021</td>
            </tr>
            <tr>
                <td align="left"><b><i>Keenetix</i></b></td>
                <td align="left"><i>Data Science, Analytics</i></td>
                <td align="left"><b>Product Manager, Data Science</b></td>
                <td align="right">Salem, NH</td>
                <td align="right">2010-2016</td>
            </tr>
            <tr>
                <td align="left"><b><i>Keenetix</i></b></td>
                <td align="left"><i>Data Science, Analytics</i></td>
                <td align="left"><b>Project Dev Manager, Data Science</b></td>
                <td align="right">Salem, NH</td>
                <td align="right">2008-2010</td>
            </tr>
            <tr>
                <td align="left"><b><i>Keenetix</i></b></td>
                <td align="left"><i>Data Science, Analytics</i></td>
                <td align="left"><b>Lead Dev Engineer, Data Science</b></td>
                <td align="right">Salem, NH</td>
                <td align="right">2005-2008</td>
            </tr>
            <tr>
                <td align="left"><b><i>Digimarc/Polaroid</i></b></td>
                <td align="left"><i>Image Analysis, Fraud Detection</i></td>
                <td align="left"><b>Principal Engineer, Data Eng Lead</b></td>
                <td align="right">Burlington, MA</td>
                <td align="right">2002-2005</td>
            </tr>
            <tr>
                <td align="left"><b><i>Comverse Technology</i></b></td>
                <td align="left"><i>DSP, Speech Recognition</i></td>
                <td align="left"><b>Principal Software Eng</b></td>
                <td align="right">Wakefield, MA</td>
                <td align="right">1999-2002</td>
            </tr>
        </table>
        """
        output = clean_html_string(raw_output)
        return output

    #ToDo: Load from configuration
    def generate_education_summary(self):
        raw_output="""
        <ul class="education-summary>
            <li><p align="justify"><b>Doctor of Philosophy (PhD)</b> Tufts University, MA</p></li>
            <li><p align="justify"><b>MBA</b> <i>Summa Cum Laude</i>, Babson College, MA</p></li>
            <li><p align="justify" class="education-summary"><b>Master of Science (MSc)</b> St.Petersburg, Russia</p></li>
        </ul>
        """
        output = clean_html_string(raw_output)
        return output

    def generate_academic_appointments(self):
        output=""
        return output

    #ToDo: 1. read experience from config
    #ToDo: 2. use genAI. Generate updated experience based on job description
    def generate_professional_experience(self):
        raw_output="""
            <table width="720" cellpadding="0" cellspacing="0">
                    <col width="140"/>
                    <col width="240"/>
                    <col width="100"/>
                    <col width="75"/>
                    <tr>
                        <td align="left"><b><i>HyperC</i></b></td>
                        <td align="left"><b>Manager ML Engineering</b></td>
                        <td align="right">San Francisco Bay, CA</td>
                        <td align="right">2023-Present</td>
                    </tr>
            </table>
            <div align="justify" class="prof-exp-details">
                <p><i>Leading a globally distributed engineering team</i></p>
                <p>Managed a global team dedicated to creating a state-of-the-art scalable distributed AI data and networking platform serving both B2B and B2C
                customers. Ensured full compliance with government regulations, privacy laws, and ethical standards.</p>
            <ul>
                <li><p align="justify" style="margin-bottom: 0.04in">Spearheaded the development of strategic direction and provided visionary leadership across various teams and stakeholders. Formulated and executed strategic objectives in alignment with executive goals, promoting a culture of collaboration and mutual support throughout the organization.</p></li>
                <li><p>Directed and nurtured a top-tier team, focusing on recruitment, motivation, and retention, transforming the team from a few individuals to over 40 in six years. Maintained attrition rates at twice below the industry average and achieved a 97% rate of employee satisfaction. Cultivated a culture of excellence, accountability, and high standards, fostering the development of new leadership within the team.</p></li>
                <li>Administered a multimillion-dollar budget throughout the lifecycle of pivotal projects, including the development and deployment of a <b>genAI ML platform</b>, an innovative <b>image processing and content extraction framework</b>, a cutting-edge <b>recommender system</b>, a <b>non-linear search engine</b>, and a comprehensive <b>experimentation</b> platform along with several <b>mobile applications</b>. Achieved a 90% reduction in operational costs and enhanced customer satisfaction by leveraging AI edge processing, substantially increasing business value and EBITDA.</li>
                <li><p>Developed and presented a compelling pitch deck during M&amp;A transactions, showcasing the company's leadership in AI technology and driving investor interest.</p></li>
            </ul></div>
            <table width="714" cellpadding="7" cellspacing="0">
                <col width="113"/>
                <col width="239"/>
                <col width="94"/>
                <col width="68"/>
                <tr>
                    <td align="left"><b><i>Google</i></b></td>
                    <td align="left"><b>Head of Data Science, CX lab</b></td>
                    <td align="right">Mountain View, CA</td>
                    <td align="right">2021-2023</td>
                </tr>
            </table>
            <div align="justify" class="prof-exp-details">
            <ul>
                <li><p align="left">Collaborated
                with marketing and product teams to build a clear vision for a
                data-driven customer segmentation project. Communicated the strategy
                internally and externally, aligning feedback, performance reviews,
                and resource allocation with the company's broader goals. The
                successful implementation of the project resulted in a 12.5%
                improvement in customer targeting accuracy and a 3.6% increase in
                customer retention.</p></li>
                <li><p align="left">Championed
                diversity and inclusion initiatives within the data science team,
                implementing an inclusive hiring strategy. Modeled inclusive
                behavior and facilitated respectful discussions to address bias in
                data analysis, ensuring equitable outcomes in the team's projects
                and discussions.</p></li>
                <li><p align="left" >Mentored
                and coached a team of data scientists to enhance their technical
                proficiency and foster a culture of continuous self-development.
                Encouraged research initiatives and “stretch” projects to
                explore innovative data analysis techniques. The team's professional
                growth led to a 40% increase in data-driven insights, driving
                strategic decision-making across the organization.</p></li></ul></div>
            <table width="714" cellpadding="7" cellspacing="0">
                <col width="113"/>
                <col width="239"/>
                <col width="94"/>
                <col width="68"/>
                <tr>
                    <td align="left"><b><i>Tensorsoft</i></b></td>
                    <td align="left"><i>Data Science, AIML, Eng</i></td>
                    <td align="left"><b>Co-founder, CTO and Lead Data Science Engineer</b></td>
                    <td align="right">Mountain View, CA</td>
                    <td align="right">2016-2021</td>
                </tr>
            </table>
            <div align="justify" class="prof-exp-details">
            <ul>
                <li>Developed and integrated customer segmentation for search relevancy</li>
                <li>Developed and maintained a critical software tools for recommendation engine</li>
                <li>Played an integral role in the development team</li>
            </ul></div>
            <table width="714" cellpadding="7" cellspacing="0">
                <col width="113"/>
                <col width="239"/>
                <col width="94"/>
                <col width="68"/>
                <tr>
                        <td align="left"><b><i>Keenetix</i></b></td>
                        <td align="left"><b>Product Manager, Data Science</b></td>
                        <td align="right">Salem, NH</td>
                        <td align="right">2010-2016</td>
                    </tr>
                    <tr>
                        <td align="left"><b><i>Keenetix</i></b></td>
                        <td align="left"><b>Project Dev Manager, Data Science</b></td>
                        <td align="right">Salem, NH</td>
                        <td align="right">2008-2010</td>
                    </tr>
                    <tr>
                        <td align="left"><b><i>Keenetix</i></b></td>
                        <td align="left"><b>Lead Dev Engineer, Data Science</b></td>
                        <td align="right">Salem, NH</td>
                        <td align="right">2005-2008</td>
                    </tr>
                </table>
            <div align="justify" class="prof-exp-details">
                <ul>
                <li><p align="left" style="margin-bottom: 0.04in">Built,
                lead, and motivated a global distributed engineering team of
                managers, engineers, and data scientists delivering scalable machine
                learning solutions in multi-spectral remote sensing for regulated
                industries, government, and NASA with a focus on customer needs.</p></li>
                <li><p align="left" style="margin-bottom: 0.04in">Created
                technical solutions based on sound engineering principals to derive
                actionable insights and to facilitate business decision-making in
                real time, by merging GIS, multi-spectral imagery, Lidar, and SAR
                satellite data with health and climate records to create
                vulnerability scores and risk maps for WHO.</p></li>
                </ul></div>
        """
        output = clean_html_string(raw_output)
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
            return self.generate_work_experience_section()

        def side_projects_fn():
            return self.generate_side_projects_section()

        def achievements_fn():
            return self.generate_achievements_section()

        def additional_skills_fn():
            return self.generate_additional_skills_section()

        def applicant_name_header_fn():
            return self.generate_applicant_name_header()

        def application_title_fn():
            return self.generate_application_title()

        def career_summary_fn():
            return self.generate_career_summary()
        def career_timeline_fn():
            return self.generate_career_timeline()
        def education_summary_fn():
            return self.generate_education_summary()
        def education_x_fn():
            return self.generate_education_summary()
        def professional_experience_fn():
            return self.generate_professional_experience()
        def academic_appointments_fn():
            return self.generate_academic_appointments()
        def skills_fn():
            return self.generate_additional_skills_section()
        def footer_fn():
            return self.generate_footer()

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
            "footer":footer_fn
        }
#
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

        full_resume_template=None
        full_resume=None
        try:
            with open(template_file, 'r') as file:
                full_resume_template = file.read().replace('\n', '')
        except Exception as e:
            print(f"Error during opening template file: {template_file}"
                  f"error: {e}")

        print(f'line 544', flush=True)
        print(f'results::\n{results}', flush=True)
        if full_resume_template is not None:
            full_resume=full_resume_template.format(
                applicant_name_header = results["applicant_name_header"],
                application_title = results["application_title"],
                career_summary = results["career_summary"],
                career_timeline = results["career_timeline"],
                education_summary = results["education_summary"],
                professional_experience = results["professional_experience"],
                achievements = results["achievements"],
                education = results["education"],
                skills = results["skills"]
            )

        else:
            try:
                with open(full_resume_template, 'r') as file:
                    full_resume = file.read().replace('\n', '')
            except Exception as e:
                print(f"Error during opening template file: {template_file}"
                      f"error: {e}")
                sys.exit()

        # Construct the final HTML resume from the results

#        full_resume = (
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
            file_name = f"final_resume.{formatted_time}"
            return file_name

        fname_full = os.path.join(os.path.dirname(__file__),'resume_output', create_filename())
        print(f'constructed final html resume. Saving to the file: {fname_full}')
        try:
            # Save the file with the generated filename
            with open(fname_full, 'w') as file:
                file.write(full_resume)
        except Exception as e:
            print(f"Error during saving html file: {fname_full}"
                      f"error: {e}")

        return full_resume