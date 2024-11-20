import os
import re
import textwrap
from typing import Dict, List

import yaml
from langchain_core.messages.ai import AIMessage
from langchain_openai import ChatOpenAI

from lib_resume_builder_AIHawk.asset_manager import PromptManager
from lib_resume_builder_AIHawk.llm_logger import LLMLogger
from lib_resume_builder_AIHawk.resume import Resume
from lib_resume_builder_AIHawk.utils import read_chunk, find_valid_path


# removes \n and multiple spaces from a string
def clean_html_string(html_string):
    # Remove newline characters and leading/trailing spaces
    cleaned_string = html_string.replace("\n", " ").strip()

    # Replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)

    return cleaned_string

class LoggerChatModel:

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.chat_history:str = None

    def reset_chat_history(self, system_instruction = None):
        #ToDo set system instruction
        self.chat_history=None

    def __call__(self, messages: List[Dict[str, str]]) -> str:

        reply = self.llm(messages)
        parsed_reply = self.parse_llmresult(reply)
        LLMLogger.log_request(prompts=messages, parsed_reply=parsed_reply)
        return reply

    def parse_llmresult(self, llmresult: AIMessage) -> Dict[str, Dict]:
        content = llmresult.content
        response_metadata = llmresult.response_metadata
        id_ = llmresult.id
        usage_metadata = llmresult.usage_metadata
        parsed_result = {
            "content": content,
            "response_metadata": {
                "model_name": response_metadata.get("model_name", ""),
                "system_fingerprint": response_metadata.get("system_fingerprint", ""),
                "finish_reason": response_metadata.get("finish_reason", ""),
                "logprobs": response_metadata.get("logprobs", None),
            },
            "id": id_,
            "usage_metadata": {
                "input_tokens": usage_metadata.get("input_tokens", 0),
                "output_tokens": usage_metadata.get("output_tokens", 0),
                "total_tokens": usage_metadata.get("total_tokens", 0),
                "cached_tokens": response_metadata.get('token_usage').get('prompt_tokens_details').get('cached_tokens', 0)
            },
        }
        return parsed_result

class LLMResumerBase:
    def __init__(self, openai_api_key, strings, tempertature_cheap=0.8, temperature_good = 0.7):
        self.llm_cheap = LoggerChatModel(ChatOpenAI(model_name="gpt-4o-mini", openai_api_key=openai_api_key, temperature=tempertature_cheap))
        self.llm_good = LoggerChatModel(ChatOpenAI(model_name="gpt-4o", openai_api_key=openai_api_key, temperature=temperature_good))
        self.strings = strings
        self.system_msg = None
        self.resume: Resume = None
        self.msg_chain = []


    def set_resume(self, resume:Resume=None):
        if isinstance(resume, Resume):
            self.resume=Resume
        elif isinstance(resume, str):
            #it can be either content or
            resume_fn = find_valid_path(resume, 'yaml', search_path=['data_folder'])
            if resume_fn:
                self.resume=read_chunk(resume_fn)


    def inject_prompt(self, prompt, system_msg='hawk_system.prompt', resume=None, job_desc=None, job_title=None):
        out_prompt = []
        if system_msg:
            system_msg_file = find_valid_path(system_msg, 'prompt', search_path=['prompts'])
            if system_msg_file:
                system_msg_content = read_chunk(system_msg_file)
                out_prompt += system_msg_content
            else: #can't find a file, treat as a text
                out_prompt+=system_msg

        if isinstance(resume, str):
            out_prompt+=[f"***Applicant's Resume:*** \n{resume}"]
        elif isinstance(resume, Resume):
            out_prompt += [f"***Applicant's Resume:*** \n{yaml.dump(resume)}"]

        if job_desc:
            out_prompt += [f"***Job Description:*** \n{resume}"]

        if self.job_desc:
            out_prompt += [f"***Job Description:*** \n{job_desc}"]

        if self.job_title:
            out_prompt += [f"***Job Description:*** \n{job_title}"]

        out_prompt = out_prompt + [prompt]

        return '\n\n'.join(out_prompt)

    @staticmethod
    def _preprocess_template_string(template: str, add_format_instructions_template:bool=False, format_instructions:str=None, sys_prompt=None, imports=[], job:str=None, resume:str = None, injection_prompt:str=None) -> str:

        # imports is a Dict[str,Dict[str,str]
        # ex. imports = {name:'system.prompt', "map":{'val0':'val0 content', 'val1':'val1 content'}
        def replace_import_lines(input_string, imports):
            output_lines = []
            for line in input_string.splitlines():
                if line.startswith("#import"):
                    _, file_name = line.split(maxsplit=1)
                    file_name = file_name.strip()
                    if os.path.exists(file_name):
                        with open(file_name, 'r', encoding='utf-8') as file:
                            file_content = file.read()
                            output_lines.append(file_content)
                    else:
                        print(f"Warning: File '{file_name}' not found. Keeping the original line.")
                        output_lines.append(line)
                else:
                    output_lines.append(line)
            return "\n".join(output_lines)

        sys_p = ''
        if sys_prompt:
            if isinstance(sys_prompt, str):
                sys_p = PromptManager().load_prompt(sys_prompt)
                if sys_p is None or sys_p.startswith('Warning: Unable to read'):
                    sys_p = ''
                #
                # prompt_path = find_valid_path(sys_prompt, "prompt", search_path=["prompts"], base_path=global_config.lib_path)
                # if prompt_path:
                #     prompt = read_chunk(prompt_path)

        template = sys_p + '\n' + template

        # Preprocess a template string to remove unnecessary indentation.
        ret = textwrap.dedent(template)
        if format_instructions:
            return ret+"\n\n"+format_instructions
        else:
            if add_format_instructions_template:
                return ret + "\n\nFormat Instructions:\n{format_instructions}"


        return textwrap.dedent(template)








