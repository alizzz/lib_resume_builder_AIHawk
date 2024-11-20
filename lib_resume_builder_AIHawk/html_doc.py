import traceback

from dotenv import load_dotenv
import os
import re

from lib_resume_builder_AIHawk.utils   import is_valid_path, read_chunk

from lib_resume_builder_AIHawk.config import GlobalConfig
#from lib_resume_builder_AIHawk.utils import read_chunk
from lib_resume_builder_AIHawk.resume import Resume, PersonalInformation, WorkExperience, Education

global_config = GlobalConfig()
load_dotenv()

#ToDo = temp plug. Replace with configurable value
DEFAULT_CSS_FILE = r"C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_style\style_hawk_al_blue.css"
main_html_template = r'C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_templates\Resume.template.html'
DEFAULT_CHUNK_PATH = os.path.join('resume_templates', 'chunks')

def format_map(cls):
    return { attr: getattr(cls, attr) for attr in dir(cls)
                if not callable(getattr(cls, attr, None)) and not attr.startswith("_")
    }

class HtmlDoc():
    def __init__(self, resume=None, css=None, css_path=None, html_template_file=None, html_template_path=None, html_chunk_path = None):
        self.resume = resume
        self.html_template = self.set_html_template(html_template_file, html_template_path) if html_template_file else global_config.html_template
        self.css_text = self.set_css(css, css_path) if css else read_chunk(DEFAULT_CSS_FILE)
        self.chunk_path = html_chunk_path if html_chunk_path else DEFAULT_CHUNK_PATH

    def set_css(self, css, path=None):
        css_content = read_chunk(fn=css, path=path)
        self.css = re.sub(r"/\*.*?\*/", "", css_content)


    def set_html_template(self, html_template_file, path=None):
        self.html_template = os.path.join(path, html_template_file) if path else html_template_file

    def html_doc(self, css_file, css_inline=True, html_doc_template=None, doc_title:str='', doc_chunk = 'html_doc'):
        head = self.html_head(css_file, css_inline, css_text=None, doc_title=doc_title)
        body = self.html_body()
        _html_doc = read_chunk(doc_chunk)
        return _html_doc.format(head=head, body=body)

    def html_head(self, css_file=None, css_include=True, css_text=None, doc_title='Job Application'):
        css_ = ''
        head_chunk = ''
        try:
            head_chunk = read_chunk('html_head')
            if css_file or css_text:
                # css_text takes precedence. if it is supplied, it is used, file is not being loaded
                # also, if it is supplied, it is going to be included inline, css_inline parameter is ignored
                if css_text:
                    css_ = f'<style type="text/css">{css_text}</style>'
                else:
                    if css_include: #it should be included inline
                        #load content from file
                        css_content = read_chunk(css_file)
                        #clean it
                        css_text = re.sub(r"/\*.*?\*/", "", css_content)
                        css_ = f'<style type="text/css">{css_text}</style>'
                    else:
                        css_=f'<link rel="stylesheet" href="{css_file}" type="text/css">'

        except Exception as e:
                print(f'Failed to set CSS - html_head error {e} {traceback.format_exc()}')

        return head_chunk.format(doc_title=doc_title, css=css_)
    def html_body(self):
        body_chunk = read_chunk('resume_body')

        map = {
            "name_header": self.header('name_header'),
            "resume_title": self.title(),
        }
        return body_chunk.format_map(map)

    def list_of_strings(self, obj, title, style=None):
        try:
            if obj is None:
                raise AttributeError('missing parameter `obj` for list_of_strings')
            title = title.lower()
            stl = style if style else title
            lofs_chunk = read_chunk('ListOfStr')
            lofs_li_chunk = read_chunk("ListOfStr_li")

            lst = []
            if obj:
                for li in obj:
                    lst.append(lofs_li_chunk.format(line=li, style = stl))
            if lst:
                return lofs_chunk.format(style=stl, title=title.capitalize(), lofs=lst)
            else:
                return f'<!-- {title.upper()} -->'
        except Exception as e:
            print(f'Error: ListOfString for {title if title else '?' } failed with error {e}')

        return f'<-- {title.upper() if title else 'title:unk' } -->'

    def title(self):
        title_chunk = read_chunk('application_title')
        return title_chunk.format(resume_title=self.resume.resume_title)
    def header(self, chunk='name_header')->str:
        chunk_html = read_chunk(chunk)
        return chunk_html.format_map(format_map(self.resume.personal_information))
