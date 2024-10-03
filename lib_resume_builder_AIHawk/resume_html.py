import os
import re
from lib_resume_builder_AIHawk import Resume
from lib_resume_builder_AIHawk.config import GlobalConfig
from dotenv import load_dotenv

global_config = GlobalConfig()
load_dotenv()

class HtmlResume():
    def __init__(self, resume=None):
        self.resume = resume
        self.html_template = global_config.html_template
