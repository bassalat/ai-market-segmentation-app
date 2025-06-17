import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import re
import time
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass

@dataclass
class ScrapedContent:
    url: str
    title: str
    content: str
    text_length: int
    extraction_quality: float
    metadata: Dict[str, Any]

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session_timeout = 30
        self.max_content_length = 1_000_000  # 1MB limit
        
    async def scrape_urls_parallel(self, urls: List[str], max_concurrent: int = 5) -> List[ScrapedContent]:
        """Scrape multiple URLs in parallel with rate limiting"""
        
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url: str) -> Optional[ScrapedContent]:
            async with semaphore:
                try:
                    return await self.scrape_single_url(url)
                except Exception as e:
                    print(f"Failed to scrape {url}: {str(e)}")
                    return None
        
        # Create tasks for all URLs
        tasks = [scrape_with_semaphore(url) for url in urls]
        
        # Execute with progress tracking
        results = []
        completed_tasks = 0
        
        for coro in asyncio.as_completed(tasks):
            result = await coro
            completed_tasks += 1
            
            if result:
                results.append(result)
            
            # Rate limiting - small delay between completions
            if completed_tasks < len(tasks):
                await asyncio.sleep(0.1)
        
        return results
    
    async def scrape_single_url(self, url: str) -> Optional[ScrapedContent]:
        """Scrape content from a single URL"""
        
        if not self._is_scrapable_url(url):
            return None
        
        try:
            async with aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.session_timeout)
            ) as session:
                async with session.get(url) as response:
                    # Check response status
                    if response.status != 200:
                        return None
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '').lower()
                    if 'text/html' not in content_type:
                        return None
                    
                    # Check content length
                    content_length = response.headers.get('content-length')
                    if content_length and int(content_length) > self.max_content_length:
                        return None
                    
                    # Read content
                    html_content = await response.text()
                    
                    # Parse and extract content
                    return self._extract_content(url, html_content)
                    
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _is_scrapable_url(self, url: str) -> bool:
        """Check if URL is suitable for scraping"""
        
        try:
            parsed = urlparse(url)
            
            # Must have valid scheme and netloc
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Block certain file types
            blocked_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
                                '.zip', '.rar', '.tar', '.gz', '.mp4', '.mp3', '.jpg', '.png', '.gif']
            
            if any(url.lower().endswith(ext) for ext in blocked_extensions):
                return False
            
            # Block certain domains (social media, etc.)
            blocked_domains = ['twitter.com', 'facebook.com', 'instagram.com', 'tiktok.com',
                              'youtube.com', 'linkedin.com', 'reddit.com']
            
            if any(domain in parsed.netloc.lower() for domain in blocked_domains):
                return False
            
            return True
            
        except Exception:
            return False
    
    def _extract_content(self, url: str, html_content: str) -> ScrapedContent:
        """Extract meaningful content from HTML"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 
                           'aside', 'advertisement', 'ads', 'cookie']):
            element.decompose()
        
        # Extract title
        title = self._extract_title(soup)
        
        # Extract main content
        content = self._extract_main_content(soup)
        
        # Calculate quality metrics
        quality_score = self._calculate_extraction_quality(content, len(html_content))
        
        # Extract metadata
        metadata = self._extract_metadata(soup, url)
        
        return ScrapedContent(
            url=url,
            title=title,
            content=content,
            text_length=len(content),
            extraction_quality=quality_score,
            metadata=metadata
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        
        # Try different title sources in order of preference
        title_selectors = [
            'h1',
            'title',
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.title',
            '.headline'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 10:
                    return title[:200]  # Limit title length
        
        return "No title found"
    
    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from HTML"""
        
        # Try to find main content areas
        content_selectors = [
            'article',
            'main',
            '[role="main"]',
            '.content',
            '.post-content',
            '.article-content',
            '.main-content',
            '#content',
            '#main',
            '.entry-content'
        ]
        
        content_text = ""
        
        # Try structured content extraction first
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > len(content_text):
                        content_text = text
                break
        
        # Fallback: extract from body if no structured content found
        if not content_text or len(content_text) < 500:
            body = soup.find('body')
            if body:
                content_text = body.get_text(separator=' ', strip=True)
        
        # Clean up the text
        content_text = self._clean_text(content_text)
        
        return content_text[:50000]  # Limit content length
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common webpage noise
        noise_patterns = [
            r'cookie policy.*?accept',
            r'subscribe.*?newsletter',
            r'follow us on.*?social',
            r'share this.*?article',
            r'print this page',
            r'email this article',
            r'related articles?',
            r'you might also like',
            r'recommended for you'
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove repetitive text (common in navigation/footers)
        sentences = text.split('.')
        unique_sentences = []
        seen_sentences = set()
        
        for sentence in sentences:
            sentence = sentence.strip()
            sentence_key = sentence.lower()[:50]  # Use first 50 chars as key
            
            if sentence_key not in seen_sentences and len(sentence) > 20:
                unique_sentences.append(sentence)
                seen_sentences.add(sentence_key)
        
        return '. '.join(unique_sentences)
    
    def _calculate_extraction_quality(self, content: str, html_length: int) -> float:
        """Calculate quality score for extracted content"""
        
        if not content or html_length == 0:
            return 0.0
        
        score = 0.0
        
        # Content length score (0-30 points)
        content_length = len(content)
        if content_length > 5000:
            score += 30
        elif content_length > 2000:
            score += 25
        elif content_length > 1000:
            score += 20
        elif content_length > 500:
            score += 15
        elif content_length > 200:
            score += 10
        
        # Content to HTML ratio (0-25 points)
        ratio = content_length / html_length
        if ratio > 0.1:
            score += 25
        elif ratio > 0.05:
            score += 20
        elif ratio > 0.02:
            score += 15
        elif ratio > 0.01:
            score += 10
        
        # Content quality indicators (0-25 points)
        quality_indicators = [
            r'\b\d+%\b',  # Percentages
            r'\$[\d,]+(?:\.\d+)?[MBK]?\b',  # Currency amounts
            r'\b\d{4}\b',  # Years
            r'\b(?:market|revenue|growth|analysis|industry|report)\b',  # Relevant keywords
            r'\b(?:million|billion|trillion)\b',  # Large numbers
        ]
        
        for pattern in quality_indicators:
            if re.search(pattern, content, re.IGNORECASE):
                score += 5
        
        # Sentence structure score (0-20 points)
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        
        if 10 <= avg_sentence_length <= 25:  # Good sentence length
            score += 20
        elif 5 <= avg_sentence_length <= 35:
            score += 15
        elif avg_sentence_length >= 5:
            score += 10
        
        return min(100.0, score)
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        
        metadata = {
            'domain': urlparse(url).netloc,
            'publish_date': None,
            'author': None,
            'description': None,
            'keywords': [],
            'article_type': None
        }
        
        # Extract description
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '')[:500]
        
        # Extract keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords.get('content', '').split(',')
            metadata['keywords'] = [k.strip() for k in keywords[:10]]
        
        # Extract author
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '[rel="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['author'] = element.get('content', '')
                else:
                    metadata['author'] = element.get_text(strip=True)
                break
        
        # Extract publish date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="publish_date"]',
            'time[datetime]',
            '.publish-date',
            '.date'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['publish_date'] = element.get('content', '')
                elif element.name == 'time':
                    metadata['publish_date'] = element.get('datetime', element.get_text(strip=True))
                else:
                    metadata['publish_date'] = element.get_text(strip=True)
                break
        
        # Determine article type
        if any(indicator in url.lower() for indicator in ['news', 'article', 'blog', 'post']):
            metadata['article_type'] = 'article'
        elif any(indicator in url.lower() for indicator in ['report', 'research', 'study']):
            metadata['article_type'] = 'report'
        elif any(indicator in url.lower() for indicator in ['about', 'company', 'profile']):
            metadata['article_type'] = 'company_info'
        else:
            metadata['article_type'] = 'general'
        
        return metadata
    
    def filter_high_quality_content(self, scraped_content: List[ScrapedContent], 
                                  min_quality: float = 60.0, max_results: int = 20) -> List[ScrapedContent]:
        """Filter and rank scraped content by quality"""
        
        # Filter by minimum quality
        high_quality = [content for content in scraped_content 
                       if content.extraction_quality >= min_quality]
        
        # Sort by quality score
        high_quality.sort(key=lambda x: x.extraction_quality, reverse=True)
        
        return high_quality[:max_results]
    
    def extract_key_insights(self, scraped_content: List[ScrapedContent]) -> Dict[str, List[str]]:
        """Extract key insights from scraped content"""
        
        insights = {
            'market_statistics': [],
            'growth_metrics': [],
            'industry_trends': [],
            'competitive_intel': [],
            'customer_insights': []
        }
        
        # Patterns for different types of insights
        patterns = {
            'market_statistics': [
                r'market size.*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion)',
                r'valued at.*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion)',
                r'worth.*?\$?([\d,]+\.?\d*)\s*(billion|million|trillion)'
            ],
            'growth_metrics': [
                r'([\d,]+\.?\d*)\s*%.*?(growth|CAGR|increase)',
                r'growing.*?([\d,]+\.?\d*)\s*%',
                r'projected to grow.*?([\d,]+\.?\d*)\s*%'
            ],
            'industry_trends': [
                r'trend.*?(?:toward|towards|in).*?([^.]{20,100})',
                r'emerging.*?(?:technology|trend|pattern).*?([^.]{20,100})',
                r'future.*?(?:outlook|prediction|forecast).*?([^.]{20,100})'
            ],
            'competitive_intel': [
                r'(?:leading|top|major)\s+(?:companies|players|competitors).*?([^.]{20,100})',
                r'market leaders.*?([^.]{20,100})',
                r'key players.*?([^.]{20,100})'
            ],
            'customer_insights': [
                r'customers.*?(?:prefer|want|need|demand).*?([^.]{20,100})',
                r'buyer.*?(?:behavior|preferences|patterns).*?([^.]{20,100})',
                r'consumer.*?(?:trends|insights|research).*?([^.]{20,100})'
            ]
        }
        
        for content in scraped_content:
            text = content.content.lower()
            
            for category, category_patterns in patterns.items():
                for pattern in category_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            insight = ' '.join(str(m) for m in match)
                        else:
                            insight = str(match)
                        
                        # Clean and validate insight
                        insight = insight.strip()
                        if len(insight) > 10 and insight not in insights[category]:
                            insights[category].append(insight)
        
        # Limit results per category
        for category in insights:
            insights[category] = insights[category][:10]
        
        return insights