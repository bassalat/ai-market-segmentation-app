import streamlit as st
import os
from dotenv import load_dotenv
from components.questionnaire import render_questionnaire
from components.results_dashboard import render_results_dashboard
from components.export_handler import render_export_options
from services.segmentation_engine import SegmentationEngine
from models.user_inputs import UserInputs, BasicInfo, BusinessModel

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Market Segmentation Tool",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Version: 1.1.0 - Fixed matplotlib dependency issue

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .cta-button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border: none;
        border-radius: 50px;
        font-size: 1.1rem;
        font-weight: bold;
        cursor: pointer;
        margin: 1rem 0;
    }
    
    .step-indicator {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    
    .step {
        padding: 0.5rem 1rem;
        margin: 0 0.5rem;
        border-radius: 20px;
        background: #f0f0f0;
        color: #666;
    }
    
    .step.active {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .segment-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e0e0e0;
        transition: transform 0.3s ease;
    }
    
    .segment-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .segment-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .segment-icon {
        font-size: 2rem;
        margin-right: 1rem;
    }
    
    .segment-name {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    
    .segment-size {
        background: #667eea;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.9rem;
        margin-left: auto;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'page' not in st.session_state:
        st.session_state.page = 'landing'
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = None
    if 'segmentation_results' not in st.session_state:
        st.session_state.segmentation_results = None
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False

def render_landing_page():
    """Render the landing page with hero section and CTA"""
    
    st.markdown("""
    <div class="main-header">
        <h1 class="hero-title">🎯 AI Market Segmentation</h1>
        <p class="hero-subtitle">Transform your go-to-market strategy with AI-powered customer segmentation</p>
        <p>Discover your ideal customer segments in minutes, not months</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 AI-Powered Analysis</h3>
            <p>Claude AI analyzes your business and market data to identify distinct customer segments with precision.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 Real-time Insights</h3>
            <p>Get live market research, competitor analysis, and trend identification as your segments are created.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📈 Actionable Reports</h3>
            <p>Download professional PDF reports with detailed personas, messaging frameworks, and implementation roadmaps.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Process overview
    st.markdown("### How it works")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **1. Share Your Business**  
        Tell us about your company, industry, and target market through our intelligent questionnaire.
        """)
    
    with col2:
        st.markdown("""
        **2. AI Analysis**  
        Our AI searches the web for market data and analyzes your business to identify opportunities.
        """)
    
    with col3:
        st.markdown("""
        **3. Get Segments**  
        Receive detailed customer segments with personas, pain points, and messaging recommendations.
        """)
    
    with col4:
        st.markdown("""
        **4. Download Report**  
        Get a professional PDF report with implementation roadmap and success metrics.
        """)
    
    st.markdown("---")
    
    # CTA section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Ready to discover your market segments?")
        
        if st.button("🚀 Start Market Segmentation", type="primary", use_container_width=True):
            st.session_state.page = 'questionnaire'
            st.rerun()
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; opacity: 0.7;">
            ✅ No signup required &nbsp;&nbsp; ⚡ Results in 5-10 minutes &nbsp;&nbsp; 🔒 Powered by Claude AI
        </div>
        """, unsafe_allow_html=True)

def render_step_indicator(current_step: str):
    """Render step indicator"""
    steps = {
        'questionnaire': 'Questionnaire',
        'processing': 'AI Analysis',
        'results': 'Results',
        'export': 'Export'
    }
    
    step_html = '<div class="step-indicator">'
    for step_key, step_name in steps.items():
        active_class = 'active' if step_key == current_step else ''
        step_html += f'<div class="step {active_class}">{step_name}</div>'
    step_html += '</div>'
    
    st.markdown(step_html, unsafe_allow_html=True)

def main():
    """Main application function"""
    initialize_session_state()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("⚠️ ANTHROPIC_API_KEY not found. Please set up your API key in the .env file.")
        st.stop()
    
    # Navigation
    if st.session_state.page == 'landing':
        render_landing_page()
    
    elif st.session_state.page == 'questionnaire':
        render_step_indicator('questionnaire')
        
        # Back button
        if st.button("← Back to Home", type="secondary"):
            st.session_state.page = 'landing'
            st.rerun()
        
        st.markdown("## Tell us about your business")
        user_inputs = render_questionnaire()
        
        if user_inputs:
            st.session_state.user_inputs = user_inputs
            st.session_state.page = 'processing'
            st.rerun()
    
    elif st.session_state.page == 'processing':
        render_step_indicator('processing')
        
        st.markdown("## 🔄 Analyzing your market...")
        st.markdown("Our AI is working hard to identify your market segments. This may take a few minutes.")
        
        try:
            # Get Serper API key from environment or use hardcoded key
            serper_api_key = os.getenv('SERPER_API_KEY', 'd02a86009eaa117bdf00747b6fcce9aa14fc1128')
            
            engine = SegmentationEngine(serper_api_key=serper_api_key)
            results = engine.process_segmentation(st.session_state.user_inputs)
            st.session_state.segmentation_results = results
            st.session_state.processing_complete = True
            st.session_state.page = 'results'
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred during processing: {str(e)}")
            st.markdown("Please try again or contact support if the issue persists.")
            
            if st.button("← Try Again"):
                st.session_state.page = 'questionnaire'
                st.rerun()
    
    elif st.session_state.page == 'results':
        render_step_indicator('results')
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("← Back to Questionnaire", type="secondary"):
                st.session_state.page = 'questionnaire'
                st.rerun()
        
        with col3:
            if st.button("Download Report →", type="primary"):
                st.session_state.page = 'export'
                st.rerun()
        
        if st.session_state.segmentation_results:
            render_results_dashboard(st.session_state.segmentation_results)
        else:
            st.error("No segmentation results found. Please start over.")
    
    elif st.session_state.page == 'export':
        render_step_indicator('export')
        
        # Back button
        if st.button("← Back to Results", type="secondary"):
            st.session_state.page = 'results'
            st.rerun()
        
        if st.session_state.segmentation_results:
            render_export_options(st.session_state.segmentation_results, st.session_state.user_inputs)
        else:
            st.error("No segmentation results found. Please start over.")

if __name__ == "__main__":
    main()