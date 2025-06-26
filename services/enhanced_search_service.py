import requests
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib
from collections import defaultdict
import re
from urllib.parse import urlparse
from services.web_scraper import WebScraper
from models.segment_models import DataSource, Citation, MarketDataPoint, SourceQuality, ContentType

class EnhancedSearchService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://google.serper.dev/search"
        
        # Check if API key is available
        if not self.api_key:
            # Service will work but without actual search capabilities
            pass
        self.cache = {}
        self.cache_duration = timedelta(hours=24)
        self.web_scraper = WebScraper()
        self.all_sources = []  # Track all sources for comprehensive bibliography
        self.source_id_counter = 0
        
    async def deep_market_search(self, company_name: str, industry: str, business_model: str) -> Dict[str, Any]:
        """Perform comprehensive market research with multiple search types and layers"""
        
        # Check if API key is available
        if not self.api_key:
            return self._generate_fallback_response(company_name, industry, business_model)
        
        # Phase 1: Generate expanded query sets
        queries = self._generate_query_sets(company_name, industry, business_model)
        
        # Phase 2: Execute searches concurrently
        all_results = await self._execute_concurrent_searches(queries)
        
        # Phase 3: Process and enrich results
        enriched_data = self._process_search_results(all_results)
        
        # Phase 4: Deep content extraction (web scraping)
        scraped_content = await self._scrape_top_results(enriched_data)
        
        # Phase 5: Extract key insights from both search and scraped data
        market_insights = self._extract_market_insights(enriched_data, scraped_content)
        
        # Phase 6: Create comprehensive source bibliography
        bibliography = self._create_research_bibliography()
        
        return {
            "raw_results": enriched_data,
            "scraped_content": scraped_content,
            "market_insights": market_insights,
            "research_sources": self.all_sources,
            "bibliography": bibliography,
            "search_metadata": {
                "total_queries": len(queries),
                "scraped_pages": len(scraped_content),
                "timestamp": datetime.now().isoformat(),
                "data_sources": self._get_data_sources(all_results),
                "source_quality_summary": self._get_source_quality_summary()
            }
        }
    
    def _generate_query_sets(self, company_name: str, industry: str, business_model: str) -> List[Dict[str, Any]]:
        """Generate comprehensive query sets for deep search"""
        
        queries = []
        
        # Market Size and Growth Queries
        market_queries = [
            {"q": f"{industry} market size 2024 2025 forecast", "type": "search"},
            {"q": f"{industry} TAM total addressable market {business_model}", "type": "search"},
            {"q": f"{industry} market growth rate CAGR projections", "type": "search"},
            {"q": f"{industry} industry analysis report 2024", "type": "search"},
            {"q": f"{industry} market trends emerging technologies", "type": "search"}
        ]
        
        # Customer Segment Queries
        segment_queries = [
            {"q": f"{industry} customer segments {business_model} buyers", "type": "search"},
            {"q": f"{business_model} {industry} target audience demographics", "type": "search"},
            {"q": f"{industry} buyer personas decision makers", "type": "search"},
            {"q": f"{industry} customer pain points challenges problems", "type": "search"},
            {"q": f"{business_model} {industry} use cases applications", "type": "search"}
        ]
        
        # Competitor Analysis Queries
        competitor_queries = [
            {"q": f"{company_name} competitors alternatives {industry}", "type": "search"},
            {"q": f"top {industry} companies {business_model} leaders", "type": "search"},
            {"q": f"{industry} startup funding rounds investments 2024", "type": "news"},
            {"q": f"{industry} market share distribution competitive landscape", "type": "search"},
            {"q": f"{company_name} vs competitors comparison analysis", "type": "search"}
        ]
        
        # Industry Trends and Insights
        trend_queries = [
            {"q": f"{industry} industry trends 2024 2025 predictions", "type": "search"},
            {"q": f"{industry} regulatory changes compliance requirements", "type": "news"},
            {"q": f"{industry} technology adoption digital transformation", "type": "search"},
            {"q": f"{industry} market opportunities gaps unmet needs", "type": "search"},
            {"q": f"{industry} industry challenges barriers entry", "type": "search"}
        ]
        
        # Academic and Research Queries
        research_queries = [
            {"q": f"{industry} market research study analysis", "type": "scholar"},
            {"q": f"{business_model} effectiveness ROI case studies", "type": "scholar"},
            {"q": f"{industry} consumer behavior research", "type": "scholar"}
        ]
        
        # Combine all queries
        all_queries = market_queries + segment_queries + competitor_queries + trend_queries + research_queries
        
        # Add metadata to each query
        for i, query in enumerate(all_queries):
            query["id"] = f"q_{i}_{hashlib.md5(query['q'].encode()).hexdigest()[:8]}"
            query["category"] = self._categorize_query(query['q'])
            
        return all_queries
    
    async def _execute_concurrent_searches(self, queries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple searches concurrently with rate limiting"""
        
        results = []
        
        # Process in batches to respect rate limits
        batch_size = 5
        delay_between_batches = 1  # seconds
        
        async with aiohttp.ClientSession() as session:
            for i in range(0, len(queries), batch_size):
                batch = queries[i:i + batch_size]
                batch_tasks = []
                
                for query in batch:
                    # Check cache first
                    cache_key = self._get_cache_key(query)
                    if cache_key in self.cache:
                        cached_result = self.cache[cache_key]
                        if self._is_cache_valid(cached_result):
                            results.append(cached_result['data'])
                            continue
                    
                    # Create search task
                    task = self._search_serper(session, query)
                    batch_tasks.append(task)
                
                # Execute batch concurrently
                if batch_tasks:
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    
                    for query, result in zip(batch, batch_results):
                        if isinstance(result, Exception):
                            print(f"Error searching for '{query['q']}': {result}")
                            continue
                        
                        # Cache successful results
                        cache_key = self._get_cache_key(query)
                        self.cache[cache_key] = {
                            'data': result,
                            'timestamp': datetime.now()
                        }
                        results.append(result)
                
                # Rate limiting between batches
                if i + batch_size < len(queries):
                    await asyncio.sleep(delay_between_batches)
        
        return results
    
    async def _search_serper(self, session: aiohttp.ClientSession, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single Serper API search"""
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Prepare search parameters based on query type
        search_params = {
            'q': query['q'],
            'gl': 'us',
            'hl': 'en'
        }
        
        # Adjust endpoint based on search type
        if query['type'] == 'news':
            url = 'https://google.serper.dev/news'
            search_params['num'] = 20
        elif query['type'] == 'scholar':
            url = 'https://google.serper.dev/scholar'
            search_params['num'] = 10
        else:
            url = 'https://google.serper.dev/search'
            search_params['num'] = 30  # Get more results for regular search
        
        try:
            async with session.post(
                url,
                json=search_params,
                headers=headers,
                timeout=30
            ) as response:
                result = await response.json()
                
                # Add query metadata to result
                result['query_metadata'] = query
                
                return result
                
        except Exception as e:
            raise Exception(f"Serper API error: {str(e)}")
    
    def _process_search_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process and structure search results by category"""
        
        processed = {
            'market_data': [],
            'customer_insights': [],
            'competitor_analysis': [],
            'industry_trends': [],
            'research_papers': [],
            'key_statistics': [],
            'expert_quotes': [],
            'news_insights': []
        }
        
        for result in results:
            if not result or 'error' in result:
                continue
                
            query_metadata = result.get('query_metadata', {})
            category = query_metadata.get('category', 'general')
            
            # Extract organic results
            organic_results = result.get('organic', [])
            for item in organic_results[:10]:  # Top 10 results per query
                
                # Create comprehensive DataSource object for each result
                data_source = self._create_data_source_from_result(item, query_metadata.get('q', ''))
                
                processed_item = {
                    'title': item.get('title', ''),
                    'snippet': item.get('snippet', ''),
                    'link': item.get('link', ''),
                    'source': self._extract_domain(item.get('link', '')),
                    'query': query_metadata.get('q', ''),
                    'data_source': data_source,  # Add comprehensive source metadata
                    'relevance_score': self._calculate_relevance(item, query_metadata)
                }
                
                # Extract key statistics from snippet
                stats = self._extract_statistics(item.get('snippet', ''))
                if stats:
                    processed['key_statistics'].extend(stats)
                
                # Categorize by content type
                if category == 'market_size':
                    processed['market_data'].append(processed_item)
                elif category == 'customer':
                    processed['customer_insights'].append(processed_item)
                elif category == 'competitor':
                    processed['competitor_analysis'].append(processed_item)
                elif category == 'trends':
                    processed['industry_trends'].append(processed_item)
            
            # Extract answer box if available
            answer_box = result.get('answer_box', {})
            if answer_box:
                processed['key_statistics'].append({
                    'type': 'answer_box',
                    'content': answer_box.get('answer', answer_box.get('snippet', '')),
                    'source': answer_box.get('link', ''),
                    'query': query_metadata.get('q', '')
                })
            
            # Extract knowledge graph
            knowledge_graph = result.get('knowledge_graph', {})
            if knowledge_graph:
                processed['market_data'].append({
                    'type': 'knowledge_graph',
                    'title': knowledge_graph.get('title', ''),
                    'description': knowledge_graph.get('description', ''),
                    'facts': knowledge_graph.get('facts', {}),
                    'query': query_metadata.get('q', '')
                })
            
            # Process People Also Ask
            related_questions = result.get('related_questions', [])
            for question in related_questions[:5]:
                processed['customer_insights'].append({
                    'type': 'related_question',
                    'question': question.get('question', ''),
                    'snippet': question.get('snippet', ''),
                    'query': query_metadata.get('q', '')
                })
        
        # Remove duplicates and sort by relevance
        for category in processed:
            processed[category] = self._deduplicate_results(processed[category])
        
        return processed
    
    async def _scrape_top_results(self, enriched_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape content from top search results for deeper analysis"""
        
        # Collect URLs from high-quality search results
        urls_to_scrape = set()
        
        # Get URLs from market data (most important)
        market_data = enriched_data.get('market_data', [])
        for item in market_data[:8]:  # Top 8 market data URLs
            if item.get('link') and item.get('relevance_score', 0) > 15:
                urls_to_scrape.add(item['link'])
        
        # Get URLs from industry trends
        trends = enriched_data.get('industry_trends', [])
        for item in trends[:5]:  # Top 5 trend URLs
            if item.get('link') and item.get('relevance_score', 0) > 10:
                urls_to_scrape.add(item['link'])
        
        # Get URLs from competitor analysis
        competitors = enriched_data.get('competitor_analysis', [])
        for item in competitors[:5]:  # Top 5 competitor URLs
            if item.get('link') and item.get('relevance_score', 0) > 10:
                urls_to_scrape.add(item['link'])
        
        # Convert to list and limit
        urls_list = list(urls_to_scrape)[:15]  # Max 15 URLs to scrape
        
        if not urls_list:
            return []
        
        try:
            # Scrape content from URLs
            scraped_results = await self.web_scraper.scrape_urls_parallel(urls_list, max_concurrent=3)
            
            # Filter high-quality content
            high_quality_content = self.web_scraper.filter_high_quality_content(
                scraped_results, min_quality=50.0, max_results=10
            )
            
            # Convert to dict format for consistency
            formatted_content = []
            for content in high_quality_content:
                formatted_content.append({
                    'url': content.url,
                    'title': content.title,
                    'content': content.content,
                    'content_length': content.text_length,
                    'quality_score': content.extraction_quality,
                    'metadata': content.metadata
                })
            
            return formatted_content
            
        except Exception as e:
            print(f"Web scraping failed: {str(e)}")
            return []
    
    def _extract_market_insights(self, enriched_data: Dict[str, Any], scraped_content: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract structured market insights from processed data"""
        
        # Combine search results with scraped content for enhanced analysis
        combined_data = enriched_data.copy()
        
        # Add scraped content insights
        scraped_insights = {}
        if scraped_content:
            scraped_insights = self._extract_scraped_insights(scraped_content)
            # Merge scraped insights with search data
            for category in ['market_data', 'customer_insights', 'competitor_analysis', 'industry_trends']:
                if category in combined_data and category in scraped_insights:
                    combined_data[category].extend(scraped_insights[category])
        
        insights = {
            'market_size': self._analyze_market_size(combined_data.get('market_data', [])),
            'growth_factors': self._extract_growth_factors(combined_data.get('industry_trends', [])),
            'customer_segments': self._analyze_customer_segments(combined_data.get('customer_insights', [])),
            'competitive_landscape': self._analyze_competitors(combined_data.get('competitor_analysis', [])),
            'key_opportunities': self._identify_opportunities(combined_data),
            'industry_challenges': self._extract_challenges(combined_data),
            'emerging_trends': self._extract_trends(combined_data.get('industry_trends', [])),
            'data_quality_score': self._calculate_data_quality(combined_data, scraped_content),
            'deep_content_analysis': scraped_insights.get('deep_analysis', {}) if scraped_content else {}
        }
        
        return insights
    
    def _extract_scraped_insights(self, scraped_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract insights from scraped webpage content"""
        
        insights = {
            'market_data': [],
            'customer_insights': [],
            'competitor_analysis': [],
            'industry_trends': [],
            'deep_analysis': {
                'total_content_analyzed': sum(c.get('content_length', 0) for c in scraped_content),
                'high_quality_pages': len([c for c in scraped_content if c.get('quality_score', 0) > 70]),
                'key_statistics': [],
                'detailed_insights': []
            }
        }
        
        for content_item in scraped_content:
            content_text = content_item.get('content', '')
            url = content_item.get('url', '')
            title = content_item.get('title', '')
            quality = content_item.get('quality_score', 0)
            
            if not content_text or quality < 50:
                continue
            
            # Extract detailed statistics from full content
            stats = self._extract_detailed_statistics(content_text)
            insights['deep_analysis']['key_statistics'].extend(stats)
            
            # Create insights based on content type
            content_metadata = content_item.get('metadata', {})
            article_type = content_metadata.get('article_type', 'general')
            
            # Enhanced insight extraction from full content
            insight_item = {
                'title': title,
                'url': url,
                'content_preview': content_text[:500] + "..." if len(content_text) > 500 else content_text,
                'quality_score': quality,
                'source_type': article_type,
                'key_points': self._extract_key_points(content_text),
                'statistics_found': len(stats)
            }
            
            # Categorize based on content analysis
            if any(keyword in content_text.lower() for keyword in 
                   ['market size', 'market value', 'industry revenue', 'tam', 'total addressable']):
                insights['market_data'].append(insight_item)
            
            if any(keyword in content_text.lower() for keyword in 
                   ['customer behavior', 'buyer preferences', 'user patterns', 'consumer trends']):
                insights['customer_insights'].append(insight_item)
            
            if any(keyword in content_text.lower() for keyword in 
                   ['competitor', 'market leader', 'competitive landscape', 'market share']):
                insights['competitor_analysis'].append(insight_item)
            
            if any(keyword in content_text.lower() for keyword in 
                   ['emerging trend', 'future outlook', 'innovation', 'technology adoption']):
                insights['industry_trends'].append(insight_item)
            
            # Add to detailed insights regardless of category
            insights['deep_analysis']['detailed_insights'].append({
                'source': url,
                'title': title,
                'key_insights': self._extract_key_sentences(content_text),
                'data_points': len(stats)
            })
        
        # Limit results
        for category in ['market_data', 'customer_insights', 'competitor_analysis', 'industry_trends']:
            insights[category] = insights[category][:10]
        
        insights['deep_analysis']['key_statistics'] = insights['deep_analysis']['key_statistics'][:20]
        insights['deep_analysis']['detailed_insights'] = insights['deep_analysis']['detailed_insights'][:15]
        
        return insights
    
    def _extract_detailed_statistics(self, text: str) -> List[Dict[str, Any]]:
        """Extract detailed statistics from full webpage content"""
        
        statistics = []
        
        # Enhanced patterns for full content analysis
        enhanced_patterns = [
            # Market size with context
            (r'(?:market|industry|sector).*?size.*?(?:was|is|valued|worth|reached).*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion|B|M|T)(?:\s+in\s+(\d{4}))?', 'market_size_detailed'),
            
            # Growth rates with timeframes
            (r'(?:grow|growth|increase|expanding).*?([\d,]+\.?\d*)\s*%.*?(?:annually|yearly|CAGR|compound|from\s+\d{4}\s+to\s+\d{4})', 'growth_rate_detailed'),
            
            # Projections and forecasts
            (r'(?:projected|expected|forecasted|anticipated).*?(?:to reach|to grow to|to be worth).*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion|B|M|T).*?(?:by|in)\s+(\d{4})', 'market_projection'),
            
            # Market share information
            (r'(?:market share|share of|holds|accounts for).*?([\d,]+\.?\d*)\s*%', 'market_share'),
            
            # User/customer statistics
            (r'(?:users|customers|subscribers|businesses).*?([\d,]+\.?\d*)\s*(?:million|billion|thousand|M|B|K)', 'user_statistics'),
            
            # Revenue figures
            (r'(?:revenue|sales|earnings).*?\$?([\d,]+\.?\d*)\s*(?:billion|million|thousand|B|M|K)(?:\s+in\s+(\d{4}))?', 'revenue_data'),
            
            # Adoption rates
            (r'(?:adoption|penetration|usage).*?(?:rate|of).*?([\d,]+\.?\d*)\s*%', 'adoption_rate'),
        ]
        
        for pattern, stat_type in enhanced_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches[:5]:  # Limit per pattern
                if isinstance(match, tuple):
                    value_parts = [part for part in match if part.strip()]
                    context_start = text.lower().find(str(match[0]).lower())
                    context = text[max(0, context_start-50):context_start+200] if context_start != -1 else ""
                else:
                    value_parts = [match]
                    context = ""
                
                statistics.append({
                    'type': stat_type,
                    'values': value_parts,
                    'context': context.strip(),
                    'confidence': self._calculate_stat_confidence(context, stat_type)
                })
        
        return statistics
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from content"""
        
        # Look for sentences with high information density
        sentences = re.split(r'[.!?]+', text)
        key_points = []
        
        # Patterns that indicate important information
        importance_indicators = [
            r'\b(?:key|important|significant|major|primary|main|critical)\b',
            r'\b(?:according to|research shows|study found|data indicates)\b',
            r'\b(?:million|billion|percent|growth|increase|decrease)\b',
            r'\b(?:trend|pattern|insight|finding|conclusion)\b'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 50 or len(sentence) > 300:
                continue
                
            # Score sentence based on importance indicators
            score = 0
            for pattern in importance_indicators:
                if re.search(pattern, sentence, re.IGNORECASE):
                    score += 1
            
            # Look for numbers and statistics
            if re.search(r'\d+(?:\.\d+)?%|\$[\d,]+|\d+\s*(?:million|billion)', sentence, re.IGNORECASE):
                score += 2
            
            if score >= 2:
                key_points.append(sentence)
        
        return key_points[:8]  # Top 8 key points
    
    def _extract_key_sentences(self, text: str) -> List[str]:
        """Extract key sentences with market insights"""
        
        sentences = re.split(r'[.!?]+', text)
        key_sentences = []
        
        # Patterns for market insight sentences
        insight_patterns = [
            r'market.*?(?:size|value|worth|revenue)',
            r'industry.*?(?:growth|trend|outlook|forecast)',
            r'customer.*?(?:behavior|preference|demand|need)',
            r'competitor.*?(?:analysis|landscape|positioning)',
            r'technology.*?(?:adoption|innovation|disruption)',
            r'business.*?(?:model|strategy|opportunity)'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 100 or len(sentence) > 400:
                continue
            
            for pattern in insight_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    key_sentences.append(sentence)
                    break
        
        return key_sentences[:10]  # Top 10 key sentences
    
    def _calculate_stat_confidence(self, context: str, stat_type: str) -> float:
        """Calculate confidence score for extracted statistics"""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on context quality
        quality_indicators = [
            'according to', 'research', 'study', 'report', 'analysis',
            'data shows', 'statistics', 'survey', 'published', 'official'
        ]
        
        for indicator in quality_indicators:
            if indicator in context.lower():
                confidence += 0.1
        
        # Boost confidence based on stat type
        high_confidence_types = ['market_size_detailed', 'growth_rate_detailed', 'market_projection']
        if stat_type in high_confidence_types:
            confidence += 0.2
        
        return min(1.0, confidence)
    
    def _extract_statistics(self, text: str) -> List[Dict[str, Any]]:
        """Extract numerical statistics and data points from text"""
        
        statistics = []
        
        # Patterns for different types of statistics
        patterns = [
            # Market size patterns
            (r'\$?([\d,]+\.?\d*)\s*(billion|million|trillion)', 'market_size'),
            (r'([\d,]+\.?\d*)\s*%\s*(growth|increase|decrease|CAGR)', 'growth_rate'),
            (r'([\d,]+)\s*(companies|customers|users|businesses)', 'count'),
            (r'by\s*(202\d|203\d)', 'projection_year'),
            # Percentage patterns
            (r'([\d,]+\.?\d*)\s*%\s*of\s*(\w+)', 'percentage_share'),
        ]
        
        for pattern, stat_type in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                statistics.append({
                    'type': stat_type,
                    'value': match,
                    'context': text[:100],
                    'raw_text': text
                })
        
        return statistics
    
    def _calculate_relevance(self, item: Dict[str, Any], query_metadata: Dict[str, Any]) -> float:
        """Calculate relevance score for search results"""
        
        score = 0.0
        query_terms = query_metadata.get('q', '').lower().split()
        
        title = item.get('title', '').lower()
        snippet = item.get('snippet', '').lower()
        
        # Title matches
        for term in query_terms:
            if term in title:
                score += 2.0
            if term in snippet:
                score += 1.0
        
        # Boost for authoritative sources
        trusted_domains = ['gartner.com', 'forrester.com', 'mckinsey.com', 'deloitte.com', 
                          'statista.com', 'idc.com', 'bloomberg.com', 'reuters.com']
        
        source = self._extract_domain(item.get('link', ''))
        if any(domain in source for domain in trusted_domains):
            score += 3.0
        
        # Recency boost
        if '2024' in snippet or '2025' in snippet:
            score += 2.0
        
        return score
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc.replace('www.', '')
        except:
            return ''
    
    def _categorize_query(self, query: str) -> str:
        """Categorize query by topic"""
        
        query_lower = query.lower()
        
        if any(term in query_lower for term in ['market size', 'tam', 'market value', 'billion', 'million']):
            return 'market_size'
        elif any(term in query_lower for term in ['customer', 'buyer', 'persona', 'segment', 'demographic']):
            return 'customer'
        elif any(term in query_lower for term in ['competitor', 'alternative', 'vs', 'comparison']):
            return 'competitor'
        elif any(term in query_lower for term in ['trend', 'future', 'emerging', 'technology']):
            return 'trends'
        else:
            return 'general'
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on content similarity"""
        
        seen = set()
        unique_results = []
        
        for result in results:
            # Create a content hash
            content = f"{result.get('title', '')}{result.get('snippet', '')}"
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_results.append(result)
        
        # Sort by relevance score if available
        unique_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return unique_results[:50]  # Keep top 50 results per category
    
    def _get_cache_key(self, query: Dict[str, Any]) -> str:
        """Generate cache key for query"""
        
        return f"{query['type']}_{hashlib.md5(query['q'].encode()).hexdigest()}"
    
    def _is_cache_valid(self, cached_item: Dict[str, Any]) -> bool:
        """Check if cached item is still valid"""
        
        return datetime.now() - cached_item['timestamp'] < self.cache_duration
    
    def _get_data_sources(self, results: List[Dict[str, Any]]) -> List[str]:
        """Extract unique data sources from results"""
        
        sources = set()
        
        for result in results:
            organic = result.get('organic', [])
            for item in organic:
                source = self._extract_domain(item.get('link', ''))
                if source:
                    sources.add(source)
        
        return list(sources)[:20]  # Top 20 sources
    
    def _analyze_market_size(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze and extract market size information"""
        
        market_values = []
        growth_rates = []
        projections = []
        
        for item in market_data:
            # Extract market values
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            
            # Enhanced pattern to capture more context
            market_patterns = [
                # Pattern with "market size" context
                r'(?:market size|market value|market worth|TAM|total addressable market).*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion|B|M)',
                # Pattern with "valued at" context
                r'(?:valued at|worth|reached|estimated at).*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion|B|M)',
                # Pattern with industry/sector context
                r'(?:industry|sector|market).*?(?:is|was|reached).*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion|B|M)'
            ]
            
            for pattern in market_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    value, unit = match
                    try:
                        numeric_value = float(value.replace(',', ''))
                    except (ValueError, TypeError):
                        continue  # Skip invalid values
                    
                    # Validate the market size is reasonable
                    normalized_value = self._normalize_market_value(value, unit)
                    
                    # Sanity check - recruitment tech shouldn't be trillions
                    if normalized_value > 5_000_000:  # > $5 trillion is suspicious
                        continue
                    
                    # Additional context validation
                    context_snippet = item.get('snippet', '')[:300].lower()
                    
                    # Dynamic relevance keywords based on industry
                    query_text = item.get('query', '').lower()
                    relevance_keywords = self._get_industry_keywords(query_text)
                    
                    # Check if the value is actually about the relevant industry
                    is_relevant = any(keyword in context_snippet for keyword in relevance_keywords)
                    
                    # If no relevance keywords found, check the query that found this
                    if not is_relevant and 'query' in item:
                        query_text = item.get('query', '').lower()
                        is_relevant = any(keyword in query_text for keyword in relevance_keywords)
                    
                    market_values.append({
                        'value': normalized_value,
                        'raw': f"${value} {unit}",
                        'source': item.get('source', ''),
                        'context': context_snippet,
                        'is_relevant': is_relevant,
                        'confidence': self._calculate_value_confidence(numeric_value, unit, context_snippet)
                    })
            
            # Look for growth rates
            growth_pattern = r'([\d,]+\.?\d*)\s*%\s*(CAGR|growth|increase)'
            growth_matches = re.findall(growth_pattern, text, re.IGNORECASE)
            
            for match in growth_matches:
                rate, type = match
                try:
                    rate_value = float(rate.replace(',', ''))
                except (ValueError, TypeError):
                    continue  # Skip invalid rates
                
                # Sanity check for growth rates
                if rate_value > 100:  # > 100% annual growth is suspicious
                    continue
                    
                growth_rates.append({
                    'rate': rate_value,
                    'type': type,
                    'source': item.get('source', ''),
                    'context': item.get('snippet', '')[:200]
                })
        
        # Filter and prioritize relevant market values
        relevant_values = [v for v in market_values if v.get('is_relevant', False)]
        if not relevant_values:
            # If no relevant values found, use all but with lower confidence
            relevant_values = market_values
        
        # Sort by confidence and value
        relevant_values.sort(key=lambda x: (x.get('confidence', 0), x['value']), reverse=True)
        
        # Calculate consensus values with preference for smaller, more realistic values
        if relevant_values:
            # For market size, prefer values in reasonable range
            reasonable_values = [v for v in relevant_values if 10 <= v['value'] <= 100_000]  # $10M to $100B
            
            if reasonable_values:
                # Use median of reasonable values
                median_value = reasonable_values[len(reasonable_values)//2]['value']
            else:
                # Fall back to smallest value if all seem too large
                median_value = min(relevant_values, key=lambda x: x['value'])['value']
        else:
            median_value = None
        
        if growth_rates:
            # Filter out extreme growth rates
            reasonable_growth = [g for g in growth_rates if 0 < g['rate'] <= 50]
            if reasonable_growth:
                avg_growth = sum(g['rate'] for g in reasonable_growth) / len(reasonable_growth)
            else:
                avg_growth = sum(g['rate'] for g in growth_rates) / len(growth_rates)
        else:
            avg_growth = None
        
        return {
            'current_market_size': median_value,
            'market_values_found': relevant_values[:5],  # Top 5 values
            'growth_rate': avg_growth,
            'growth_rates_found': growth_rates[:5],
            'data_points': len(market_values) + len(growth_rates),
            'confidence_level': self._assess_market_data_confidence(relevant_values, growth_rates)
        }
    
    def _calculate_value_confidence(self, numeric_value: float, unit: str, context: str) -> float:
        """Calculate confidence score for a market value"""
        
        confidence = 0.5  # Base confidence
        
        # Check for specific market size indicators in context
        if any(term in context for term in ['market size', 'market value', 'TAM', 'total addressable']):
            confidence += 0.2
        
        # Check for year mentions (more recent = higher confidence)
        import re
        year_matches = re.findall(r'20[2-9]\d', context)
        if year_matches:
            latest_year = max(int(year) for year in year_matches)
            if latest_year >= 2023:
                confidence += 0.15
            elif latest_year >= 2021:
                confidence += 0.1
        
        # Reasonable value ranges get higher confidence
        unit_lower = unit.lower()
        if unit_lower in ['billion', 'b']:
            if 0.1 <= numeric_value <= 100:  # $100M to $100B is reasonable for most tech markets
                confidence += 0.15
        elif unit_lower in ['million', 'm']:
            if 100 <= numeric_value <= 10000:  # $100M to $10B
                confidence += 0.15
        
        return min(1.0, confidence)
    
    def _assess_market_data_confidence(self, market_values: List[Dict], growth_rates: List[Dict]) -> str:
        """Assess overall confidence in market data"""
        
        if not market_values:
            return "Low"
        
        avg_confidence = sum(v.get('confidence', 0) for v in market_values[:3]) / min(3, len(market_values))
        relevant_count = sum(1 for v in market_values if v.get('is_relevant', False))
        
        if avg_confidence >= 0.7 and relevant_count >= 2:
            return "High"
        elif avg_confidence >= 0.5 or relevant_count >= 1:
            return "Medium"
        else:
            return "Low"
    
    def _normalize_market_value(self, value: str, unit: str) -> float:
        """Normalize market values to millions"""
        
        try:
            numeric_value = float(value.replace(',', ''))
        except (ValueError, TypeError):
            return 0.0  # Return 0 for invalid values
        
        unit_lower = unit.lower()
        if unit_lower in ['trillion', 't']:
            return numeric_value * 1_000_000
        elif unit_lower in ['billion', 'b']:
            return numeric_value * 1_000
        elif unit_lower in ['million', 'm']:
            return numeric_value
        else:
            # If no unit specified, try to infer from value magnitude
            if numeric_value > 1000:
                return numeric_value / 1_000  # Assume thousands, convert to millions
            else:
                return numeric_value  # Assume already in millions
    
    def _get_industry_keywords(self, query_text: str) -> List[str]:
        """Get relevant keywords based on the industry being searched"""
        
        query_lower = query_text.lower()
        
        # Common industry keyword mappings
        industry_keywords = {
            'recruitment': ['recruitment', 'recruiting', 'hiring', 'hr tech', 'talent', 'staffing', 'human resource', 'applicant tracking', 'ats'],
            'saas': ['saas', 'software as a service', 'cloud software', 'subscription software', 'enterprise software'],
            'fintech': ['fintech', 'financial technology', 'payment', 'banking', 'lending', 'insurance tech', 'insurtech'],
            'healthcare': ['healthcare', 'health tech', 'medical', 'hospital', 'clinical', 'patient', 'telemedicine', 'digital health'],
            'ecommerce': ['ecommerce', 'e-commerce', 'online retail', 'marketplace', 'online shopping', 'digital commerce'],
            'edtech': ['edtech', 'education technology', 'learning', 'training', 'online education', 'e-learning'],
            'martech': ['martech', 'marketing technology', 'advertising', 'marketing automation', 'crm', 'customer data'],
            'proptech': ['proptech', 'property technology', 'real estate tech', 'property management', 'realestate'],
            'agtech': ['agtech', 'agriculture technology', 'farming', 'agricultural', 'agritech'],
            'logistics': ['logistics', 'supply chain', 'shipping', 'freight', 'delivery', 'transportation tech'],
            'cybersecurity': ['cybersecurity', 'security software', 'data protection', 'network security', 'infosec'],
            'ai': ['artificial intelligence', 'machine learning', 'deep learning', 'ai platform', 'ml ops'],
            'blockchain': ['blockchain', 'crypto', 'cryptocurrency', 'defi', 'web3', 'distributed ledger'],
            'iot': ['iot', 'internet of things', 'connected devices', 'smart home', 'industrial iot', 'sensors']
        }
        
        # Find matching industry
        for industry, keywords in industry_keywords.items():
            if any(keyword in query_lower for keyword in keywords[:3]):  # Check first few keywords
                return keywords
        
        # If no specific industry match, extract potential keywords from query
        # This handles cases where the industry name is directly in the query
        words = query_lower.split()
        potential_keywords = []
        
        # Look for industry/market/tech patterns
        for i, word in enumerate(words):
            if word in ['industry', 'market', 'tech', 'technology', 'software', 'platform']:
                # Get the word before if it exists
                if i > 0:
                    potential_keywords.append(words[i-1])
                    potential_keywords.append(f"{words[i-1]} {word}")
            
            # Also include significant words (length > 4, not common words)
            if len(word) > 4 and word not in ['market', 'size', 'trends', 'analysis', 'growth']:
                potential_keywords.append(word)
        
        # If we found potential keywords, use them
        if potential_keywords:
            return potential_keywords[:5]
        
        # Fallback: extract the most significant words from the query
        significant_words = [w for w in words if len(w) > 3 and w not in 
                            ['market', 'size', 'trends', 'analysis', 'growth', 'total', 'addressable']]
        
        return significant_words[:5] if significant_words else ['technology', 'software']
    
    def _extract_growth_factors(self, trends_data: List[Dict[str, Any]]) -> List[str]:
        """Extract key growth factors from trends data"""
        
        growth_factors = []
        factor_keywords = [
            'driving growth', 'growth driver', 'key factor', 'contributing to',
            'fueling', 'accelerating', 'enabling', 'adoption of', 'demand for'
        ]
        
        for item in trends_data:
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            
            for keyword in factor_keywords:
                if keyword in text.lower():
                    # Extract the sentence containing the keyword
                    sentences = text.split('.')
                    for sentence in sentences:
                        if keyword in sentence.lower():
                            growth_factors.append(sentence.strip())
                            break
        
        # Remove duplicates and return top factors
        unique_factors = list(set(growth_factors))
        return unique_factors[:10]
    
    def _analyze_customer_segments(self, customer_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Analyze and extract customer segment information"""
        
        segments = defaultdict(list)
        segment_keywords = {
            'enterprise': ['enterprise', 'large company', 'fortune 500', 'corporate'],
            'smb': ['smb', 'small business', 'medium business', 'small and medium'],
            'startup': ['startup', 'early stage', 'new business'],
            'government': ['government', 'public sector', 'federal', 'state'],
            'healthcare': ['healthcare', 'hospital', 'medical', 'clinic'],
            'retail': ['retail', 'e-commerce', 'online store', 'merchant'],
            'financial': ['financial', 'bank', 'fintech', 'insurance']
        }
        
        for item in customer_data:
            text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            
            for segment, keywords in segment_keywords.items():
                if any(keyword in text for keyword in keywords):
                    segments[segment].append({
                        'description': item.get('snippet', ''),
                        'source': item.get('source', '')
                    })
        
        # Format segments
        formatted_segments = []
        for segment, mentions in segments.items():
            if mentions:
                formatted_segments.append({
                    'name': segment.title(),
                    'mentions': len(mentions),
                    'insights': mentions[:3]  # Top 3 insights per segment
                })
        
        return sorted(formatted_segments, key=lambda x: x['mentions'], reverse=True)
    
    def _analyze_competitors(self, competitor_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze competitor landscape"""
        
        competitors = defaultdict(lambda: {'mentions': 0, 'contexts': []})
        
        # Common competitor indicators
        competitor_patterns = [
            r'competitors?\s+include\s+([^,\.\n]+(?:,\s*[^,\.\n]+)*)',
            r'([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+competes',
            r'alternatives?\s+to\s+\w+\s+include\s+([^,\.\n]+(?:,\s*[^,\.\n]+)*)',
            r'market\s+leaders?\s+(?:include\s+)?([^,\.\n]+(?:,\s*[^,\.\n]+)*)'
        ]
        
        for item in competitor_data:
            text = f"{item.get('title', '')} {item.get('snippet', '')}"
            
            for pattern in competitor_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    # Extract individual company names
                    companies = re.split(r',\s*|\s+and\s+', match)
                    for company in companies:
                        company = company.strip()
                        if len(company) > 2 and len(company) < 50:
                            competitors[company]['mentions'] += 1
                            competitors[company]['contexts'].append(item.get('snippet', '')[:200])
        
        # Sort by mentions
        top_competitors = sorted(
            competitors.items(),
            key=lambda x: x[1]['mentions'],
            reverse=True
        )[:20]
        
        return {
            'top_competitors': [
                {
                    'name': name,
                    'mentions': data['mentions'],
                    'contexts': data['contexts'][:2]
                }
                for name, data in top_competitors
            ],
            'total_competitors_found': len(competitors)
        }
    
    def _identify_opportunities(self, enriched_data: Dict[str, Any]) -> List[str]:
        """Identify market opportunities from all data"""
        
        opportunities = []
        opportunity_keywords = [
            'opportunity', 'gap in the market', 'unmet need', 'underserved',
            'potential for', 'room for improvement', 'lacking', 'demand for'
        ]
        
        # Search across all categories
        all_items = []
        for category, items in enriched_data.items():
            if isinstance(items, list):
                all_items.extend(items)
        
        for item in all_items:
            if isinstance(item, dict):
                text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
                
                for keyword in opportunity_keywords:
                    if keyword in text:
                        # Extract surrounding context
                        index = text.find(keyword)
                        start = max(0, index - 100)
                        end = min(len(text), index + 200)
                        opportunity = text[start:end].strip()
                        
                        if opportunity and len(opportunity) > 50:
                            opportunities.append(opportunity)
        
        # Remove duplicates and return top opportunities
        unique_opportunities = list(set(opportunities))
        return unique_opportunities[:10]
    
    def _extract_challenges(self, enriched_data: Dict[str, Any]) -> List[str]:
        """Extract industry challenges and pain points"""
        
        challenges = []
        challenge_keywords = [
            'challenge', 'problem', 'pain point', 'struggle', 'difficulty',
            'barrier', 'obstacle', 'issue', 'concern', 'limitation'
        ]
        
        # Search across relevant categories
        relevant_categories = ['industry_trends', 'customer_insights', 'market_data']
        
        for category in relevant_categories:
            items = enriched_data.get(category, [])
            for item in items:
                if isinstance(item, dict):
                    text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
                    
                    for keyword in challenge_keywords:
                        if keyword in text:
                            # Extract sentence containing the keyword
                            sentences = text.split('.')
                            for sentence in sentences:
                                if keyword in sentence and len(sentence) > 30:
                                    challenges.append(sentence.strip())
                                    break
        
        # Remove duplicates and return top challenges
        unique_challenges = list(set(challenges))
        return unique_challenges[:10]
    
    def _extract_trends(self, trends_data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract and categorize emerging trends"""
        
        trends = defaultdict(list)
        trend_categories = {
            'technology': ['ai', 'automation', 'digital', 'cloud', 'iot', 'blockchain'],
            'market': ['consolidation', 'fragmentation', 'globalization', 'localization'],
            'customer': ['personalization', 'experience', 'self-service', 'omnichannel'],
            'business': ['subscription', 'saas', 'platform', 'marketplace', 'ecosystem']
        }
        
        for item in trends_data:
            text = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
            
            for category, keywords in trend_categories.items():
                for keyword in keywords:
                    if keyword in text:
                        trends[category].append({
                            'trend': keyword,
                            'context': item.get('snippet', '')[:200],
                            'source': item.get('source', '')
                        })
        
        # Format trends
        formatted_trends = []
        for category, trend_list in trends.items():
            if trend_list:
                formatted_trends.append({
                    'category': category.title(),
                    'trends': trend_list[:5],  # Top 5 per category
                    'strength': len(trend_list)
                })
        
        return sorted(formatted_trends, key=lambda x: x['strength'], reverse=True)
    
    def _calculate_data_quality(self, enriched_data: Dict[str, Any], scraped_content: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        
        total_items = 0
        authoritative_sources = 0
        recent_data = 0
        
        trusted_domains = ['gartner.com', 'forrester.com', 'mckinsey.com', 'deloitte.com',
                          'statista.com', 'idc.com', 'bloomberg.com', 'reuters.com',
                          'techcrunch.com', 'forbes.com', 'businesswire.com']
        
        for category, items in enriched_data.items():
            if isinstance(items, list):
                total_items += len(items)
                
                for item in items:
                    if isinstance(item, dict):
                        source = item.get('source', '')
                        if any(domain in source for domain in trusted_domains):
                            authoritative_sources += 1
                        
                        text = f"{item.get('title', '')} {item.get('snippet', '')}"
                        if '2024' in text or '2025' in text:
                            recent_data += 1
        
        # Add scraped content metrics
        scraped_quality_boost = 0
        deep_content_length = 0
        high_quality_pages = 0
        
        if scraped_content:
            deep_content_length = sum(c.get('content_length', 0) for c in scraped_content)
            high_quality_pages = len([c for c in scraped_content if c.get('quality_score', 0) > 70])
            
            # Boost quality score based on scraped content
            if deep_content_length > 50000:  # Substantial content analyzed
                scraped_quality_boost += 20
            elif deep_content_length > 20000:
                scraped_quality_boost += 15
            elif deep_content_length > 10000:
                scraped_quality_boost += 10
            
            if high_quality_pages > 5:
                scraped_quality_boost += 15
            elif high_quality_pages > 2:
                scraped_quality_boost += 10
        
        quality_score = 0
        if total_items > 0:
            authority_ratio = authoritative_sources / total_items
            recency_ratio = recent_data / total_items
            coverage_score = min(1.0, total_items / 100)  # Normalize to 100 items
            
            base_score = (authority_ratio * 0.4 + recency_ratio * 0.4 + coverage_score * 0.2) * 100
            quality_score = min(100, base_score + scraped_quality_boost)
        
        # Determine enhanced data coverage
        coverage_level = 'Limited'
        if scraped_content and len(scraped_content) > 5 and total_items > 100:
            coverage_level = 'Comprehensive+'
        elif scraped_content and len(scraped_content) > 2 and total_items > 50:
            coverage_level = 'Enhanced'
        elif total_items > 100:
            coverage_level = 'Comprehensive'
        elif total_items > 50:
            coverage_level = 'Good'
        
        return {
            'overall_score': round(quality_score, 1),
            'total_data_points': total_items,
            'authoritative_sources': authoritative_sources,
            'recent_data_points': recent_data,
            'scraped_pages': len(scraped_content) if scraped_content else 0,
            'deep_content_length': deep_content_length,
            'high_quality_pages': high_quality_pages,
            'data_coverage': coverage_level,
            'enhancement_boost': scraped_quality_boost
        }
    
    # ===== ENHANCED SOURCE TRACKING METHODS =====
    
    def _create_data_source_from_result(self, result: Dict[str, Any], query_context: str = "") -> DataSource:
        """Create comprehensive DataSource object from search result"""
        
        self.source_id_counter += 1
        url = result.get('link', '')
        title = result.get('title', 'Untitled')
        snippet = result.get('snippet', '')
        
        # Parse domain and determine source quality
        domain = urlparse(url).netloc.lower() if url else ''
        source_quality = self._determine_source_quality(domain, title, snippet)
        content_type = self._determine_content_type(url, title, snippet)
        
        # Extract publication date if available
        publication_date = self._extract_publication_date(result)
        
        # Calculate confidence and relevance scores
        confidence_score = self._calculate_confidence_score(result, query_context)
        relevance_score = self._calculate_relevance_score(result, query_context)
        
        # Determine domain authority (simplified scoring)
        domain_authority = self._get_domain_authority(domain)
        
        # Extract organization/author info
        author, organization = self._extract_author_info(result, domain)
        
        source = DataSource(
            url=url,
            title=title,
            author=author,
            organization=organization,
            publication_date=publication_date,
            domain_authority=domain_authority,
            content_type=content_type,
            source_quality=source_quality,
            confidence_score=confidence_score,
            relevance_score=relevance_score,
            data_quality_rating=self._calculate_data_quality_rating(result, domain),
            country_focus=self._detect_country_focus(snippet, title)
        )
        
        # Add to master source list
        self.all_sources.append(source)
        
        return source
    
    def _determine_source_quality(self, domain: str, title: str, snippet: str) -> SourceQuality:
        """Determine source quality tier based on domain and content"""
        
        # Tier 1: Academic, Government, Major Research Firms
        tier_1_domains = [
            'edu', 'gov', 'gartner.com', 'mckinsey.com', 'bcg.com', 'bain.com',
            'deloitte.com', 'pwc.com', 'kpmg.com', 'ey.com', 'forrester.com',
            'idc.com', 'statista.com', 'census.gov', 'oecd.org', 'worldbank.org',
            'imf.org', 'scholar.google.com', 'researchgate.net', 'nature.com',
            'science.org', 'ieee.org', 'acm.org'
        ]
        
        # Tier 2: Industry Reports, Major Publications
        tier_2_domains = [
            'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com', 'economist.com',
            'hbr.org', 'mit.edu', 'stanford.edu', 'harvard.edu', 'techcrunch.com',
            'venturebeat.com', 'crunchbase.com', 'pitchbook.com', 'cbinsights.com',
            'grandviewresearch.com', 'marketsandmarkets.com', 'mordorintelligence.com'
        ]
        
        # Tier 3: Company Blogs, Trade Publications
        tier_3_domains = [
            'medium.com', 'linkedin.com', 'inc.com', 'entrepreneur.com',
            'fastcompany.com', 'wired.com', 'zdnet.com', 'computerworld.com'
        ]
        
        # Check domain quality
        for domain_check in tier_1_domains:
            if domain_check in domain:
                return SourceQuality.TIER_1
        
        for domain_check in tier_2_domains:
            if domain_check in domain:
                return SourceQuality.TIER_2
        
        for domain_check in tier_3_domains:
            if domain_check in domain:
                return SourceQuality.TIER_3
        
        # Check content indicators
        academic_indicators = ['research', 'study', 'analysis', 'report', 'whitepaper']
        if any(indicator in title.lower() or indicator in snippet.lower() 
               for indicator in academic_indicators):
            return SourceQuality.TIER_3
        
        return SourceQuality.TIER_4
    
    def _determine_content_type(self, url: str, title: str, snippet: str) -> ContentType:
        """Determine content type based on URL and content indicators"""
        
        title_lower = title.lower()
        snippet_lower = snippet.lower()
        url_lower = url.lower() if url else ''
        
        # Check for academic papers
        if any(indicator in title_lower for indicator in ['study', 'research', 'analysis']):
            if any(domain in url_lower for domain in ['.edu', 'scholar', 'researchgate']):
                return ContentType.ACADEMIC_PAPER
        
        # Check for industry reports
        if any(indicator in title_lower for indicator in ['report', 'market size', 'industry analysis']):
            return ContentType.INDUSTRY_REPORT
        
        # Check for financial reports
        if any(indicator in title_lower for indicator in ['earnings', 'financial', 'quarterly', 'annual report']):
            return ContentType.FINANCIAL_REPORT
        
        # Check for white papers
        if 'whitepaper' in title_lower or 'white paper' in title_lower:
            return ContentType.WHITE_PAPER
        
        # Check for press releases
        if any(indicator in title_lower for indicator in ['announces', 'press release', 'launches']):
            return ContentType.PRESS_RELEASE
        
        # Check for government data
        if '.gov' in url_lower or 'government' in title_lower:
            return ContentType.GOVERNMENT_DATA
        
        # Check for conference presentations
        if any(indicator in title_lower for indicator in ['conference', 'presentation', 'summit']):
            return ContentType.CONFERENCE_PRESENTATION
        
        return ContentType.NEWS_ARTICLE
    
    def _extract_publication_date(self, result: Dict[str, Any]) -> Optional[datetime]:
        """Extract publication date from search result"""
        
        # Check for date in result metadata
        if 'date' in result:
            try:
                return datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
            except:
                pass
        
        # Try to extract from snippet or title
        date_patterns = [
            r'(\d{4})',  # Just year
            r'(\w+ \d{1,2}, \d{4})',  # Month Day, Year
            r'(\d{1,2}/\d{1,2}/\d{4})',  # MM/DD/YYYY
        ]
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    # Simple year extraction
                    year_match = re.search(r'(\d{4})', matches[0])
                    if year_match:
                        year = int(year_match.group(1))
                        if 2000 <= year <= datetime.now().year:
                            return datetime(year, 1, 1)
                except:
                    continue
        
        return None
    
    def _calculate_confidence_score(self, result: Dict[str, Any], query_context: str) -> float:
        """Calculate confidence score for search result"""
        
        score = 0.5  # Base score
        
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Boost for authoritative sources
        domain = urlparse(result.get('link', '')).netloc.lower()
        if any(auth_domain in domain for auth_domain in ['edu', 'gov', 'gartner', 'mckinsey']):
            score += 0.3
        
        # Boost for recent content
        if any(recent_indicator in title + snippet 
               for recent_indicator in ['2024', '2025', 'recent', 'latest']):
            score += 0.2
        
        # Boost for specific metrics
        if any(metric in title + snippet 
               for metric in ['billion', 'million', 'market size', 'growth rate']):
            score += 0.2
        
        return min(1.0, score)
    
    def _calculate_relevance_score(self, result: Dict[str, Any], query_context: str) -> float:
        """Calculate relevance score for search result"""
        
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        text = title + ' ' + snippet
        
        # Extract key terms from query context
        query_terms = query_context.lower().split()
        
        # Calculate term overlap
        matches = sum(1 for term in query_terms if term in text)
        relevance = matches / len(query_terms) if query_terms else 0.5
        
        return min(1.0, relevance)
    
    def _get_domain_authority(self, domain: str) -> int:
        """Get simplified domain authority score (0-100)"""
        
        # High authority domains
        high_authority = {
            'edu': 90, 'gov': 95, 'gartner.com': 85, 'mckinsey.com': 90,
            'bloomberg.com': 85, 'reuters.com': 85, 'wsj.com': 85,
            'techcrunch.com': 75, 'crunchbase.com': 80
        }
        
        for auth_domain, score in high_authority.items():
            if auth_domain in domain:
                return score
        
        # Medium authority for common business sites
        if any(indicator in domain for indicator in ['research', 'report', 'news']):
            return 60
        
        return 40  # Default score
    
    def _extract_author_info(self, result: Dict[str, Any], domain: str) -> tuple:
        """Extract author and organization information"""
        
        # Try to extract organization from domain
        domain_parts = domain.split('.')
        if len(domain_parts) >= 2:
            organization = domain_parts[-2].title()
        else:
            organization = domain
        
        # Common organization mappings
        org_mappings = {
            'gartner': 'Gartner, Inc.',
            'mckinsey': 'McKinsey & Company',
            'bloomberg': 'Bloomberg L.P.',
            'reuters': 'Thomson Reuters',
            'techcrunch': 'TechCrunch'
        }
        
        for key, mapped_org in org_mappings.items():
            if key in domain:
                organization = mapped_org
                break
        
        return None, organization  # Author typically not available in search results
    
    def _calculate_data_quality_rating(self, result: Dict[str, Any], domain: str) -> float:
        """Calculate overall data quality rating"""
        
        quality_factors = []
        
        # Domain credibility
        if any(cred_domain in domain for cred_domain in ['edu', 'gov', 'gartner']):
            quality_factors.append(0.9)
        elif any(cred_domain in domain for cred_domain in ['bloomberg', 'reuters']):
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.6)
        
        # Content depth (based on snippet length)
        snippet_length = len(result.get('snippet', ''))
        if snippet_length > 200:
            quality_factors.append(0.8)
        elif snippet_length > 100:
            quality_factors.append(0.7)
        else:
            quality_factors.append(0.5)
        
        # Data specificity
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        if any(metric in text for metric in ['$', '%', 'billion', 'million']):
            quality_factors.append(0.8)
        else:
            quality_factors.append(0.6)
        
        return sum(quality_factors) / len(quality_factors)
    
    def _detect_country_focus(self, snippet: str, title: str) -> Optional[str]:
        """Detect geographic focus from content"""
        
        text = f"{title} {snippet}".lower()
        
        # Country indicators
        countries = [
            'united states', 'usa', 'america', 'china', 'india', 'germany',
            'japan', 'united kingdom', 'uk', 'france', 'canada', 'australia'
        ]
        
        for country in countries:
            if country in text:
                return country.title()
        
        # Regional indicators
        regions = ['europe', 'asia', 'north america', 'global', 'worldwide']
        for region in regions:
            if region in text:
                return region.title()
        
        return None
    
    def _create_research_bibliography(self) -> Dict[str, Any]:
        """Create comprehensive research bibliography"""
        
        # Group sources by quality tier
        sources_by_tier = {}
        sources_by_type = {}
        
        for source in self.all_sources:
            tier = source.source_quality.value
            content_type = source.content_type.value
            
            if tier not in sources_by_tier:
                sources_by_tier[tier] = []
            sources_by_tier[tier].append(source)
            
            if content_type not in sources_by_type:
                sources_by_type[content_type] = []
            sources_by_type[content_type].append(source)
        
        # Calculate bibliography statistics
        unique_domains = len(set(urlparse(s.url).netloc for s in self.all_sources if s.url))
        avg_quality = sum(s.data_quality_rating for s in self.all_sources) / len(self.all_sources) if self.all_sources else 0
        
        # Get publication date range
        dates = [s.publication_date for s in self.all_sources if s.publication_date]
        date_range = None
        if dates:
            min_date = min(dates)
            max_date = max(dates)
            date_range = f"{min_date.year}-{max_date.year}"
        
        return {
            'sources_by_tier': sources_by_tier,
            'sources_by_type': sources_by_type,
            'total_sources': len(self.all_sources),
            'unique_domains': unique_domains,
            'average_source_quality': round(avg_quality, 2),
            'publication_date_range': date_range,
            'apa_citations': [source.get_citation_text() for source in self.all_sources]
        }
    
    def _get_source_quality_summary(self) -> Dict[str, int]:
        """Get summary of source quality distribution"""
        
        quality_counts = {}
        for source in self.all_sources:
            quality = source.source_quality.value
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        return quality_counts
    
    def create_market_data_point(self, value: str, metric_type: str, 
                                 sources: List[DataSource], 
                                 currency: str = "USD",
                                 time_period: str = None,
                                 geographic_scope: str = None) -> MarketDataPoint:
        """Create a MarketDataPoint with comprehensive source attribution"""
        
        # Create citations for the sources
        citations = []
        for i, source in enumerate(sources):
            citation = Citation(
                source_id=f"source_{self.source_id_counter + i}",
                verification_status="verified" if source.source_quality in [SourceQuality.TIER_1, SourceQuality.TIER_2] else "unverified",
                confidence_level="high" if source.confidence_score > 0.7 else "medium" if source.confidence_score > 0.4 else "low"
            )
            citations.append(citation)
        
        # Calculate cross-validation
        cross_validated = len(sources) >= 2
        
        # Calculate overall confidence
        avg_confidence = sum(s.confidence_score for s in sources) / len(sources) if sources else 0.0
        
        return MarketDataPoint(
            value=value,
            metric_type=metric_type,
            currency=currency,
            time_period=time_period,
            geographic_scope=geographic_scope,
            sources=sources,
            citations=citations,
            confidence_score=avg_confidence,
            cross_validated=cross_validated
        )
    
    def _generate_fallback_response(self, company_name: str, industry: str, business_model: str) -> Dict[str, Any]:
        """Generate a fallback response when API key is not available"""
        return {
            'search_metadata': {
                'total_queries': 0,
                'data_sources': [],
                'scraped_pages': 0,
                'search_note': 'Limited search capabilities - API key not provided'
            },
            'market_insights': {
                'market_size': {
                    'current_market_size': 0,
                    'confidence_level': 'Low - No search data available'
                },
                'data_quality_score': {
                    'overall_score': 0,
                    'total_data_points': 0,
                    'authoritative_sources': 0,
                    'recent_data_points': 0,
                    'deep_content_length': 0
                }
            }
        }
    
    async def search_web(self, query: str, max_results: int = 5) -> str:
        """Simple search method for compatibility with enhanced questionnaire service"""
        if not self.api_key:
            return f"Search query: {query} (No search results - API key not available)"
        
        # Use the existing search infrastructure
        try:
            async with aiohttp.ClientSession() as session:
                search_query = {"text": query, "priority": "medium", "type": "general"}
                result = await self._search_serper(session, search_query)
                
                # Extract relevant information from results
                if result and "organic" in result:
                    search_results = []
                    for item in result["organic"][:max_results]:
                        search_results.append(f"Title: {item.get('title', '')}\nSnippet: {item.get('snippet', '')}\n")
                    return "\n".join(search_results)
                else:
                    return f"Search query: {query} (No results found)"
        except Exception as e:
            return f"Search query: {query} (Search failed: {str(e)})"