from dataclasses import dataclass
from typing import List, Optional, Dict, Any
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
    # Industry & Target Customer (PRD Priority: ⭐️⭐️⭐️)
    target_company_types: List[str]  # fintech, HR tech, retail, etc.
    target_company_sizes: List[CompanySize]  # startup, SMB, mid-market, enterprise
    target_industries: List[str]
    geographic_focus: List[str]
    
    # Buyer Roles (PRD Priority: ⭐️⭐️⭐️)
    decision_maker_roles: List[str]  # CTO, Head of Ops, etc.
    
    # Pain Points & Use Cases (PRD Priority: ⭐️⭐️⭐️)
    main_problem_solved: str  # Core problem the product solves
    practical_use_cases: str  # 1-2 practical ways customers use product
    pain_points: str
    
    # Deal Dynamics (PRD Priority: ⭐️⭐️)
    deal_size_range: str
    sales_cycle_length: str
    
    # Tool Fit (PRD Priority: ⭐️⭐️)
    integration_requirements: str  # Tools customers need to integrate with
    
    # Triggers & Timing (PRD Priority: ⭐️⭐️)
    buying_triggers: str  # When customers are likely to buy (after funding, org change)
    
    # Lead Source (PRD Priority: ⭐️⭐️)
    current_lead_sources: List[str]  # outbound, inbound, referrals
    
    # Budget Sense (PRD Priority: ⭐️⭐️)
    customer_budget_sensitivity: str  # tight budgets vs willing to pay for value

@dataclass
class B2CInputs:
    # Target Customer (PRD Priority: ⭐️⭐️⭐️)
    primary_target_customer: str  # students, working professionals, freelancers, mothers, Gen Z
    target_age_groups: List[str]
    gender_focus: str
    geographic_markets: List[str]
    
    # Buying Behavior (PRD Priority: ⭐️⭐️⭐️)
    purchase_frequency: str  # one-time, monthly, seasonally
    purchase_context: str  # for themselves, as gift, for others
    
    # Purchase Triggers (PRD Priority: ⭐️⭐️⭐️)
    buying_triggers: str  # holiday, stress, travel, life milestone
    
    # Motivations & Lifestyle (PRD Priority: ⭐️⭐️⭐️)
    customer_priorities: str  # convenience, looking good, saving money, feeling healthy
    price_vs_quality_focus: str  # price-conscious vs quality-focused
    
    # Product Fit (PRD Priority: ⭐️⭐️)
    product_type: str  # physical, digital, mix
    discovery_channels: List[str]  # Instagram, TikTok, Google, friends
    
    # Competitive Context (PRD Priority: ⭐️⭐️)
    existing_alternatives: str  # popular alternatives or brands customers use
    
    # Additional B2C fields
    income_brackets: List[str]
    product_category: str
    customer_motivations: List[str]
    lifestyle_categories: List[str]

@dataclass
class DocumentContext:
    has_context: bool = False
    processed_content: Dict[str, Any] = None
    summary: str = ""
    file_count: int = 0
    content_length: int = 0
    data_points: int = 0

@dataclass
class UserInputs:
    basic_info: BasicInfo
    b2b_inputs: Optional[B2BInputs] = None
    b2c_inputs: Optional[B2CInputs] = None
    document_context: Optional[DocumentContext] = None