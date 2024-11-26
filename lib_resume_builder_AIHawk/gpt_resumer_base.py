import os
import re
import textwrap
import traceback
from typing import Dict, List
import json
import yaml
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.messages.base import BaseMessage
from langchain_core.messages.system import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from lib_resume_builder_AIHawk.asset_manager import PromptManager
from lib_resume_builder_AIHawk.llm_logger import LLMLogger
from lib_resume_builder_AIHawk.resume import Resume
from lib_resume_builder_AIHawk.utils import read_chunk, find_valid_path
from src.job import Job, JobRelevance

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

    def __call__(self, messages: List[BaseMessage]) -> str:

        reply:AIMessage = self.llm(messages)
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
    def __init__(self, openai_api_key, strings=None, tempertature_cheap=0.8, temperature_good = 0.7):
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

        # if self.job_desc:
        #     out_prompt += [f"***Job Description:*** \n{job_desc}"]
        #
        # if self.job_title:
        #     out_prompt += [f"***Job Description:*** \n{job_title}"]

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

        if sys_p:
            template = sys_p + '\n' + template

        # Preprocess a template string to remove unnecessary indentation.
        ret = textwrap.dedent(template)
        if format_instructions:
            return ret+"\n\n"+format_instructions
        else:
            if add_format_instructions_template:
                return ret + "\n\nFormat Instructions:\n{format_instructions}"


        return textwrap.dedent(template)

    def is_relevant_job(self, job: Job,
                        relevance_criteria: str = 'software development, software engineering, machine learning, data science, analytics, or AI') -> bool:
        relevant = False

        if job.relevancy and job.relevancy.lower() !='unk':
            print(f"In is_relevant for jobid:{job.id}. Value has been set to {job.is_relevant}. skipping")
            return job.is_relevant

        try:
            if job.job_description_summary:
                job_desc = job.job_description_summary
            else:
                if not job.description:
                    raise Exception('Both job description and job description summary are empty. Unable to continue')
                job_desc = job.description

            parser = PydanticOutputParser(pydantic_object=JobRelevance)

            prompt = self._load_and_prepare_prompt(prompt_key='is_job_description_relevant',
                                                   map_data={"relevance_criteria": relevance_criteria,
                                                             "job_desc": job.job_description_summary},
                                                   parser=parser, msg_chain=self.msg_chain)

            relevance: JobRelevance = self._invoke_chain(prompt, parser=parser, msg_chain=self.msg_chain,
                                                         llm=self.llm_cheap)

            print(
                f'JobRelevance: Job: {job.title} at {job.company} is {'' if relevance.relevant else 'not'} relevant with confidence {relevance.confidence * 100}%')

            job.relevancy = relevance.relevant
            job.is_relevant_confidence = relevance.confidence
            job.industry = relevance.industry
            job.family = relevance.family

            return job.relevancy
        except Exception as e:
            print(f"Error while extracting job relevance for job id: {job.id} Error:{e} {traceback.format_exc()}")

        try:
            if job.job_description_summary:
                job_desc = job.job_description_summary
            else:
                if not job.description:
                    raise Exception('Both job description and job description summary are empty. Unable to continue')
                job_desc = job.description
            # ToDo Load prompt from file (or dict)
            parser = PydanticOutputParser(pydantic_object=JobRelevance)
            prompt_is_relevant = """You are an experienced HR professional and job desciption analyst. 
            Read the job description and thoroughly analyze it. Answer the question if this job is relevant to {relevance_criteria}. 
            Answer only the relevance and your confidence in the answer. Respond with the valid json using the following format
            "relevant": "Yes"  or "No",
            "confidence": how confident are you,
            "industry": what industry job is in,
            "job family": job family

            **Job description** 
              {job_desc}

            do not output anything else. Do not output ```json or ```
            """

            prompt_sanitize_template = self._preprocess_template_string(prompt_is_relevant)
            prompt = ChatPromptTemplate.from_template(prompt_sanitize_template)
            chain = prompt | self.llm_cheap | StrOutputParser()

            # ToDo Removed while testing. Restore when testing is finished
            # output = chain.invoke({"relevance_criteria": relevance_criteria, "job_desc": job_desc})
            output = """{ "relevant": "Yes", "confidence": 0.95, "industry": "Technology", "job family": "AI/ML Engineering and Product Development" }"""

            j = json.loads(output, strict=False)
            job.relevancy = j["relevant"]
            job.is_relevant_confidence = j['confidence']
            job.industry = j['industry']
            job.family = j['job family']
            relevant = j["relevant"].lower() in ['yes', 'y', 'true', 't']
            print(f'Is_relevant for {job.title} at {job.company} returns {output}')
        except Exception as e:
            print(f'Exception in is_relevant position. Error: {e}')

        return relevant

    #this is from GPTAnswerer, probably not needed here
    def set_job_application_profile(self, job_application_profile):
        self.job_application_profile = job_application_profile



    def _load_and_prepare_prompt(self,  prompt_key: str, map_data: dict= {}, parser=None, msg_chain: List[BaseMessage]=[],
                                 do_not_use_long_message_chain:bool = True, no_system_prompt:bool=False) -> ChatPromptTemplate:
        try:
            if not parser:
                parser = StrOutputParser()

            if isinstance(parser, StrOutputParser):
                format_instructions = "Provide a plain text response without any extra formatting"
            else:
                try:
                    format_instructions = parser.get_format_instructions()
                except:
                    format_instructions = ''

            prompt_template = PromptManager().load_prompt(prompt_key, map=map_data)
            formatted_prompt = self._preprocess_template_string(
                prompt_template, format_instructions=format_instructions
            )

            #Note: To maintain continuity of responses we need to send msg_chain
            #But it is expensive - a lot of tokens in the chain
            #Also every requiest is pretty much self-sufficient, and does not depend on previous answers
            #therefore here we reduce number of messages in the chain, and pretend that this is the first message
            human_message = HumanMessage(formatted_prompt, prompt_key=prompt_key, job_id=map_data.get("job_id"))

            msg_chain.append(human_message)
            if do_not_use_long_message_chain:
                msg = [SystemMessage(self.system_msg)] if (not no_system_prompt and self.system_msg)  else []

                msg.append(human_message)
            else:
                msg = [m for m in msg_chain]

            return ChatPromptTemplate(msg)
        except Exception as e:
            print(f"Error loading or preparing prompt {prompt_key}: {e}")
            #self.logger.error(f"Error loading or preparing prompt {prompt_key}: {e}")
            raise e

    def _invoke_chain(self, prompt_template, parser, msg_chain: List[BaseMessage]=[], key:str=None, llm:LoggerChatModel=None):
        try:
            if not llm: llm = self.llm_cheap

            chain = prompt_template | llm
            output:AIMessage = chain.invoke({})

            msg_chain.append(output)
            return parser.invoke(output)
        except Exception as e:
            print(f"Error invoking chain: {e}")
            raise e