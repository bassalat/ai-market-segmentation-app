import streamlit as st
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
from datetime import datetime
from models.segment_models import SegmentationResults
from models.user_inputs import UserInputs

def render_export_options(results: SegmentationResults, user_inputs: UserInputs):
    """Render export options and generate downloadable reports"""
    
    st.markdown("## 📥 Download Your Market Segmentation Report")
    
    st.markdown("""
    Your comprehensive market segmentation analysis is ready! Choose from the options below 
    to download your personalized report with all segment details, personas, and implementation recommendations.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Report preview
        st.markdown("### 📊 Report Contents")
        
        with st.expander("📋 Executive Summary", expanded=True):
            st.markdown(f"""
            - **Business:** {user_inputs.basic_info.company_name}
            - **Industry:** {user_inputs.basic_info.industry}
            - **Segments Identified:** {len(results.segments)}
            - **Total Market Opportunity:** {results.market_analysis.total_addressable_market}
            """)
        
        with st.expander("🎯 Detailed Segment Profiles"):
            for segment in results.segments:
                st.markdown(f"**{segment.name}** ({segment.size_percentage}% of market)")
        
        with st.expander("📈 Implementation Roadmap"):
            st.markdown("90-day action plan with prioritized segments and quick wins")
        
        with st.expander("📊 Market Analysis"):
            st.markdown("Industry trends, competitive landscape, and market opportunities")
    
    with col2:
        st.markdown("### 🎯 Export Options")
        
        # PDF Report Generation
        if st.button("📄 Download PDF Report", type="primary", use_container_width=True):
            pdf_buffer = generate_pdf_report(results, user_inputs)
            
            st.download_button(
                label="📥 Download Full Report (PDF)",
                data=pdf_buffer.getvalue(),
                file_name=f"market_segmentation_report_{user_inputs.basic_info.company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        # JSON Export for data integration
        if st.button("💾 Download Data (JSON)", type="secondary", use_container_width=True):
            json_data = export_to_json(results, user_inputs)
            
            st.download_button(
                label="📥 Download Data (JSON)",
                data=json_data,
                file_name=f"segmentation_data_{user_inputs.basic_info.company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.markdown("---")
        
        # Additional options
        st.markdown("### 🔄 What's Next?")
        
        if st.button("🔄 Start New Analysis", use_container_width=True):
            # Clear session state and restart
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = 'landing'
            st.rerun()
        
        if st.button("💡 Get Implementation Help", use_container_width=True):
            st.info("""
            **Next Steps:**
            1. Review each segment's messaging hooks
            2. Set up tracking for key metrics
            3. Create targeted campaigns
            4. A/B test different approaches
            5. Monitor and optimize performance
            """)
        
        if st.button("📞 Schedule Consultation", use_container_width=True):
            st.info("""
            **Professional Services Available:**
            - Strategy refinement sessions
            - Campaign development
            - Implementation support
            - Performance optimization
            """)

def generate_pdf_report(results: SegmentationResults, user_inputs: UserInputs) -> io.BytesIO:
    """Generate a comprehensive PDF report"""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2E4F99')
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#2E4F99')
    )
    
    # Title Page
    elements.append(Paragraph("Market Segmentation Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Company info table
    company_data = [
        ['Company:', user_inputs.basic_info.company_name],
        ['Industry:', user_inputs.basic_info.industry],
        ['Business Model:', user_inputs.basic_info.business_model.value],
        ['Report Date:', datetime.now().strftime('%B %d, %Y')]
    ]
    
    company_table = Table(company_data, colWidths=[2*inch, 4*inch])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F2F6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(company_table)
    elements.append(Spacer(1, 30))
    
    # Executive Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_text = f"""
    This report presents a comprehensive market segmentation analysis for {user_inputs.basic_info.company_name}, 
    identifying {len(results.segments)} distinct customer segments within the {user_inputs.basic_info.industry} industry. 
    The analysis reveals significant market opportunities with actionable insights for go-to-market strategy development.
    
    Total Addressable Market: {results.market_analysis.total_addressable_market}
    """
    elements.append(Paragraph(summary_text, styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Key Insights
    elements.append(Paragraph("Key Market Insights", heading_style))
    for i, insight in enumerate(results.market_analysis.key_insights, 1):
        elements.append(Paragraph(f"{i}. {insight}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    elements.append(PageBreak())
    
    # Market Analysis
    elements.append(Paragraph("Market Analysis", title_style))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Industry Trends", heading_style))
    for trend in results.market_analysis.industry_trends:
        elements.append(Paragraph(f"• {trend}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    if results.market_analysis.competitive_landscape:
        elements.append(Paragraph("Competitive Landscape", heading_style))
        elements.append(Paragraph(results.market_analysis.competitive_landscape, styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Industry growth factors
    if hasattr(results.market_analysis, 'industry_growth_factors') and results.market_analysis.industry_growth_factors:
        elements.append(Paragraph("Industry Growth Factors", heading_style))
        for factor in results.market_analysis.industry_growth_factors:
            elements.append(Paragraph(f"• {factor}", styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Industry CAGR
    if hasattr(results.market_analysis, 'industry_cagr') and results.market_analysis.industry_cagr:
        elements.append(Paragraph("Industry Growth Rate", heading_style))
        elements.append(Paragraph(f"CAGR: {results.market_analysis.industry_cagr}", styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Commercial urgencies
    if hasattr(results.market_analysis, 'commercial_urgencies') and results.market_analysis.commercial_urgencies:
        elements.append(Paragraph("Commercial Urgencies", heading_style))
        for urgency in results.market_analysis.commercial_urgencies:
            elements.append(Paragraph(f"• {urgency}", styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Top competitors
    if hasattr(results.market_analysis, 'top_competitors') and results.market_analysis.top_competitors:
        elements.append(Paragraph("Top Competitors", heading_style))
        
        competitor_data = [['Company', 'Funding', 'Specialty', 'Position']]
        for comp in results.market_analysis.top_competitors[:5]:
            competitor_data.append([
                comp.name,
                comp.funding,
                comp.solution_specialty[:50] + "..." if len(comp.solution_specialty) > 50 else comp.solution_specialty,
                comp.market_position[:50] + "..." if len(comp.market_position) > 50 else comp.market_position
            ])
        
        competitor_table = Table(competitor_data, colWidths=[1.5*inch, 1.5*inch, 2*inch, 1.5*inch])
        competitor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F2F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(competitor_table)
        elements.append(Spacer(1, 20))
    
    elements.append(PageBreak())
    
    # Segment Profiles
    elements.append(Paragraph("Detailed Segment Profiles", title_style))
    
    for i, segment in enumerate(results.segments, 1):
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(f"Segment {i}: {segment.name}", heading_style))
        
        # Segment overview table
        segment_data = [
            ['Market Share:', f"{segment.size_percentage}%"],
            ['Size Estimation:', segment.size_estimation],
        ]
        
        segment_table = Table(segment_data, colWidths=[2*inch, 4*inch])
        segment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F2F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(segment_table)
        elements.append(Spacer(1, 15))
        
        # Characteristics
        if segment.characteristics:
            elements.append(Paragraph("Key Characteristics:", styles['Heading4']))
            for char in segment.characteristics:
                elements.append(Paragraph(f"• {char}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Pain Points
        if segment.pain_points:
            elements.append(Paragraph("Primary Pain Points:", styles['Heading4']))
            for pain in segment.pain_points:
                elements.append(Paragraph(f"• {pain}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Messaging Hooks
        if segment.messaging_hooks:
            elements.append(Paragraph("Messaging Recommendations:", styles['Heading4']))
            for hook in segment.messaging_hooks:
                elements.append(Paragraph(f"• {hook}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Preferred Channels
        if segment.preferred_channels:
            elements.append(Paragraph("Preferred Channels:", styles['Heading4']))
            channel_text = ", ".join(segment.preferred_channels)
            elements.append(Paragraph(channel_text, styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Use Cases
        if hasattr(segment, 'use_cases') and segment.use_cases:
            elements.append(Paragraph("Use Cases:", styles['Heading4']))
            for use_case in segment.use_cases:
                elements.append(Paragraph(f"• {use_case}", styles['Normal']))
            elements.append(Spacer(1, 10))
        
        # Role-specific Pain Points
        if hasattr(segment, 'role_specific_pain_points') and segment.role_specific_pain_points:
            elements.append(Paragraph("Role-Specific Pain Points:", styles['Heading4']))
            for role, pains in segment.role_specific_pain_points.items():
                if pains:
                    elements.append(Paragraph(f"{role}:", styles['Heading5']))
                    for pain in pains:
                        elements.append(Paragraph(f"  • {pain}", styles['Normal']))
            elements.append(Spacer(1, 15))
        
        if i < len(results.segments):
            elements.append(PageBreak())
    
    # Implementation Roadmap
    elements.append(PageBreak())
    elements.append(Paragraph("Implementation Roadmap", title_style))
    elements.append(Spacer(1, 20))
    
    for phase, tasks in results.implementation_roadmap.items():
        elements.append(Paragraph(phase, heading_style))
        for task in tasks:
            elements.append(Paragraph(f"• {task}", styles['Normal']))
        elements.append(Spacer(1, 15))
    
    # Quick Wins
    elements.append(Paragraph("Quick Wins", heading_style))
    for win in results.quick_wins:
        elements.append(Paragraph(f"• {win}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    # Success Metrics
    elements.append(Paragraph("Success Metrics", heading_style))
    for metric in results.success_metrics:
        elements.append(Paragraph(f"• {metric}", styles['Normal']))
    
    # Appendix
    elements.append(PageBreak())
    elements.append(Paragraph("Methodology & Data Sources", title_style))
    methodology_text = """
    This market segmentation analysis was conducted using AI-powered analysis combining:
    
    • Business information provided by the client
    • Real-time web research for market trends and competitive intelligence
    • Claude AI's advanced natural language processing for pattern recognition
    • Industry best practices for market segmentation
    • Demographic and psychographic analysis frameworks
    
    The segments identified represent distinct customer groups based on behavioral patterns, 
    needs, preferences, and market characteristics. Implementation recommendations are based 
    on proven go-to-market strategies adapted to your specific industry and business model.
    """
    elements.append(Paragraph(methodology_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def export_to_json(results: SegmentationResults, user_inputs: UserInputs) -> str:
    """Export segmentation data to JSON format"""
    import json
    
    export_data = {
        "metadata": {
            "company_name": user_inputs.basic_info.company_name,
            "industry": user_inputs.basic_info.industry,
            "business_model": user_inputs.basic_info.business_model.value,
            "generated_date": datetime.now().isoformat(),
            "total_segments": len(results.segments)
        },
        "market_analysis": {
            "total_addressable_market": results.market_analysis.total_addressable_market,
            "key_insights": results.market_analysis.key_insights,
            "industry_trends": results.market_analysis.industry_trends,
            "competitive_landscape": results.market_analysis.competitive_landscape
        },
        "segments": []
    }
    
    for segment in results.segments:
        segment_data = {
            "name": segment.name,
            "size_percentage": segment.size_percentage,
            "size_estimation": segment.size_estimation,
            "characteristics": segment.characteristics,
            "pain_points": segment.pain_points,
            "buying_triggers": segment.buying_triggers,
            "preferred_channels": segment.preferred_channels,
            "messaging_hooks": segment.messaging_hooks,
            "persona_description": segment.persona_description,
            "demographics": segment.demographics,
            "psychographics": segment.psychographics
        }
        export_data["segments"].append(segment_data)
    
    export_data["implementation"] = {
        "roadmap": results.implementation_roadmap,
        "quick_wins": results.quick_wins,
        "success_metrics": results.success_metrics
    }
    
    return json.dumps(export_data, indent=2)