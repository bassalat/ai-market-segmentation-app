"""
Jobs-To-Be-Done (JTBD) Analysis Service
Implements comprehensive JTBD framework per PRD specifications for 6 key roles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from models.user_inputs import UserInputs, B2BInputs, B2CInputs
from services.claude_service import ClaudeService


@dataclass
class JobMapping:
    """Individual job mapping for JTBD framework"""
    functional_job: str  # "I need to _____ so I can _____"
    emotional_job: str   # "I want to feel _____ when I use this"
    social_job: str      # "I want others to see me as _____"
    triggers: List[str]  # Events that initiate their job
    friction_points: List[str]  # What's preventing completion today
    current_workarounds: List[str]  # Hacks or tools currently used


@dataclass
class RoleJTBD:
    """Complete JTBD analysis for a specific role"""
    role_name: str
    core_job_description: str
    job_mappings: List[JobMapping]
    decision_journey: Dict[str, Any]
    psychographic_profile: Dict[str, Any]
    pain_point_severity: Dict[str, int]  # 1-10 severity ratings


class JTBDAnalysisService:
    """Service for implementing JTBD framework analysis"""
    
    def __init__(self):
        self.claude_service = ClaudeService()
        
        # PRD-specified role templates
        self.b2b_role_templates = {
            'cybersecurity_specialist': {
                'title': 'Cybersecurity Specialist/CISO',
                'core_job': 'Protect the organization\'s digital assets by preventing, detecting, and responding to cyber threats',
                'key_responsibilities': [
                    'Threat detection and monitoring',
                    'Vulnerability assessment and risk prioritization', 
                    'Incident response coordination',
                    'Compliance management and reporting',
                    'Security automation and process optimization',
                    'Strategic security decision making'
                ]
            },
            'it_manager': {
                'title': 'IT Manager/System Administrator',
                'core_job': 'Maintain and secure the organization\'s IT infrastructure to ensure reliable operations and data security',
                'key_responsibilities': [
                    'Infrastructure deployment and maintenance',
                    'User access control and authentication',
                    'Compliance support and data management',
                    'IT automation and workflow optimization',
                    'Incident management and resolution',
                    'Budget management and cost optimization'
                ]
            },
            'operations_manager': {
                'title': 'Operations Manager/Business Manager',
                'core_job': 'Ensure smooth business operations while maintaining compliance with regulations and minimizing risks',
                'key_responsibilities': [
                    'Policy adherence and enforcement',
                    'Operational risk identification and mitigation',
                    'Cross-team collaboration and communication',
                    'Data access control and governance',
                    'Performance monitoring and KPI tracking',
                    'Process optimization and automation'
                ]
            },
            'msp_mssp': {
                'title': 'Managed Service Provider (MSP/MSSP)',
                'core_job': 'Provide comprehensive security and IT management services to multiple clients effectively and efficiently',
                'key_responsibilities': [
                    'Multi-tenant service delivery',
                    'Continuous threat monitoring across clients',
                    'Scalable security solution deployment',
                    'Compliance management as a service',
                    'Automated security operations scaling',
                    'Client relationship and support management'
                ]
            },
            'developer': {
                'title': 'Developer',
                'core_job': 'Build and integrate secure solutions that enhance application functionality and protect against threats',
                'key_responsibilities': [
                    'Security feature integration via APIs/SDKs',
                    'Secure coding practices implementation',
                    'Development process automation',
                    'Platform integration and documentation usage',
                    'Community engagement and learning',
                    'Technical support and issue resolution'
                ]
            },
            'soc_analyst': {
                'title': 'SOC Analyst (L1)',
                'core_job': 'Monitor and analyze security events and alerts to identify potential threats and escalate them appropriately',
                'key_responsibilities': [
                    'Real-time security event monitoring',
                    'Alert analysis and correlation',
                    'Incident response and workflow execution',
                    'Escalation and context documentation',
                    'Report generation and updates',
                    'Repetitive task automation and alert management'
                ]
            }
        }
    
    async def analyze_jtbd_framework(self, user_inputs: UserInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive JTBD analysis based on business model and inputs
        """
        
        if user_inputs.b2b_inputs:
            return await self._analyze_b2b_jtbd(user_inputs.b2b_inputs, business_context)
        elif user_inputs.b2c_inputs:
            return await self._analyze_b2c_jtbd(user_inputs.b2c_inputs, business_context)
        else:
            # Fallback to general analysis
            return await self._analyze_general_jtbd(user_inputs, business_context)
    
    async def _analyze_b2b_jtbd(self, b2b_inputs: B2BInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze JTBD for B2B business model with role-specific focus - OPTIMIZED"""
        
        # OPTIMIZATION: Process all roles in a single API call to reduce tokens by 80%
        
        # Identify relevant roles based on decision makers
        relevant_roles = self._identify_relevant_b2b_roles(b2b_inputs.decision_maker_roles)
        
        # OPTIMIZATION: Batch all role analysis into one call
        all_role_analyses = await self._generate_batch_role_jtbd(
            relevant_roles, b2b_inputs, business_context
        )
        
        # OPTIMIZATION: Generate insights and journey mapping together
        insights_and_journey = await self._generate_combined_insights_and_journey(
            all_role_analyses, b2b_inputs, business_context
        )
        
        return {
            'framework_type': 'B2B',
            'role_analyses': all_role_analyses,
            'overall_insights': insights_and_journey['insights'],
            'decision_journey_map': insights_and_journey['journey'],
            'trigger_events_calendar': self._generate_trigger_calendar(b2b_inputs, all_role_analyses),
            'pain_point_severity_matrix': self._generate_pain_severity_matrix(all_role_analyses)
        }
    
    async def _analyze_b2c_jtbd(self, b2c_inputs: B2CInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze JTBD for B2C business model with customer journey focus"""
        
        jtbd_prompt = f"""
        Analyze the Jobs-To-Be-Done framework for this B2C business:

        Business Context: {business_context}
        B2C Inputs: {b2c_inputs}

        Create comprehensive JTBD analysis including:

        1. PRIMARY CUSTOMER JOBS:
           - Functional Job: "When I [situation], I want to [motivation], so I can [outcome]"
           - Emotional Job: Core emotional need and desired feeling
           - Social Job: How they want to be perceived by others

        2. JOB TRIGGERS & CONTEXT:
           - Specific situations that trigger the job
           - Timing and frequency patterns
           - Environmental factors that influence the job

        3. CURRENT FRICTION POINTS:
           - What prevents them from getting the job done today
           - Inadequate solutions they're currently using
           - Gaps in existing alternatives

        4. SUCCESS CRITERIA:
           - How they measure if the job is well done
           - What "progress" looks like to them
           - Emotional satisfaction indicators

        5. DECISION JOURNEY STAGES:
           - Problem recognition triggers
           - Information search behavior
           - Evaluation criteria and priorities
           - Purchase decision factors
           - Post-purchase success measures

        Format as structured JSON with detailed analysis for each component.
        """
        
        jtbd_analysis = await self.claude_service.get_completion(jtbd_prompt)
        
        return {
            'framework_type': 'B2C',
            'customer_jtbd': jtbd_analysis,
            'decision_journey_map': await self._generate_b2c_decision_journey(b2c_inputs, jtbd_analysis),
            'trigger_events_calendar': self._generate_b2c_trigger_calendar(b2c_inputs),
            'psychographic_insights': await self._generate_b2c_psychographics(b2c_inputs, jtbd_analysis)
        }
    
    def _identify_relevant_b2b_roles(self, decision_maker_roles: List[str]) -> Dict[str, Dict[str, Any]]:
        """Identify which B2B role templates are most relevant based on decision makers"""
        
        role_mapping = {
            'CEO/Founder': ['operations_manager'],
            'CTO/VP Engineering': ['it_manager', 'developer'],
            'CMO/VP Marketing': ['operations_manager'],
            'CFO/Finance': ['operations_manager'],
            'VP Sales': ['operations_manager'],
            'Operations Manager': ['operations_manager'],
            'HR Director': ['operations_manager'],
            'CISO/Security': ['cybersecurity_specialist'],
            'Procurement': ['operations_manager'],
            'Department Manager': ['operations_manager', 'it_manager'],
            'End Users': ['soc_analyst', 'developer'],
            'IT Administrator': ['it_manager', 'soc_analyst']
        }
        
        relevant_roles = {}
        
        # Add roles based on decision makers
        for decision_maker in decision_maker_roles:
            if decision_maker in role_mapping:
                for role_key in role_mapping[decision_maker]:
                    relevant_roles[role_key] = self.b2b_role_templates[role_key]
        
        # Always include MSP/MSSP if multiple company sizes targeted (suggests service model)
        if len(decision_maker_roles) > 2:
            relevant_roles['msp_mssp'] = self.b2b_role_templates['msp_mssp']
        
        # Ensure we have at least 2 roles for comparison
        if len(relevant_roles) < 2:
            relevant_roles['cybersecurity_specialist'] = self.b2b_role_templates['cybersecurity_specialist']
            relevant_roles['it_manager'] = self.b2b_role_templates['it_manager']
        
        return relevant_roles
    
    async def _generate_batch_role_jtbd(self, relevant_roles: Dict[str, Dict], b2b_inputs: B2BInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JTBD analysis for all roles in a single optimized call"""
        
        # OPTIMIZATION: Extract only essential context
        business_summary = {
            'company': business_context.get('basic_info', {}).get('company_name', 'Unknown'),
            'industry': business_context.get('basic_info', {}).get('industry', 'Unknown'),
            'description': business_context.get('basic_info', {}).get('description', 'Unknown')[:150]
        }
        
        # OPTIMIZATION: Condensed role data
        role_summaries = []
        for role_key, role_template in list(relevant_roles.items())[:4]:  # Limit to top 4 roles
            role_summaries.append({
                'key': role_key,
                'title': role_template['title'],
                'core_job': role_template['core_job'][:100]  # Truncate
            })
        
        # OPTIMIZATION: Single batch prompt for all roles
        batch_jtbd_prompt = f"""
        JTBD analysis for {len(role_summaries)} B2B roles:

        Business: {business_summary['company']} - {business_summary['description']} ({business_summary['industry']})
        
        Decision Makers: {b2b_inputs.decision_maker_roles[:3]}
        Problem: {b2b_inputs.main_problem_solved[:100] if b2b_inputs.main_problem_solved else 'Unknown'}

        Roles: {role_summaries}

        For each role analyze:
        1. Functional job (main task they need to accomplish)
        2. Emotional job (how they want to feel)
        3. Social job (how they want to be perceived)
        4. Top 2 trigger events
        5. Top 2 friction points
        6. Success criteria (how they measure success)

        JSON format with role_key as keys, max 100 words per role.
        """
        
        return await self.claude_service.get_completion(batch_jtbd_prompt, max_tokens=2000)
    
    async def _generate_combined_insights_and_journey(self, role_analyses: Dict[str, Any], b2b_inputs: B2BInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and decision journey in a single optimized call"""
        
        insights_prompt = f"""
        B2B JTBD insights and decision journey:

        Role Analyses: {str(role_analyses)[:500]}
        Company: {business_context.get('basic_info', {}).get('company_name', 'Unknown')}
        Deal Size: {b2b_inputs.deal_size_range}
        Sales Cycle: {b2b_inputs.sales_cycle_length}

        Provide:
        1. Key insights (3 common patterns across roles)
        2. Decision journey (5 phases: trigger→explore→evaluate→decide→implement)
        3. Stakeholder involvement (who's involved when)
        4. Main barriers (3 biggest obstacles)

        JSON format with 'insights' and 'journey' keys, under 200 words total.
        """
        
        return await self.claude_service.get_completion(insights_prompt, max_tokens=1500)
    
    async def _generate_role_jtbd(self, role_template: Dict[str, Any], b2b_inputs: B2BInputs, business_context: Dict[str, Any]) -> RoleJTBD:
        """Generate detailed JTBD analysis for a specific role"""
        
        jtbd_prompt = f"""
        Create a comprehensive Jobs-To-Be-Done analysis for the {role_template['title']} role:

        Role Information:
        - Title: {role_template['title']}
        - Core Job: {role_template['core_job']}
        - Key Responsibilities: {role_template['key_responsibilities']}

        Business Context: {business_context}
        B2B Context: {b2b_inputs}

        Create detailed JTBD analysis with:

        1. FUNCTIONAL JOBS (3-5 specific jobs):
           For each job: "When I [situation], I want to [action], so I can [outcome]"
           - Include trigger situations
           - Specify desired actions/capabilities
           - Clear outcome/benefit statements

        2. EMOTIONAL JOBS:
           - Core emotional needs (feeling secure, confident, efficient, etc.)
           - Emotional outcomes they want to achieve
           - Feelings they want to avoid (stress, overwhelm, vulnerability)

        3. SOCIAL JOBS:
           - How they want to be perceived by peers/management
           - Professional reputation factors
           - Team/organizational standing

        4. JOB TRIGGERS & TIMING:
           - Specific events that create urgency for each job
           - Cyclical/seasonal patterns
           - External factors (regulations, threats, business changes)

        5. CURRENT FRICTION & WORKAROUNDS:
           - What prevents them from getting jobs done effectively today
           - Inadequate tools or processes they currently use
           - Time/resource constraints

        6. SUCCESS CRITERIA:
           - How they measure job completion
           - KPIs or metrics that matter to them
           - Quality indicators for job success

        7. DECISION JOURNEY FACTORS:
           - Information sources they trust
           - Evaluation criteria for solutions
           - Approval processes they navigate
           - Implementation considerations

        Format as structured JSON with detailed analysis for each component.
        Focus on the specific pain points and use cases from the business context.
        """
        
        role_jtbd_data = await self.claude_service.get_completion(jtbd_prompt)
        
        return role_jtbd_data
    
    async def _generate_jtbd_insights(self, role_analyses: Dict[str, Any], b2b_inputs: B2BInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall JTBD insights across all roles"""
        
        insights_prompt = f"""
        Based on the role-specific JTBD analyses, generate overall insights:

        Role Analyses: {role_analyses}
        Business Context: {business_context}

        Provide:
        1. COMMON JOBS ACROSS ROLES:
           - Jobs that appear across multiple roles
           - Shared pain points and triggers
           - Universal success criteria

        2. ROLE-SPECIFIC DIFFERENTIATION:
           - Unique jobs for each role
           - Different perspectives on similar problems
           - Varying success criteria and priorities

        3. INTEGRATION OPPORTUNITIES:
           - Where roles collaborate on shared jobs
           - Cross-functional workflow requirements
           - Shared metrics and outcomes

        4. STRATEGIC INSIGHTS:
           - Primary vs secondary job priorities
           - Most critical pain points to solve
           - Highest-impact opportunity areas

        5. MESSAGING IMPLICATIONS:
           - Role-specific value propositions
           - Common themes for unified messaging
           - Differentiation points for targeted communication

        Format as structured JSON with actionable insights.
        """
        
        return await self.claude_service.get_completion(insights_prompt)
    
    async def _generate_b2b_decision_journey(self, b2b_inputs: B2BInputs, role_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Generate B2B decision journey mapping"""
        
        journey_prompt = f"""
        Create a comprehensive B2B decision journey map:

        B2B Context: {b2b_inputs}
        Role Analyses: {role_analyses}

        Map the decision journey including:

        1. TRIGGER PHASE:
           - Events that initiate buying process
           - Pain point recognition
           - Urgency factors

        2. EXPLORATION PHASE:
           - Information search behavior
           - Stakeholder involvement
           - Internal discussion patterns

        3. EVALUATION PHASE:
           - Solution comparison criteria
           - Stakeholder alignment processes
           - Risk assessment factors

        4. DECISION PHASE:
           - Final approval processes
           - Budget approval requirements
           - Implementation planning

        5. IMPLEMENTATION PHASE:
           - Onboarding expectations
           - Success measurement criteria
           - Ongoing evaluation factors

        For each phase, specify:
        - Role involvement and influence
        - Key decision criteria
        - Information needs
        - Potential friction points
        - Success factors

        Format as structured JSON with phase-by-phase breakdown.
        """
        
        return await self.claude_service.get_completion(journey_prompt)
    
    async def _generate_b2c_decision_journey(self, b2c_inputs: B2CInputs, jtbd_analysis: Any) -> Dict[str, Any]:
        """Generate B2C customer decision journey mapping"""
        
        journey_prompt = f"""
        Create a comprehensive B2C customer decision journey:

        B2C Context: {b2c_inputs}
        JTBD Analysis: {jtbd_analysis}

        Map the customer journey including:

        1. PROBLEM RECOGNITION:
           - Trigger events and situations
           - Pain point awareness
           - Emotional drivers

        2. INFORMATION SEARCH:
           - Research behavior and channels
           - Influence sources (friends, reviews, etc.)
           - Information consumption patterns

        3. ALTERNATIVE EVALUATION:
           - Comparison criteria and priorities
           - Decision-making factors
           - Emotional vs rational considerations

        4. PURCHASE DECISION:
           - Final decision triggers
           - Purchase barriers and objections
           - Conversion factors

        5. POST-PURCHASE EXPERIENCE:
           - Success measurement
           - Satisfaction indicators
           - Repeat purchase factors

        For each stage, specify:
        - Emotional state and mindset
        - Information needs and sources
        - Decision criteria and priorities
        - Potential friction points
        - Optimization opportunities

        Format as structured JSON with detailed journey mapping.
        """
        
        return await self.claude_service.get_completion(journey_prompt)
    
    def _generate_trigger_calendar(self, b2b_inputs: B2BInputs, role_analyses: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate timing-based trigger event calendar"""
        
        # Extract triggers from inputs and role analyses
        calendar_triggers = {
            'immediate': [],
            'quarterly': [],
            'annual': [],
            'event_driven': []
        }
        
        # Add triggers from B2B inputs
        if b2b_inputs.buying_triggers:
            triggers = b2b_inputs.buying_triggers.split(',')
            for trigger in triggers:
                trigger = trigger.strip()
                if any(word in trigger.lower() for word in ['funding', 'breach', 'incident', 'urgent']):
                    calendar_triggers['immediate'].append(trigger)
                elif any(word in trigger.lower() for word in ['quarter', 'review', 'budget']):
                    calendar_triggers['quarterly'].append(trigger)
                elif any(word in trigger.lower() for word in ['annual', 'yearly', 'compliance']):
                    calendar_triggers['annual'].append(trigger)
                else:
                    calendar_triggers['event_driven'].append(trigger)
        
        return calendar_triggers
    
    def _generate_b2c_trigger_calendar(self, b2c_inputs: B2CInputs) -> Dict[str, List[str]]:
        """Generate B2C trigger event calendar"""
        
        calendar_triggers = {
            'seasonal': [],
            'life_events': [],
            'emotional': [],
            'situational': []
        }
        
        if b2c_inputs.buying_triggers:
            triggers = b2c_inputs.buying_triggers.split(',')
            for trigger in triggers:
                trigger = trigger.strip()
                if any(word in trigger.lower() for word in ['holiday', 'season', 'winter', 'summer']):
                    calendar_triggers['seasonal'].append(trigger)
                elif any(word in trigger.lower() for word in ['job', 'moving', 'marriage', 'birth', 'graduation']):
                    calendar_triggers['life_events'].append(trigger)
                elif any(word in trigger.lower() for word in ['stress', 'anxiety', 'excitement', 'celebration']):
                    calendar_triggers['emotional'].append(trigger)
                else:
                    calendar_triggers['situational'].append(trigger)
        
        return calendar_triggers
    
    def _generate_pain_severity_matrix(self, role_analyses: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """Generate pain point severity matrix across roles"""
        
        # This would be enhanced with actual pain point analysis from role_analyses
        # For now, returning a structure that could be populated
        severity_matrix = {}
        
        for role_key in role_analyses.keys():
            severity_matrix[role_key] = {
                'security_threats': 9,
                'compliance_requirements': 8,
                'operational_efficiency': 7,
                'cost_management': 6,
                'skill_gaps': 5
            }
        
        return severity_matrix
    
    async def _generate_b2c_psychographics(self, b2c_inputs: B2CInputs, jtbd_analysis: Any) -> Dict[str, Any]:
        """Generate detailed psychographic analysis for B2C"""
        
        psycho_prompt = f"""
        Generate detailed psychographic analysis:

        B2C Context: {b2c_inputs}
        JTBD Analysis: {jtbd_analysis}

        Provide comprehensive psychographic insights:

        1. VALUES & BELIEFS:
           - Core values that drive behavior
           - Belief systems affecting purchase decisions
           - Priorities and life philosophy

        2. LIFESTYLE PATTERNS:
           - Daily routines and habits
           - Social activities and preferences
           - Technology usage patterns
           - Media consumption behavior

        3. PERSONALITY TRAITS:
           - Decision-making style (analytical, impulsive, etc.)
           - Risk tolerance and innovation adoption
           - Social orientation (introvert/extrovert)
           - Achievement motivation

        4. MOTIVATIONAL DRIVERS:
           - Primary motivations for product category
           - Emotional triggers and responses
           - Success and status indicators

        5. BEHAVIORAL PREFERENCES:
           - Communication channel preferences
           - Shopping and buying patterns
           - Brand interaction preferences
           - Service and support expectations

        Format as structured JSON with detailed psychographic profiling.
        """
        
        return await self.claude_service.get_completion(psycho_prompt)
    
    async def _analyze_general_jtbd(self, user_inputs: UserInputs, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback JTBD analysis for businesses without specific B2B/B2C inputs"""
        
        general_prompt = f"""
        Create a general JTBD analysis for this business:

        Business Context: {business_context}
        User Inputs: {user_inputs}

        Provide:
        1. PRIMARY CUSTOMER JOBS
        2. KEY TRIGGER EVENTS
        3. MAIN FRICTION POINTS
        4. SUCCESS CRITERIA
        5. DECISION JOURNEY OVERVIEW

        Format as structured JSON with general JTBD framework.
        """
        
        general_analysis = await self.claude_service.get_completion(general_prompt)
        
        return {
            'framework_type': 'General',
            'general_jtbd': general_analysis,
            'recommended_enhancements': [
                'Add specific B2B or B2C questionnaire data for detailed role analysis',
                'Include decision maker roles for B2B JTBD mapping',
                'Specify customer demographics for B2C psychographic analysis'
            ]
        }