"""
Go-to-Market Strategy Development Service
Implements comprehensive GTM strategy per PRD specifications including messaging frameworks,
value propositions, campaign planning, and sales enablement
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from models.user_inputs import UserInputs
from services.claude_service import ClaudeService


@dataclass
class MessageHouse:
    """Message House structure for organized messaging"""
    main_value_proposition: str
    key_pillars: List[str]
    supporting_points: Dict[str, List[str]]
    proof_sources: List[str]
    differentiation_hooks: List[str]


@dataclass
class SegmentMessaging:
    """Messaging framework for specific segment"""
    segment_name: str
    value_proposition: str
    pain_point_messaging: Dict[str, str]  # pain_point -> message
    benefit_statements: List[str]
    compelling_hooks: List[str]
    objection_responses: Dict[str, str]
    channel_preferences: List[str]
    tone_guidelines: str


@dataclass
class CampaignPlan:
    """Campaign planning structure"""
    phase: str  # 30/60/90 day
    objectives: List[str]
    target_segments: List[str]
    key_messages: List[str]
    channels: List[str]
    content_types: List[str]
    success_metrics: List[str]
    budget_allocation: Dict[str, float]


class GTMStrategyService:
    """Service for developing comprehensive go-to-market strategies"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
    
    async def develop_gtm_strategy(
        self, 
        user_inputs: UserInputs,
        business_context: Dict[str, Any],
        jtbd_analysis: Dict[str, Any],
        market_analysis: Any,
        segments: List[Any]
    ) -> Dict[str, Any]:
        """
        Develop comprehensive GTM strategy per PRD Phase 4 requirements
        """
        
        # Generate messaging framework for each segment
        segment_messaging = await self._generate_segment_messaging(
            segments, jtbd_analysis, business_context, user_inputs
        )
        
        # Create overall message house
        message_house = await self._create_message_house(
            user_inputs, business_context, segment_messaging
        )
        
        # Generate campaign planning toolkit
        campaign_plans = await self._generate_campaign_plans(
            segments, segment_messaging, business_context, user_inputs
        )
        
        # Create sales enablement package
        sales_enablement = await self._create_sales_enablement(
            segments, segment_messaging, jtbd_analysis, business_context
        )
        
        # Generate channel recommendations
        channel_strategy = await self._develop_channel_strategy(
            user_inputs, business_context, segment_messaging
        )
        
        # Create competitive positioning
        competitive_positioning = await self._develop_competitive_positioning(
            user_inputs, market_analysis, segment_messaging
        )
        
        return {
            'messaging_framework': {
                'message_house': message_house,
                'segment_messaging': segment_messaging
            },
            'campaign_planning': {
                'campaign_plans': campaign_plans,
                'channel_strategy': channel_strategy
            },
            'sales_enablement': sales_enablement,
            'competitive_positioning': competitive_positioning,
            'implementation_roadmap': await self._create_implementation_roadmap(
                campaign_plans, channel_strategy, sales_enablement
            )
        }
    
    async def _generate_segment_messaging(
        self, 
        segments: List[Any], 
        jtbd_analysis: Dict[str, Any], 
        business_context: Dict[str, Any],
        user_inputs: UserInputs
    ) -> Dict[str, SegmentMessaging]:
        """Generate messaging framework for all segments in a single optimized call"""
        
        # OPTIMIZATION: Process all segments in one API call to reduce tokens by 80%
        
        # Extract only essential context
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'industry': business_context.get('basic_info', {}).get('industry', 'Unknown'),
            'model': business_context.get('basic_info', {}).get('business_model', 'Unknown')
        }
        
        # Extract key JTBD insights only
        jtbd_summary = {
            'framework_type': jtbd_analysis.get('framework_type', 'Unknown'),
            'key_insights': str(jtbd_analysis.get('overall_insights', {}))[:300] if 'overall_insights' in jtbd_analysis else 'N/A'
        }
        
        # Create condensed segment data
        segment_data = []
        for segment in segments[:4]:  # Limit to top 4 segments
            segment_data.append({
                'name': segment.name,
                'size': f"{segment.size_percentage}%",
                'characteristics': segment.characteristics[:3],  # Top 3 only
                'pain_points': segment.pain_points[:2]  # Top 2 only
            })
        
        # OPTIMIZATION: Single condensed prompt for all segments
        batch_messaging_prompt = f"""
        Create messaging for {len(segment_data)} segments:

        Business: {business_summary['company']} ({business_summary['industry']})
        Model: {business_summary['model']}
        JTBD: {jtbd_summary['framework_type']} - {jtbd_summary['key_insights']}

        Segments: {segment_data}

        For each segment provide:
        1. Value prop (1 sentence)
        2. Key benefits (3 bullets)
        3. Top messaging hooks (2 hooks)
        4. Channel preferences (2 channels)
        5. Objection responses (1 main objection)

        JSON format, max 150 words per segment.
        """
        
        # Single API call instead of multiple calls
        all_messaging = await self.claude_service.get_completion(batch_messaging_prompt, max_tokens=2000)
        
        return all_messaging
    
    async def _create_message_house(
        self,
        user_inputs: UserInputs,
        business_context: Dict[str, Any],
        segment_messaging: Dict[str, Any]
    ) -> MessageHouse:
        """Create overall message house structure - OPTIMIZED"""
        
        # OPTIMIZATION: Condensed context and focused output
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'industry': business_context.get('basic_info', {}).get('industry', 'Unknown'),
            'description': business_context.get('basic_info', {}).get('description', 'Unknown')[:150]
        }
        
        message_house_prompt = f"""
        Message House for {business_summary['company']}:

        Business: {business_summary['description']} ({business_summary['industry']})
        Segment Messaging: {str(segment_messaging)[:400]}

        Create:
        1. Main value prop (1 sentence)
        2. Key pillars (3 themes with 2 supporting points each)
        3. Differentiation (3 unique advantages)
        4. Proof needed (3 evidence types)

        JSON format, under 200 words total.
        """
        
        return await self.claude_service.get_completion(message_house_prompt, max_tokens=1200)
    
    async def _generate_campaign_plans(
        self,
        segments: List[Any],
        segment_messaging: Dict[str, Any],
        business_context: Dict[str, Any],
        user_inputs: UserInputs
    ) -> Dict[str, CampaignPlan]:
        """Generate 30/60/90-day campaign plans - OPTIMIZED"""
        
        # OPTIMIZATION: Simplified context and focused output
        top_segments = [seg.name for seg in segments[:3]]  # Top 3 segments only
        
        campaign_prompt = f"""
        90-day campaign plan for {business_context.get('basic_info', {}).get('company_name', 'Company')}:

        Top Segments: {top_segments}
        Industry: {business_context.get('basic_info', {}).get('industry', 'Unknown')}

        Create:
        Phase 1 (0-30 days): Focus top segment, 3 key activities, 2 metrics
        Phase 2 (30-60 days): Expand segments, 3 scaling activities, 2 metrics  
        Phase 3 (60-90 days): Optimize all, 3 optimization activities, 2 metrics

        For each phase: objectives, activities, channels, budget allocation (%)
        JSON format, under 250 words total.
        """
        
        return await self.claude_service.get_completion(campaign_prompt, max_tokens=1500)
    
    async def _create_sales_enablement(
        self,
        segments: List[Any],
        segment_messaging: Dict[str, Any],
        jtbd_analysis: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create sales enablement package - OPTIMIZED"""
        
        # OPTIMIZATION: Condensed context and focused output
        top_segments = [seg.name for seg in segments[:2]]  # Top 2 segments only
        business_name = business_context.get('basic_info', {}).get('company_name', 'Company')
        
        sales_prompt = f"""
        Sales enablement for {business_name}:

        Top Segments: {top_segments}
        Framework: {jtbd_analysis.get('framework_type', 'Unknown')}

        Create:
        1. Top objections (2 per segment) + responses
        2. ROI calculator framework (key metrics)
        3. Competitive advantages (3 main points)
        4. Discovery questions (3 key questions)
        5. Demo flow (key features to highlight)

        JSON format, under 200 words total.
        """
        
        return await self.claude_service.get_completion(sales_prompt, max_tokens=1200)
    
    async def _develop_channel_strategy(
        self,
        user_inputs: UserInputs,
        business_context: Dict[str, Any],
        segment_messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Develop channel strategy - OPTIMIZED"""
        
        # OPTIMIZATION: Extract only essential channel info
        current_channels = []
        if user_inputs.b2b_inputs and user_inputs.b2b_inputs.current_lead_sources:
            current_channels = user_inputs.b2b_inputs.current_lead_sources[:3]  # Top 3 only
        elif user_inputs.b2c_inputs and user_inputs.b2c_inputs.discovery_channels:
            current_channels = user_inputs.b2c_inputs.discovery_channels[:3]  # Top 3 only
        
        business_model = business_context.get('basic_info', {}).get('business_model', 'Unknown')
        
        channel_prompt = f"""
        Channel strategy for {business_model} business:

        Current: {current_channels}
        Industry: {business_context.get('basic_info', {}).get('industry', 'Unknown')}

        Recommend:
        1. Primary channels (3 best for this business model)
        2. Content strategy (content types per channel)
        3. Budget allocation (% split across channels)
        4. Key metrics (2 KPIs per channel)
        5. Quick wins (3 immediate actions)

        JSON format, under 200 words total.
        """
        
        return await self.claude_service.get_completion(channel_prompt, max_tokens=1200)
    
    async def _develop_competitive_positioning(
        self,
        user_inputs: UserInputs,
        market_analysis: Any,
        segment_messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Develop competitive positioning - OPTIMIZED"""
        
        # OPTIMIZATION: Extract essential competitive info only
        competitors = []
        if hasattr(market_analysis, 'top_competitors'):
            competitors = [comp.name for comp in market_analysis.top_competitors[:3]]  # Top 3 only
        
        company_name = user_inputs.basic_info.company_name
        industry = user_inputs.basic_info.industry
        
        positioning_prompt = f"""
        Competitive positioning for {company_name} in {industry}:

        Main Competitors: {competitors}
        Description: {user_inputs.basic_info.description[:100]}

        Create:
        1. Core positioning (1 statement vs competition)
        2. Key differentiators (3 unique advantages)
        3. Competitive responses (2 main defensive strategies)
        4. Proof points (3 evidence types needed)
        5. White space (2 opportunity areas)

        JSON format, under 150 words total.
        """
        
        return await self.claude_service.get_completion(positioning_prompt, max_tokens=1000)
    
    async def _create_implementation_roadmap(
        self,
        campaign_plans: Dict[str, Any],
        channel_strategy: Dict[str, Any],
        sales_enablement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation roadmap - OPTIMIZED"""
        
        # OPTIMIZATION: High-level roadmap without detailed context
        roadmap_prompt = f"""
        GTM implementation roadmap:

        Create 12-week timeline:
        Weeks 1-4: Foundation (team setup, messaging, initial channels)
        Weeks 5-8: Launch (campaign execution, sales enablement)
        Weeks 9-12: Optimize (measure, adjust, scale)

        For each phase:
        1. Key activities (2-3 per phase)
        2. Success metrics (2 per phase)
        3. Resources needed (team roles)
        4. Risks (1-2 per phase)

        JSON format, under 200 words total.
        """
        
        return await self.claude_service.get_completion(roadmap_prompt, max_tokens=1200)