import os
from pathlib import Path
import tempfile
import inquirer
from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.utils import HTML_to_PDF
import webbrowser
import os
import tempfile
import webbrowser
from pathlib import Path

import inquirer

from lib_resume_builder_AIHawk.config import global_config
from lib_resume_builder_AIHawk.utils import HTML_to_PDF


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

    def pdf_base64(self, job_description_url=None, job_description_text=None, html_file_name=None, delete_html_file=True):
        if (job_description_url is not None and job_description_text is not None):
            raise ValueError("Exactly one of 'job_description_url' or 'job_description_text' must be provided..")

        if self.selected_style is None:
            raise ValueError("You must choose a style before generating the PDF.")

        style_path = self.style_manager.get_style_path(self.selected_style)

        temp_html_file = None
        if html_file_name is None: #create temp file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.html', encoding='utf-8') as temp_html_file:
                html_file_name = temp_html_file.name

        if job_description_url is None and job_description_text is None:
            self.resume_generator.create_resume(style_path, html_file_name)
        elif job_description_url is not None and job_description_text is None:
            self.resume_generator.create_resume_job_description_url(style_path, job_description_url, html_file_name)
        elif job_description_url is None and job_description_text is not None:
            self.resume_generator.create_resume_job_description_text(style_path, job_description_text, html_file_name)
        else:
                return None
        pdf_base64 = HTML_to_PDF(html_file_name)
        if delete_html_file:
            os.remove(html_file_name)
        if temp_html_file is not None:
            temp_html_file.close()

        return pdf_base64