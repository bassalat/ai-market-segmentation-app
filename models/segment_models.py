from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class Segment:
    name: str
    characteristics: List[str]
    size_percentage: float
    size_estimation: str
    pain_points: List[str]
    buying_triggers: List[str]
    preferred_channels: List[str]
    messaging_hooks: List[str]
    persona_description: str
    demographics: Dict[str, str]
    psychographics: List[str]
    use_cases: List[str]
    role_specific_pain_points: Dict[str, List[str]]

@dataclass
class Competitor:
    name: str
    funding: str
    solution_specialty: str
    market_position: str

@dataclass
class MarketAnalysis:
    total_addressable_market: str
    key_insights: List[str]
    segments: List[Segment]
    industry_trends: List[str]
    competitive_landscape: str
    industry_growth_factors: List[str]
    industry_cagr: str
    commercial_urgencies: List[str]
    top_competitors: List[Competitor]

@dataclass
class SegmentationResults:
    market_analysis: MarketAnalysis
    segments: List[Segment]
    implementation_roadmap: Dict[str, List[str]]
    quick_wins: List[str]
    success_metrics: List[str]