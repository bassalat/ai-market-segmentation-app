from typing import Dict, Any
import streamlit as st
import time
import asyncio
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
        
        # Track overall analysis time
        self.analysis_start_time = time.time()
        
        # Initialize variables for summary
        metadata = {}
        market_insights = {}
        quality_data = {}
        
        # Phase 1: Data Collection
        with st.status("🔍 Collecting comprehensive market data...", expanded=True) as status:
            st.write("**What's happening:** Executing deep market research with multiple search layers")
            
            if self.enhanced_search_service:
                # Show search strategy
                with st.expander("🔎 Search Strategy Details", expanded=False):
                    st.write("**Search Categories:**")
                    st.write("• Market Size & TAM Analysis")
                    st.write("• Customer Segments & Demographics")
                    st.write("• Competitor Landscape")
                    st.write("• Industry Trends & Growth Factors")
                    st.write("• Academic Research & Reports")
                
                start_time = time.time()
                
                # Run enhanced search
                search_results = asyncio.run(
                    self.enhanced_search_service.deep_market_search(
                        user_inputs.basic_info.company_name,
                        user_inputs.basic_info.industry,
                        user_inputs.basic_info.business_model.value
                    )
                )
                
                elapsed_time = time.time() - start_time
                
                # Display detailed search statistics
                metadata = search_results.get('search_metadata', {})
                market_insights = search_results.get('market_insights', {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Searches Executed", metadata.get('total_queries', 0))
                with col2:
                    st.metric("Sources Analyzed", len(metadata.get('data_sources', [])))
                with col3:
                    st.metric("Pages Scraped", metadata.get('scraped_pages', 0))
                
                # Show key findings preview
                if market_insights.get('market_size', {}).get('current_market_size'):
                    market_size = market_insights['market_size']['current_market_size']
                    confidence = market_insights['market_size'].get('confidence_level', 'Unknown')
                    if market_size >= 1_000:
                        st.info(f"📈 **Market Size Found:** ${market_size/1_000:.1f}B (Confidence: {confidence})")
                    else:
                        st.info(f"📈 **Market Size Found:** ${market_size:.1f}M (Confidence: {confidence})")
                
                # Data quality metrics
                quality_data = market_insights.get('data_quality_score', {})
                quality_score = quality_data.get('overall_score', 0)
                
                with st.expander("📊 Data Quality Breakdown", expanded=False):
                    st.write(f"**Overall Quality Score:** {quality_score}%")
                    st.write(f"**Total Data Points:** {quality_data.get('total_data_points', 0)}")
                    st.write(f"**Authoritative Sources:** {quality_data.get('authoritative_sources', 0)}")
                    st.write(f"**Recent Data (2024-2025):** {quality_data.get('recent_data_points', 0)}")
                    st.write(f"**Deep Content Analyzed:** {quality_data.get('deep_content_length', 0):,} characters")
                
                st.success(f"✅ Market intelligence collected in {elapsed_time:.1f} seconds")
                
                # Format for Claude consumption
                formatted_search_data = self._format_enhanced_search_results(search_results)
                
                # Store search results for later display
                self.search_results_summary = search_results
                
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
        with st.status("📊 Analyzing market landscape with Claude AI...", expanded=True) as status:
            st.write("**What's happening:** Claude is analyzing all collected data to understand your market")
            
            # Show what Claude is analyzing
            with st.expander("🤖 AI Analysis Process", expanded=False):
                st.write("**Claude is extracting:**")
                st.write("• Total Addressable Market (TAM) size and projections")
                st.write("• Industry growth rates and CAGR")
                st.write("• Key market drivers and trends")
                st.write("• Commercial urgencies and timing factors")
                st.write("• Top competitors and their positioning")
                st.write("• Market opportunities and challenges")
            
            # Show data being sent to Claude
            with st.expander("📄 Data Sent to Claude AI", expanded=False):
                st.write("**Business Context:**")
                st.write(f"• Company: {user_inputs.basic_info.company_name}")
                st.write(f"• Industry: {user_inputs.basic_info.industry}")
                st.write(f"• Business Model: {user_inputs.basic_info.business_model.value}")
                st.write(f"• Target Market: {user_inputs.basic_info.target_market}")
                st.write("\n**Market Intelligence:**")
                st.write(f"• {len(formatted_search_data.split())} words of market data")
                st.write("• Search results from multiple sources")
                st.write("• Scraped content from authoritative sites")
            
            # Show actual Claude prompt (optional)
            with st.expander("🤖 View Claude AI Prompt", expanded=False):
                st.code(self.claude_service._build_market_analysis_prompt(
                    user_inputs, formatted_search_data
                )[:1000] + "...", language="text")
            
            start_time = time.time()
            market_analysis = self.claude_service.analyze_market(user_inputs, formatted_search_data)
            elapsed_time = time.time() - start_time
            
            # Show what Claude found
            st.success(f"✅ Market analysis complete in {elapsed_time:.1f} seconds")
            
            # Preview key findings
            if hasattr(market_analysis, 'total_addressable_market'):
                with st.expander("🎯 Key Market Findings", expanded=True):
                    st.write(f"**TAM:** {market_analysis.total_addressable_market}")
                    if hasattr(market_analysis, 'industry_growth_rate'):
                        st.write(f"**Growth Rate:** {market_analysis.industry_growth_rate}")
                    if hasattr(market_analysis, 'key_competitors') and market_analysis.key_competitors:
                        st.write(f"**Competitors Found:** {len(market_analysis.key_competitors)}")
        
        # Phase 3: Segment Identification
        with st.status("🎯 Identifying market segments with Claude AI...", expanded=True) as status:
            st.write("**What's happening:** Claude is identifying distinct customer groups based on patterns in the data")
            
            # Show segmentation methodology
            with st.expander("🔬 Segmentation Methodology", expanded=False):
                st.write("**Claude analyzes multiple dimensions:**")
                st.write("• Company size and industry vertical")
                st.write("• Pain points and challenges")
                st.write("• Buying behavior and decision factors")
                st.write("• Technology adoption levels")
                st.write("• Budget and resource availability")
                st.write("• Geographic and regulatory factors")
            
            # Show progress
            progress_placeholder = st.empty()
            progress_placeholder.write("🔄 Analyzing customer patterns...")
            
            start_time = time.time()
            segments = self.claude_service.generate_segments(user_inputs, market_analysis)
            elapsed_time = time.time() - start_time
            
            # Clear progress and show results
            progress_placeholder.empty()
            
            # Display segment preview
            st.success(f"✅ {len(segments)} distinct segments identified in {elapsed_time:.1f} seconds")
            
            # Show segment summary
            with st.expander("📊 Segment Overview", expanded=True):
                for i, segment in enumerate(segments, 1):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**Segment {i}:** {segment.name}")
                    with col2:
                        st.write(f"Size: {segment.size_percentage}%")
        
        # Phase 4: Persona Generation
        with st.status("👥 Creating detailed personas with Claude AI...", expanded=True) as status:
            st.write("**What's happening:** Claude is creating realistic buyer personas for each segment")
            
            # Show persona creation process
            with st.expander("🎭 Persona Creation Process", expanded=False):
                st.write("**For each segment, Claude creates:**")
                st.write("• Demographic profiles (age, role, experience)")
                st.write("• Psychographic insights (values, motivations)")
                st.write("• Daily challenges and pain points")
                st.write("• Decision-making criteria")
                st.write("• Communication preferences")
                st.write("• Objections and concerns")
            
            enhanced_segments = []
            total_time = 0
            
            # Create progress bar
            progress_bar = st.progress(0)
            
            for i, segment in enumerate(segments, 1):
                # Update progress
                progress = (i - 1) / len(segments)
                progress_bar.progress(progress)
                
                # Show current segment being processed
                status_text = st.empty()
                status_text.write(f"🔄 Creating persona for **{segment.name}**...")
                
                start_time = time.time()
                enhanced_segment = self.claude_service.generate_personas(segment, user_inputs)
                elapsed_time = time.time() - start_time
                total_time += elapsed_time
                
                enhanced_segments.append(enhanced_segment)
                
                # Update status
                status_text.write(f"✅ Persona created for **{segment.name}** ({elapsed_time:.1f}s)")
                
                # Show persona preview
                if enhanced_segment.personas:
                    persona = enhanced_segment.personas[0]
                    with st.expander(f"Preview: {persona.name}", expanded=False):
                        st.write(f"**Role:** {persona.role}")
                        st.write(f"**Age:** {persona.age}")
                        st.write(f"**Key Challenge:** {persona.pain_points[0] if persona.pain_points else 'N/A'}")
            
            # Complete progress bar
            progress_bar.progress(1.0)
            st.success(f"✅ All {len(segments)} personas created in {total_time:.1f} seconds")
        
        # Phase 5: Implementation Planning
        with st.status("📋 Generating implementation roadmap...", expanded=True) as status:
            st.write("**What's happening:** Creating actionable go-to-market recommendations")
            
            # Show what's being generated
            with st.expander("🚀 Implementation Components", expanded=False):
                st.write("**Strategic Planning:**")
                st.write("• 90-day phased roadmap")
                st.write("• Priority segment sequencing")
                st.write("• Quick win opportunities")
                st.write("• Success metrics and KPIs")
                st.write("• Channel recommendations")
                st.write("• Budget allocation guidance")
            
            start_time = time.time()
            
            # Generate implementation components with progress updates
            progress_text = st.empty()
            
            progress_text.write("📊 Analyzing segment priorities...")
            implementation_roadmap = self._generate_implementation_roadmap(enhanced_segments)
            
            progress_text.write("🎯 Identifying quick wins...")
            quick_wins = self._identify_quick_wins(enhanced_segments)
            
            progress_text.write("📈 Defining success metrics...")
            success_metrics = self._define_success_metrics(enhanced_segments, user_inputs)
            
            elapsed_time = time.time() - start_time
            progress_text.empty()
            
            # Show summary of recommendations
            st.success(f"✅ Implementation plan ready in {elapsed_time:.1f} seconds")
            
            # Preview key recommendations
            with st.expander("💡 Key Recommendations Preview", expanded=True):
                st.write("**Quick Wins:**")
                for win in quick_wins[:3]:
                    st.write(f"• {win}")
                st.write("\n**Success Metrics:**")
                for metric in success_metrics[:3]:
                    st.write(f"• {metric}")
        
        # Update market analysis with segments
        market_analysis.segments = enhanced_segments
        
        # Final summary
        st.divider()
        st.markdown("### 🎉 Analysis Complete!")
        
        # Show overall statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Segments Created", len(enhanced_segments))
        with col2:
            st.metric("Personas Generated", sum(len(s.personas) for s in enhanced_segments))
        with col3:
            st.metric("Data Points Analyzed", market_insights.get('data_quality_score', {}).get('total_data_points', 0))
        with col4:
            total_analysis_time = time.time() - self.analysis_start_time if hasattr(self, 'analysis_start_time') else 0
            st.metric("Total Time", f"{total_analysis_time:.1f}s")
        
        # Show what was accomplished
        with st.expander("📊 Analysis Summary", expanded=True):
            st.write("**Market Intelligence Gathered:**")
            st.write(f"• Analyzed {metadata.get('total_queries', 0)} search queries")
            st.write(f"• Scraped {metadata.get('scraped_pages', 0)} authoritative web pages")
            st.write(f"• Processed {quality_data.get('deep_content_length', 0):,} characters of content")
            
            st.write("\n**AI Analysis Performed:**")
            st.write(f"• Generated {len(enhanced_segments)} customer segments")
            st.write(f"• Created {sum(len(s.personas) for s in enhanced_segments)} detailed personas")
            st.write("• Analyzed market size, growth, and competitive landscape")
            st.write("• Developed implementation roadmap and success metrics")
            
            st.write("\n**Ready for Download:**")
            st.write("• Professional PDF report")
            st.write("• Machine-readable JSON data")
            st.write("• Implementation roadmap")
        
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
            
            # Format the market size properly
            market_size = market_size_data['current_market_size']
            if market_size >= 1_000:  # If over $1B (1000M), show as billions
                formatted_report.append(f"- Current Market Size: ${market_size/1_000:.1f}B")
            else:
                formatted_report.append(f"- Current Market Size: ${market_size:.1f}M")
            
            if market_size_data.get('growth_rate'):
                formatted_report.append(f"- Growth Rate: {market_size_data['growth_rate']:.1f}% CAGR")
            
            # Add confidence level
            confidence = market_size_data.get('confidence_level', 'Unknown')
            formatted_report.append(f"- Data Confidence: {confidence}")
            
            # Add supporting data points
            market_values = market_size_data.get('market_values_found', [])
            if market_values:
                formatted_report.append(f"- Supporting Data Points:")
                for value in market_values[:3]:
                    relevance = "✓" if value.get('is_relevant', False) else "?"
                    confidence_score = value.get('confidence', 0)
                    formatted_report.append(f"  {relevance} {value['raw']} ({value['source']}) [Conf: {confidence_score:.2f}]")
        
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