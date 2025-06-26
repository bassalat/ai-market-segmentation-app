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
        """Generate messaging framework for each segment"""
        
        segment_messaging = {}
        
        for segment in segments:
            messaging_prompt = f"""
            Create a comprehensive messaging framework for this market segment:

            Segment: {segment.name}
            Description: {segment.description}
            Size: {segment.size_percentage}% of market
            Key Characteristics: {segment.characteristics}
            Pain Points: {segment.pain_points}

            JTBD Analysis: {jtbd_analysis}
            Business Context: {business_context}
            User Inputs: {user_inputs}

            Create detailed messaging framework including:

            1. SEGMENT-SPECIFIC VALUE PROPOSITION:
               - Primary value statement (one clear sentence)
               - Supporting value points (3-5 bullets)
               - Quantified benefits where possible

            2. PAIN POINT MESSAGING MAP:
               - For each major pain point, create specific messaging
               - Address the functional, emotional, and social aspects
               - Include urgency and consequence messaging

            3. BENEFIT-FOCUSED STATEMENTS:
               - Outcome-driven value statements
               - Before/after scenarios
               - ROI and success metrics messaging

            4. COMPELLING HOOKS & ANGLES:
               - Attention-grabbing opening lines
               - Curiosity-driven statements
               - Pattern-interrupt messaging
               - Social proof angles

            5. OBJECTION HANDLING:
               - Common objections for this segment
               - Response strategies and proof points
               - Risk reversal and guarantee messaging

            6. CHANNEL PREFERENCES & TONE:
               - Preferred communication channels
               - Content format preferences
               - Messaging tone and voice guidelines
               - Technical depth and complexity level

            7. PROOF POINTS & VALIDATION:
               - Case studies and testimonials needed
               - Metrics and benchmarks to highlight
               - Third-party validation sources

            Format as structured JSON with detailed messaging components.
            Make messaging specific to this segment's unique characteristics and JTBD insights.
            """
            
            messaging_data = await self.claude_service.get_completion(messaging_prompt)
            segment_messaging[segment.name] = messaging_data
        
        return segment_messaging
    
    async def _create_message_house(
        self,
        user_inputs: UserInputs,
        business_context: Dict[str, Any],
        segment_messaging: Dict[str, Any]
    ) -> MessageHouse:
        """Create overall message house structure"""
        
        message_house_prompt = f"""
        Create a comprehensive Message House for this business:

        Business Context: {business_context}
        User Inputs: {user_inputs}
        Segment Messaging: {segment_messaging}

        Build a Message House structure with:

        1. MAIN VALUE PROPOSITION:
           - Single, clear value statement that works across segments
           - Addresses the core problem and unique solution
           - Differentiates from competition

        2. KEY MESSAGING PILLARS (3-4 pillars):
           - Core themes that support the main value prop
           - Each pillar should be provable and defensible
           - Pillars should ladder up to overall positioning

        3. SUPPORTING POINTS (for each pillar):
           - 3-5 supporting messages per pillar
           - Include features, benefits, and proof points
           - Address different audience priorities

        4. PROOF SOURCES:
           - Types of evidence needed for each pillar
           - Customer testimonials and case studies
           - Data points and metrics
           - Third-party validation

        5. DIFFERENTIATION HOOKS:
           - What makes this unique vs competition
           - Key advantages and capabilities
           - Moats and barriers to entry

        6. MESSAGING HIERARCHY:
           - Primary messages (always include)
           - Secondary messages (context-dependent)
           - Tertiary messages (nice-to-have)

        Format as structured JSON with organized message house components.
        Ensure consistency across all segment messaging while maintaining flexibility.
        """
        
        return await self.claude_service.get_completion(message_house_prompt)
    
    async def _generate_campaign_plans(
        self,
        segments: List[Any],
        segment_messaging: Dict[str, Any],
        business_context: Dict[str, Any],
        user_inputs: UserInputs
    ) -> Dict[str, CampaignPlan]:
        """Generate 30/60/90-day campaign plans"""
        
        campaign_prompt = f"""
        Create comprehensive 30/60/90-day campaign plans:

        Segments: {[segment.name for segment in segments]}
        Segment Messaging: {segment_messaging}
        Business Context: {business_context}
        User Inputs: {user_inputs}

        Create detailed campaign plans for each phase:

        PHASE 1 (0-30 DAYS) - FOUNDATION:
        - Primary objectives and goals
        - Target segments priority order
        - Key messages and positioning
        - Initial channel launches
        - Content creation priorities
        - Success metrics and KPIs
        - Budget allocation recommendations

        PHASE 2 (30-60 DAYS) - EXPANSION:
        - Scaled objectives
        - Additional segment targeting
        - Message testing and optimization
        - Channel expansion
        - Content variety and formats
        - Performance optimization
        - Budget reallocation based on results

        PHASE 3 (60-90 DAYS) - OPTIMIZATION:
        - Advanced objectives
        - Full segment coverage
        - Refined messaging based on data
        - Multi-channel integration
        - Advanced content strategies
        - Conversion optimization
        - ROI maximization tactics

        For each phase, include:
        - Specific activities and tactics
        - Resource requirements
        - Timeline and milestones
        - Success criteria
        - Risk mitigation strategies

        Also include:
        - A/B testing frameworks
        - Creative brief templates
        - Campaign measurement plans
        - Optimization triggers and thresholds

        Format as structured JSON with phase-by-phase breakdown.
        """
        
        return await self.claude_service.get_completion(campaign_prompt)
    
    async def _create_sales_enablement(
        self,
        segments: List[Any],
        segment_messaging: Dict[str, Any],
        jtbd_analysis: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create comprehensive sales enablement package"""
        
        sales_prompt = f"""
        Create a comprehensive sales enablement package:

        Segments: {[segment.name for segment in segments]}
        Segment Messaging: {segment_messaging}
        JTBD Analysis: {jtbd_analysis}
        Business Context: {business_context}

        Develop sales enablement materials including:

        1. OBJECTION HANDLING SCRIPTS:
           - Common objections by segment
           - Response frameworks and talk tracks
           - Proof points and evidence
           - Objection prevention strategies

        2. ROI CALCULATORS:
           - Segment-specific value calculations
           - Cost savings frameworks
           - Productivity improvement metrics
           - Time-to-value assessments

        3. COMPETITIVE BATTLECARDS:
           - Key competitor comparison points
           - Competitive advantages messaging
           - Competitive weakness exploitation
           - Win/loss factor analysis

        4. DISCOVERY QUESTION FRAMEWORKS:
           - Segment-specific discovery questions
           - Pain point qualification questions
           - Budget and authority questions
           - Timing and urgency questions

        5. DEMO SCRIPTS & FLOWS:
           - Segment-customized demo flows
           - Key feature highlights
           - Value demonstration techniques
           - Use case scenarios

        6. PROPOSAL TEMPLATES:
           - Value proposition templates
           - ROI justification templates
           - Implementation planning templates
           - Success metrics frameworks

        7. SALES PROCESS MAPPING:
           - Segment-specific sales stages
           - Decision maker involvement
           - Required deliverables per stage
           - Qualification criteria

        Format as structured JSON with practical sales tools and templates.
        Include specific examples and scripts that can be immediately used.
        """
        
        return await self.claude_service.get_completion(sales_prompt)
    
    async def _develop_channel_strategy(
        self,
        user_inputs: UserInputs,
        business_context: Dict[str, Any],
        segment_messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Develop comprehensive channel strategy"""
        
        # Extract current lead sources for context
        current_channels = []
        if user_inputs.b2b_inputs and user_inputs.b2b_inputs.current_lead_sources:
            current_channels = user_inputs.b2b_inputs.current_lead_sources
        elif user_inputs.b2c_inputs and user_inputs.b2c_inputs.discovery_channels:
            current_channels = user_inputs.b2c_inputs.discovery_channels
        
        channel_prompt = f"""
        Develop a comprehensive channel strategy:

        Business Context: {business_context}
        Current Channels: {current_channels}
        Segment Messaging: {segment_messaging}
        User Inputs: {user_inputs}

        Create detailed channel strategy including:

        1. CHANNEL MIX RECOMMENDATIONS:
           - Primary channels for each segment
           - Secondary and tertiary channel options
           - Channel effectiveness by segment
           - Budget allocation across channels

        2. CONTENT STRATEGY BY CHANNEL:
           - Content types and formats per channel
           - Messaging adaptation guidelines
           - Content calendar frameworks
           - Repurposing strategies

        3. CHANNEL-SPECIFIC TACTICS:
           - Platform-specific best practices
           - Optimization strategies
           - Measurement approaches
           - Success benchmarks

        4. INTEGRATED CAMPAIGN FLOWS:
           - Multi-channel customer journeys
           - Cross-channel messaging coordination
           - Attribution tracking approaches
           - Conversion optimization tactics

        5. BUDGET ALLOCATION MODEL:
           - Channel investment priorities
           - Expected ROI by channel
           - Testing budget allocation
           - Scale-up investment framework

        6. PERFORMANCE MEASUREMENT:
           - Channel-specific KPIs
           - Attribution models
           - Optimization triggers
           - Reporting frameworks

        Consider the business model (B2B vs B2C) and adapt recommendations accordingly.
        Include both paid and organic channel strategies.
        Format as structured JSON with actionable channel recommendations.
        """
        
        return await self.claude_service.get_completion(channel_prompt)
    
    async def _develop_competitive_positioning(
        self,
        user_inputs: UserInputs,
        market_analysis: Any,
        segment_messaging: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Develop competitive positioning framework"""
        
        positioning_prompt = f"""
        Develop comprehensive competitive positioning:

        User Inputs: {user_inputs}
        Market Analysis: {market_analysis}
        Segment Messaging: {segment_messaging}

        Create competitive positioning framework including:

        1. COMPETITIVE LANDSCAPE MAPPING:
           - Direct and indirect competitors
           - Competitive strengths and weaknesses
           - Market positioning analysis
           - White space opportunities

        2. DIFFERENTIATION STRATEGY:
           - Unique value propositions
           - Competitive advantages
           - Moats and barriers to entry
           - Innovation differentiators

        3. POSITIONING STATEMENTS:
           - Core positioning statement
           - Segment-specific positioning
           - Competitive comparison messaging
           - Category creation opportunities

        4. COMPETITIVE RESPONSE PLAYBOOK:
           - Competitor attack strategies
           - Defensive positioning tactics
           - Win/loss factor analysis
           - Competitive intelligence needs

        5. MESSAGING DIFFERENTIATION:
           - vs. Competitor A messaging
           - vs. Competitor B messaging
           - vs. Status quo messaging
           - vs. DIY solutions messaging

        6. PROOF POINT STRATEGY:
           - Competitive benchmarks
           - Customer testimonials
           - Performance comparisons
           - Third-party validations

        Format as structured JSON with actionable positioning strategy.
        Include specific messaging and tactical recommendations.
        """
        
        return await self.claude_service.get_completion(positioning_prompt)
    
    async def _create_implementation_roadmap(
        self,
        campaign_plans: Dict[str, Any],
        channel_strategy: Dict[str, Any],
        sales_enablement: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create implementation roadmap for GTM strategy"""
        
        roadmap_prompt = f"""
        Create a comprehensive GTM implementation roadmap:

        Campaign Plans: {campaign_plans}
        Channel Strategy: {channel_strategy}
        Sales Enablement: {sales_enablement}

        Develop implementation roadmap including:

        1. WEEK-BY-WEEK TIMELINE (First 12 weeks):
           - Specific activities and deliverables
           - Resource requirements
           - Dependencies and prerequisites
           - Milestone checkpoints

        2. TEAM ROLES & RESPONSIBILITIES:
           - Marketing team responsibilities
           - Sales team responsibilities
           - Product team involvement
           - External resource needs

        3. BUDGET & RESOURCE PLANNING:
           - Phase-by-phase budget allocation
           - Team time requirements
           - Tool and platform costs
           - External service needs

        4. SUCCESS METRICS & TRACKING:
           - Leading indicators
           - Lagging indicators
           - Weekly/monthly reporting
           - Optimization triggers

        5. RISK MANAGEMENT:
           - Potential roadblocks
           - Mitigation strategies
           - Contingency plans
           - Success criteria adjustments

        6. OPTIMIZATION FRAMEWORK:
           - Testing and learning approach
           - Data collection requirements
           - Decision-making processes
           - Iteration cycles

        Format as structured JSON with detailed implementation guidance.
        Include practical timelines and actionable next steps.
        """
        
        return await self.claude_service.get_completion(roadmap_prompt)