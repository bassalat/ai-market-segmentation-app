import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from models.segment_models import SegmentationResults

def render_results_dashboard(results: SegmentationResults):
    """Render the interactive results dashboard"""
    
    st.markdown("## 🎯 Your Market Segmentation Results")
    
    # Overview section
    render_overview_section(results.market_analysis)
    
    # Segments visualization
    render_segments_overview(results.segments)
    
    # Detailed segment cards
    render_segment_cards(results.segments)
    
    # Enhanced market insights
    render_enhanced_insights(results.market_analysis)
    
    # Implementation roadmap
    render_implementation_section(results)

def render_overview_section(market_analysis):
    """Render the market overview section"""
    
    st.markdown("### 📊 Market Overview")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Total Addressable Market")
        st.info(market_analysis.total_addressable_market)
        
        st.markdown("#### Key Market Insights")
        for i, insight in enumerate(market_analysis.key_insights, 1):
            st.markdown(f"**{i}.** {insight}")
    
    with col2:
        st.markdown("#### Industry Trends")
        for trend in market_analysis.industry_trends:
            st.markdown(f"• {trend}")
        
        if hasattr(market_analysis, 'industry_cagr') and market_analysis.industry_cagr:
            st.markdown("#### Industry Growth")
            st.info(f"**CAGR:** {market_analysis.industry_cagr}")
        
        if market_analysis.competitive_landscape:
            st.markdown("#### Competitive Landscape")
            st.markdown(market_analysis.competitive_landscape)

def render_segments_overview(segments):
    """Render segments overview with charts"""
    
    st.markdown("### 🎯 Market Segments Overview")
    
    if not segments:
        st.warning("No segments were generated. Please try again with different inputs.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Segment size distribution pie chart
        segment_names = [segment.name for segment in segments]
        segment_sizes = [segment.size_percentage for segment in segments]
        
        fig_pie = px.pie(
            values=segment_sizes,
            names=segment_names,
            title="Segment Size Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Segment characteristics comparison
        if segments:
            segment_data = []
            for segment in segments:
                segment_data.append({
                    'Segment': segment.name,
                    'Size %': segment.size_percentage,
                    'Pain Points': len(segment.pain_points),
                    'Channels': len(segment.preferred_channels),
                    'Triggers': len(segment.buying_triggers)
                })
            
            df = pd.DataFrame(segment_data)
            
            fig_bar = px.bar(
                df,
                x='Segment',
                y='Size %',
                title="Segment Market Share",
                color='Size %',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(
                height=400, 
                showlegend=False,
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

def render_enhanced_insights(market_analysis):
    """Render enhanced market insights including growth factors, CAGR, urgencies, and competitors"""
    
    st.markdown("### 📈 Enhanced Market Intelligence")
    
    # Growth factors and urgencies
    col1, col2 = st.columns(2)
    
    with col1:
        if hasattr(market_analysis, 'industry_growth_factors') and market_analysis.industry_growth_factors:
            st.markdown("#### 🚀 Industry Growth Factors")
            for factor in market_analysis.industry_growth_factors:
                st.markdown(f"• {factor}")
    
    with col2:
        if hasattr(market_analysis, 'commercial_urgencies') and market_analysis.commercial_urgencies:
            st.markdown("#### ⚡ Commercial Urgencies")
            for urgency in market_analysis.commercial_urgencies:
                st.markdown(f"• {urgency}")
    
    # Competitive analysis
    if hasattr(market_analysis, 'top_competitors') and market_analysis.top_competitors:
        st.markdown("#### 🏆 Top 5 Competitors")
        
        # Create competitor cards
        for i, competitor in enumerate(market_analysis.top_competitors[:5], 1):
            with st.expander(f"**{i}. {competitor.name}**", expanded=i<=2):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Funding:** {competitor.funding}")
                    st.markdown(f"**Market Position:** {competitor.market_position}")
                
                with col2:
                    st.markdown(f"**Solution Specialty:**")
                    st.markdown(competitor.solution_specialty)

def render_segment_cards(segments):
    """Render detailed segment cards"""
    
    st.markdown("### 👥 Detailed Segment Profiles")
    
    for i, segment in enumerate(segments):
        with st.expander(f"🎯 **{segment.name}** ({segment.size_percentage}% of market)", expanded=i==0):
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Main segment info
                st.markdown(f"**Market Size:** {segment.size_estimation}")
                
                st.markdown("**Key Characteristics:**")
                for char in segment.characteristics:
                    st.markdown(f"• {char}")
                
                if segment.persona_description:
                    st.markdown("**Persona Description:**")
                    st.markdown(segment.persona_description)
                
                # Pain points and triggers
                if segment.pain_points:
                    st.markdown("**Primary Pain Points:**")
                    for pain in segment.pain_points:
                        st.markdown(f"🔸 {pain}")
                
                if segment.buying_triggers:
                    st.markdown("**Buying Triggers:**")
                    for trigger in segment.buying_triggers:
                        st.markdown(f"⚡ {trigger}")
                
                # Use cases
                if hasattr(segment, 'use_cases') and segment.use_cases:
                    st.markdown("**Use Cases:**")
                    for use_case in segment.use_cases:
                        st.markdown(f"🎯 {use_case}")
            
            with col2:
                # Demographics
                if segment.demographics:
                    st.markdown("**Demographics:**")
                    for key, value in segment.demographics.items():
                        if value:
                            st.markdown(f"**{key.title()}:** {value}")
                
                # Psychographics
                if segment.psychographics:
                    st.markdown("**Psychographics:**")
                    for psycho in segment.psychographics:
                        st.markdown(f"• {psycho}")
                
                # Preferred channels
                if segment.preferred_channels:
                    st.markdown("**Preferred Channels:**")
                    for channel in segment.preferred_channels:
                        st.markdown(f"📱 {channel}")
                
                # Role-specific pain points
                if hasattr(segment, 'role_specific_pain_points') and segment.role_specific_pain_points:
                    st.markdown("**Role-Specific Pain Points:**")
                    for role, pains in segment.role_specific_pain_points.items():
                        if pains:
                            st.markdown(f"**{role}:**")
                            for pain in pains:
                                st.markdown(f"  • {pain}")
            
            # Messaging section
            if segment.messaging_hooks:
                st.markdown("---")
                st.markdown("**💬 Messaging Recommendations:**")
                
                cols = st.columns(len(segment.messaging_hooks))
                for idx, hook in enumerate(segment.messaging_hooks):
                    with cols[idx % len(cols)]:
                        st.markdown(f"""
                        <div style="background: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;">
                            <strong>Hook {idx + 1}:</strong><br>
                            {hook}
                        </div>
                        """, unsafe_allow_html=True)

def render_implementation_section(results: SegmentationResults):
    """Render implementation roadmap and recommendations"""
    
    st.markdown("### 🚀 Implementation Roadmap")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Phase-by-Phase Plan")
        
        for phase, tasks in results.implementation_roadmap.items():
            with st.expander(f"**{phase}**", expanded=phase.startswith("Phase 1")):
                for task in tasks:
                    st.markdown(f"• {task}")
    
    with col2:
        st.markdown("#### ⚡ Quick Wins")
        
        for i, win in enumerate(results.quick_wins, 1):
            st.markdown(f"**{i}.** {win}")
        
        st.markdown("#### 📈 Success Metrics")
        
        for metric in results.success_metrics[:6]:  # Show first 6 metrics
            st.markdown(f"• {metric}")
    
    # Priority matrix visualization
    if len(results.segments) > 1:
        st.markdown("#### 🎯 Segment Priority Matrix")
        
        # Create a simple priority matrix based on size and ease of targeting
        segment_data = []
        for segment in results.segments:
            # Simple scoring based on size and number of characteristics
            ease_score = max(1, 10 - len(segment.characteristics))  # Fewer characteristics = easier to target
            segment_data.append({
                'Segment': segment.name,
                'Market Size': segment.size_percentage,
                'Ease of Targeting': ease_score,
                'Size Description': f"{segment.size_percentage}% of market"
            })
        
        df = pd.DataFrame(segment_data)
        
        fig_scatter = px.scatter(
            df,
            x='Ease of Targeting',
            y='Market Size',
            size='Market Size',
            hover_name='Segment',
            hover_data=['Size Description'],
            title="Segment Priority Matrix (Size vs. Ease of Targeting)",
            labels={'Ease of Targeting': 'Ease of Targeting (1-10)', 'Market Size': 'Market Size (%)'}
        )
        
        # Add quadrant lines
        fig_scatter.add_hline(y=df['Market Size'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        fig_scatter.add_vline(x=df['Ease of Targeting'].median(), line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig_scatter.add_annotation(x=8, y=df['Market Size'].max()*0.9, text="High Priority", showarrow=False, font=dict(size=12, color="green"))
        fig_scatter.add_annotation(x=2, y=df['Market Size'].max()*0.9, text="Long-term", showarrow=False, font=dict(size=12, color="orange"))
        fig_scatter.add_annotation(x=8, y=df['Market Size'].min()*1.1, text="Quick Wins", showarrow=False, font=dict(size=12, color="blue"))
        fig_scatter.add_annotation(x=2, y=df['Market Size'].min()*1.1, text="Low Priority", showarrow=False, font=dict(size=12, color="red"))
        
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Detailed Analytics", type="secondary", use_container_width=True):
            st.info("Detailed analytics would include conversion predictions, ROI calculations, and channel effectiveness scores.")
    
    with col2:
        if st.button("🎨 Generate Marketing Assets", type="secondary", use_container_width=True):
            st.info("This would generate sample ad copy, landing page suggestions, and creative briefs for each segment.")
    
    with col3:
        if st.button("📈 Create A/B Test Plan", type="secondary", use_container_width=True):
            st.info("This would create a testing framework to validate segment assumptions and optimize messaging.")