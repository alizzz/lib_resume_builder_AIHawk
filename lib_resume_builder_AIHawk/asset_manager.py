import os
import traceback
from typing import List, Dict, Optional, Union
from lib_resume_builder_AIHawk.config import GlobalConfig

global_config = GlobalConfig()

class AssetManager:
    def __init__(self, path: str, base_path:str=None):
        self.path = path
        self.base_path = base_path

    def load_asset(self, key: str, ext:str=None, map:Dict[str,str]=None, comment_line_starts_with='#!') -> str:
        asset = None
        fp = None

        try:
            file_path = os.path.join(self.base_path, self.path, f"{key}")
            file_path_ext = os.path.join(self.base_path, self.path, f"{key}.{ext}")
            if os.path.isfile(file_path):
                fp = file_path
            elif os.path.isfile(file_path_ext):
                fp = file_path_ext
            else:
                print(f"Warning: Unable to read asset {key}")
                return None

            with open(fp, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if comment_line_starts_with:
                    asset = ''.join([ln for ln in lines if ln and not ln.strip().startswith(comment_line_starts_with) ])
                else:
                    asset = f.read()
            if map:
                asset = asset.format_map(map)

        except Exception as e:
            print(f'Failed to load asset {key}. Error:{e} TB:{traceback.format_exc()}')
            return None
        return asset if asset else print(f"Warning: Unable to read asset {key}")

class PromptManager(AssetManager):
    def __init__(self):
        super().__init__(path = 'prompts', base_path=global_config.lib_path)
    def load_prompt(self, key: str, ext='prompt', map:Dict[str,str]=None) -> str:
        return self.load_asset(key, ext, map)

class ChunkManager(AssetManager):
    def __init__(self):
        super().__init__(path = r'resume_templates\chunks', base_path=global_config.lib_path)
    def load_chunk(self, key: str, ext='chunk', map:Dict[str,str]=None) -> str:
        return self.load_asset(key, ext, map)