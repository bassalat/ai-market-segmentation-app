"""
Messaging Framework Service
Specialized service for creating value propositions, messaging pillars, and compelling hooks
per PRD Phase 4 specifications
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from services.claude_service import ClaudeService


@dataclass
class ValueProposition:
    """Value proposition structure"""
    primary_statement: str
    supporting_points: List[str]
    target_audience: str
    differentiators: List[str]
    proof_points: List[str]


@dataclass
class MessagingPillar:
    """Individual messaging pillar"""
    pillar_name: str
    core_message: str
    supporting_messages: List[str]
    proof_points: List[str]
    audience_relevance: Dict[str, str]  # audience -> relevance note


@dataclass
class CompellingHook:
    """Compelling messaging hook"""
    hook_text: str
    hook_type: str  # attention, curiosity, pattern-interrupt, social-proof
    target_audience: str
    channel_suitability: List[str]
    emotional_trigger: str


class MessagingFrameworkService:
    """Specialized service for creating messaging frameworks"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
    
    async def create_messaging_framework(
        self,
        user_inputs: Any,
        business_context: Dict[str, Any],
        jtbd_analysis: Dict[str, Any],
        segments: List[Any],
        competitive_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive messaging framework per PRD specifications
        """
        
        # Generate segment-specific value propositions
        value_propositions = await self._generate_value_propositions(
            segments, jtbd_analysis, business_context, user_inputs
        )
        
        # Create key messaging pillars
        messaging_pillars = await self._create_messaging_pillars(
            user_inputs, business_context, value_propositions, competitive_context
        )
        
        # Generate compelling hooks
        compelling_hooks = await self._generate_compelling_hooks(
            segments, jtbd_analysis, messaging_pillars, business_context
        )
        
        # Create pain point communications
        pain_point_messaging = await self._create_pain_point_communications(
            segments, jtbd_analysis, business_context
        )
        
        # Generate benefit-focused statements
        benefit_statements = await self._generate_benefit_statements(
            segments, value_propositions, jtbd_analysis
        )
        
        return {
            'value_propositions': value_propositions,
            'messaging_pillars': messaging_pillars,
            'compelling_hooks': compelling_hooks,
            'pain_point_messaging': pain_point_messaging,
            'benefit_statements': benefit_statements,
            'framework_summary': await self._create_framework_summary(
                value_propositions, messaging_pillars, compelling_hooks
            )
        }
    
    async def _generate_value_propositions(
        self,
        segments: List[Any],
        jtbd_analysis: Dict[str, Any],
        business_context: Dict[str, Any],
        user_inputs: Any
    ) -> Dict[str, ValueProposition]:
        """Generate value propositions for each segment"""
        
        value_props = {}
        
        for segment in segments:
            value_prop_prompt = f"""
            Create a compelling value proposition for this market segment:

            Segment: {segment.name}
            Description: {getattr(segment, 'persona_description', 'No description available')}
            Key Characteristics: {segment.characteristics}
            Pain Points: {segment.pain_points}
            Use Cases: {getattr(segment, 'use_cases', [])}

            JTBD Analysis: {jtbd_analysis}
            Business Context: {business_context}
            Business Model: {getattr(user_inputs.basic_info, 'business_model', 'Unknown')}

            Create a comprehensive value proposition including:

            1. PRIMARY VALUE STATEMENT:
               - One clear, compelling sentence (max 20 words)
               - Focus on the primary outcome/benefit
               - Should be specific to this segment's needs
               - Must differentiate from generic solutions

            2. SUPPORTING POINTS (3-5 bullets):
               - Specific benefits this segment cares about
               - Address functional, emotional, and social jobs
               - Include quantifiable outcomes where possible
               - Connect to their most critical pain points

            3. TARGET AUDIENCE SPECIFICITY:
               - Who exactly this value prop is for
               - Their role, situation, and context
               - Why they specifically need this solution

            4. KEY DIFFERENTIATORS:
               - What makes this unique for this segment
               - Competitive advantages they care about
               - Capabilities others don't offer

            5. PROOF POINTS NEEDED:
               - Evidence required to support claims
               - Metrics and benchmarks to highlight
               - Customer examples and case studies
               - Third-party validations

            6. EMOTIONAL RESONANCE:
               - Emotional benefits and outcomes
               - Fear/pain avoidance messaging
               - Aspiration and success visualization

            Format as structured JSON with detailed value proposition components.
            Make it specific to this segment's JTBD and pain points.
            """
            
            value_prop_data = await self.claude_service.get_completion(value_prop_prompt)
            value_props[segment.name] = value_prop_data
        
        return value_props
    
    async def _create_messaging_pillars(
        self,
        user_inputs: Any,
        business_context: Dict[str, Any],
        value_propositions: Dict[str, Any],
        competitive_context: Dict[str, Any] = None
    ) -> List[MessagingPillar]:
        """Create key messaging pillars"""
        
        pillars_prompt = f"""
        Create 3-4 key messaging pillars for this business:

        Business Context: {business_context}
        Value Propositions: {value_propositions}
        Competitive Context: {competitive_context}
        User Inputs: {user_inputs}

        Develop messaging pillars that:

        1. PILLAR STRUCTURE (for each pillar):
           - Pillar Name: Clear, memorable theme
           - Core Message: One sentence that captures the pillar
           - Supporting Messages: 3-5 messages that prove the pillar
           - Proof Points: Evidence, data, examples
           - Audience Relevance: Why each segment cares

        2. PILLAR CRITERIA:
           - Provable: Can be backed with evidence
           - Defensible: Competitors can't easily copy
           - Relevant: Matters to target audiences
           - Memorable: Easy to understand and recall
           - Differentiating: Sets us apart from competition

        3. PILLAR THEMES TO CONSIDER:
           - Innovation & Technology Leadership
           - Ease of Use & Implementation
           - Results & ROI Delivery
           - Security & Reliability
           - Support & Partnership
           - Scalability & Flexibility
           - Cost Effectiveness
           - Speed & Efficiency

        4. INTEGRATION REQUIREMENTS:
           - How pillars support value propositions
           - How pillars address JTBD insights
           - How pillars counter competitive threats
           - How pillars ladder up to overall positioning

        Create pillars that work across segments while allowing customization.
        Format as structured JSON with detailed pillar development.
        """
        
        return await self.claude_service.get_completion(pillars_prompt)
    
    async def _generate_compelling_hooks(
        self,
        segments: List[Any],
        jtbd_analysis: Dict[str, Any],
        messaging_pillars: List[Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, List[CompellingHook]]:
        """Generate compelling messaging hooks by segment"""
        
        hooks_by_segment = {}
        
        for segment in segments:
            hooks_prompt = f"""
            Create compelling messaging hooks for this segment:

            Segment: {segment.name}
            Description: {getattr(segment, 'persona_description', 'No description available')}
            Pain Points: {segment.pain_points}
            Characteristics: {segment.characteristics}

            JTBD Analysis: {jtbd_analysis}
            Messaging Pillars: {messaging_pillars}
            Business Context: {business_context}

            Generate 10-15 compelling hooks across these categories:

            1. ATTENTION-GRABBING HOOKS (3-4 hooks):
               - Stop-scrolling statements
               - Surprising statistics or facts
               - Bold contrarian views
               - Provocative questions

            2. CURIOSITY-DRIVEN HOOKS (3-4 hooks):
               - "How to" teasers
               - Secret/insider knowledge
               - Unexpected benefits
               - Mystery elements

            3. PATTERN-INTERRUPT HOOKS (2-3 hooks):
               - Challenge conventional wisdom
               - Flip expected narratives
               - Contrarian perspectives
               - New way of thinking

            4. SOCIAL PROOF HOOKS (2-3 hooks):
               - Customer success stories
               - Industry endorsements
               - Peer recommendations
               - Expert validations

            5. URGENCY/FEAR HOOKS (2-3 hooks):
               - Risk of inaction
               - Competitive threats
               - Market timing
               - Opportunity cost

            For each hook, specify:
            - Hook text (15-30 words)
            - Hook type and category
            - Target audience within segment
            - Best channels for this hook
            - Emotional trigger it activates
            - Supporting proof needed

            Make hooks specific to this segment's JTBD and pain points.
            Format as structured JSON with detailed hook analysis.
            """
            
            hooks_data = await self.claude_service.get_completion(hooks_prompt)
            hooks_by_segment[segment.name] = hooks_data
        
        return hooks_by_segment
    
    async def _create_pain_point_communications(
        self,
        segments: List[Any],
        jtbd_analysis: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Create pain point-specific communications"""
        
        pain_communications = {}
        
        for segment in segments:
            pain_prompt = f"""
            Create pain point-specific communications for this segment:

            Segment: {segment.name}
            Pain Points: {segment.pain_points}
            JTBD Analysis: {jtbd_analysis}
            Business Context: {business_context}

            For each major pain point, create:

            1. PAIN POINT IDENTIFICATION:
               - Clearly articulate the pain point
               - Quantify the impact if possible
               - Describe current consequences

            2. AGITATION MESSAGING:
               - Why this pain is getting worse
               - Cost of inaction
               - Competitive risks
               - Time sensitivity

            3. SOLUTION MESSAGING:
               - How we specifically solve this pain
               - Unique approach or methodology
               - Expected outcomes and timeline

            4. TRANSFORMATION MESSAGING:
               - Before/after scenarios
               - Success stories and examples
               - Vision of improved state

            5. PROOF MESSAGING:
               - Evidence of solution effectiveness
               - Customer testimonials
               - Metrics and benchmarks
               - Risk mitigation

            6. CHANNEL ADAPTATION:
               - Email version (longer form)
               - Social media version (short)
               - Sales conversation version
               - Website copy version

            Address functional, emotional, and social aspects of each pain point.
            Format as structured JSON with pain-specific messaging.
            """
            
            pain_data = await self.claude_service.get_completion(pain_prompt)
            pain_communications[segment.name] = pain_data
        
        return pain_communications
    
    async def _generate_benefit_statements(
        self,
        segments: List[Any],
        value_propositions: Dict[str, Any],
        jtbd_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate benefit-focused value statements"""
        
        benefit_statements = {}
        
        for segment in segments:
            benefits_prompt = f"""
            Create benefit-focused value statements for this segment:

            Segment: {segment.name}
            Value Proposition: {value_propositions.get(segment.name, {})}
            JTBD Analysis: {jtbd_analysis}

            Generate 15-20 benefit statements across categories:

            1. OUTCOME-DRIVEN BENEFITS (5-6 statements):
               - Specific results and achievements
               - Measurable improvements
               - Success metrics and KPIs

            2. EFFICIENCY BENEFITS (3-4 statements):
               - Time savings
               - Process improvements
               - Resource optimization
               - Automation gains

            3. COMPETITIVE BENEFITS (3-4 statements):
               - Market advantages
               - Competitive positioning
               - First-mover benefits
               - Differentiation value

            4. RISK MITIGATION BENEFITS (2-3 statements):
               - Security improvements
               - Compliance achievements
               - Risk reduction
               - Insurance value

            5. GROWTH BENEFITS (3-4 statements):
               - Revenue increase potential
               - Market expansion opportunities
               - Scalability advantages
               - Innovation enablement

            For each benefit statement:
            - Focus on outcomes, not features
            - Quantify when possible
            - Make it specific to this segment
            - Address their JTBD priorities
            - Include emotional benefits

            Format as structured JSON with categorized benefit statements.
            """
            
            benefits_data = await self.claude_service.get_completion(benefits_prompt)
            benefit_statements[segment.name] = benefits_data
        
        return benefit_statements
    
    async def _create_framework_summary(
        self,
        value_propositions: Dict[str, Any],
        messaging_pillars: List[Any],
        compelling_hooks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create overall messaging framework summary"""
        
        summary_prompt = f"""
        Create a comprehensive messaging framework summary:

        Value Propositions: {value_propositions}
        Messaging Pillars: {messaging_pillars}
        Compelling Hooks: {compelling_hooks}

        Provide executive summary including:

        1. MESSAGING HIERARCHY:
           - Primary messages (always use)
           - Secondary messages (context-dependent)
           - Tertiary messages (nice-to-have)

        2. CROSS-SEGMENT THEMES:
           - Common threads across segments
           - Universal value propositions
           - Shared messaging elements

        3. DIFFERENTIATION SUMMARY:
           - Key competitive differentiators
           - Unique value propositions
           - Positioning advantages

        4. IMPLEMENTATION GUIDELINES:
           - How to use this framework
           - Customization by segment
           - Channel adaptation rules
           - Message testing recommendations

        5. SUCCESS METRICS:
           - How to measure message effectiveness
           - Leading indicators of resonance
           - Optimization triggers
           - Performance benchmarks

        Format as structured JSON with actionable framework guidance.
        """
        
        return await self.claude_service.get_completion(summary_prompt)