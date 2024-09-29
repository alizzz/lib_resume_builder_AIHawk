import json
import os
import random
import tempfile
import textwrap
import time
import re
import copy
import os
import os.path
import sys
import traceback
import inspect
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
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
#from lib_resume_builder_AIHawk.resume_template import resume_template_job_experience, resume_template
import lib_resume_builder_AIHawk.resume_templates.resume_template
from lib_resume_builder_AIHawk.utils import printcolor, printred, printyellow, read_format_string, get_content
from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt_resumer_base import LLMResumerBase, LLMLogger, LoggerChatModel, clean_html_string
from lib_resume_builder_AIHawk.resume import PersonalInformation, Resume



load_dotenv()
# ToDo: make it read config file

template_file = os.path.join(os.path.dirname(__file__), 'resume_templates',
                             os.environ.get('RESUME_TEMPLATE', 'hawk_resume_template.html'))
css_file = os.path.join(os.path.dirname(__file__), 'resume_style', 'style_hawk.css')
fullresume_file_backup = os.path.join(os.path.dirname(__file__), 'resume_templates', 'hawk_resume_sample.html')


class LLMCoverJobDescription(LLMResumerBase):
    def __init__(self, openai_api_key, strings):
        #self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=0.8))
        #self.llm_good = LoggerChatModel(ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, temperature=0.7))
        #self.strings = strings
        super().__init__(openai_api_key=openai_api_key, strings=strings)
        self.resume_ = None
        self.job = None

    def set_resume(self, resume):
        self.resume_ = copy.deepcopy(resume)
        # printcolor(f'in LLMResumeJobDescription.setresume::self._resume.experience_details[0].position:{self._resume.experience_details[0].position}', "magenta")

    def create_header(self, delim = ' | ', pi:PersonalInformation=None):
        chunk_ ="""<div id = "header">< table >< tr >< td class ="left-aligned-column" >< span class ="applicant_name_header" > {name_prefix}{name} {surname}{name_suffix} < /span > < /td >< td class ="right-aligned-column" > < span class ="phone" > {phone} < /span > < span class ="table-cell-delimeter" > {delim_1} < /span > < span class ="email" > {email} < /span > < /td >< / tr > < / table ></div>"""
        if pi is None:
            pi = self.resume_.personal_information
        html = global_config.get_html_chunk(chunk_name='name_header', default=chunk_)
        return html.format(**(pi.dict()), delim_1 = delim)

    def create_cover_body_ai(self, personal_information:PersonalInformation, resume_path:str, job_description:str, company_name:str, title:str, prompt:str='cover_letter_body.prompt'):
        cover_letter_prompt=''
        resume = ''
        with open(os.path.join(global_config.PROMPTS_PATH, prompt), 'r', encoding='utf-8') as f:
            cover_letter_prompt = f.read()

        with open(os.path.join(resume_path),'w',encoding='utf-8') as f:
            resume = f.read()

        header_prompt_template = self._preprocess_template_string(cover_letter_prompt)
        prompt = ChatPromptTemplate.from_template(header_prompt_template)
        chain = prompt | self.llm_cheap | StrOutputParser()
        output = chain.invoke({
            "resume": resume,
            "job_description": self.job_description
        })
        return output


