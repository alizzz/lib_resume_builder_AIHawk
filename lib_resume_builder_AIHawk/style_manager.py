import os
from pathlib import Path
from typing import Dict, List, Tuple
from pathlib import Path

class StyleManager:
    
    def __init__(self, styles_file=None, styles_directory=None):
        self.styles_directory = styles_directory
        self.styles_file = styles_file

    def set_styles_directory(self, styles_directory: Path):
        self.styles_directory = styles_directory

    def set_styles_file(self, file_name: str):
        self.styles_file = file_name

    def get_styles(self) -> Dict[str, Tuple[str, str]]:
        styles_to_files = {}
        try:
            files = os.listdir(self.styles_directory)
            for f in files:
                file_path = self.styles_directory / Path(f)
                style_name, author_link = self.get_style_name_from_file(file_path)
                if style_name is not None: styles_to_files[style_name] = (f, author_link)
                #if file_path.is_file():
                #    with open(file_path, 'r', encoding='utf-8') as file:
                #        first_line = file.readline().strip()
                #        if first_line.startswith("/*") and first_line.endswith("*/"):
                #            content = first_line[2:-2].strip()
                #            if '$' in content:
                #                style_name, author_link = content.split('$', 1)
                #                style_name = style_name.strip()
                #                author_link = author_link.strip()
                #                styles_to_files[style_name] = (f, author_link)
        except FileNotFoundError:
            print(f"Directory {self.styles_directory} not found.")
        except PermissionError:
            print(f"Permission denied to access {self.styles_directory}.")
        return styles_to_files

    def format_choices(self, styles_to_files: Dict[str, Tuple[str, str]]) -> List[str]:
        return [f"{style_name} (style author -> {author_link})" for style_name, (file_name, author_link) in styles_to_files.items()]

    def get_style_path(self, selected_style: str) -> Path:
        file_name = self.styles_file
        if file_name is None or len(file_name)==0:
            styles = self.get_styles()
            file_name, _ = styles[selected_style]
            self.styles_file = file_name
        ret_path = Path.joinpath(self.styles_directory, file_name)
        return ret_path

    def get_style_name_from_file(self, file_path) -> Tuple[str, str] :
        style_name = None
        author_link=None
        try:
            if file_path.name.startswith('--'): return (None, None)
            if file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as file:
                    first_line = file.readline().strip()
                    if first_line.startswith("/*") and first_line.endswith("*/"):
                        content = first_line[2:-2].strip()
                        if '$' in content:
                            style_name, author_link = content.split('$', 1)
                            style_name = style_name.strip()
                            author_link = author_link.strip()
                        else:
                            style_name = content.strip()
                            author_link = 'UNK'
                            print(f'StyleManager::get_style_name_from_file. There is no $ sign in the first line. Use {content} as style name, and UNK as Author\'s name. File: {file_path}' )
                    else:
                        print(f'StyleManager::get_style_name_from_file. File: {file_path} does not start with /* ... */')

            else:
                print(f'StyleManager::get_style_name_from_file. File: {file_path} is not a valid file path')

        except FileNotFoundError:
            print(f"Directory {self.styles_directory} not found.")
        except PermissionError:
            print(f"Permission denied to access {self.styles_directory}.")
        except Exception as e:
            print(f'Exception in StyleManager::get_style_name_from_file. File: {file_path}. Exception:{e}')

        return (style_name, author_link)