import traceback

from dotenv import load_dotenv
import os
import re

from lib_resume_builder_AIHawk.utils   import is_valid_path, read_chunk

from lib_resume_builder_AIHawk.config import GlobalConfig
from lib_resume_builder_AIHawk.html_doc import HtmlDoc, format_map
#from lib_resume_builder_AIHawk.utils import read_chunk
from lib_resume_builder_AIHawk.resume import Resume, PersonalInformation, WorkExperience, Education

global_config = GlobalConfig()
load_dotenv()

#ToDo = temp plug. Replace with configurable value
DEFAULT_CSS_FILE = r"C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_style\style_hawk_al_blue.css"
main_html_template = r'C:\Users\al\PycharmProjects\lib_resume_builder_AIHawk\lib_resume_builder_AIHawk\resume_templates\Resume.template.html'
DEFAULT_CHUNK_PATH = os.path.join('resume_templates', 'chunks')

class HtmlResume(HtmlDoc):
    def __init__(self, resume=None, css=None, css_path=None, html_template_file=None, html_template_path=None, html_chunk_path = None):
        super().__init__(resume, css, css_path, html_template_file, html_template_path, html_chunk_path)
        # self.resume = resume
        # self.html_template = self.set_html_template(html_template_file, html_template_path) if html_template_file else global_config.html_template
        # self.css_text = self.set_css(css, css_path) if css else read_chunk(DEFAULT_CSS_FILE)
        # self.chunk_path = html_chunk_path if html_chunk_path else DEFAULT_CHUNK_PATH

    def set_css(self, css, path=None):
        css_content = read_chunk(fn=css, path=path)
        self.css = re.sub(r"/\*.*?\*/", "", css_content)


    def set_html_template(self, html_template_file, path=None):
        self.html_template = os.path.join(path, html_template_file) if path else html_template_file

    # def html_doc(self, css_file, css_inline=True, html_doc_template=None, doc_title:str = 'Job Application Resume', doc_chunk = 'html_doc'):
    #     return super().html_doc(css_file, css_inline, html_doc_template, doc_title, doc_chunk)

    # def html_head(self, css_file=None, css_include=True, css_text=None, doc_title='Resume'):
    #     css_ = ''
    #     head_chunk = ''
    #     try:
    #         head_chunk = read_chunk('html_head')
    #         if css_file or css_text:
    #             # css_text takes precedence. if it is supplied, it is used, file is not being loaded
    #             # also, if it is supplied, it is going to be included inline, css_inline parameter is ignored
    #             if css_text:
    #                 css_ = f'<style type="text/css">{css_text}</style>'
    #             else:
    #                 if css_include: #it should be included inline
    #                     #load content from file
    #                     css_content = read_chunk(css_file)
    #                     #clean it
    #                     css_text = re.sub(r"/\*.*?\*/", "", css_content)
    #                     css_ = f'<style type="text/css">{css_text}</style>'
    #                 else:
    #                     css_=f'<link rel="stylesheet" href="{css_file}" type="text/css">'
    #
    #     except Exception as e:
    #             print(f'Failed to set CSS - html_head error {e} {traceback.format_exc()}')
    #
    #     return head_chunk.format(doc_title=doc_title, css=css_)
    def html_body(self):
        body_chunk = read_chunk('resume_body')

        map = {
            "name_header": self.header('name_header'),
            "resume_title": self.title(),
            "career_summary":self.career_summary(),
            "education_timeline":self.education_timeline(),
            "employment_timeline": self.work_experiences_timeline(),
            "work_experiences":self.work_experiences(),
            "achievements":self.achievements(),
            "skills":self.skills(),
            "projects":self.projects(),
            "certifications":self.list_of_strings(self.resume.certifications, title='certifications'),
            "languages":self.languages(),
            "interests":self.list_of_strings(self.resume.interests, title='interests')
        }
        return body_chunk.format_map(map)

    def projects(self):
        prjs_chunk = read_chunk('projects')
        prj_row_chunk = read_chunk('project_li')
        if self.resume.languages:
            rows = [prj_row_chunk.format(name=prj.name,
                                         description=prj.description if prj.description else "",
                                         link=prj.link if prj.link else '')
                    for prj in self.resume.projects if prj]
            return prjs_chunk.format(project_rows=''.join(rows))
        else:
            return "<!-- projects -->"

    def certifications(self):
        return ''
    def languages(self):
        try:
            if self.resume.languages:
                lngs_chunk = read_chunk('languages')
                lng_row_chunk = read_chunk('language_li')
                rows = [lng_row_chunk.format(key=lng.language, value=lng.proficiency) for lng in self.resume.languages if
                        lng]
                return lngs_chunk.format(language_rows=''.join(rows))
        except Exception as e:
            print(f'Error: languages failed with error {e}')
        return "<!-- languages -->"
    def interests(self):
        return ''

    def title(self):
        title_chunk = read_chunk('application_title')
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
            if exp:
                map = self.work_experience_map(exp)
                work_exp_row_chunk = read_chunk('exp_details_row')
                exp_details_row+=work_exp_row_chunk.format_map(map)
            else:
                print('Warning: Resume work experience is empty')

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

