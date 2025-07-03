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
        """Create detailed competitor profiles with business metrics per PRD - OPTIMIZED"""
        
        # MAJOR OPTIMIZATION: Process ALL competitors in a single API call
        # This reduces token usage from 8-12 separate calls to just 1 call
        
        # Limit to top 6 competitors to control token usage
        top_competitors = competitors[:6] if len(competitors) > 6 else competitors
        
        # Single batch profile creation
        all_profiles = await self._create_batch_competitor_profiles(top_competitors, business_context)
        
        return all_profiles
    
    async def _create_batch_competitor_profiles(
        self,
        competitors: List[str],
        business_context: Dict[str, Any]
    ) -> List[CompetitorProfile]:
        """Create profiles for all competitors in a single optimized API call"""
        
        # OPTIMIZATION: Single search for all competitors if available
        all_competitor_data = ""
        if self.search_service:
            search_query = f"{' '.join(competitors)} company profiles funding revenue business models"
            search_results = await self.search_service.search_web(search_query, max_results=8)
            all_competitor_data = search_results
        
        # OPTIMIZATION: Condensed context - only essential business info
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'industry': business_context.get('basic_info', {}).get('industry', 'Unknown'),
            'description': business_context.get('basic_info', {}).get('description', 'Unknown')[:200]  # Truncate long descriptions
        }
        
        # OPTIMIZATION: Much shorter, focused prompt
        batch_prompt = f"""
        Create competitor profiles for: {', '.join(competitors)}

        Search Data: {all_competitor_data}
        Our Business: {business_summary}

        For each competitor, provide:
        1. Company name, HQ, size, founded year
        2. Revenue range, funding, customers
        3. Main product focus, target market
        4. Pricing model, overlap % with us (0-100)
        5. Key strengths, positioning vs us

        Keep each profile under 150 words. Format as JSON array.
        If data unavailable, use reasonable estimates for the industry.
        """
        
        return await self.claude_service.get_completion(batch_prompt, max_tokens=2000)
    
    async def _generate_feature_comparison(
        self,
        competitor_profiles: List[Any],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> Dict[str, Any]:
        """Generate feature comparison matrix - OPTIMIZED"""
        
        # OPTIMIZATION: Condensed prompt with only essential comparisons
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'description': business_context.get('basic_info', {}).get('description', 'Unknown')[:150]
        }
        
        comparison_prompt = f"""
        Feature comparison for {business_summary['company']}:

        Our Product: {business_summary['description']}
        Top 3 Competitors: {str(competitor_profiles)[:800]}  # Truncated

        Compare in 4 key areas:
        1. Core Features - What we do vs them
        2. Pricing - Our model vs theirs
        3. Target Market - Who we serve vs them
        4. Key Differentiators - Our advantages

        For each area: rate importance (1-10) and our advantage (Strong/Weak/Neutral).
        Keep response under 300 words total. JSON format.
        """
        
        return await self.claude_service.get_completion(comparison_prompt, max_tokens=1500)
    
    async def _analyze_market_overlap(
        self,
        competitor_profiles: List[Any],
        segments: List[Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze market overlap - OPTIMIZED"""
        
        # OPTIMIZATION: Extract only segment names and competitor names
        segment_names = [getattr(seg, 'name', 'Unknown') for seg in segments[:4]]  # Limit to top 4
        competitor_names = [prof.get('company_name', 'Unknown') if isinstance(prof, dict) else 'Unknown' for prof in competitor_profiles[:4]]  # Limit to top 4
        
        overlap_prompt = f"""
        Market overlap analysis:

        Our Segments: {segment_names}
        Main Competitors: {competitor_names}
        Industry: {business_context.get('basic_info', {}).get('industry', 'Unknown')}

        Analyze:
        1. Which segments have high/low competition
        2. White space opportunities (underserved segments)
        3. Our best differentiation opportunities
        4. Top 3 strategic recommendations

        Keep response under 200 words. JSON format.
        """
        
        return await self.claude_service.get_completion(overlap_prompt, max_tokens=1200)
    
    async def _analyze_pricing_strategies(
        self,
        competitor_profiles: List[Any],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> Dict[str, Any]:
        """Analyze competitor pricing - OPTIMIZED"""
        
        # OPTIMIZATION: Extract only pricing-relevant competitor info
        pricing_info = []
        for prof in competitor_profiles[:4]:  # Limit to top 4
            if isinstance(prof, dict):
                pricing_info.append({
                    'name': prof.get('company_name', 'Unknown'),
                    'model': prof.get('pricing_model', 'Unknown')
                })
        
        pricing_prompt = f"""
        Pricing analysis for {business_context.get('basic_info', {}).get('company_name', 'Unknown')}:

        Competitors: {pricing_info}
        Our Business: {business_context.get('basic_info', {}).get('description', 'Unknown')[:100]}

        Analyze:
        1. Common pricing models in our market
        2. Price positioning opportunities (premium/value)
        3. Pricing recommendations for our solution
        4. Competitive pricing risks

        Keep response under 150 words. JSON format.
        """
        
        return await self.claude_service.get_completion(pricing_prompt, max_tokens=1000)
    
    async def _generate_positioning_recommendations(
        self,
        competitor_profiles: List[Any],
        feature_comparison: Dict[str, Any],
        market_overlap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate positioning recommendations - OPTIMIZED"""
        
        # OPTIMIZATION: Extract only key insights for positioning
        key_insights = {
            'top_competitors': [prof.get('company_name', 'Unknown') if isinstance(prof, dict) else 'Unknown' for prof in competitor_profiles[:3]],
            'our_advantages': str(feature_comparison).split('advantages')[0] if 'advantages' in str(feature_comparison) else 'Unknown',
            'white_spaces': str(market_overlap).split('white')[0] if 'white' in str(market_overlap) else 'Unknown'
        }
        
        positioning_prompt = f"""
        Positioning strategy:

        Top Competitors: {key_insights['top_competitors']}
        Our Advantages: {key_insights['our_advantages'][:200]}
        Market Gaps: {key_insights['white_spaces'][:200]}

        Recommend:
        1. Core positioning statement vs competition
        2. Key differentiators to emphasize
        3. Best market segments to target
        4. Messaging strategy summary

        Keep response under 200 words. JSON format.
        """
        
        return await self.claude_service.get_completion(positioning_prompt, max_tokens=1200)
    
    async def _create_competitive_summary(
        self,
        competitor_profiles: List[Any],
        feature_comparison: Dict[str, Any],
        market_overlap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create executive summary - OPTIMIZED"""
        
        # OPTIMIZATION: Create summary from previous analysis without re-processing
        summary_prompt = f"""
        Executive Summary of Competitive Analysis:

        Competitors Found: {len(competitor_profiles)} companies
        Analysis Complete: Feature comparison, market overlap, positioning

        Summarize in 4 key points:
        1. Competitive Landscape (high-level overview)
        2. Our Competitive Advantages (top 3)
        3. Main Threats (top 2)
        4. Strategic Recommendations (top 3 actions)

        Keep response under 150 words total. JSON format.
        """
        
        return await self.claude_service.get_completion(summary_prompt, max_tokens=1000)