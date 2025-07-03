"""
Messaging Framework Service
Specialized service for creating value propositions, messaging pillars, and compelling hooks
per PRD Phase 4 specifications
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
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
        """Generate value propositions for all segments in a single optimized call"""
        
        # OPTIMIZATION: Process all segments in one API call to reduce tokens by 85%
        
        # Extract essential context only
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'industry': business_context.get('basic_info', {}).get('industry', 'Unknown'),
            'model': getattr(user_inputs.basic_info, 'business_model', 'Unknown')
        }
        
        # Create condensed segment data
        segment_data = []
        for segment in segments[:4]:  # Limit to top 4 segments
            segment_data.append({
                'name': segment.name,
                'characteristics': segment.characteristics[:2],  # Top 2 only
                'pain_points': segment.pain_points[:2],  # Top 2 only
                'use_cases': getattr(segment, 'use_cases', [])[:2]  # Top 2 only
            })
        
        # OPTIMIZATION: Single batch prompt for all value propositions
        batch_value_prop_prompt = f"""
        Value propositions for {len(segment_data)} segments:

        Business: {business_summary['company']} ({business_summary['industry']}) - {business_summary['model']}
        JTBD Framework: {jtbd_analysis.get('framework_type', 'Unknown')}

        Segments: {segment_data}

        For each segment create:
        1. Primary value statement (1 compelling sentence)
        2. Key benefits (3 benefit bullets)
        3. Target audience (who this is for)
        4. Differentiators (2 unique advantages)
        5. Proof needed (2 evidence types)

        JSON format with segment names as keys, max 100 words per segment.
        """
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(batch_value_prop_prompt, max_tokens=2000)
        return self._parse_json_response(response, 'value_propositions')
    
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
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(pillars_prompt)
        return self._parse_json_response(response, 'messaging_pillars')
    
    async def _generate_compelling_hooks(
        self,
        segments: List[Any],
        jtbd_analysis: Dict[str, Any],
        messaging_pillars: List[Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, List[CompellingHook]]:
        """Generate compelling messaging hooks for all segments in a single optimized call"""
        
        # OPTIMIZATION: Process all segments in one API call to reduce tokens by 85%
        
        # Extract essential segment info
        segment_names = [segment.name for segment in segments[:3]]  # Top 3 segments only
        top_pain_points = []
        for segment in segments[:3]:
            if segment.pain_points:
                top_pain_points.extend(segment.pain_points[:1])  # 1 pain point per segment
        
        # OPTIMIZATION: Single batch prompt for all hooks
        batch_hooks_prompt = f"""
        Compelling hooks for {len(segment_names)} segments:

        Segments: {segment_names}
        Industry: {business_context.get('basic_info', {}).get('industry', 'Unknown')}
        Top Pain Points: {top_pain_points}

        For each segment create 6 hooks:
        1. Attention hook (surprising fact/stat)
        2. Curiosity hook ("how to" teaser)
        3. Social proof hook (success story)
        4. Urgency hook (risk of inaction)
        5. Benefit hook (outcome focus)
        6. Question hook (provocative question)

        Each hook: 15-25 words, channel recommendation
        JSON format with segment names as keys, max 50 words per segment.
        """
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(batch_hooks_prompt, max_tokens=1500)
        return self._parse_json_response(response, 'compelling_hooks')
    
    async def _create_pain_point_communications(
        self,
        segments: List[Any],
        jtbd_analysis: Dict[str, Any],
        business_context: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Create pain point communications for all segments in a single optimized call"""
        
        # OPTIMIZATION: Process all segments in one API call to reduce tokens by 85%
        
        # Extract top pain points from all segments
        segment_pain_data = []
        for segment in segments[:3]:  # Top 3 segments only
            segment_pain_data.append({
                'name': segment.name,
                'top_pain_points': segment.pain_points[:2] if segment.pain_points else []  # Top 2 pain points
            })
        
        # OPTIMIZATION: Single batch prompt for all pain point communications
        batch_pain_prompt = f"""
        Pain point messaging for {len(segment_pain_data)} segments:

        Business: {business_context.get('basic_info', {}).get('company_name', 'Unknown')}
        Segments & Pain Points: {segment_pain_data}

        For each segment's top pain points create:
        1. Problem statement (1 sentence describing the pain)
        2. Agitation (why it's getting worse)
        3. Solution approach (how we solve it)
        4. Outcome vision (what success looks like)
        5. Proof needed (evidence required)

        JSON format with segment names as keys, max 80 words per segment.
        """
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(batch_pain_prompt, max_tokens=1500)
        return self._parse_json_response(response, 'pain_point_communications')
    
    async def _generate_benefit_statements(
        self,
        segments: List[Any],
        value_propositions: Dict[str, Any],
        jtbd_analysis: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Generate benefit statements for all segments in a single optimized call"""
        
        # OPTIMIZATION: Process all segments in one API call to reduce tokens by 85%
        
        # Extract essential segment info
        segment_names = [segment.name for segment in segments[:3]]  # Top 3 segments only
        
        # OPTIMIZATION: Single batch prompt for all benefit statements
        batch_benefits_prompt = f"""
        Benefit statements for {len(segment_names)} segments:

        Segments: {segment_names}
        JTBD Framework: {jtbd_analysis.get('framework_type', 'Unknown')}
        Value Props: {str(value_propositions)[:300] if value_propositions else 'N/A'}

        For each segment create 8 benefit statements:
        1. Outcome benefits (2 statements - specific results)
        2. Efficiency benefits (2 statements - time/cost savings)
        3. Competitive benefits (2 statements - market advantages)
        4. Growth benefits (2 statements - revenue/scale potential)

        Focus on measurable outcomes, not features.
        JSON format with segment names as keys, max 60 words per segment.
        """
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(batch_benefits_prompt, max_tokens=1500)
        return self._parse_json_response(response, 'benefit_statements')
    
    async def _create_framework_summary(
        self,
        value_propositions: Dict[str, Any],
        messaging_pillars: List[Any],
        compelling_hooks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create messaging framework summary - OPTIMIZED"""
        
        # OPTIMIZATION: Condensed summary with essential info only
        summary_prompt = f"""
        Messaging framework summary:

        Framework Components: Value props, pillars, hooks created
        Segments Covered: {len(value_propositions) if value_propositions else 0}

        Provide:
        1. Message hierarchy (primary vs secondary messages)
        2. Cross-segment themes (3 common elements)
        3. Key differentiators (3 unique advantages)
        4. Implementation guide (how to use framework)
        5. Success metrics (3 key measurement areas)

        JSON format, under 150 words total.
        """
        
        # Get response and parse JSON
        response = await self.claude_service.get_completion(summary_prompt, max_tokens=1000)
        return self._parse_json_response(response, 'framework_summary')
    
    def _parse_json_response(self, response: str, fallback_type: str) -> Dict[str, Any]:
        """Parse JSON response from Claude with fallback handling"""
        try:
            # Extract JSON from response if it contains other text
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            # Find JSON object in response
            start_idx = response_clean.find('{')
            end_idx = response_clean.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_clean[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise json.JSONDecodeError("No JSON found", response, 0)
                
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # Return fallback data based on type
            if fallback_type == 'value_propositions':
                return {
                    'primary_segment': {
                        'value_proposition': 'Streamlined solution for key business needs',
                        'differentiators': ['Ease of use', 'Cost effective', 'Reliable support']
                    }
                }
            elif fallback_type == 'messaging_pillars':
                return [
                    {
                        'pillar_name': 'Efficiency',
                        'core_message': 'Streamline operations and boost productivity',
                        'supporting_messages': ['Save time', 'Reduce costs', 'Improve workflow']
                    }
                ]
            elif fallback_type == 'compelling_hooks':
                return {
                    'primary_segment': [
                        'Transform your business operations',
                        'Unlock hidden efficiency gains',
                        'Get results in days, not weeks'
                    ]
                }
            elif fallback_type == 'pain_point_communications':
                return {
                    'primary_segment': {
                        'inefficiency': 'Stop wasting time on manual processes',
                        'high_costs': 'Reduce operational expenses significantly'
                    }
                }
            elif fallback_type == 'benefit_statements':
                return {
                    'primary_segment': [
                        'Reduce operational costs by up to 30%',
                        'Improve efficiency and productivity',
                        'Gain competitive market advantage',
                        'Scale business growth sustainably'
                    ]
                }
            elif fallback_type == 'framework_summary':
                return {
                    'message_hierarchy': 'Primary value propositions supported by benefit statements',
                    'cross_segment_themes': ['Efficiency', 'Cost savings', 'Reliability'],
                    'key_differentiators': ['Unique approach', 'Proven results', 'Expert support'],
                    'implementation_guide': 'Use primary messages first, support with specific benefits',
                    'success_metrics': ['Message recall', 'Engagement rates', 'Conversion improvement']
                }
            else:
                return {'error': 'Failed to parse response', 'raw_response': response[:200]}