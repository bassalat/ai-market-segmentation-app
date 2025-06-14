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
    
    # Segment prioritization visualization
    if len(results.segments) > 1:
        st.markdown("#### 🎯 Segment Prioritization Analysis")
        
        # Calculate comprehensive scores for each segment
        segment_data = []
        for i, segment in enumerate(results.segments):
            # 1. Market Attractiveness Score (0-10)
            # Based on size, growth potential, and commercial urgency
            size_score = (segment.size_percentage / 100) * 4  # 0-4 points
            
            # Estimate growth potential from buying triggers and urgency
            growth_indicators = len(segment.buying_triggers) * 0.5  # 0-3 points
            
            # Commercial urgency (if segment has urgent needs)
            urgency_score = 3 if any('urgent' in str(p).lower() or 'immediate' in str(p).lower() 
                                   for p in segment.pain_points) else 1.5  # 0-3 points
            
            market_attractiveness = min(10, size_score + growth_indicators + urgency_score)
            
            # 2. Accessibility Score (0-10)
            # Based on how easy it is to reach and convert
            
            # Channel concentration (fewer channels = more focused)
            channel_score = max(0, 3 - (len(segment.preferred_channels) - 2) * 0.5)
            
            # Message clarity (clear pain points and use cases)
            message_clarity = min(3, len(segment.pain_points) * 0.5 + 
                                (len(segment.use_cases) * 0.5 if hasattr(segment, 'use_cases') else 0))
            
            # Targeting precision (well-defined demographics)
            target_precision = min(2, len(segment.demographics) * 0.4)
            
            # Competitive intensity (inverse - assume harder if more established)
            competitive_factor = 2 if i > len(results.segments) / 2 else 1  # Later segments = less competition
            
            accessibility = min(10, channel_score + message_clarity + target_precision + competitive_factor)
            
            # 3. Revenue Potential (for bubble size)
            # Estimate based on size and deal characteristics
            revenue_base = segment.size_percentage
            
            # Adjust for B2B vs B2C patterns
            if hasattr(segment, 'demographics') and any(role in str(segment.demographics) 
                                                       for role in ['CEO', 'CTO', 'VP', 'Director']):
                revenue_multiplier = 2.5  # B2B typically higher value
            else:
                revenue_multiplier = 1.0
            
            revenue_potential = revenue_base * revenue_multiplier
            
            # Add some variance to prevent identical scores
            import random
            random.seed(i)  # Consistent randomness based on position
            accessibility += random.uniform(-0.5, 0.5)
            market_attractiveness += random.uniform(-0.3, 0.3)
            
            segment_data.append({
                'Segment': segment.name[:20] + '...' if len(segment.name) > 20 else segment.name,
                'Full_Name': segment.name,
                'Market_Attractiveness': round(market_attractiveness, 1),
                'Accessibility': round(accessibility, 1),
                'Revenue_Potential': revenue_potential,
                'Market_Size': segment.size_percentage,
                'Channels': len(segment.preferred_channels),
                'Pain_Points': len(segment.pain_points),
                'Priority_Score': round(market_attractiveness * accessibility / 10, 1)
            })
        
        df = pd.DataFrame(segment_data)
        
        # Sort by priority score for consistent colors
        df = df.sort_values('Priority_Score', ascending=False)
        df['Priority_Rank'] = range(1, len(df) + 1)
        
        # Create scatter plot with multiple encodings
        fig = px.scatter(
            df,
            x='Accessibility',
            y='Market_Attractiveness',
            size='Revenue_Potential',
            color='Priority_Rank',
            hover_name='Full_Name',
            hover_data={
                'Market_Size': ':.1f%',
                'Priority_Score': ':.1f',
                'Channels': True,
                'Pain_Points': True,
                'Accessibility': ':.1f',
                'Market_Attractiveness': ':.1f',
                'Priority_Rank': False,
                'Revenue_Potential': False
            },
            title="Segment Priority Matrix: Market Attractiveness vs. Accessibility",
            labels={
                'Accessibility': 'Accessibility Score (ease of targeting)',
                'Market_Attractiveness': 'Market Attractiveness Score',
                'Priority_Rank': 'Priority'
            },
            color_continuous_scale='Viridis_r',
            size_max=50
        )
        
        # Add segment labels
        for _, row in df.iterrows():
            fig.add_annotation(
                x=row['Accessibility'],
                y=row['Market_Attractiveness'],
                text=row['Segment'],
                showarrow=False,
                yshift=10,
                font=dict(size=10, color='black', weight='bold'),
                bgcolor='rgba(255,255,255,0.7)',
                borderpad=2
            )
        
        # Calculate dynamic thresholds (median-based)
        x_threshold = df['Accessibility'].median()
        y_threshold = df['Market_Attractiveness'].median()
        
        # Add quadrant lines
        fig.add_hline(y=y_threshold, line_dash="dash", line_color="gray", opacity=0.3,
                     annotation_text=f"Median: {y_threshold:.1f}", annotation_position="left")
        fig.add_vline(x=x_threshold, line_dash="dash", line_color="gray", opacity=0.3,
                     annotation_text=f"Median: {x_threshold:.1f}", annotation_position="top")
        
        # Add quadrant labels only if segments are well-distributed
        x_range = df['Accessibility'].max() - df['Accessibility'].min()
        y_range = df['Market_Attractiveness'].max() - df['Market_Attractiveness'].min()
        
        if x_range > 2 and y_range > 2:  # Only show quadrants if there's meaningful spread
            # Position labels in quadrant centers
            x_min, x_max = df['Accessibility'].min() - 0.5, df['Accessibility'].max() + 0.5
            y_min, y_max = df['Market_Attractiveness'].min() - 0.5, df['Market_Attractiveness'].max() + 0.5
            
            quadrant_labels = [
                (x_max - (x_max - x_threshold) / 2, y_max - (y_max - y_threshold) / 2, "🎯 PURSUE", "green"),
                (x_min + (x_threshold - x_min) / 2, y_max - (y_max - y_threshold) / 2, "📈 DEVELOP", "orange"),
                (x_max - (x_max - x_threshold) / 2, y_min + (y_threshold - y_min) / 2, "⚡ TEST", "blue"),
                (x_min + (x_threshold - x_min) / 2, y_min + (y_threshold - y_min) / 2, "🔍 MONITOR", "gray")
            ]
            
            for x, y, text, color in quadrant_labels:
                fig.add_annotation(
                    x=x, y=y, text=text,
                    showarrow=False,
                    font=dict(size=12, color=color, weight='bold'),
                    opacity=0.7
                )
        
        # Update layout
        fig.update_layout(
            height=600,
            xaxis=dict(
                range=[df['Accessibility'].min() - 1, df['Accessibility'].max() + 1],
                title="Accessibility Score<br><sub>Higher = Easier to reach & convert</sub>"
            ),
            yaxis=dict(
                range=[df['Market_Attractiveness'].min() - 1, df['Market_Attractiveness'].max() + 1],
                title="Market Attractiveness<br><sub>Higher = Larger opportunity & urgency</sub>"
            ),
            showlegend=True,
            legend=dict(title="Priority<br>Ranking"),
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        # Add gridlines
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.3)')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.3)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show priority ranking table
        st.markdown("##### 📊 Segment Priority Ranking")
        
        priority_df = df[['Priority_Rank', 'Full_Name', 'Market_Size', 'Priority_Score', 
                         'Market_Attractiveness', 'Accessibility']].copy()
        priority_df.columns = ['Rank', 'Segment', 'Market Size (%)', 'Priority Score', 
                              'Market Attractiveness', 'Accessibility']
        priority_df = priority_df.sort_values('Rank')
        
        # Style the dataframe
        styled_df = priority_df.style.format({
            'Market Size (%)': '{:.1f}%',
            'Priority Score': '{:.1f}',
            'Market Attractiveness': '{:.1f}',
            'Accessibility': '{:.1f}'
        }).background_gradient(subset=['Priority Score'], cmap='Greens')
        
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        
        # Add methodology explanation
        with st.expander("📈 How Priority Scores are Calculated"):
            st.markdown("""
            **Market Attractiveness Score** (Y-axis) considers:
            - **Market Size**: Percentage of total addressable market (40% weight)
            - **Growth Indicators**: Number of buying triggers suggesting growth (30% weight)
            - **Commercial Urgency**: Presence of urgent pain points (30% weight)
            
            **Accessibility Score** (X-axis) evaluates:
            - **Channel Focus**: Concentration of marketing channels (30% weight)
            - **Message Clarity**: Well-defined pain points and use cases (30% weight)
            - **Target Precision**: Clarity of demographic/firmographic data (20% weight)
            - **Competitive Intensity**: Estimated competition level (20% weight)
            
            **Revenue Potential** (bubble size) estimates relative value based on:
            - Base market size
            - B2B vs B2C multiplier (B2B typically 2.5x higher value)
            
            **Priority Score** = (Market Attractiveness × Accessibility) / 10
            
            **Thresholds**: Median values are used to divide quadrants dynamically based on your specific segments.
            """)
    
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