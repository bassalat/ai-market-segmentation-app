from typing import Dict, Any
import streamlit as st
from models.user_inputs import UserInputs
from models.segment_models import SegmentationResults, MarketAnalysis
from services.claude_service import ClaudeService
from services.enhanced_search_service import EnhancedSearchService

class SegmentationEngine:
    def __init__(self, serper_api_key: str = None):
        self.claude_service = ClaudeService()
        self.enhanced_search_service = EnhancedSearchService(serper_api_key) if serper_api_key else None
    
    def process_segmentation(self, user_inputs: UserInputs) -> SegmentationResults:
        """Main processing pipeline for market segmentation"""
        
        # Phase 1: Data Collection
        with st.status("🔍 Collecting comprehensive market data...", expanded=True) as status:
            st.write("Executing deep market research with multiple search layers...")
            
            if self.enhanced_search_service:
                import asyncio
                # Run enhanced search
                search_results = asyncio.run(
                    self.enhanced_search_service.deep_market_search(
                        user_inputs.basic_info.company_name,
                        user_inputs.basic_info.industry,
                        user_inputs.basic_info.business_model.value
                    )
                )
                
                # Display search statistics
                metadata = search_results.get('search_metadata', {})
                st.write(f"📊 Executed {metadata.get('total_queries', 0)} targeted searches")
                st.write(f"🌐 Analyzed data from {len(metadata.get('data_sources', []))} sources")
                
                # Extract market insights for Claude
                market_insights = search_results.get('market_insights', {})
                quality_score = market_insights.get('data_quality_score', {}).get('overall_score', 0)
                st.write(f"✅ Market intelligence collected (Quality Score: {quality_score}%)")
                
                # Format for Claude consumption
                formatted_search_data = self._format_enhanced_search_results(search_results)
            else:
                st.write("⚠️ Enhanced search not available - using basic search")
                # Fallback to basic search if API key not provided
                from services.search_service import SearchService
                basic_search = SearchService()
                formatted_search_data = basic_search.search_market_data(
                    user_inputs.basic_info.company_name,
                    user_inputs.basic_info.industry,
                    user_inputs.basic_info.business_model.value
                )
                st.write("✅ Basic market data collected")
        
        # Phase 2: Market Analysis
        with st.status("📊 Analyzing market landscape...", expanded=True) as status:
            st.write("Analyzing industry trends and competitive landscape...")
            market_analysis = self.claude_service.analyze_market(user_inputs, formatted_search_data)
            st.write("✅ Market analysis complete")
        
        # Phase 3: Segment Identification
        with st.status("🎯 Identifying market segments...", expanded=True) as status:
            st.write("Identifying distinct customer segments...")
            segments = self.claude_service.generate_segments(user_inputs, market_analysis)
            st.write(f"✅ {len(segments)} segments identified")
        
        # Phase 4: Persona Generation
        with st.status("👥 Creating detailed personas...", expanded=True) as status:
            enhanced_segments = []
            for i, segment in enumerate(segments, 1):
                st.write(f"Creating persona for segment {i}: {segment.name}")
                enhanced_segment = self.claude_service.generate_personas(segment, user_inputs)
                enhanced_segments.append(enhanced_segment)
            st.write("✅ All personas created")
        
        # Phase 5: Implementation Planning
        with st.status("📋 Generating implementation roadmap...", expanded=True) as status:
            st.write("Creating go-to-market recommendations...")
            implementation_roadmap = self._generate_implementation_roadmap(enhanced_segments)
            quick_wins = self._identify_quick_wins(enhanced_segments)
            success_metrics = self._define_success_metrics(enhanced_segments, user_inputs)
            st.write("✅ Implementation plan ready")
        
        # Update market analysis with segments
        market_analysis.segments = enhanced_segments
        
        return SegmentationResults(
            market_analysis=market_analysis,
            segments=enhanced_segments,
            implementation_roadmap=implementation_roadmap,
            quick_wins=quick_wins,
            success_metrics=success_metrics
        )
    
    def _generate_implementation_roadmap(self, segments) -> Dict[str, list]:
        """Generate implementation roadmap based on segments"""
        
        # Prioritize segments by size and market opportunity
        priority_segments = sorted(segments, key=lambda x: x.size_percentage, reverse=True)
        
        roadmap = {
            "Phase 1 (0-30 days)": [
                f"Focus on {priority_segments[0].name} segment - highest market opportunity",
                "Develop messaging framework for primary segment",
                "Set up tracking and analytics",
                "Create initial marketing materials"
            ],
            "Phase 2 (30-60 days)": [
                f"Expand to {priority_segments[1].name if len(priority_segments) > 1 else 'secondary'} segment",
                "Test and optimize messaging across channels",
                "Gather customer feedback and iterate",
                "Scale successful campaigns"
            ],
            "Phase 3 (60-90 days)": [
                "Roll out to remaining segments",
                "Implement cross-segment strategies",
                "Optimize conversion funnels",
                "Plan for scale and growth"
            ]
        }
        
        return roadmap
    
    def _identify_quick_wins(self, segments) -> list:
        """Identify quick wins based on segment analysis"""
        quick_wins = [
            f"Target {segments[0].name} through {segments[0].preferred_channels[0] if segments[0].preferred_channels else 'digital channels'}",
            f"Address {segments[0].pain_points[0] if segments[0].pain_points else 'primary pain point'} in messaging",
            "Implement basic analytics tracking",
            "Create segment-specific landing pages",
            "Set up email nurture sequences"
        ]
        
        return quick_wins
    
    def _define_success_metrics(self, segments, user_inputs) -> list:
        """Define success metrics based on business model and segments"""
        
        base_metrics = [
            "Segment identification accuracy",
            "Message-to-market fit scores",
            "Customer acquisition cost by segment",
            "Conversion rate optimization"
        ]
        
        if user_inputs.basic_info.business_model.value == "B2B":
            base_metrics.extend([
                "Sales qualified leads by segment",
                "Sales cycle length reduction",
                "Deal size improvement",
                "Pipeline velocity increase"
            ])
        else:
            base_metrics.extend([
                "Customer lifetime value by segment",
                "Repeat purchase rate",
                "Average order value",
                "Brand awareness metrics"
            ])
        
        return base_metrics
    
    def _format_enhanced_search_results(self, search_results: Dict[str, Any]) -> str:
        """Format enhanced search results for Claude consumption"""
        
        raw_results = search_results.get('raw_results', {})
        market_insights = search_results.get('market_insights', {})
        
        # Build comprehensive market intelligence report
        formatted_report = []
        
        # Market Size and Growth
        market_size_data = market_insights.get('market_size', {})
        if market_size_data.get('current_market_size'):
            formatted_report.append(f"MARKET SIZE ANALYSIS:")
            formatted_report.append(f"- Current Market Size: ${market_size_data['current_market_size']:.1f}M")
            if market_size_data.get('growth_rate'):
                formatted_report.append(f"- Growth Rate: {market_size_data['growth_rate']:.1f}% CAGR")
            
            # Add supporting data points
            market_values = market_size_data.get('market_values_found', [])
            for value in market_values[:3]:
                formatted_report.append(f"  • {value['raw']} ({value['source']})")
        
        # Key Statistics
        if raw_results.get('key_statistics'):
            formatted_report.append(f"\nKEY MARKET STATISTICS:")
            for stat in raw_results['key_statistics'][:10]:
                if isinstance(stat, dict) and stat.get('content'):
                    formatted_report.append(f"- {stat['content']}")
        
        # Growth Factors
        growth_factors = market_insights.get('growth_factors', [])
        if growth_factors:
            formatted_report.append(f"\nKEY GROWTH DRIVERS:")
            for factor in growth_factors[:5]:
                formatted_report.append(f"- {factor}")
        
        # Competitive Landscape
        competitors = market_insights.get('competitive_landscape', {})
        top_competitors = competitors.get('top_competitors', [])
        if top_competitors:
            formatted_report.append(f"\nCOMPETITIVE LANDSCAPE:")
            for comp in top_competitors[:8]:
                formatted_report.append(f"- {comp['name']} (mentioned {comp['mentions']} times)")
        
        # Customer Segments
        customer_segments = market_insights.get('customer_segments', [])
        if customer_segments:
            formatted_report.append(f"\nIDENTIFIED CUSTOMER SEGMENTS:")
            for segment in customer_segments[:5]:
                formatted_report.append(f"- {segment['name']}: {segment['mentions']} mentions")
        
        # Market Opportunities
        opportunities = market_insights.get('key_opportunities', [])
        if opportunities:
            formatted_report.append(f"\nMARKET OPPORTUNITIES:")
            for opp in opportunities[:5]:
                formatted_report.append(f"- {opp}")
        
        # Industry Challenges
        challenges = market_insights.get('industry_challenges', [])
        if challenges:
            formatted_report.append(f"\nINDUSTRY CHALLENGES:")
            for challenge in challenges[:5]:
                formatted_report.append(f"- {challenge}")
        
        # Emerging Trends
        trends = market_insights.get('emerging_trends', [])
        if trends:
            formatted_report.append(f"\nEMERGING TRENDS:")
            for trend_category in trends[:3]:
                formatted_report.append(f"- {trend_category['category']}: {len(trend_category['trends'])} trends identified")
        
        # Raw Market Data Highlights
        market_data = raw_results.get('market_data', [])
        if market_data:
            formatted_report.append(f"\nMARKET DATA INSIGHTS:")
            for item in market_data[:10]:
                if item.get('snippet') and len(item['snippet']) > 50:
                    formatted_report.append(f"- {item['snippet'][:200]}...")
        
        # Customer Insights
        customer_insights = raw_results.get('customer_insights', [])
        if customer_insights:
            formatted_report.append(f"\nCUSTOMER BEHAVIOR INSIGHTS:")
            for item in customer_insights[:8]:
                if item.get('snippet') and len(item['snippet']) > 50:
                    formatted_report.append(f"- {item['snippet'][:200]}...")
        
        # Deep Content Analysis (from web scraping)
        deep_analysis = market_insights.get('deep_content_analysis', {})
        if deep_analysis and deep_analysis.get('total_content_analyzed', 0) > 0:
            formatted_report.append(f"\nDEEP CONTENT ANALYSIS:")
            formatted_report.append(f"- Content Analyzed: {deep_analysis.get('total_content_analyzed', 0):,} characters")
            formatted_report.append(f"- High-Quality Pages: {deep_analysis.get('high_quality_pages', 0)}")
            
            # Add key statistics from scraped content
            key_stats = deep_analysis.get('key_statistics', [])
            if key_stats:
                formatted_report.append(f"- Enhanced Statistics Found: {len(key_stats)}")
                for stat in key_stats[:5]:
                    if isinstance(stat, dict) and stat.get('context'):
                        formatted_report.append(f"  • {stat['type']}: {stat.get('context', '')[:150]}...")
            
            # Add detailed insights
            detailed_insights = deep_analysis.get('detailed_insights', [])
            if detailed_insights:
                formatted_report.append(f"\nKEY INSIGHTS FROM DEEP ANALYSIS:")
                for insight in detailed_insights[:3]:
                    formatted_report.append(f"- Source: {insight.get('title', 'Unknown')}")
                    key_insights = insight.get('key_insights', [])
                    for key_insight in key_insights[:2]:
                        formatted_report.append(f"  • {key_insight[:200]}...")
        
        # Enhanced scraped content highlights
        if search_results.get('scraped_content'):
            scraped_content = search_results['scraped_content']
            formatted_report.append(f"\nSCRAPED CONTENT HIGHLIGHTS:")
            for content in scraped_content[:3]:
                formatted_report.append(f"- {content.get('title', 'Unknown')} (Quality: {content.get('quality_score', 0):.1f}%)")
                formatted_report.append(f"  Content: {content.get('content_preview', '')[:150]}...")
        
        # Data Quality Summary
        quality_data = market_insights.get('data_quality_score', {})
        if quality_data:
            formatted_report.append(f"\nENHANCED DATA QUALITY SUMMARY:")
            formatted_report.append(f"- Overall Quality Score: {quality_data.get('overall_score', 0)}%")
            formatted_report.append(f"- Total Data Points: {quality_data.get('total_data_points', 0)}")
            formatted_report.append(f"- Authoritative Sources: {quality_data.get('authoritative_sources', 0)}")
            formatted_report.append(f"- Scraped Pages: {quality_data.get('scraped_pages', 0)}")
            formatted_report.append(f"- Deep Content Length: {quality_data.get('deep_content_length', 0):,} chars")
            formatted_report.append(f"- Data Coverage: {quality_data.get('data_coverage', 'Unknown')}")
            if quality_data.get('enhancement_boost', 0) > 0:
                formatted_report.append(f"- Enhancement Boost: +{quality_data.get('enhancement_boost', 0)}% from deep analysis")
        
        return "\n".join(formatted_report)