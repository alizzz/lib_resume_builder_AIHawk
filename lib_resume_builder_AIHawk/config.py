from pathlib import Path
import datetime
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import List, Dict, Optional, Union
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
        self.STRINGS_MODULE_RESUME_PATH: Path = None
        self.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH: Path = None
        self.STRINGS_MODULE_NAME: str = None
        self.STYLES_DIRECTORY: Path = None
        self.LOG_OUTPUT_FILE_PATH: Path = None
        self.API_KEY: str = None
        self.CONTEXT: Context = None
        self.html_template = """
                            <!DOCTYPE html>
                            <html lang="en">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Resume</title>
                                <link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;600&display=swap" rel="stylesheet" />
                                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" /> 
                                <link rel="stylesheet" href="$style_path" />                        
                            </head>
                            $markdown
                            </body>
                            </html>
                            """

# Creazione dell'istanza globale
global_config = GlobalConfig()