from pydantic import BaseModel
from typing import List

class SubsidyScheme(BaseModel):
    scheme_id: str
    scheme_name: str
    relevance: str
    eligibility_status: str
    eligibility_factors: List[str]
    required_information: List[str]
    support_information: str
    verification_required: bool
    data_source: str
