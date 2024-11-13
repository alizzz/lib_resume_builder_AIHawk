from string import Template
import os
import re
from string import Template
from typing import Any

from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt_resume import LLMResumer
from lib_resume_builder_AIHawk.gpt_resume_job_description import LLMResumeJobDescription
from lib_resume_builder_AIHawk.module_loader import load_module


class ResumeGenerator:
    def __init__(self):
        pass
    
    def set_resume_object(self, resume_object):
         self.resume_object = resume_object

    def _create_resume(self, gpt_answerer: Any, style_path, temp_html_path, css_inline=True):
        gpt_answerer.set_resume(self.resume_object)
        template = Template(global_config.html_template)
        css = ""
        #try:
        #    with (open(style_path, 'r')) as style_file:
        #        css = style_file.read()
        #except Exception as e:
        #    print(f"Error during reading style file: {style_path}"
        #        f"error: {e}")style_path
        style = f'<link rel="stylesheet" href="{style_path}" />'
        if css_inline:
            try:
                with open(style_path,'r') as css:
                    css_content = css.read()
                    # Remove content between /* and */ at the beginning of the CSS file
                    css_content = re.sub(string=css_content, pattern=r'/\*.*?\*/',  repl='', flags=re.DOTALL)
                    style = f'<style>{css_content}</style>'
            except Exception as e:
                print(f"Failed reading css file {style_path}. Error {e}")

        html_body = gpt_answerer.generate_html_resume()
        message = template.substitute(body=html_body, inline_css=style)
        bak_directory = os.path.dirname(temp_html_path)
        if not os.path.exists(bak_directory):
            os.makedirs(bak_directory)
        with open(temp_html_path, 'w', encoding='utf-8') as temp_file:
            temp_file.write(message)
            print(f'Written temp html file: {temp_html_path}')

    def create_resume(self, style_path, temp_html_file):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumer(global_config.API_KEY, strings)
        self._create_resume(gpt_answerer, style_path, temp_html_file)

    def create_resume_job_description_url(self, style_path: str, url_job_description: str, temp_html_path):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_job_description_from_url(url_job_description)
        self._create_resume(gpt_answerer, style_path, temp_html_path)

    def create_resume_job_description_text(self, style_path: str, job_description_text: str, job_title:str, temp_html_path):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_job_description_from_text(job_description_text)
        gpt_answerer.set_job_title(job_title)
        self._create_resume(gpt_answerer, style_path, temp_html_path)
