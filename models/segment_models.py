from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class SourceQuality(Enum):
    TIER_1 = "Tier 1"  # Academic, Government, Major Research Firms
    TIER_2 = "Tier 2"  # Industry Reports, Major Publications
    TIER_3 = "Tier 3"  # Company Blogs, Trade Publications
    TIER_4 = "Tier 4"  # Social Media, Forums, Unverified

class ContentType(Enum):
    ACADEMIC_PAPER = "Academic Paper"
    INDUSTRY_REPORT = "Industry Report"
    NEWS_ARTICLE = "News Article"
    COMPANY_BLOG = "Company Blog"
    GOVERNMENT_DATA = "Government Data"
    PRESS_RELEASE = "Press Release"
    CONFERENCE_PRESENTATION = "Conference Presentation"
    MARKET_RESEARCH = "Market Research"
    FINANCIAL_REPORT = "Financial Report"
    WHITE_PAPER = "White Paper"

@dataclass
class DataSource:
    """Comprehensive source metadata for research attribution"""
    url: str
    title: str
    author: Optional[str] = None
    organization: Optional[str] = None
    publication_date: Optional[datetime] = None
    access_date: datetime = field(default_factory=datetime.now)
    domain_authority: Optional[int] = None  # 0-100 scale
    content_type: ContentType = ContentType.NEWS_ARTICLE
    source_quality: SourceQuality = SourceQuality.TIER_3
    confidence_score: float = 0.0  # 0.0-1.0 scale
    relevance_score: float = 0.0  # 0.0-1.0 scale
    data_quality_rating: float = 0.0  # 0.0-1.0 scale
    is_paywall: bool = False
    language: str = "en"
    country_focus: Optional[str] = None
    
    def get_citation_text(self) -> str:
        """Generate formatted citation text"""
        citation_parts = []
        
        if self.author:
            citation_parts.append(f"{self.author}")
        elif self.organization:
            citation_parts.append(f"{self.organization}")
        
        citation_parts.append(f'"{self.title}"')
        
        if self.publication_date:
            citation_parts.append(f"({self.publication_date.year})")
        
        citation_parts.append(f"Retrieved from {self.url}")
        
        return ". ".join(citation_parts)
    
    def get_quality_indicator(self) -> str:
        """Get visual quality indicator"""
        quality_stars = {
            SourceQuality.TIER_1: "★★★★★",
            SourceQuality.TIER_2: "★★★★☆", 
            SourceQuality.TIER_3: "★★★☆☆",
            SourceQuality.TIER_4: "★★☆☆☆"
        }
        return quality_stars.get(self.source_quality, "★☆☆☆☆")

@dataclass
class Citation:
    """Detailed citation with specific reference information"""
    source_id: str  # Reference to DataSource
    page_number: Optional[int] = None
    section: Optional[str] = None
    quote_text: Optional[str] = None
    context: Optional[str] = None
    verification_status: str = "unverified"  # verified, unverified, disputed
    confidence_level: str = "medium"  # high, medium, low
    
    def get_inline_citation(self) -> str:
        """Generate inline citation format"""
        parts = [self.source_id]
        if self.page_number:
            parts.append(f"p. {self.page_number}")
        return f"[{', '.join(parts)}]"

@dataclass
class MarketDataPoint:
    """Individual market statistic with full source attribution"""
    value: str
    metric_type: str  # market_size, growth_rate, market_share, etc.
    currency: Optional[str] = "USD"
    time_period: Optional[str] = None
    geographic_scope: Optional[str] = None
    sources: List[DataSource] = field(default_factory=list)
    citations: List[Citation] = field(default_factory=list)
    confidence_score: float = 0.0
    cross_validated: bool = False
    
    def get_formatted_value_with_citation(self) -> str:
        """Get value with inline citations"""
        citation_text = ", ".join([c.get_inline_citation() for c in self.citations])
        return f"{self.value} {citation_text}" if citation_text else self.value

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
    # Enhanced with source tracking
    market_data: List[MarketDataPoint] = field(default_factory=list)
    sources: List[DataSource] = field(default_factory=list)
    confidence_score: float = 0.0
    validation_notes: List[str] = field(default_factory=list)
    
    @property
    def description(self) -> str:
        """Alias for persona_description for backward compatibility"""
        return self.persona_description

@dataclass
class CompetitiveAnalysis:
    """Enhanced competitive analysis with SWOT and detailed intelligence"""
    name: str
    funding: str
    solution_specialty: str
    market_position: str
    # Enhanced competitive intelligence
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    opportunities: List[str] = field(default_factory=list)
    threats: List[str] = field(default_factory=list)
    pricing_model: Optional[str] = None
    target_segments: List[str] = field(default_factory=list)
    geographic_presence: List[str] = field(default_factory=list)
    technology_stack: List[str] = field(default_factory=list)
    key_partnerships: List[str] = field(default_factory=list)
    recent_developments: List[str] = field(default_factory=list)
    sources: List[DataSource] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Competitor:
    """Legacy compatibility - redirects to CompetitiveAnalysis"""
    name: str
    funding: str
    solution_specialty: str
    market_position: str

@dataclass
class MarketIntelligence:
    """Comprehensive market intelligence with enhanced analytics"""
    # Market size and growth
    total_addressable_market: MarketDataPoint
    serviceable_addressable_market: Optional[MarketDataPoint] = None
    serviceable_obtainable_market: Optional[MarketDataPoint] = None
    market_growth_rate: Optional[MarketDataPoint] = None
    historical_growth: List[MarketDataPoint] = field(default_factory=list)
    
    # Geographic analysis
    geographic_breakdown: Dict[str, MarketDataPoint] = field(default_factory=dict)
    emerging_markets: List[str] = field(default_factory=list)
    mature_markets: List[str] = field(default_factory=list)
    
    # Market dynamics
    market_maturity_stage: str = "unknown"  # emerging, growth, mature, decline
    seasonal_factors: List[str] = field(default_factory=list)
    cyclical_patterns: List[str] = field(default_factory=list)
    regulatory_factors: List[str] = field(default_factory=list)
    
    # Technology and innovation
    technology_adoption_curve: Optional[str] = None
    innovation_timeline: List[str] = field(default_factory=list)
    disruptive_technologies: List[str] = field(default_factory=list)
    
    # Source attribution
    sources: List[DataSource] = field(default_factory=list)
    research_methodology: List[str] = field(default_factory=list)
    data_quality_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class MarketAnalysis:
    """Enhanced market analysis with comprehensive intelligence"""
    # Core analysis (legacy compatibility)
    total_addressable_market: str
    key_insights: List[str]
    segments: List[Segment]
    industry_trends: List[str]
    competitive_landscape: str
    industry_growth_factors: List[str]
    industry_cagr: str
    commercial_urgencies: List[str]
    top_competitors: List[Competitor]
    
    # Enhanced intelligence
    market_intelligence: Optional[MarketIntelligence] = None
    competitive_analysis: List[CompetitiveAnalysis] = field(default_factory=list)
    
    # Source attribution and quality
    all_sources: List[DataSource] = field(default_factory=list)
    research_quality_score: float = 0.0
    source_diversity_score: float = 0.0
    data_recency_score: float = 0.0
    cross_validation_score: float = 0.0
    
    # Research metadata
    research_date: datetime = field(default_factory=datetime.now)
    research_scope: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    confidence_level: str = "medium"

@dataclass
class ResearchBibliography:
    """Comprehensive bibliography and source management"""
    sources_by_tier: Dict[str, List[DataSource]] = field(default_factory=dict)
    sources_by_type: Dict[str, List[DataSource]] = field(default_factory=dict)
    total_sources: int = 0
    unique_domains: int = 0
    average_source_quality: float = 0.0
    publication_date_range: Optional[str] = None
    geographic_coverage: List[str] = field(default_factory=list)
    
    def generate_apa_bibliography(self) -> List[str]:
        """Generate APA format bibliography"""
        citations = []
        for source in sorted(self.sources_by_tier.get('all', []), 
                           key=lambda x: x.author or x.organization or ""):
            citations.append(source.get_citation_text())
        return citations
    
    def get_source_quality_summary(self) -> Dict[str, int]:
        """Get summary of source quality distribution"""
        quality_counts = {}
        for sources in self.sources_by_tier.values():
            for source in sources:
                quality = source.source_quality.value
                quality_counts[quality] = quality_counts.get(quality, 0) + 1
        return quality_counts

@dataclass
class SegmentationResults:
    """Enhanced segmentation results with comprehensive research attribution"""
    # Core results (legacy compatibility)
    market_analysis: MarketAnalysis
    segments: List[Segment]
    implementation_roadmap: Dict[str, List[str]]
    quick_wins: List[str]
    success_metrics: List[str]
    
    # Enhanced research components
    research_bibliography: ResearchBibliography = field(default_factory=ResearchBibliography)
    data_collection_summary: Dict[str, int] = field(default_factory=dict)
    quality_assessment: Dict[str, float] = field(default_factory=dict)
    
    # Research methodology and validation
    search_queries_used: List[str] = field(default_factory=list)
    validation_methods: List[str] = field(default_factory=list)
    research_limitations: List[str] = field(default_factory=list)
    
    # Export and sharing metadata
    generation_timestamp: datetime = field(default_factory=datetime.now)
    research_version: str = "2.0"
    citations_included: bool = True