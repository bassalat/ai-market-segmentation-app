from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum

class BusinessModel(Enum):
    B2B = "B2B"
    B2C = "B2C"
    BOTH = "Both"

class CompanySize(Enum):
    STARTUP = "Startup"
    SMB = "Small/Medium Business"
    MID_MARKET = "Mid-Market"
    ENTERPRISE = "Enterprise"

@dataclass
class BasicInfo:
    company_name: str
    industry: str
    business_model: BusinessModel
    description: str

@dataclass
class B2BInputs:
    target_company_sizes: List[CompanySize]
    target_industries: List[str]
    deal_size_range: str
    sales_cycle_length: str
    decision_maker_roles: List[str]
    pain_points: str
    geographic_focus: List[str]

@dataclass
class B2CInputs:
    target_age_groups: List[str]
    gender_focus: str
    income_brackets: List[str]
    geographic_markets: List[str]
    product_category: str
    purchase_frequency: str
    customer_motivations: List[str]
    lifestyle_categories: List[str]

@dataclass
class UserInputs:
    basic_info: BasicInfo
    b2b_inputs: Optional[B2BInputs] = None
    b2c_inputs: Optional[B2CInputs] = None