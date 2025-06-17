#!/usr/bin/env python3
"""
Test script for the Enhanced Search Service
"""

import asyncio
import json
from services.enhanced_search_service import EnhancedSearchService

async def test_enhanced_search():
    """Test the enhanced search functionality"""
    
    # Initialize service
    api_key = "d02a86009eaa117bdf00747b6fcce9aa14fc1128"
    search_service = EnhancedSearchService(api_key)
    
    print("🔍 Testing Enhanced Search Service with Serper.dev")
    print("=" * 60)
    
    # Test parameters
    company_name = "TechStart Inc"
    industry = "SaaS"
    business_model = "B2B"
    
    try:
        # Run deep market search
        print(f"Searching for: {company_name} in {industry} ({business_model})")
        print("This will execute 25+ targeted searches...")
        print()
        
        results = await search_service.deep_market_search(company_name, industry, business_model)
        
        # Display results summary
        metadata = results.get('search_metadata', {})
        market_insights = results.get('market_insights', {})
        
        print("📊 SEARCH RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Queries Executed: {metadata.get('total_queries', 0)}")
        print(f"Data Sources: {len(metadata.get('data_sources', []))}")
        print(f"Timestamp: {metadata.get('timestamp', 'Unknown')}")
        print()
        
        # Market Size Analysis
        market_size = market_insights.get('market_size', {})
        if market_size:
            print("💰 MARKET SIZE ANALYSIS")
            print("-" * 30)
            if market_size.get('current_market_size'):
                print(f"Current Market Size: ${market_size['current_market_size']:.1f}M")
            if market_size.get('growth_rate'):
                print(f"Growth Rate: {market_size['growth_rate']:.1f}% CAGR")
            print(f"Data Points Found: {market_size.get('data_points', 0)}")
            print()
        
        # Competitive Landscape
        competitors = market_insights.get('competitive_landscape', {})
        top_competitors = competitors.get('top_competitors', [])
        if top_competitors:
            print("🏆 TOP COMPETITORS")
            print("-" * 30)
            for i, comp in enumerate(top_competitors[:5], 1):
                print(f"{i}. {comp['name']} ({comp['mentions']} mentions)")
            print()
        
        # Customer Segments
        segments = market_insights.get('customer_segments', [])
        if segments:
            print("👥 CUSTOMER SEGMENTS IDENTIFIED")
            print("-" * 30)
            for segment in segments[:5]:
                print(f"• {segment['name']}: {segment['mentions']} mentions")
            print()
        
        # Key Opportunities
        opportunities = market_insights.get('key_opportunities', [])
        if opportunities:
            print("🚀 KEY OPPORTUNITIES")
            print("-" * 30)
            for i, opp in enumerate(opportunities[:3], 1):
                print(f"{i}. {opp[:100]}...")
            print()
        
        # Web Scraping Results
        scraped_content = results.get('scraped_content', [])
        if scraped_content:
            print("🌐 WEB SCRAPING RESULTS")
            print("-" * 30)
            print(f"Pages Scraped: {len(scraped_content)}")
            total_content = sum(c.get('content_length', 0) for c in scraped_content)
            print(f"Total Content Analyzed: {total_content:,} characters")
            
            high_quality = [c for c in scraped_content if c.get('quality_score', 0) > 70]
            print(f"High-Quality Pages: {len(high_quality)}")
            
            # Show sample scraped content
            for i, content in enumerate(scraped_content[:2], 1):
                print(f"\n{i}. {content.get('title', 'No title')[:50]}...")
                print(f"   Quality Score: {content.get('quality_score', 0):.1f}%")
                print(f"   Content Length: {content.get('content_length', 0):,} chars")
                print(f"   Preview: {content.get('content', '')[:150]}...")
            print()
        
        # Deep Content Analysis
        deep_analysis = market_insights.get('deep_content_analysis', {})
        if deep_analysis and deep_analysis.get('total_content_analyzed', 0) > 0:
            print("🔍 DEEP CONTENT ANALYSIS")
            print("-" * 30)
            print(f"Content Analyzed: {deep_analysis.get('total_content_analyzed', 0):,} characters")
            print(f"High-Quality Pages: {deep_analysis.get('high_quality_pages', 0)}")
            
            key_stats = deep_analysis.get('key_statistics', [])
            if key_stats:
                print(f"Enhanced Statistics: {len(key_stats)}")
                for stat in key_stats[:3]:
                    print(f"  • {stat.get('type', 'Unknown')}: {stat.get('confidence', 0):.2f} confidence")
            print()
        
        # Data Quality
        quality = market_insights.get('data_quality_score', {})
        if quality:
            print("📈 ENHANCED DATA QUALITY METRICS")
            print("-" * 30)
            print(f"Overall Score: {quality.get('overall_score', 0)}%")
            print(f"Total Data Points: {quality.get('total_data_points', 0)}")
            print(f"Authoritative Sources: {quality.get('authoritative_sources', 0)}")
            print(f"Scraped Pages: {quality.get('scraped_pages', 0)}")
            print(f"Deep Content: {quality.get('deep_content_length', 0):,} chars")
            print(f"Data Coverage: {quality.get('data_coverage', 'Unknown')}")
            if quality.get('enhancement_boost', 0) > 0:
                print(f"Enhancement Boost: +{quality.get('enhancement_boost', 0)}%")
            print()
        
        # Sample of raw data
        raw_results = results.get('raw_results', {})
        market_data = raw_results.get('market_data', [])
        if market_data:
            print("📄 SAMPLE MARKET DATA")
            print("-" * 30)
            for i, item in enumerate(market_data[:3], 1):
                print(f"{i}. {item.get('title', 'No title')[:60]}...")
                print(f"   Source: {item.get('source', 'Unknown')}")
                print(f"   Snippet: {item.get('snippet', '')[:100]}...")
                print()
        
        print("✅ Enhanced search with web scraping completed successfully!")
        
        # Calculate enhancement level
        enhancement_level = "Standard"
        if scraped_content and len(scraped_content) > 5:
            enhancement_level = "Deep+"
        elif scraped_content and len(scraped_content) > 2:
            enhancement_level = "Enhanced"
        
        print(f"🚀 Search Enhancement Level: {enhancement_level}")
        print(f"📊 Quality Score: {quality.get('overall_score', 0)}%")
        print(f"🌐 With {len(scraped_content)} pages of deep content analysis")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_search())