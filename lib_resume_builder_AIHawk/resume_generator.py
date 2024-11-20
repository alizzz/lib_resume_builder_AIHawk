from string import Template
import os
import re
from string import Template
from typing import Any
import copy

from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.gpt_resume import LLMResumer
from lib_resume_builder_AIHawk.gpt_resume_job_description import LLMResumeJobDescription
from lib_resume_builder_AIHawk.module_loader import load_module
from src.job import Job


class ResumeGenerator:
    def __init__(self):
        pass

    def set_resume_object(self, resume_object):
         self.resume_object = resume_object

    def _create_resume_html(self, gpt_answerer: Any, style_path, css_inline=True, prefer_resume_obj_generator=True, job:Job = None)->str:
        gpt_answerer.set_resume(self.resume_object)
        gpt_answerer.set_job(job)

        template = Template(global_config.html_template)
        style = f'<link rel="stylesheet" href="{style_path}" />'
        if css_inline:
            try:
                with open(style_path, 'r') as css:
                    css_content = css.read()
                    # Remove content between /* and */ at the beginning of the CSS file
                    css_content = re.sub(string=css_content, pattern=r'/\*.*?\*/', repl='', flags=re.DOTALL)
                    style = f'<style type="text/css">{css_content}</style>'
            except Exception as e:
                print(f"Failed reading css file {style_path}. Error {e}")

        html, cover = gpt_answerer.generate_html_resume(style_path)
        #generate html resume also updated its copy of resume
        self.resume_object=copy.deepcopy(gpt_answerer.resume)

        if not html or '<!DOCTYPE html>' not in html:  # html is not a full file - need to update
            html = template.substitute(body=html, inline_css=style)

        return html, cover



    def _create_resume(self, gpt_answerer: Any, style_path, css_inline=True, job:Job = None):
        resume, cover = self._create_resume_html(gpt_answerer, style_path, css_inline, job=job)
        return resume, cover


        return html



    def create_resume(self, style_path):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumer(global_config.API_KEY, strings)
        resume, cover = self._create_resume(gpt_answerer, style_path, job=job)
        return resume, cover

    def create_resume_job_description_url(self, style_path: str, url_job_description: str, job_title:str, job:Job=None):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_job_description_from_url(url_job_description)
        gpt_answerer.set_job_title(job_title)
        gpt_answerer.set_job(job)
        resume, cover = self._create_resume(gpt_answerer, style_path, job=job)
        return resume, cover

    def create_resume_job_description_text(self, style_path: str, job_description_text: str, job_title:str, job:Job=None):
        strings = load_module(global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH, global_config.STRINGS_MODULE_NAME)
        gpt_answerer = LLMResumeJobDescription(global_config.API_KEY, strings)
        gpt_answerer.set_job_description_from_text(job_description_text)
        gpt_answerer.set_job_title(job_title)
        gpt_answerer.set_job(job)
        gpt_answerer.set_default_injection_prompt()
        resume, cover = self._create_resume(gpt_answerer, style_path, job=job)
        return resume, cover
