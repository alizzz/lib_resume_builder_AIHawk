import json
import os.path
import textwrap
import traceback
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv
import csv

from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompt_values import StringPromptValue
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from lib_resume_builder_AIHawk.config import global_config

load_dotenv()


class LLMLogger:

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    @staticmethod
    def log_request(prompts, parsed_reply: Dict[str, Dict], key:str=""):
        try:
            calls_log = global_config.LOG_OUTPUT_FILE_PATH / f"open_ai_calls.{datetime.now().strftime("%Y-%m-%d")}.json"
            usage_log = global_config.LOG_OUTPUT_FILE_PATH / f"open_ai_usage.{datetime.now().strftime("%Y-%m-%d")}.csv"
            job_id = ''
            prompt_key = ''
            if isinstance(prompts, StringPromptValue):
                prompts = prompts.text
                last_human_message = None
            elif isinstance(prompts, Dict):
                # Convert prompts to a dictionary if they are not in the expected format
                try:
                    last_human_message = next((item for item in reversed(prompts.messages) if item.get("type") == 'human'), None)
                    job_id = last_human_message.get("job_id")
                    prompt_key = last_human_message.get("prompt_key")

                except Exception as e:
                    print(f'Unable to log job_id and prompt_key. ke={key}. prompts type: {type(prompts)} Error:{e}')

                prompts = {
                        f"prompt_{i + 1}": prompt.content
                        for i, prompt in enumerate(prompts.messages)
                }
            else:
                try:
                    last_human_message:HumanMessage = next((item for item in reversed(prompts.messages) if item.type.lower() == 'human'), None)
                    job_id = last_human_message.job_id
                    prompt_key = last_human_message.prompt_key
                    prompts = {
                        f"prompt_{i + 1}": prompt.content
                        for i, prompt in enumerate(prompts.messages)
                    }
                except Exception as e:
                    print(f'Unable to log job_id and prompt_key. ke={key}. prompts type: {type(prompts)} Error:{e}')

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Extract token usage details from the response
            token_usage = parsed_reply["usage_metadata"]
            output_tokens = token_usage["output_tokens"]
            input_tokens = token_usage["input_tokens"]
            cached_tokens= token_usage["cached_tokens"]
            total_tokens = token_usage["total_tokens"]

            # Extract model details from the response
            model_name:str = parsed_reply["response_metadata"]["model_name"]
            if model_name.startswith('gpt-4o'):
                if model_name.startswith('gpt-4o-mini'):
                    prompt_price_per_input_token = 0.15/1000000
                    prompt_price_per_output_token= 0.6/1000000
                    prompt_price_per_cached_token= 0.075/1000000
                else:
                    prompt_price_per_input_token = 2.5/1000000
                    prompt_price_per_output_token = 10/1000000
                    prompt_price_per_cached_token = 1.25/1000000
            else:
                #unknown model, assuming more expensive one
                prompt_price_per_input_token = 2.5 / 1000000
                prompt_price_per_output_token = 10 / 1000000
                prompt_price_per_cached_token = 1.25 / 1000000

            # Calculate the total cost of the API call
            input_tokens_cost = input_tokens * prompt_price_per_input_token
            input_cached_tokens_cost = cached_tokens * prompt_price_per_cached_token
            output_tokens_cost = output_tokens * prompt_price_per_output_token

            total_cost = input_tokens_cost + input_cached_tokens_cost + output_tokens_cost
            print(f'Model:{model_name}. key:{key if key else 'unk'}. id:{job_id}, prompt:{prompt_key} '
                  f'Total cost:{total_cost}/{total_tokens} (input tokens: {input_tokens_cost}/{input_tokens}, cached tokens:{input_cached_tokens_cost}/{cached_tokens}, output tokens:{output_tokens_cost}/{output_tokens})')
            # Create a log entry with all relevant information
            log_entry = {
                "model": model_name,
                "time": current_time,
                "job_id": job_id,
                "prompt_key": prompt_key,
                "key": key if key else '',
                "prompts": prompts,
                "replies": parsed_reply["content"],  # Response content
                "total_tokens": total_tokens,
                "input_tokens": input_tokens,
                "cached_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "input_tokens_cost": input_tokens_cost,
                "cached_tokens_cost": input_cached_tokens_cost,
                "output_tokens_cost": output_tokens_cost,
                "total_cost": total_cost
            }
            log_usage_entry={
                "model": model_name,
                "time": current_time,
                "job_id": job_id,
                "prompt_key": prompt_key,
                "key": key if key else '',
                "total_tokens": total_tokens,
                "input_tokens": input_tokens,
                "cached_tokens": cached_tokens,
                "output_tokens": output_tokens,
                "input_tokens_cost": input_tokens_cost,
                "cached_tokens_cost": input_cached_tokens_cost,
                "output_tokens_cost": output_tokens_cost,
                "total_cost": total_cost
            }
            # Write the log entry to the log file in JSON format
            with open(calls_log, "a", encoding="utf-8") as f:
                json_string = json.dumps(log_entry, ensure_ascii=False, indent=4)
                f.write(json_string + "\n")

            key_row = None
            if not os.path.exists(usage_log):
                key_row = [k for k in log_usage_entry.keys()]
            with open(usage_log, 'a', encoding="utf-8", newline='') as f2:
                writer = csv.writer(f2)
                if key_row: writer.writerow(key_row)
                writer.writerow([v for v in log_usage_entry.values()])
        except Exception as e:
            print(f'Exception in LLMLogger::log_request. Error: {e} {traceback.format_exc()}')

