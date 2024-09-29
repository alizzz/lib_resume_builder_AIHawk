import os
import datetime
from pathlib import Path
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv
import inspect
from lib_resume_builder_AIHawk.utils import get_dict_names_from_dir

load_dotenv()
DEBUG = os.environ.get('DEBUG', '').lower() in ['y', 'yes', 'true', 't', '1', 'on']
class JobContext(BaseModel):
    job_description_url: Optional[HttpUrl]=None
    job_description_raw_html: Optional[str]=None
    job_description_gpt: Optional[str]=None
    job_title: Optional[str]=None
    job_office_policy: Optional[str]=None
    organization_name: Optional[str]=None
    html_raw_source: Optional[str]=None
    is_applied: Optional[bool]=None
    date_applied: Optional[str]=None
    def clear(self):
        self.job_description_url=None
        self.job_description_raw_html=""
        self.job_description_gpt=""
        self.job_title=""
        self.job_office_policy=""
        self.organization_name=""
        self.html_raw_source=""
        self.is_applied=False
        self.date_applied=None

class ResumeContext(BaseModel):
    html_raw: Optional[str]=None
    pdf_path: Optional[str]=None
    def clear(self):
        self.html_raw=""
        self.pdf_path=""
class Context(BaseModel):
    date_created: Optional[str]=datetime.datetime.now().__str__()
    resume: Optional[ResumeContext]=ResumeContext()
    job: Optional[JobContext]=JobContext()

    def clear(self):
        self.date_created = datetime.datetime.now().__str__()
        self.resume = ResumeContext()
        self.job = JobContext()

class GlobalConfig:
    def __init__(self):
        # Inizialmente tutti i valori sono None
        self.PROMPTS_PATH: Path = os.environ.get("PROMPTS_PATH", None)
        self.STRINGS_MODULE_RESUME_PATH: Path = os.environ.get('STRINGS_MODULE_RESUME_PATH', None)
        self.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH: Path = os.environ.get('STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH', None)
        self.STRINGS_MODULE_NAME: str = os.environ.get('STRINGS_MODULE_NAME', None)
        self.STYLES_DIRECTORY: Path = os.environ.get('STYLES_DIRECTORY', None)
        self.TEMPLATES_DIRECTORY: Path = os.environ.get('TEMPLATES_DIRECTORY', None)
        self.LOG_OUTPUT_FILE_PATH: Path = os.environ.get('LOG_OUTPUT_FILE_PATH', None)
        self.API_KEY: str = os.environ.get('API_KEY', None)
        self.CONTEXT: Context = os.environ.get('CONTEXT', None)
        self.html_template_chunk = get_dict_names_from_dir(os.path.join(os.path.dirname(__file__), 'resume_templates', 'chunks'))
        self.prompt_dict = get_dict_names_from_dir(os.path.join(os.path.dirname(__file__), 'resume_prompt'))
        #{
        #    'name_header': 'name_header.chunk',
        #    'exp_timeline_long_row':'exp_timeline_long_row.chunk',
        #    'exp_timeline_long_table':'exp_timeline_long_table.chunk',
        #    'edu_summary':'edu_summary_table.chunk',
        #    'edu_summary_li':'edu_summary_li.chunk'
        #}
        #load if stored in .env file
        self.html_template = self.get_html_template(os.environ.get('HTML_TEMPLATE_FILE', None), 'resume_templates')

    @staticmethod
    def get_html_template(template_file, dir='resume_templates'):
        _html_template = """
                            <!DOCTYPE html>
                            <html lang="en">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Resume</title>
                                <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&display=swap" />
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" /> 
                                $inline_css
                            </head>
                                $body
                            </html>
                            """
        if template_file is None: return _html_template
        html_template = None
        try:
            with open(os.path.join(template_file, dir), 'r') as f:
                html_template = f.read()
        except:
            pass
        if html_template is None or len(html_template) == 0:
            if DEBUG: print("WARNING: html_template is not found. Using default one")
            html_template = _html_template
        return html_template


    def get_html_chunk(self, chunk_name:str, default:str):
        chunk = None
        try:
            chunk_file = self.html_template_chunk[chunk_name]
            if chunk_file is not None and len(chunk_file)>0:
                with open(os.path.join(self.TEMPLATES_DIRECTORY, 'chunks', chunk_file),'r', encoding='utf-8') as f:
                    chunk = f.read()
        except Exception as e:
            if DEBUG:
                print(f'Failed to load html chunk {chunk_name}. Exception {e}')
        if chunk is None:
            if DEBUG: print(f'Using default value for chunk {chunk_name}')
        return chunk if not None else default

    def unpack_members(self, cls, param_only=True):
        try:
            return cls.dict()
        except:
            pass

        cls_m = {}
        members = inspect.getmembers(cls)
        for name, member in members:
            try:
                if not callable(member) and not name.startswith('__') and not name.startswith('_'):
                    cls_m[name] = member
            except Exception as e:
                print(f'Exception in unpack_members for {type(cls)}. Error:{e}')

        return cls_m

# Creazione dell'istanza globale
global_config = GlobalConfig()