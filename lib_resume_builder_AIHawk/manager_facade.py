import os
import webbrowser
from pathlib import Path

import inquirer
import yaml

from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.utils import HTML2PDF  # this one prints using pdfkit directly from string or from file


from src.job import Job
from src.g_data import GSheets, GDrive
from src.global_config import GlobalConfigSingle

gc = GlobalConfigSingle.create()

class FacadeManager:
    def __init__(self, api_key, style_manager, resume_generator, resume_object, log_path, selected_style = None):
        # Ottieni il percorso assoluto della directory della libreria
        lib_directory = Path(__file__).resolve().parent
        global_config.PROMPTS_PATH = lib_directory / "prompts"
        global_config.STRINGS_MODULE_RESUME_PATH = lib_directory / "resume_prompt/strings_feder-cr.py"
        global_config.STRINGS_MODULE_RESUME_JOB_DESCRIPTION_PATH = lib_directory / "resume_job_description_prompt/strings_feder-cr.py"
        global_config.STRINGS_MODULE_NAME = "strings_feder_cr"
        global_config.STYLES_DIRECTORY = lib_directory / "resume_style"
        global_config.TEMPLATES_DIRECTORY = lib_directory / 'resume_templates'
        global_config.LOG_OUTPUT_FILE_PATH = log_path
        global_config.API_KEY = api_key
        self.style_manager = style_manager
        self.style_manager.set_styles_directory(global_config.STYLES_DIRECTORY)
        self.resume_generator = resume_generator
        self.resume_generator.set_resume_object(resume_object)
        self.selected_style = selected_style  # Proprietà per memorizzare lo stile selezionato

    def prompt_user(self, choices: list[str], message: str) -> str:
        questions = [
            inquirer.List('selection', message=message, choices=choices),
        ]
        return inquirer.prompt(questions)['selection']

    def prompt_for_url(self, message: str) -> str:
        questions = [
            inquirer.Text('url', message=message),
        ]
        return inquirer.prompt(questions)['url']

    def prompt_for_text(self, message: str) -> str:
        questions = [
            inquirer.Text('text', message=message),
        ]
        return inquirer.prompt(questions)['text']

    def choose_style(self):
        styles = self.style_manager.get_styles()
        if not styles:
            print("No styles available")
            return None
        final_style_choice = "Create your resume style in CSS"
        formatted_choices = self.style_manager.format_choices(styles)
        formatted_choices.append(final_style_choice)
        selected_choice='AL'
        #selected_choice = self.prompt_user(formatted_choices, "Which style would you like to adopt?")
        if selected_choice == final_style_choice:
            tutorial_url = "https://github.com/feder-cr/lib_resume_builder_AIHawk/blob/main/how_to_contribute/web_designer.md"
            print("\nOpening tutorial in your browser...")
            webbrowser.open(tutorial_url)
            exit()
        else:
            self.selected_style = selected_choice.split(' (')[0]
            print("\nSelected style: "+self.selected_style)

#    def create_html_resume(self, job:Job):
#        htmlResume = HtmlResume(self.resume_generator.resume_object, css = self.style_manager.get_style_path(self.selected_style) )
#        pass

    def _resume_html(self, job_description_url: object = None,
                   html_file_name: object = None,
                   delete_html_file: object = True, job:Job = None) -> str:

        if (job_description_url is not None and Job.description is not None):
            raise ValueError("Exactly one of 'job_description_url' or 'Job.description' must be provided..")

        if self.selected_style is None:
            raise ValueError("You must choose a style before generating the PDF.")

        style_path = self.style_manager.get_style_path(self.selected_style)

        if job_description_url is None and job.description is None:
            html, cover = self.resume_generator.create_resume(style_path)
        elif job_description_url is not None and job.description is None:
            html, cover = self.resume_generator.create_resume_job_description_url(style_path, job_description_url, job=job)
        elif job_description_url is None and job.description is not None:
            html, cover = self.resume_generator.create_resume_job_description_text(style_path, job=job)
        else:
                return None
        return html, cover

    def pdf_base64(self, job_description_url: object = None,
                   resume_html_file_name = None,
                   delete_html_file = False, job:Job=None) -> object:

        USE_PDFKIT = True #ToDo - add to the configuration
        resume_html, cover_html = self._resume_html(job_description_url, job=job)

        with open(resume_html_file_name, 'w', encoding='utf-8') as html_file:
            html_file.write(resume_html)
            print(f'Written resume html file: {resume_html_file_name}')

        cover_html_file_name = f'{'.'.join(os.path.splitext(resume_html_file_name)[0].split('.')[:-1])}.Cover.html'
        with open(cover_html_file_name, 'w', encoding='utf-8') as html_file:
            html_file.write(cover_html)
            print(f'Written cover letter html file: {cover_html_file_name}')

        with open(f'{os.path.splitext(resume_html_file_name)[0]}.yaml', 'w', encoding='utf-8') as yaml_file:
            yaml.dump(self.resume_generator.resume_object.dict(), yaml_file)

        #gsheets update
        #ID	Company	Status	Position	Salary Range	Office Policy   Location    Notes	Job Posting	Path	Date Job Was Found
        pdf_base64 = None
        if USE_PDFKIT:
            print(f'Using HTML2PDF aka pdfkit/wkhtmltopdf based pdf generator')
            HTML2PDF(resume_html, f'{os.path.splitext(resume_html_file_name)[0]}.pdf')
            HTML2PDF(cover_html, f'{os.path.splitext(cover_html_file_name)[0]}.pdf')

        else:
            print(f'WARNING: Not Implemented: Using HTML_to_PDF aka browser based pdf generator')
            # pdf_base64 = HTML_to_PDF(html_file_name)
            # if delete_html_file:
            #      os.remove(html_file_name)
            #
        try:
            gsheets_row_values = [[job.get_dt_string(fmt='%Y-%m-%d'), job.id, job.company, 'Found', job.title, job.compensation, job.office_policy, job.location, '',job.link, job.get_fname(), job.get_dt_string(fmt='%Y-%m-%d')]]
            gs = GSheets()
            sheet_name = gc.get("sheet_name")
            cells = gs.find(sheet_name, "A:B", job.id)
            if not cells:
                row = gs.find_first_non_empty_cell_in_column(sheet_name, 'B')
                gs.update(sheet_name,f'A{row}', gsheets_row_values)
            else:
                c, r = gs.split_RC_into_R_and_C(cells[0])
                gs.update(sheet_name, f'A{r}', gsheets_row_values)
        except Exception as e:
            print(f'Failed saving data to GSheets for id:{job.id} Error:{e}')

        # saving files to GDrive
        try:
            gd = GDrive()
            local_folder_name=os.path.dirname(resume_html_file_name)
            g_parent_folder_id = gc.get("gdrive_data_path_id")
            gd.upload_folder(local_folder_name, gparent_folder_id=g_parent_folder_id)
        except Exception as e:
            print(f'Failed saving data to GDrive for id:{job.id} Error:{e}')

        return pdf_base64