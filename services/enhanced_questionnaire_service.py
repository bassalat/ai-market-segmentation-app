"""
Enhanced Questionnaire Service for PRD-compliant data collection
Implements systematic B2B/B2C data collection per PRD specifications
"""

import asyncio
from typing import Dict, List, Any, Optional
from models.user_inputs import UserInputs, B2BInputs, B2CInputs
from services.claude_service import ClaudeService
from services.enhanced_search_service import EnhancedSearchService


class EnhancedQuestionnaireService:
    """Service for processing enhanced questionnaire data per PRD requirements"""
    
    def __init__(self, serper_api_key: str = None):
        self.claude_service = ClaudeService()
        self.search_service = EnhancedSearchService(serper_api_key) if serper_api_key else None
    
    async def process_inputs(self, user_inputs: UserInputs) -> Dict[str, Any]:
        """
        Process user inputs according to PRD Phase 1 requirements
        Returns comprehensive market research and validation
        """
        
        # Extract business context
        business_context = self._extract_business_context(user_inputs)
        
        # Validate input completeness per PRD priorities
        validation_results = self._validate_prd_compliance(user_inputs)
        
        # Perform 30-minute automated market research
        market_research = await self._perform_automated_research(business_context)
        
        # Generate insights and recommendations
        insights = await self._generate_insights(user_inputs, market_research)
        
        return {
            'business_context': business_context,
            'validation_results': validation_results,
            'market_research': market_research,
            'insights': insights,
            'completeness_score': validation_results['completeness_score']
        }
    
    def _extract_business_context(self, user_inputs: UserInputs) -> Dict[str, Any]:
        """Extract structured business context from user inputs"""
        
        context = {
            'basic_info': {
                'company_name': user_inputs.basic_info.company_name,
                'industry': user_inputs.basic_info.industry,
                'business_model': user_inputs.basic_info.business_model.value,
                'description': user_inputs.basic_info.description
            }
        }
        
        # Add B2B context if available
        if user_inputs.b2b_inputs:
            context['b2b_context'] = self._extract_b2b_context(user_inputs.b2b_inputs)
        
        # Add B2C context if available
        if user_inputs.b2c_inputs:
            context['b2c_context'] = self._extract_b2c_context(user_inputs.b2c_inputs)
        
        # Add document context if available
        if user_inputs.document_context and user_inputs.document_context.has_context:
            context['document_context'] = {
                'summary': user_inputs.document_context.summary,
                'key_insights': user_inputs.document_context.processed_content.get('key_insights', []),
                'data_points': user_inputs.document_context.data_points
            }
        
        return context
    
    def _extract_b2b_context(self, b2b_inputs: B2BInputs) -> Dict[str, Any]:
        """Extract B2B-specific context per PRD specifications"""
        
        return {
            'industry_targeting': {
                'company_types': b2b_inputs.target_company_types,
                'company_sizes': [size.value for size in b2b_inputs.target_company_sizes],
                'industries': b2b_inputs.target_industries,
                'geographic_focus': b2b_inputs.geographic_focus
            },
            'buyer_dynamics': {
                'decision_makers': b2b_inputs.decision_maker_roles,
                'deal_size': b2b_inputs.deal_size_range,
                'sales_cycle': b2b_inputs.sales_cycle_length,
                'budget_sensitivity': b2b_inputs.customer_budget_sensitivity
            },
            'product_fit': {
                'main_problem': b2b_inputs.main_problem_solved,
                'use_cases': b2b_inputs.practical_use_cases,
                'integrations': b2b_inputs.integration_requirements,
                'triggers': b2b_inputs.buying_triggers
            },
            'go_to_market': {
                'lead_sources': b2b_inputs.current_lead_sources,
                'customer_acquisition': 'B2B focused on ' + ', '.join(b2b_inputs.current_lead_sources)
            }
        }
    
    def _extract_b2c_context(self, b2c_inputs: B2CInputs) -> Dict[str, Any]:
        """Extract B2C-specific context per PRD specifications"""
        
        return {
            'target_customer': {
                'primary_customer': b2c_inputs.primary_target_customer,
                'demographics': {
                    'age_groups': b2c_inputs.target_age_groups,
                    'gender_focus': b2c_inputs.gender_focus,
                    'income_brackets': b2c_inputs.income_brackets,
                    'geographic_markets': b2c_inputs.geographic_markets
                }
            },
            'buying_behavior': {
                'frequency': b2c_inputs.purchase_frequency,
                'context': b2c_inputs.purchase_context,
                'triggers': b2c_inputs.buying_triggers,
                'priorities': b2c_inputs.customer_priorities,
                'price_sensitivity': b2c_inputs.price_vs_quality_focus
            },
            'product_market_fit': {
                'product_type': b2c_inputs.product_type,
                'discovery_channels': b2c_inputs.discovery_channels,
                'alternatives': b2c_inputs.existing_alternatives,
                'category': b2c_inputs.product_category
            },
            'psychographics': {
                'motivations': b2c_inputs.customer_motivations,
                'lifestyle': b2c_inputs.lifestyle_categories
            }
        }
    
    def _validate_prd_compliance(self, user_inputs: UserInputs) -> Dict[str, Any]:
        """Validate input completeness according to PRD priority levels"""
        
        validation = {
            'critical_fields': [],  # ⭐⭐⭐ priority
            'important_fields': [],  # ⭐⭐ priority
            'optional_fields': [],  # ⭐ priority
            'missing_critical': [],
            'missing_important': [],
            'completeness_score': 0
        }
        
        # Validate B2B inputs if present
        if user_inputs.b2b_inputs:
            validation.update(self._validate_b2b_inputs(user_inputs.b2b_inputs))
        
        # Validate B2C inputs if present
        if user_inputs.b2c_inputs:
            validation.update(self._validate_b2c_inputs(user_inputs.b2c_inputs))
        
        # Calculate completeness score
        total_critical = len(validation['critical_fields'])
        completed_critical = total_critical - len(validation['missing_critical'])
        
        total_important = len(validation['important_fields'])
        completed_important = total_important - len(validation['missing_important'])
        
        if total_critical > 0:
            critical_score = (completed_critical / total_critical) * 70  # 70% weight for critical
            important_score = (completed_important / total_important) * 30 if total_important > 0 else 30  # 30% weight for important
            validation['completeness_score'] = critical_score + important_score
        else:
            validation['completeness_score'] = 100
        
        return validation
    
    def _validate_b2b_inputs(self, b2b_inputs: B2BInputs) -> Dict[str, Any]:
        """Validate B2B inputs according to PRD priority specifications"""
        
        validation = {
            'critical_fields': [
                'target_company_types', 'target_company_sizes', 'decision_maker_roles',
                'main_problem_solved', 'practical_use_cases'
            ],
            'important_fields': [
                'geographic_focus', 'deal_size_range', 'sales_cycle_length',
                'integration_requirements', 'buying_triggers', 'current_lead_sources',
                'customer_budget_sensitivity'
            ],
            'optional_fields': ['target_industries'],
            'missing_critical': [],
            'missing_important': []
        }
        
        # Check critical fields
        if not b2b_inputs.target_company_types or not b2b_inputs.target_company_types[0]:
            validation['missing_critical'].append('target_company_types')
        if not b2b_inputs.target_company_sizes:
            validation['missing_critical'].append('target_company_sizes')
        if not b2b_inputs.decision_maker_roles:
            validation['missing_critical'].append('decision_maker_roles')
        if not b2b_inputs.main_problem_solved:
            validation['missing_critical'].append('main_problem_solved')
        if not b2b_inputs.practical_use_cases:
            validation['missing_critical'].append('practical_use_cases')
        
        # Check important fields
        if not b2b_inputs.geographic_focus:
            validation['missing_important'].append('geographic_focus')
        if not b2b_inputs.deal_size_range:
            validation['missing_important'].append('deal_size_range')
        if not b2b_inputs.sales_cycle_length:
            validation['missing_important'].append('sales_cycle_length')
        if not b2b_inputs.integration_requirements:
            validation['missing_important'].append('integration_requirements')
        if not b2b_inputs.buying_triggers:
            validation['missing_important'].append('buying_triggers')
        if not b2b_inputs.current_lead_sources:
            validation['missing_important'].append('current_lead_sources')
        if not b2b_inputs.customer_budget_sensitivity:
            validation['missing_important'].append('customer_budget_sensitivity')
        
        return validation
    
    def _validate_b2c_inputs(self, b2c_inputs: B2CInputs) -> Dict[str, Any]:
        """Validate B2C inputs according to PRD priority specifications"""
        
        validation = {
            'critical_fields': [
                'primary_target_customer', 'target_age_groups', 'purchase_frequency',
                'buying_triggers', 'customer_priorities', 'discovery_channels'
            ],
            'important_fields': [
                'geographic_markets', 'purchase_context', 'price_vs_quality_focus',
                'product_type', 'existing_alternatives'
            ],
            'optional_fields': ['gender_focus', 'income_brackets', 'product_category'],
            'missing_critical': [],
            'missing_important': []
        }
        
        # Check critical fields
        if not b2c_inputs.primary_target_customer:
            validation['missing_critical'].append('primary_target_customer')
        if not b2c_inputs.target_age_groups:
            validation['missing_critical'].append('target_age_groups')
        if not b2c_inputs.purchase_frequency:
            validation['missing_critical'].append('purchase_frequency')
        if not b2c_inputs.buying_triggers:
            validation['missing_critical'].append('buying_triggers')
        if not b2c_inputs.customer_priorities:
            validation['missing_critical'].append('customer_priorities')
        if not b2c_inputs.discovery_channels:
            validation['missing_critical'].append('discovery_channels')
        
        # Check important fields
        if not b2c_inputs.geographic_markets:
            validation['missing_important'].append('geographic_markets')
        if not b2c_inputs.purchase_context:
            validation['missing_important'].append('purchase_context')
        if not b2c_inputs.price_vs_quality_focus:
            validation['missing_important'].append('price_vs_quality_focus')
        if not b2c_inputs.product_type:
            validation['missing_important'].append('product_type')
        if not b2c_inputs.existing_alternatives:
            validation['missing_important'].append('existing_alternatives')
        
        return validation
    
    async def _perform_automated_research(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform 30-minute automated market research per PRD specifications
        """
        
        industry = business_context['basic_info']['industry']
        company_name = business_context['basic_info']['company_name']
        description = business_context['basic_info']['description']
        
        # Research tasks to perform in parallel
        research_tasks = []
        
        # Industry analysis
        research_tasks.append(
            self._research_industry_analysis(industry, description)
        )
        
        # Competitive landscape
        research_tasks.append(
            self._research_competitive_landscape(industry, description, company_name)
        )
        
        # Market sizing and growth
        research_tasks.append(
            self._research_market_sizing(industry, description)
        )
        
        # Commercial urgencies and trends
        research_tasks.append(
            self._research_commercial_urgencies(industry, business_context)
        )
        
        # Execute research tasks in parallel
        try:
            research_results = await asyncio.gather(*research_tasks, return_exceptions=True)
            
            return {
                'industry_analysis': research_results[0] if not isinstance(research_results[0], Exception) else {},
                'competitive_landscape': research_results[1] if not isinstance(research_results[1], Exception) else {},
                'market_sizing': research_results[2] if not isinstance(research_results[2], Exception) else {},
                'commercial_urgencies': research_results[3] if not isinstance(research_results[3], Exception) else {},
                'research_quality_score': self._calculate_research_quality(research_results)
            }
        except Exception as e:
            # Fallback to sequential processing if parallel fails
            return await self._perform_sequential_research(business_context)
    
    async def _research_industry_analysis(self, industry: str, description: str) -> Dict[str, Any]:
        """Research industry growth factors, CAGR, and market maturity"""
        
        # Get search results if search service is available
        search_results = ""
        if self.search_service:
            query = f"{industry} market size CAGR growth drivers technology trends 2024 2025"
            search_results = await self.search_service.search_web(query, max_results=5)
        
        analysis_prompt = f"""
        Based on the following search results about the {industry} industry, provide a comprehensive industry analysis:

        Search Results:
        {search_results}

        Business Context: {description}

        Please provide:
        1. Current market size and valuation
        2. CAGR (Compound Annual Growth Rate) for next 5+ years
        3. Key technology drivers contributing to growth
        4. Regulatory changes affecting the industry
        5. Consumer behavior shifts impacting the market
        6. Market maturity assessment (emerging, growth, mature, declining)
        7. Key growth opportunities and challenges

        Format as structured JSON with clear categories.
        """
        
        return await self.claude_service.get_completion(analysis_prompt)
    
    async def _research_competitive_landscape(self, industry: str, description: str, company_name: str) -> Dict[str, Any]:
        """Research detailed competitive landscape with business metrics"""
        
        # Get search results if search service is available
        search_results = ""
        if self.search_service:
            query = f"{industry} companies competitors funding revenue business model {company_name}"
            search_results = await self.search_service.search_web(query, max_results=8)
        
        competitive_prompt = f"""
        Based on the search results, identify and analyze the top 5-8 competitors in the {industry} space:

        Search Results:
        {search_results}

        Business Context: {description}

        For each competitor, provide (per PRD requirements):
        1. Company name and headquarters location
        2. Organization size (employee count)
        3. Inception year
        4. Annual revenue (if available)
        5. Total funding raised and recent funding rounds
        6. Number of customers/users
        7. Regions of operation
        8. Target industries and customer segments
        9. Product/solution focus and specialty
        10. GTM strategy (positioning, channel approach)
        11. Pricing model (tiered, user-based, usage-based)
        12. Overlap percentage with our business model
        13. Key strengths and market positioning

        Format as structured JSON array with competitor objects.
        """
        
        return await self.claude_service.get_completion(competitive_prompt)
    
    async def _research_market_sizing(self, industry: str, description: str) -> Dict[str, Any]:
        """Research market sizing, TAM, and growth projections"""
        
        # Get search results if search service is available
        search_results = ""
        if self.search_service:
            query = f"{industry} total addressable market TAM SAM SOM market size valuation projections"
            search_results = await self.search_service.search_web(query, max_results=5)
        
        sizing_prompt = f"""
        Based on the search results, provide comprehensive market sizing analysis:

        Search Results:
        {search_results}

        Business Context: {description}

        Please provide:
        1. Total Addressable Market (TAM) - current size and 5-year projection
        2. Serviceable Addressable Market (SAM) for our specific niche
        3. Serviceable Obtainable Market (SOM) - realistic market share potential
        4. Market growth trajectory and key drivers
        5. Regional market breakdown (if available)
        6. Market segment sizes and opportunities
        7. Emerging market opportunities and white spaces

        Format as structured JSON with clear market sizing metrics.
        """
        
        return await self.claude_service.get_completion(sizing_prompt)
    
    async def _research_commercial_urgencies(self, industry: str, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Research commercial urgencies, timing factors, and market pressures"""
        
        # Extract specific context for urgency research
        if 'b2b_context' in business_context:
            triggers = business_context['b2b_context']['product_fit'].get('triggers', '')
        elif 'b2c_context' in business_context:
            triggers = business_context['b2c_context']['buying_behavior'].get('triggers', '')
        else:
            triggers = ''
        
        # Get search results if search service is available
        search_results = ""
        if self.search_service:
            query = f"{industry} regulatory changes compliance requirements market pressures urgency factors {triggers}"
            search_results = await self.search_service.search_web(query, max_results=5)
        
        urgency_prompt = f"""
        Based on the search results, identify commercial urgencies and timing factors:

        Search Results:
        {search_results}

        Business Context: {business_context}

        Please identify:
        1. New regulations or compliance requirements driving urgency
        2. Merger & acquisition activity creating buying triggers
        3. Security breaches or incidents affecting the industry
        4. Rapid competition or market disruptions
        5. Economic factors creating pressure or opportunity
        6. Technology changes requiring adaptation
        7. Seasonal or cyclical buying patterns
        8. Industry events or milestones that trigger purchases

        Format as structured JSON with urgency categories and specific factors.
        """
        
        return await self.claude_service.get_completion(urgency_prompt)
    
    async def _perform_sequential_research(self, business_context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback sequential research if parallel processing fails"""
        
        industry = business_context['basic_info']['industry']
        description = business_context['basic_info']['description']
        company_name = business_context['basic_info']['company_name']
        
        try:
            industry_analysis = await self._research_industry_analysis(industry, description)
            competitive_landscape = await self._research_competitive_landscape(industry, description, company_name)
            market_sizing = await self._research_market_sizing(industry, description)
            commercial_urgencies = await self._research_commercial_urgencies(industry, business_context)
            
            return {
                'industry_analysis': industry_analysis,
                'competitive_landscape': competitive_landscape,
                'market_sizing': market_sizing,
                'commercial_urgencies': commercial_urgencies,
                'research_quality_score': 85  # Sequential processing score
            }
        except Exception as e:
            return {
                'industry_analysis': {},
                'competitive_landscape': {},
                'market_sizing': {},
                'commercial_urgencies': {},
                'research_quality_score': 0,
                'error': str(e)
            }
    
    def _calculate_research_quality(self, research_results: List[Any]) -> int:
        """Calculate research quality score based on successful data collection"""
        
        successful_tasks = sum(1 for result in research_results if not isinstance(result, Exception))
        total_tasks = len(research_results)
        
        if total_tasks == 0:
            return 0
        
        return int((successful_tasks / total_tasks) * 100)
    
    async def _generate_insights(self, user_inputs: UserInputs, market_research: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights and recommendations based on collected data"""
        
        insight_prompt = f"""
        Based on the enhanced questionnaire data and market research, provide strategic insights:

        User Inputs: {user_inputs}
        Market Research: {market_research}

        Please provide:
        1. Key market opportunities identified
        2. Potential risks or challenges
        3. Recommended focus areas for segmentation
        4. Missing data that could improve analysis
        5. Strategic recommendations for next steps
        6. Confidence level in the data collected (1-10)

        Format as structured JSON with actionable insights.
        """
        
        return await self.claude_service.get_completion(insight_prompt)