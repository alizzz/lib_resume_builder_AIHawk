from dotenv import load_dotenv
import os
import re

from lib_resume_builder_AIHawk.config import GlobalConfig
#from lib_resume_builder_AIHawk.utils import read_chunk
from lib_resume_builder_AIHawk.resume import Resume, PersonalInformation, WorkExperience, Education

global_config = GlobalConfig()
load_dotenv()

#ToDo = temp plug. Replace with configurable value
DEFAULT_CSS_FILE = r"C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_style\style_hawk_al_blue.css"
main_html_template = r'C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_templates\Resume.html'
DEFAULT_CHUNK_PATH = os.path.join('resume_templates', 'chunks')
def read_chunk(fn, path='', ext='chunk', enc='utf-8', **kwargs)->str:
    #first check if chunk file exists
    def chunk_path(fn:str, path='', ext='chunk')->str:
        fn_ext = f'{fn}.{ext}'
        if not path: path = os.path.dirname(os.path.relpath(__file__))
        checks = {"fn":fn,
                 "fn.ext":fn_ext,
                 r"path\fn":os.path.join(path, fn),
                 r"path\fn.ext": os.path.join(path, fn_ext),
                 r"path\chunks\fn": os.path.join(path, 'chunks', fn),
                 r"path\chunks\fn.ext": os.path.join(path, 'chunks', fn_ext),
                  r"path\resume_templates\chunks\fn": os.path.join(path,'resume_templates','chunks', fn),
                  r"path\resume_templates\chunks\fn.ext": os.path.join(path,'resume_templates','chunks', fn_ext)

                  }

        chunk_name = ''
        for f in checks.values():
            if os.path.isfile(f):
                chunk_name=f
                break

        if not chunk_name:
            print(f'WARNING: fn_ext is not found', "yellow")

        return chunk_name

    chunk_fname = chunk_path(fn, path, ext)

    if not chunk_fname:
        raise FileNotFoundError()

    try:
        with open(chunk_fname, "r", encoding=enc) as file:
            chunk_fmt = file.read()
            #removing comments
            chunk_fmt = re.sub(r'<!--.*?-->', '', chunk_fmt, flags=re.DOTALL)

        if chunk_fmt:
            if kwargs:
                return chunk_fmt.format(**kwargs)
            else:
                return chunk_fmt

    except FileNotFoundError:
        print(f'FileNotFound exception for {fn} from Resume::html::get_chunk()')
    except Exception as e:
        print(f'Exception for {fn} from Resume::html::get_chunk(). Exception:{e}')

    return ""

def format_map(cls):
    return { attr: getattr(cls, attr) for attr in dir(cls)
                if not callable(getattr(cls, attr, None)) and not attr.startswith("_")
    }

class HtmlResume():
    def __init__(self, resume=None, css=None, chunk_path=None):
        self.resume = resume
        self.html_template = global_config.html_template
        self.css = read_chunk(css) if css else read_chunk(DEFAULT_CSS_FILE)
        self.chunk_path = chunk_path if chunk_path else DEFAULT_CHUNK_PATH

    
    def html(self):
        html_template = read_chunk(main_html_template)
        map = {
            "inline_css":self.css,
            "name_header": self.header('name_header'),
            "resume_title": self.title(),
            "career_summary":self.career_summary(),
            "education_timeline":self.education_timeline(),
            "employment_timeline": self.work_experiences_timeline(),
            "work_experiences":self.work_experiences(),
            "achievements":self.achievements(),
            "skills":self.skills(),
            "projects":"",
            "certifications":"",
            "languages":"",
            "interests":""
        }
        return html_template.format_map(map)

    def title(self):
        title_chunk = read_chunk('resume_title')
        return title_chunk.format(resume_title=self.resume.resume_title)
    def header(self, chunk='name_header')->str:
        chunk_html = read_chunk(chunk)
        return chunk_html.format_map(format_map(self.resume.personal_information))

    def career_summary(self)->str:
        try:
            career_summary_chunk = read_chunk('career_summary')
            career_summary_line_chunk = read_chunk("career_summary_p")
            career_summary_highlight_line_chunk = read_chunk("career_summary_highlight_line")

            cslst = []
            for cs in self.resume.career_summary:
                cslst.append(career_summary_line_chunk.format(line=cs))

            cshlst = []
            for csh in self.resume.career_highlights:
                csh_ = career_summary_highlight_line_chunk.format(name=csh.key, description=csh.value)
                cshlst.append(csh_)

            map = {
                "career_summary": '\n'.join(cslst),
                "career_summary_highlights": '\n'.join(cshlst)
            }
            return career_summary_chunk.format_map(map)
        except Exception as e:
            print(f'Error: HtmlResume::career_summary() failed with error {e}')
    def education_timeline(self)->str:
        edu_timeline_chunk = read_chunk('education_summary')
        edu_timeline_line_chunk = read_chunk('edu_summary_li')
        #ToDo Order by graduation date?
        lines = []
        for e in self.resume.education_details:
            edu_li_map = {
                "degree":e.degree,
                "field_of_study": e.field_of_study,
                "university":e.university,
                "gpa":e.gpa,
                "graduation_year":e.graduation_year
            }
            lines.append(edu_timeline_line_chunk.format_map(edu_li_map))

        edu_summary_lines = "\n".join(lines)
        return edu_timeline_chunk.format(edu_summary_lines=edu_summary_lines)

    def work_experience_map(self, exp: WorkExperience):
        # experience key responsibilities
        exp_key_resp_chunk = read_chunk('exp_key_responsib')
        exp_key_resp_row_chunk = read_chunk('exp_key_responsib_row')
        exp_kr_rows = []

        # exp_kr_rows = [exp_key_resp_row_chunk.format(exp_key_responsibility_row=exp_key_row) for exp_key_row in exp.key_responsibilities if exp_key_row]
        if exp.key_responsibilities:
            for keyresp_row in exp.key_responsibilities:
                if keyresp_row:
                    exp_kr_rows.append(exp_key_resp_row_chunk.format(exp_key_responsibility_row=keyresp_row))
        else:
            exp_kr_rows=[]

        exp_key_resps = '\n'.join(exp_kr_rows) if exp_kr_rows else ''

        exp_skills_chunk = read_chunk('exp_skills')
        exp_skills = ', '.join(exp.skills_acquired)

        map = {
            "position": exp.position,
            "company": exp.company,
            "employment_period": exp.employment_period,
            "location": exp.location,
            "industry": exp.industry,
            "exp_summary": exp.summary,
            "exp_key_resps": exp_key_resp_chunk.format(exp_key_resp_rows=exp_key_resps),
            "exp_skills": exp_skills_chunk.format(exp_skills=exp_skills)
        }

        return map

    def work_experiences_timeline(self) -> str:
        exp_timeline_chunk = read_chunk('exp_timeline')
        exp_timeline_row_chunk = read_chunk('exp_timeline_row')
        exp_timeline_rows = ''
        for exp in self.resume.work_experiences:
            if exp:
                exp_timeline_rows+=exp_timeline_row_chunk.format_map(self.work_experience_map(exp))

        return exp_timeline_chunk.format(exp_timeline_rows=exp_timeline_rows)

    def work_experiences(self)->str:
        work_exp_chunk = read_chunk('exp_details')
        exp_details_row = ''
        for exp in self.resume.work_experiences:
            map = self.work_experience_map(exp)
            work_exp_row_chunk = read_chunk('exp_details_row')
            exp_details_row+=work_exp_row_chunk.format_map(map)

        return work_exp_chunk.format(exp_details_rows = exp_details_row)

    def achievements(self)->str:
        achs_chunk = read_chunk('achievements')
        ach_row_chunk = read_chunk('achievement_li')

        rows = [ach_row_chunk.format(name=ach.name, description=ach.description) for ach in self.resume.achievements if ach]
        achs = achs_chunk.format(achievement_rows = ''.join(rows))
        return achs
    
    def skills(self)->str:
        skills_chunk = read_chunk('skills')
        skills_row_chunk = read_chunk("skill_li")

        skill_rows='\n'.join([skills_row_chunk.format(category=sk.key, skill_lst=sk.value) for sk in self.resume.skills if sk])
        return skills_chunk.format(skills=skill_rows)

    def projects(self)->str:
        pass
    
    def certifications(self)->str:
        pass
    
    def languages(self)->str:
        pass
    
    def interests(self)->str:
        pass

