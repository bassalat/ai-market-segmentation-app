import requests
from typing import List, Dict
from bs4 import BeautifulSoup
import time

class SearchService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search_market_data(self, company_name: str, industry: str, business_model: str) -> str:
        """Search for market data and trends relevant to the business"""
        search_queries = [
            f"{industry} market size trends 2024",
            f"{industry} customer segments analysis",
            f"{company_name} competitors market analysis",
            f"{business_model} {industry} buying behavior",
            f"{industry} customer pain points challenges"
        ]
        
        results = []
        for query in search_queries[:3]:  # Limit to first 3 queries to avoid rate limits
            try:
                search_result = self._perform_search(query)
                if search_result:
                    results.append(f"Query: {query}\nResults: {search_result}\n")
                time.sleep(1)  # Rate limiting
            except Exception as e:
                results.append(f"Query: {query}\nError: Could not retrieve data\n")
        
        return "\n".join(results) if results else "No market data retrieved"
    
    def _perform_search(self, query: str) -> str:
        """Perform a web search using DuckDuckGo (as a fallback)"""
        try:
            # Using DuckDuckGo instant answer API as a simple alternative
            url = "https://api.duckduckgo.com/"
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant information
                abstract = data.get('Abstract', '')
                related_topics = [topic.get('Text', '') for topic in data.get('RelatedTopics', [])[:3]]
                
                result = []
                if abstract:
                    result.append(f"Summary: {abstract}")
                
                if related_topics:
                    result.append(f"Related insights: {'; '.join(related_topics)}")
                
                return " | ".join(result) if result else "No specific data found"
            
            return "Search unavailable"
            
        except Exception as e:
            return f"Search error: {str(e)}"
    
    def search_competitor_analysis(self, industry: str, company_size: str = "") -> str:
        """Search for competitor information in the industry"""
        query = f"{industry} leading companies competitors market share"
        if company_size:
            query += f" {company_size}"
        
        return self._perform_search(query)
    
    def search_customer_insights(self, industry: str, business_model: str) -> str:
        """Search for customer behavior and preferences in the industry"""
        query = f"{business_model} {industry} customer behavior preferences buying patterns"
        return self._perform_search(query)