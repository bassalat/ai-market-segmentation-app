"""
Advanced Competitive Intelligence Service
Implements comprehensive competitive analysis per PRD specifications including
detailed competitor profiling, market overlap analysis, feature comparison matrices, and pricing intelligence
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from services.claude_service import ClaudeService
from services.enhanced_search_service import EnhancedSearchService
import asyncio


@dataclass
class CompetitorProfile:
    """Detailed competitor profile per PRD specifications"""
    company_name: str
    headquarters: str
    organization_size: str  # employee count
    inception_year: int
    annual_revenue: str
    total_funding: str
    recent_funding: str
    customer_count: str
    regions_operating: List[str]
    target_industries: List[str]
    serving_size: List[str]  # SMB, Mid-Market, Enterprise
    product_focus: str
    specialty: str
    gtm_positioning: str
    channel_approach: str
    pricing_model: str
    overlap_percentage: int
    key_strengths: List[str]
    market_positioning: str


@dataclass
class FeatureComparison:
    """Feature comparison matrix entry"""
    feature_category: str
    our_capability: str
    competitor_capability: str
    advantage: str  # 'us', 'them', 'neutral'
    importance_score: int  # 1-10
    notes: str


@dataclass
class MarketOverlap:
    """Market overlap analysis"""
    competitor_name: str
    overlap_percentage: int
    overlap_areas: List[str]
    white_space_opportunities: List[str]
    competitive_threats: List[str]
    differentiation_opportunities: List[str]


class CompetitiveIntelligenceService:
    """Service for advanced competitive intelligence analysis"""
    
    def __init__(self, serper_api_key: str = None):
        self.claude_service = ClaudeService()
        self.search_service = EnhancedSearchService(serper_api_key) if serper_api_key else None
    
    async def analyze_competitive_landscape(
        self,
        user_inputs: Any,
        business_context: Dict[str, Any],
        market_analysis: Any,
        segments: List[Any]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive competitive intelligence analysis per PRD specifications
        """
        
        # Identify key competitors through multiple sources
        competitors = await self._identify_competitors(
            user_inputs, business_context, market_analysis
        )
        
        # Create detailed competitor profiles with business metrics
        competitor_profiles = await self._create_competitor_profiles(
            competitors, business_context, user_inputs
        )
        
        # Generate feature comparison matrix (Us vs Them)
        feature_comparison = await self._generate_feature_comparison(
            competitor_profiles, business_context, user_inputs
        )
        
        # Analyze market overlap and white spaces
        market_overlap = await self._analyze_market_overlap(
            competitor_profiles, segments, business_context
        )
        
        # Develop pricing intelligence
        pricing_intelligence = await self._analyze_pricing_strategies(
            competitor_profiles, business_context, user_inputs
        )
        
        # Create competitive positioning recommendations
        positioning_recommendations = await self._generate_positioning_recommendations(
            competitor_profiles, feature_comparison, market_overlap
        )
        
        return {
            'competitor_profiles': competitor_profiles,
            'feature_comparison_matrix': feature_comparison,
            'market_overlap_analysis': market_overlap,
            'pricing_intelligence': pricing_intelligence,
            'positioning_recommendations': positioning_recommendations,
            'competitive_summary': await self._create_competitive_summary(
                competitor_profiles, feature_comparison, market_overlap
            )
        }
    
    async def _identify_competitors(
        self,
        user_inputs: Any,
        business_context: Dict[str, Any],
        market_analysis: Any
    ) -> List[str]:
        """Identify key competitors through multiple sources"""
        
        # Extract business context for competitor identification
        industry = business_context['basic_info']['industry']
        description = business_context['basic_info']['description']
        company_name = business_context['basic_info']['company_name']
        
        # Search for competitors using enhanced search if available
        if self.search_service:
            competitor_search_results = await self.search_service.search_web(
                f"{industry} companies competitors alternatives {description}",
                max_results=10
            )
            
            # Extract competitor names from search results
            competitor_identification_prompt = f"""
            Identify key competitors from these search results:

            Search Results: {competitor_search_results}
            Our Business: {company_name} - {description}
            Industry: {industry}

            Extract 8-12 main competitors. Include:
            - Direct competitors (same market, similar solution)
            - Indirect competitors (different approach, same problem)
            - Alternative solutions (different category, overlapping use cases)

            For each competitor, provide just the company name.
            Format as a simple JSON array of company names.
            """
            
            competitors_data = await self.claude_service.get_completion(competitor_identification_prompt)
        else:
            # Fallback competitor identification without search
            competitors_data = await self._identify_competitors_without_search(
                user_inputs, business_context, market_analysis
            )
        
        return competitors_data
    
    async def _identify_competitors_without_search(
        self,
        user_inputs: Any,
        business_context: Dict[str, Any],
        market_analysis: Any
    ) -> List[str]:
        """Fallback competitor identification when search is not available"""
        
        competitor_prompt = f"""
        Based on the business context, identify likely competitors:

        Business Context: {business_context}
        User Inputs: {user_inputs}
        Market Analysis: {market_analysis}

        Identify 8-12 potential competitors including:
        1. Direct competitors in the same space
        2. Indirect competitors solving similar problems
        3. Alternative solutions and approaches
        4. Established players in adjacent markets

        Return as a JSON array of company names.
        """
        
        return await self.claude_service.get_completion(competitor_prompt)
    
    async def _create_competitor_profiles(
        self,
        competitors: List[str],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> List[CompetitorProfile]:
        """Create detailed competitor profiles with business metrics per PRD"""
        
        competitor_profiles = []
        
        # Process competitors in batches to avoid overwhelming the system
        batch_size = 3
        for i in range(0, len(competitors), batch_size):
            batch = competitors[i:i + batch_size]
            
            # Search for detailed information about each competitor
            profile_tasks = []
            for competitor in batch:
                profile_tasks.append(
                    self._create_single_competitor_profile(competitor, business_context)
                )
            
            # Execute profiles in parallel
            batch_profiles = await asyncio.gather(*profile_tasks, return_exceptions=True)
            
            for profile in batch_profiles:
                if not isinstance(profile, Exception):
                    competitor_profiles.append(profile)
        
        return competitor_profiles
    
    async def _create_single_competitor_profile(
        self,
        competitor_name: str,
        business_context: Dict[str, Any]
    ) -> CompetitorProfile:
        """Create detailed profile for a single competitor"""
        
        # Search for competitor information if search service available
        competitor_data = ""
        if self.search_service:
            search_query = f"{competitor_name} company funding revenue employees headquarters business model"
            search_results = await self.search_service.search_web(search_query, max_results=5)
            competitor_data = search_results
        
        profile_prompt = f"""
        Create a comprehensive competitor profile for {competitor_name}:

        Search Data: {competitor_data}
        Our Business Context: {business_context}

        Provide detailed profile including all PRD-specified business metrics:

        1. BASIC COMPANY INFORMATION:
           - Company name: {competitor_name}
           - Headquarters location (city, state/country)
           - Organization size (employee count range)
           - Inception/founding year
           - Current status (startup, growth, mature, public, etc.)

        2. FINANCIAL METRICS:
           - Annual revenue (or revenue range if public/known)
           - Total funding raised (if applicable)
           - Recent funding round details (amount, type, date)
           - Valuation (if known)

        3. MARKET PRESENCE:
           - Number of customers/users (if known)
           - Regions of operation (geographic presence)
           - Target industries served
           - Serving size focus (SMB, Mid-Market, Enterprise, Individual)

        4. PRODUCT & POSITIONING:
           - Product/solution focus and specialty
           - Key differentiators and unique selling points
           - Market positioning and messaging themes
           - Target customer personas

        5. GTM STRATEGY:
           - Go-to-market approach and positioning
           - Channel strategy (direct, partner, hybrid)
           - Sales model (self-serve, sales-led, etc.)
           - Marketing and customer acquisition approach

        6. PRICING & BUSINESS MODEL:
           - Pricing model (tiered, user-based, usage-based, etc.)
           - Pricing transparency (published vs custom)
           - Business model (SaaS, one-time, freemium, etc.)
           - Revenue streams

        7. COMPETITIVE ASSESSMENT:
           - Overlap percentage with our business (0-100%)
           - Key strengths and competitive advantages
           - Potential weaknesses or gaps
           - Market positioning relative to our solution

        If information is not available from search results, provide reasonable estimates 
        based on company characteristics and industry patterns.
        Mark uncertain information clearly.

        Format as structured JSON with all specified fields.
        """
        
        return await self.claude_service.get_completion(profile_prompt)
    
    async def _generate_feature_comparison(
        self,
        competitor_profiles: List[Any],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> Dict[str, Any]:
        """Generate comprehensive feature comparison matrix (Us vs Them)"""
        
        comparison_prompt = f"""
        Create a comprehensive feature comparison matrix:

        Our Business: {business_context}
        User Inputs: {user_inputs}
        Competitor Profiles: {competitor_profiles}

        Create detailed "Us vs Them" feature comparison including:

        1. FEATURE CATEGORIES:
           - Core product capabilities
           - Integration and connectivity
           - User experience and interface
           - Security and compliance
           - Scalability and performance
           - Support and services
           - Pricing and packaging
           - Implementation and onboarding

        2. COMPARISON MATRIX:
           For each feature category, compare:
           - Our capabilities and approach
           - Each major competitor's capabilities
           - Relative advantages/disadvantages
           - Importance to target customers (1-10)
           - Confidence level in assessment

        3. COMPETITIVE GAPS:
           - Areas where competitors are stronger
           - Missing features or capabilities
           - Innovation opportunities
           - Investment priorities

        4. COMPETITIVE ADVANTAGES:
           - Our unique differentiators
           - Features competitors lack
           - Superior implementation approaches
           - Barriers to competitive copying

        5. MARKET REQUIREMENTS:
           - Must-have vs nice-to-have features
           - Emerging requirements and trends
           - Customer feedback and requests
           - Compliance and regulatory needs

        Include confidence levels for assessments and note information sources.
        Format as structured JSON with detailed comparison matrix.
        """
        
        return await self.claude_service.get_completion(comparison_prompt)
    
    async def _analyze_market_overlap(
        self,
        competitor_profiles: List[Any],
        segments: List[Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market overlap and identify white space opportunities"""
        
        overlap_prompt = f"""
        Analyze market overlap and white space opportunities:

        Competitor Profiles: {competitor_profiles}
        Our Market Segments: {segments}
        Business Context: {business_context}

        Provide comprehensive overlap analysis:

        1. SEGMENT-LEVEL OVERLAP:
           For each of our target segments:
           - Which competitors also target this segment
           - Intensity of competition (low/medium/high)
           - Competitor positioning in this segment
           - Our differentiation opportunities

        2. COMPETITIVE DENSITY MAP:
           - Segments with high competitive density
           - Segments with moderate competition
           - Underserved or white space segments
           - Emerging segment opportunities

        3. WHITE SPACE IDENTIFICATION:
           - Market gaps not addressed by competitors
           - Underserved customer needs
           - Geographic or vertical opportunities
           - Use case or application gaps

        4. COMPETITIVE THREATS:
           - Direct competition risks
           - Potential market entry threats
           - Competitive response scenarios
           - Market share erosion risks

        5. DIFFERENTIATION OPPORTUNITIES:
           - How to position against each competitor
           - Unique value propositions
           - Messaging differentiation
           - Product differentiation paths

        6. STRATEGIC RECOMMENDATIONS:
           - Priority segments to focus on
           - Segments to avoid or deprioritize
           - Competitive moats to build
           - Market positioning strategy

        Format as structured JSON with detailed overlap analysis and recommendations.
        """
        
        return await self.claude_service.get_completion(overlap_prompt)
    
    async def _analyze_pricing_strategies(
        self,
        competitor_profiles: List[Any],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> Dict[str, Any]:
        """Analyze competitor pricing strategies and intelligence"""
        
        pricing_prompt = f"""
        Analyze competitive pricing strategies and intelligence:

        Competitor Profiles: {competitor_profiles}
        Business Context: {business_context}
        User Inputs: {user_inputs}

        Provide comprehensive pricing intelligence:

        1. PRICING MODEL ANALYSIS:
           For each major competitor:
           - Pricing model (tiered, per-user, usage-based, etc.)
           - Pricing transparency (published vs custom)
           - Free tier or trial offerings
           - Enterprise pricing approach

        2. PRICE POINT COMPARISON:
           - Entry-level pricing comparisons
           - Mid-tier pricing analysis
           - Enterprise pricing patterns
           - Price per value unit analysis

        3. PACKAGING STRATEGIES:
           - Feature bundling approaches
           - Tier differentiation strategies
           - Add-on and upsell pricing
           - Professional services pricing

        4. COMPETITIVE PRICING POSITIONING:
           - Premium vs value positioning
           - Market price leadership
           - Pricing elasticity considerations
           - Value-based pricing evidence

        5. PRICING TRENDS:
           - Recent pricing changes
           - Market pricing evolution
           - Emerging pricing models
           - Customer feedback on pricing

        6. PRICING RECOMMENDATIONS:
           - Optimal pricing positioning
           - Competitive pricing strategies
           - Value communication approaches
           - Pricing test recommendations

        Include confidence levels and note when pricing information is estimated.
        Format as structured JSON with detailed pricing analysis.
        """
        
        return await self.claude_service.get_completion(pricing_prompt)
    
    async def _generate_positioning_recommendations(
        self,
        competitor_profiles: List[Any],
        feature_comparison: Dict[str, Any],
        market_overlap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate competitive positioning recommendations"""
        
        positioning_prompt = f"""
        Generate comprehensive competitive positioning recommendations:

        Competitor Profiles: {competitor_profiles}
        Feature Comparison: {feature_comparison}
        Market Overlap Analysis: {market_overlap}

        Develop positioning strategy including:

        1. COMPETITIVE POSITIONING FRAMEWORK:
           - Core positioning statement vs competition
           - Key differentiators to emphasize
           - Competitive advantages to highlight
           - Positioning pillars and themes

        2. SEGMENT-SPECIFIC POSITIONING:
           - How to position in each target segment
           - Competitor-specific messaging
           - Unique value propositions by segment
           - Competitive displacement strategies

        3. MESSAGING STRATEGY:
           - Head-to-head comparison messaging
           - Indirect competitive messaging
           - Category creation opportunities
           - Thought leadership positioning

        4. COMPETITIVE RESPONSE PLAYBOOK:
           - How to respond to competitor claims
           - Defensive positioning strategies
           - Counter-attack messaging
           - Competitive objection handling

        5. MARKET POSITIONING:
           - Where to compete vs avoid
           - Blue ocean opportunities
           - Category definition strategy
           - Market education approach

        6. IMPLEMENTATION ROADMAP:
           - Positioning rollout strategy
           - Message testing recommendations
           - Competitive monitoring needs
           - Success metrics and tracking

        Format as structured JSON with actionable positioning recommendations.
        """
        
        return await self.claude_service.get_completion(positioning_prompt)
    
    async def _create_competitive_summary(
        self,
        competitor_profiles: List[Any],
        feature_comparison: Dict[str, Any],
        market_overlap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create executive summary of competitive intelligence"""
        
        summary_prompt = f"""
        Create an executive summary of competitive intelligence:

        Competitor Profiles: {competitor_profiles}
        Feature Comparison: {feature_comparison}
        Market Overlap: {market_overlap}

        Provide executive summary including:

        1. COMPETITIVE LANDSCAPE OVERVIEW:
           - Number and types of competitors identified
           - Market maturity and competitive intensity
           - Key market dynamics and trends
           - Competitive threats and opportunities

        2. TOP COMPETITIVE INSIGHTS:
           - Most significant competitive threats
           - Biggest competitive advantages we have
           - Critical gaps to address
           - Market positioning opportunities

        3. STRATEGIC RECOMMENDATIONS:
           - Priority competitive actions
           - Investment recommendations
           - Market positioning strategy
           - Competitive monitoring priorities

        4. KEY BATTLEGROUNDS:
           - Most competitive market segments
           - Feature areas of intense competition
           - Pricing battlegrounds
           - Customer acquisition competition

        5. SUCCESS FACTORS:
           - How to win against competition
           - Sustainable competitive advantages
           - Moats to build and defend
           - Market leadership opportunities

        Format as structured JSON with executive-level insights and recommendations.
        """
        
        return await self.claude_service.get_completion(summary_prompt)