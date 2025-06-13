from typing import Dict, Any
import streamlit as st
from models.user_inputs import UserInputs
from models.segment_models import SegmentationResults, MarketAnalysis
from services.claude_service import ClaudeService
from services.search_service import SearchService

class SegmentationEngine:
    def __init__(self):
        self.claude_service = ClaudeService()
        self.search_service = SearchService()
    
    def process_segmentation(self, user_inputs: UserInputs) -> SegmentationResults:
        """Main processing pipeline for market segmentation"""
        
        # Phase 1: Data Collection
        with st.status("🔍 Collecting market data...", expanded=True) as status:
            st.write("Searching for industry trends and market data...")
            search_results = self.search_service.search_market_data(
                user_inputs.basic_info.company_name,
                user_inputs.basic_info.industry,
                user_inputs.basic_info.business_model.value
            )
            st.write("✅ Market data collected")
        
        # Phase 2: Market Analysis
        with st.status("📊 Analyzing market landscape...", expanded=True) as status:
            st.write("Analyzing industry trends and competitive landscape...")
            market_analysis = self.claude_service.analyze_market(user_inputs, search_results)
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