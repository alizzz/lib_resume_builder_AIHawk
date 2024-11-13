from typing import List, Dict, Optional, Union
import yaml
import os.path
import copy
import json
from string import Template
from pydantic import BaseModel, EmailStr, HttpUrl
from utils import custom_json_serializer#, class_to_text, create_vector_docs
from langchain_core.documents import Document as LangchainDoc
from langchain.text_splitter import RecursiveCharacterTextSplitter

def read_chunk(fn, path='', enc='utf-8', **kwargs):
    if not (os.path.exists(fn) and os.path.isfile(fn)):
        raise FileNotFoundError()
    try:
        with open(fn, "r", encoding=enc) as file:
            chunk_fmt = file.read()

        if chunk_fmt:
            if kwargs:
                return chunk_fmt.format(**kwargs)
            else:
                return chunk_fmt
        else:
            return None

    except FileNotFoundError:
        print(f'FileNotFound exception for {fn} from Resume::html::get_chunk()')
    except Exception as e:
        print(f'Exception for {fn} from Resume::html::get_chunk(). Exception:{e}')

def normalize_exam_format(exam):
    if isinstance(exam, dict):
        return [{k: v} for k, v in exam.items()]
    return exam


# Definizione dei modelli Pydantic
class PersonalInformation(BaseModel):
    name: Optional[str]
    surname: Optional[str]
    date_of_birth: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    phone_prefix: Optional[str]
    phone: Optional[str]
    email: Optional[EmailStr]
    github: Optional[HttpUrl]
    linkedin: Optional[HttpUrl]
    years_technical_experience: Optional[str]
    years_mgmt_experience: Optional[str]
    name_prefix: Optional[str]
    name_suffix: Optional[str]

class Education(BaseModel):
    degree: Optional[str]
    university: Optional[str]
    gpa: Optional[str]
    graduation_year: Optional[str]
    field_of_study: Optional[str]
    exam: Optional[Union[List[Dict[str, str]], Dict[str, str]]]

class Achievement(BaseModel):
    name: Optional[str]
    description: Optional[str]
    def text(self):
        return f'{self.name}:{self.description}'

class WorkExperience(BaseModel):
    position: Optional[str]
    company: Optional[str]
    employment_period: Optional[str]
    location: Optional[str]
    industry: Optional[str]
    summary: Optional[str]
    key_responsibilities: Optional[List[str]]
    skills_acquired: Optional[List[str]]
    #achievements: Optional[List[Achievement]]
    def text(self):
        return (f'position: {self.position}; '
            f'company: {self.company}; '
            f'employment period: {self.employment_period}; '
            f'location: {self.location}; '
            f'industry: {self.industry}; '
            f'summary responsibilities: {self.summary}'
            f'key responsibilities: {";".join(self.key_responsibilities) if self.key_responsibilities else ""}'
            f'skills: {",".join(self.skills_acquired) if self.skills_acquired else ""}')

class Project(BaseModel):
    name: Optional[str]
    description: Optional[str]
    link: Optional[HttpUrl]

class Language(BaseModel):
    language: Optional[str]
    proficiency: Optional[str]

class Availability(BaseModel):
    notice_period: Optional[str]

class SalaryExpectations(BaseModel):
    salary_range_usd: Optional[str]

class SelfIdentification(BaseModel):
    gender: Optional[str]
    pronouns: Optional[str]
    veteran: Optional[str]
    disability: Optional[str]
    ethnicity: Optional[str]

class LegalAuthorization(BaseModel):
    eu_work_authorization: Optional[str]
    us_work_authorization: Optional[str]
    requires_us_visa: Optional[str]
    requires_us_sponsorship: Optional[str]
    requires_eu_visa: Optional[str]  # Added field
    legally_allowed_to_work_in_eu: Optional[str]  # Added field
    legally_allowed_to_work_in_us: Optional[str]  # Added field
    requires_eu_sponsorship: Optional[str]

class Skill(BaseModel):
    category: Optional[str]
    skill_lst: Optional[str]
    def text(self):
        return f'{self.category}: {self.skill_lst}'

class KeyValue(BaseModel):
    key: Optional[str]
    value: Optional[str]

    def text(self):
        return f'{self.key}:{self.value}'

    def html(self, li_kv_class='li-kv', li_kv_name_class = 'kv-name', li_kv_desc_class='kv-desc', li_kv_delim=' '):
        d =copy.deepcopy(self.dict())
        d['li_kv_class']=li_kv_class
        d['li_kv_name_class']=li_kv_name_class
        d['li_kv_desc_class']=li_kv_desc_class
        d['li_kv_delim']=li_kv_delim if self.name else ''
        return read_chunk(r'resume_templates\chunks\li_name_desc.chunk', **d)

class CareerSummary(BaseModel):
    career_summary: Optional[List[str]]
    def text(self) -> str:
        # Format each item with a bullet point and join them with new lines
        if self.career_summary:
            return "\n".join(f"- {item}" for item in self.career_summary)
        return ""


class CareerHighlights(BaseModel):
    highlights: Optional[List[KeyValue]]

    def text(self) -> str:
        if self.highlights:
            return "\n".join(f"- {highlight.key}: {highlight.value}" for highlight in self.highlights if
                             highlight.key and highlight.value)
        return ""

class WorkExperiences(BaseModel):
    work_experiences: Optional[List[WorkExperience]]
    def text(self):
        if self.work_experiences:
            "\n\n".join(experience.text()
                        for experience in self.work_experiences)
class ListOfStrings(BaseModel):
    ul:Optional[List[str]]

class Resume(BaseModel):
    personal_information: Optional[PersonalInformation]
    resume_title: Optional[str]
    career_summary:Optional[List[str]]
    career_highlights: Optional[List[KeyValue]]
    education_details: Optional[List[Education]]
    work_experiences: Optional[List[WorkExperience]]
    achievements: Optional[List[Achievement]]
    skills: Optional[List[KeyValue]]
    projects: Optional[List[Project]]
    certifications: Optional[List[str]]
    languages: Optional[List[Language]]
    interests: Optional[List[str]]
    availability: Optional[Availability]
    salary_expectations: Optional[SalaryExpectations]
    self_identification: Optional[SelfIdentification]
    legal_authorization: Optional[LegalAuthorization]
    style_path:Optional[str]

    def __init__(self, yaml_str: str):
        try:
            # Parse the YAML string
            data = yaml.safe_load(yaml_str)

            # Normalize the exam format
            #if 'education_details' in data:
            #    for ed in data['education_details']:
            #        if 'exam' in ed:
            #            ed['exam'] = self.normalize_exam_format(ed['exam'])

            # Create an instance of Resume from the parsed data
            super().__init__(**data)
            print(f'Resume __init__ completed')
        except yaml.YAMLError as e:
            raise ValueError("Error parsing YAML file.") from e
        except Exception as e:
            raise Exception(f"Unexpected error while parsing YAML: {e}") from e
