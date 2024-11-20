import traceback

from dotenv import load_dotenv
import os
import re

from lib_resume_builder_AIHawk.html_doc import HtmlDoc, format_map
from lib_resume_builder_AIHawk.utils   import is_valid_path, read_chunk
from lib_resume_builder_AIHawk.config import GlobalConfig
from lib_resume_builder_AIHawk.resume import Resume, PersonalInformation, WorkExperience, Education

global_config = GlobalConfig()
load_dotenv()

#ToDo = temp plug. Replace with configurable value
DEFAULT_CSS_FILE = r"C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_style\style_hawk_al_blue.css"
main_html_template = r'C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_templates\Resume.template.html'
DEFAULT_CHUNK_PATH = os.path.join('resume_templates', 'chunks')

class HtmlCover(HtmlDoc):
    def __init__(self, resume=None, css=None, css_path=None, html_template_file=None, html_template_path=None, html_chunk_path = None):
        super().__init__(resume, css, css_path, html_template_file, html_template_path, html_chunk_path)

    def set_css(self, css, path=None):
        css_content = read_chunk(fn=css, path=path)
        self.css = re.sub(r"/\*.*?\*/", "", css_content)


    def set_html_template(self, html_template_file, path=None):
        self.html_template = os.path.join(path, html_template_file) if path else html_template_file

    # def html_doc(self, css_file, css_inline=True, html_doc_template=None, doc_title:str='Job Application - Cover', doc_chunk = 'html_doc'):
    #     return super().html_doc(css_file, css_inline, html_doc_template, doc_title, doc_chunk)

    # def html_head(self, css_file=None, css_include=True, css_text=None, doc_title='Resume'):
    #     return super().html_head(css_file=None, css_include=True, css_text=None, doc_title='Job Application - Cover')

    def title(self):
        title_chunk = read_chunk('cover_title')
        return title_chunk.format(cover_title=self.resume.resume_title)

    def html_body(self):
        body_chunk = read_chunk('cover_body')
        body_p_chunk = read_chunk('cover_body_p')

        content = '\n'.join([body_p_chunk.format(line=ln.strip()) for ln in self.resume.cover_text if ln and len(ln.strip())>2])

        map = {
            "name_header": self.header('name_header'),
            "resume_title": self.title(),
            "cover_content":content,
            "prefix": self.resume.personal_information.name_prefix,
            "name": self.resume.personal_information.name,
            "surname": self.resume.personal_information.surname,
            "suffix": self.resume.personal_information.name_suffix
        }
        return body_chunk.format_map(map)
