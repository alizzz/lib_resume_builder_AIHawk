from pydantic import BaseModel

class JobRelevance(BaseModel):
    title:str
    relevant:bool
    confidence:float
    industry:str
    family:str

