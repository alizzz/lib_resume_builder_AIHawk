import re
import copy
import os
import os.path
import re

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# from lib_resume_builder_AIHawk.resume_template import resume_template_job_experience, resume_template
from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt_resumer_base import LLMResumerBase
from lib_resume_builder_AIHawk.resume import PersonalInformation

load_dotenv()
# ToDo: make it read config file

template_file = os.path.join(os.path.dirname(__file__), 'resume_templates',
                             os.environ.get('RESUME_TEMPLATE', 'hawk_resume_template.html'))
css_file = os.path.join(os.path.dirname(__file__), 'resume_style', 'style_hawk.css')
fullresume_file_backup = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_sample.html')

def text_from_html(html:str) ->str:
    # Step 1: Remove content inside <style> tags
    html_string_no_style = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL)

    # Step 2: Extract content from <body> tag only
    body_content = re.search(r'<body.*?>(.*?)</body>', html_string_no_style, flags=re.DOTALL)
    if body_content:
        body_html = body_content.group(1)
    else:
        body_html = html_string_no_style  # fallback if body tag is missing

    # Step 3: Remove remaining HTML tags
    text = re.sub('<[^<]+?>', '', body_html)
    return text

class LLMCoverJobDescription(LLMResumerBase):
    def __init__(self, openai_api_key, strings, resume = None, job_desc:str=None):
        # LLMResumerBase creates the following three members
        #self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.8))
        #self.llm_good = LoggerChatModel(ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, temperature=0.7))
        #self.strings = strings
        super().__init__(openai_api_key=openai_api_key, strings=strings)
        self.resume_ = resume
        self.job_desc = job_desc

    def set_job_description(self, job_desc:str):
        self.job = job_desc

    def set_resume(self, resume):
        self.resume_ = copy.deepcopy(resume)
        # printcolor(f'in LLMResumeJobDescription.setresume::self._resume.experience_details[0].position:{self._resume.experience_details[0].position}', "magenta")

    def create_header(self, delim = ' | ', pi:PersonalInformation=None):
        chunk_ ="""<div id = "header">< table >< tr >< td class ="left-aligned-column" >< span class ="applicant_name_header" > {name_prefix}{name} {surname}{name_suffix} < /span > < /td >< td class ="right-aligned-column" > < span class ="phone" > {phone} < /span > < span class ="table-cell-delimeter" > {delim_1} < /span > < span class ="email" > {email} < /span > < /td >< / tr > < / table ></div>"""
        if pi is None:
            pi = self.resume_.personal_information
        html = global_config.get_html_chunk(chunk_name='name_header', default=chunk_)
        return html.format(**(pi.dict()), delim_1 = delim)

    def create_cover_body_ai(self, personal_information:PersonalInformation, resume_path:str, job_description:str, company_name:str, title:str, company:str, prompt:str='cover_letter_body.prompt'):
        cover_letter_prompt=''
        resume = ''
        with open(os.path.join(global_config.PROMPTS_PATH, prompt), 'r', encoding='utf-8') as f:
            cover_letter_prompt = f.read()

        with open(os.path.join(resume_path),'w',encoding='utf-8') as f:
            resume = text_from_html(f.read())

        header_prompt_template = self._preprocess_template_string(cover_letter_prompt)
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_good | StrOutputParser()
        output = chain.invoke({
            "name_prefix": personal_information.name_prefix,
            "name": personal_information.name,
            "surname": personal_information.surname,
            "name_suffix": personal_information.name_suffix,
            "company": company,
            "title": title,
            "resume": resume,
            "job_description": job_description
        })
        return output