import os
import json
from typing import Dict, List, Optional
from anthropic import Anthropic
from models.user_inputs import UserInputs, BusinessModel
from models.segment_models import Segment, MarketAnalysis, SegmentationResults, Competitor

class ClaudeService:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    
    def analyze_market(self, user_inputs: UserInputs, search_results: str = "") -> MarketAnalysis:
        prompt = self._build_market_analysis_prompt(user_inputs, search_results)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_market_analysis(response.content[0].text)
    
    def generate_segments(self, user_inputs: UserInputs, market_analysis: MarketAnalysis) -> List[Segment]:
        prompt = self._build_segmentation_prompt(user_inputs, market_analysis)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=6000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_segments(response.content[0].text)
    
    def generate_personas(self, segment: Segment, user_inputs: UserInputs) -> Segment:
        prompt = self._build_persona_prompt(segment, user_inputs)
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_persona(response.content[0].text, segment)
    
    def _build_market_analysis_prompt(self, user_inputs: UserInputs, search_results: str) -> str:
        business_type = "B2B" if user_inputs.basic_info.business_model == BusinessModel.B2B else "B2C"
        
        prompt = f"""
        Analyze the following business for comprehensive market segmentation:
        
        Business Details:
        - Company: {user_inputs.basic_info.company_name}
        - Industry: {user_inputs.basic_info.industry}
        - Business Model: {business_type}
        - Description: {user_inputs.basic_info.description}
        
        Additional Context:
        {self._format_additional_inputs(user_inputs)}
        
        Web Search Results:
        {search_results}
        
        Please provide a comprehensive market analysis including:
        1. Total Addressable Market estimation with size and growth projections (ALL MONETARY VALUES MUST BE IN USD - convert from other currencies if needed)
        2. 4-6 key market insights and opportunities
        3. Industry trends affecting this business
        4. Factors driving industry growth (technology, regulations, consumer behavior, etc.)
        5. Industry CAGR (Compound Annual Growth Rate) with timeframe
        6. Current commercial urgencies and market pressures
        7. Top 5 competitors with their funding status and solution specialties (funding amounts in USD)
        8. Competitive landscape overview
        
        IMPORTANT: All monetary values, market sizes, and funding amounts MUST be converted to USD. If source data is in EUR, GBP, JPY, or other currencies, convert to USD using current exchange rates.
        
        Format your response as JSON with the following structure:
        {{
            "total_addressable_market": "TAM description with size estimates in USD (e.g., $XX billion USD)",
            "key_insights": ["insight1", "insight2", "insight3", "insight4"],
            "industry_trends": ["trend1", "trend2", "trend3", "trend4"],
            "industry_growth_factors": ["factor1", "factor2", "factor3"],
            "industry_cagr": "X.X% CAGR (2024-2029)",
            "commercial_urgencies": ["urgency1", "urgency2", "urgency3"],
            "competitive_landscape": "overall competitive overview",
            "top_competitors": [
                {{
                    "name": "Competitor Name",
                    "funding": "$XX million USD (Series X)",
                    "solution_specialty": "What they specialize in",
                    "market_position": "Market position description"
                }}
            ]
        }}
        """
        
        return prompt
    
    def _build_segmentation_prompt(self, user_inputs: UserInputs, market_analysis: MarketAnalysis) -> str:
        business_type = "B2B" if user_inputs.basic_info.business_model == BusinessModel.B2B else "B2C"
        
        prompt = f"""
        Based on the market analysis and business details, identify 4-6 distinct market segments for this {business_type} business:
        
        Business: {user_inputs.basic_info.company_name}
        Industry: {user_inputs.basic_info.industry}
        Description: {user_inputs.basic_info.description}
        
        Market Context:
        - TAM: {market_analysis.total_addressable_market}
        - Key Insights: {', '.join(market_analysis.key_insights)}
        - Trends: {', '.join(market_analysis.industry_trends)}
        
        Additional Context:
        {self._format_additional_inputs(user_inputs)}
        
        For each segment, provide:
        1. Creative, memorable segment name
        2. Key characteristics (3-5 bullet points)
        3. Size estimation (% of TAM and approximate market value in USD)
        4. Primary pain points (3-4 points)
        5. Buying triggers (3-4 points)
        6. Preferred communication channels
        7. Messaging hooks (3-4 compelling angles)
        8. Specific use cases (3-4 practical applications)
        9. Role-specific pain points (if B2B, map pain points to specific roles)
        
        IMPORTANT: All monetary values must be in USD. Convert from other currencies if necessary.
        
        Format as JSON array of segments:
        [
            {{
                "name": "Segment Name",
                "characteristics": ["char1", "char2", "char3"],
                "size_percentage": 25.0,
                "size_estimation": "Detailed size description with USD values (e.g., $X billion USD market opportunity)",
                "pain_points": ["pain1", "pain2", "pain3"],
                "buying_triggers": ["trigger1", "trigger2", "trigger3"],
                "preferred_channels": ["channel1", "channel2", "channel3"],
                "messaging_hooks": ["hook1", "hook2", "hook3"],
                "use_cases": ["use_case1", "use_case2", "use_case3"],
                "role_specific_pain_points": {{
                    "role1": ["pain1", "pain2"],
                    "role2": ["pain1", "pain2"]
                }}
            }}
        ]
        """
        
        return prompt
    
    def _build_persona_prompt(self, segment: Segment, user_inputs: UserInputs) -> str:
        business_type = "B2B" if user_inputs.basic_info.business_model == BusinessModel.B2B else "B2C"
        
        prompt = f"""
        Create a detailed persona for the "{segment.name}" segment in the {business_type} context:
        
        Segment Characteristics:
        {', '.join(segment.characteristics)}
        
        Pain Points:
        {', '.join(segment.pain_points)}
        
        Generate a comprehensive persona including:
        1. Detailed persona description (2-3 paragraphs)
        2. Demographics/Firmographics (specific details)
        3. Psychographics (values, attitudes, lifestyle)
        4. Goals and motivations
        5. Challenges and frustrations
        6. Decision-making process
        7. Information sources they trust
        
        Format as JSON:
        {{
            "persona_description": "Detailed 2-3 paragraph description",
            "demographics": {{
                "age": "age range or role level",
                "location": "geographic details",
                "company_size": "if B2B",
                "income": "if B2C",
                "education": "education level",
                "other_relevant": "other key demographic info"
            }},
            "psychographics": ["value1", "value2", "attitude3", "lifestyle4"]
        }}
        """
        
        return prompt
    
    def _format_additional_inputs(self, user_inputs: UserInputs) -> str:
        if user_inputs.b2b_inputs:
            return f"""
            B2B Context:
            - Target Company Sizes: {', '.join([size.value for size in user_inputs.b2b_inputs.target_company_sizes])}
            - Target Industries: {', '.join(user_inputs.b2b_inputs.target_industries)}
            - Deal Size Range: {user_inputs.b2b_inputs.deal_size_range}
            - Sales Cycle: {user_inputs.b2b_inputs.sales_cycle_length}
            - Decision Makers: {', '.join(user_inputs.b2b_inputs.decision_maker_roles)}
            - Geographic Focus: {', '.join(user_inputs.b2b_inputs.geographic_focus)}
            - Pain Points: {user_inputs.b2b_inputs.pain_points}
            """
        elif user_inputs.b2c_inputs:
            return f"""
            B2C Context:
            - Target Ages: {', '.join(user_inputs.b2c_inputs.target_age_groups)}
            - Gender Focus: {user_inputs.b2c_inputs.gender_focus}
            - Income Brackets: {', '.join(user_inputs.b2c_inputs.income_brackets)}
            - Geographic Markets: {', '.join(user_inputs.b2c_inputs.geographic_markets)}
            - Product Category: {user_inputs.b2c_inputs.product_category}
            - Purchase Frequency: {user_inputs.b2c_inputs.purchase_frequency}
            - Customer Motivations: {', '.join(user_inputs.b2c_inputs.customer_motivations)}
            - Lifestyle Categories: {', '.join(user_inputs.b2c_inputs.lifestyle_categories)}
            """
        return ""
    
    def _parse_market_analysis(self, response: str) -> MarketAnalysis:
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
                data = json.loads(json_str)
                
                # Parse competitors
                competitors = []
                for comp_data in data.get("top_competitors", []):
                    if isinstance(comp_data, dict):
                        competitor = Competitor(
                            name=comp_data.get("name", ""),
                            funding=comp_data.get("funding", ""),
                            solution_specialty=comp_data.get("solution_specialty", ""),
                            market_position=comp_data.get("market_position", "")
                        )
                        competitors.append(competitor)
                
                return MarketAnalysis(
                    total_addressable_market=data.get("total_addressable_market", ""),
                    key_insights=data.get("key_insights", []),
                    segments=[],  # Will be populated later
                    industry_trends=data.get("industry_trends", []),
                    competitive_landscape=data.get("competitive_landscape", ""),
                    industry_growth_factors=data.get("industry_growth_factors", []),
                    industry_cagr=data.get("industry_cagr", ""),
                    commercial_urgencies=data.get("commercial_urgencies", []),
                    top_competitors=competitors
                )
            else:
                raise json.JSONDecodeError("No JSON found", response, 0)
                
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # Fallback parsing - try to extract info from text
            lines = response.split('\n')
            tam = "Analysis pending..."
            insights = ["Market analysis in progress..."]
            trends = ["Trend analysis pending..."]
            competitive = "Competitive analysis pending..."
            
            # Try to extract some basic info from text
            for line in lines:
                if "market" in line.lower() and ("size" in line.lower() or "tam" in line.lower()):
                    tam = line.strip()
                elif "insight" in line.lower() or "key" in line.lower():
                    insights = [line.strip()]
                elif "trend" in line.lower():
                    trends = [line.strip()]
                elif "compet" in line.lower():
                    competitive = line.strip()
            
            return MarketAnalysis(
                total_addressable_market=tam,
                key_insights=insights,
                segments=[],
                industry_trends=trends,
                competitive_landscape=competitive,
                industry_growth_factors=["Analysis pending..."],
                industry_cagr="Analysis pending...",
                commercial_urgencies=["Analysis pending..."],
                top_competitors=[]
            )
    
    def _parse_segments(self, response: str) -> List[Segment]:
        try:
            # Extract JSON from response if it contains other text
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:]
            if response_clean.endswith("```"):
                response_clean = response_clean[:-3]
            
            # Find JSON array in response
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_clean[start_idx:end_idx]
                segments_data = json.loads(json_str)
            else:
                # Try to find individual JSON objects
                segments_data = []
                obj_start = 0
                while True:
                    obj_start = response_clean.find('{', obj_start)
                    if obj_start == -1:
                        break
                    obj_end = response_clean.find('}', obj_start) + 1
                    if obj_end > obj_start:
                        try:
                            obj = json.loads(response_clean[obj_start:obj_end])
                            segments_data.append(obj)
                            obj_start = obj_end
                        except:
                            obj_start += 1
                    else:
                        break
            
            segments = []
            for seg_data in segments_data:
                if isinstance(seg_data, dict):
                    segment = Segment(
                        name=seg_data.get("name", "Unnamed Segment"),
                        characteristics=seg_data.get("characteristics", []),
                        size_percentage=self._safe_float_conversion(seg_data.get("size_percentage", 0.0)),
                        size_estimation=seg_data.get("size_estimation", ""),
                        pain_points=seg_data.get("pain_points", []),
                        buying_triggers=seg_data.get("buying_triggers", []),
                        preferred_channels=seg_data.get("preferred_channels", []),
                        messaging_hooks=seg_data.get("messaging_hooks", []),
                        persona_description="",  # Will be populated later
                        demographics={},  # Will be populated later
                        psychographics=[],  # Will be populated later
                        use_cases=seg_data.get("use_cases", []),
                        role_specific_pain_points=seg_data.get("role_specific_pain_points", {})
                    )
                    segments.append(segment)
            
            return segments if segments else self._create_fallback_segments()
            
        except (json.JSONDecodeError, KeyError, AttributeError, ValueError) as e:
            return self._create_fallback_segments()
    
    def _create_fallback_segments(self) -> List[Segment]:
        """Create fallback segments when parsing fails"""
        return [
            Segment(
                name="Primary Market Segment",
                characteristics=["Analysis in progress..."],
                size_percentage=40.0,
                size_estimation="Segment analysis pending",
                pain_points=["Analysis pending"],
                buying_triggers=["Analysis pending"],
                preferred_channels=["Digital channels"],
                messaging_hooks=["Value-focused messaging"],
                persona_description="",
                demographics={},
                psychographics=[],
                use_cases=["Analysis pending"],
                role_specific_pain_points={}
            ),
            Segment(
                name="Secondary Market Segment", 
                characteristics=["Analysis in progress..."],
                size_percentage=30.0,
                size_estimation="Segment analysis pending",
                pain_points=["Analysis pending"],
                buying_triggers=["Analysis pending"],
                preferred_channels=["Traditional channels"],
                messaging_hooks=["Feature-focused messaging"],
                persona_description="",
                demographics={},
                psychographics=[],
                use_cases=["Analysis pending"],
                role_specific_pain_points={}
            ),
            Segment(
                name="Tertiary Market Segment",
                characteristics=["Analysis in progress..."],
                size_percentage=30.0,
                size_estimation="Segment analysis pending", 
                pain_points=["Analysis pending"],
                buying_triggers=["Analysis pending"],
                preferred_channels=["Social media"],
                messaging_hooks=["Benefit-focused messaging"],
                persona_description="",
                demographics={},
                psychographics=[],
                use_cases=["Analysis pending"],
                role_specific_pain_points={}
            )
        ]
    
    def _parse_persona(self, response: str, segment: Segment) -> Segment:
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
                persona_data = json.loads(json_str)
                
                if isinstance(persona_data, dict):
                    segment.persona_description = persona_data.get("persona_description", "")
                    segment.demographics = persona_data.get("demographics", {})
                    segment.psychographics = persona_data.get("psychographics", [])
            
            return segment
            
        except (json.JSONDecodeError, KeyError, AttributeError) as e:
            # Fallback - extract basic info from text
            segment.persona_description = response[:500] if len(response) > 500 else response
            return segment
    
    def _safe_float_conversion(self, value, default=0.0):
        """Safely convert a value to float with fallback"""
        try:
            if value is None or value == "":
                return default
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                # Clean the string first
                cleaned = value.strip().replace(',', '').replace('$', '').replace('%', '')
                if cleaned == "":
                    return default
                return float(cleaned)
            return default
        except (ValueError, TypeError):
            return default