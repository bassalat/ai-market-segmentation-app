import streamlit as st
from models.user_inputs import UserInputs, BasicInfo, B2BInputs, B2CInputs, BusinessModel, CompanySize

def render_questionnaire():
    """Render the dynamic questionnaire based on user selections"""
    
    # Initialize form data in session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    with st.form("market_segmentation_form"):
        st.markdown("### Basic Information")
        
        # Basic info section
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company/Product Name *",
                value=st.session_state.form_data.get('company_name', ''),
                placeholder="e.g., Acme Corp, MyApp"
            )
        
        with col2:
            industry = st.selectbox(
                "Industry/Category *",
                options=[
                    "Technology/Software",
                    "Healthcare",
                    "Financial Services",
                    "E-commerce/Retail",
                    "Education",
                    "Manufacturing",
                    "Professional Services",
                    "Media/Entertainment",
                    "Real Estate",
                    "Food & Beverage",
                    "Automotive",
                    "Energy",
                    "Non-profit",
                    "Other"
                ],
                index=0 if 'industry' not in st.session_state.form_data else [
                    "Technology/Software", "Healthcare", "Financial Services", "E-commerce/Retail",
                    "Education", "Manufacturing", "Professional Services", "Media/Entertainment",
                    "Real Estate", "Food & Beverage", "Automotive", "Energy", "Non-profit", "Other"
                ].index(st.session_state.form_data.get('industry', 'Technology/Software'))
            )
        
        business_model = st.selectbox(
            "Business Model *",
            options=["B2B", "B2C", "Both"],
            index=0 if 'business_model' not in st.session_state.form_data else 
            ["B2B", "B2C", "Both"].index(st.session_state.form_data.get('business_model', 'B2B'))
        )
        
        description = st.text_area(
            "Brief Description of Your Business *",
            value=st.session_state.form_data.get('description', ''),
            placeholder="Describe what your company does, your main products/services, and your value proposition...",
            height=100
        )
        
        # Store basic info in session state
        st.session_state.form_data.update({
            'company_name': company_name,
            'industry': industry,
            'business_model': business_model,
            'description': description
        })
        
        # Conditional sections based on business model
        b2b_inputs = None
        b2c_inputs = None
        
        if business_model in ["B2B", "Both"]:
            st.markdown("---")
            st.markdown("### B2B Specific Questions")
            
            b2b_inputs = render_b2b_questions()
        
        if business_model in ["B2C", "Both"]:
            st.markdown("---")
            st.markdown("### B2C Specific Questions")
            
            b2c_inputs = render_b2c_questions()
        
        # Submit button
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Generate Market Segments", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not all([company_name, industry, description]):
                st.error("Please fill in all required fields marked with *")
                return None
            
            if len(description) < 20:
                st.error("Please provide a more detailed business description (at least 20 characters)")
                return None
            
            # Create UserInputs object
            basic_info = BasicInfo(
                company_name=company_name,
                industry=industry,
                business_model=BusinessModel(business_model),
                description=description
            )
            
            user_inputs = UserInputs(
                basic_info=basic_info,
                b2b_inputs=b2b_inputs,
                b2c_inputs=b2c_inputs
            )
            
            return user_inputs
    
    return None

def render_b2b_questions():
    """Render B2B specific questions"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_company_sizes = st.multiselect(
            "Target Company Sizes",
            options=["Startup", "Small/Medium Business", "Mid-Market", "Enterprise"],
            default=st.session_state.form_data.get('target_company_sizes', ["Small/Medium Business", "Mid-Market"])
        )
        
        deal_size_range = st.selectbox(
            "Typical Deal Size Range",
            options=[
                "Under $1K",
                "$1K - $10K", 
                "$10K - $50K",
                "$50K - $100K",
                "$100K - $500K",
                "$500K - $1M",
                "Over $1M"
            ],
            index=st.session_state.form_data.get('deal_size_index', 2)
        )
        
        sales_cycle_length = st.selectbox(
            "Sales Cycle Length",
            options=[
                "Less than 1 month",
                "1-3 months",
                "3-6 months", 
                "6-12 months",
                "Over 12 months"
            ],
            index=st.session_state.form_data.get('sales_cycle_index', 1)
        )
    
    with col2:
        target_industries = st.multiselect(
            "Target Industries (if specific)",
            options=[
                "Technology", "Healthcare", "Financial Services", "Manufacturing",
                "Retail", "Education", "Government", "Media", "Real Estate",
                "Professional Services", "Non-profit", "Other"
            ],
            default=st.session_state.form_data.get('target_industries', [])
        )
        
        decision_maker_roles = st.multiselect(
            "Key Decision Maker Roles",
            options=[
                "CEO/Founder", "CTO/VP Engineering", "CMO/VP Marketing", "CFO/Finance",
                "VP Sales", "Operations Manager", "HR Director", "Procurement",
                "Department Manager", "End Users", "IT Administrator"
            ],
            default=st.session_state.form_data.get('decision_maker_roles', ["CEO/Founder"])
        )
        
        geographic_focus = st.multiselect(
            "Geographic Focus",
            options=[
                # Regions
                "Global", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East", "Africa",
                # Major Countries (alphabetical)
                "Australia", "Austria", "Belgium", "Brazil", "Canada", "China", "Denmark", 
                "Finland", "France", "Germany", "India", "Indonesia", "Ireland", "Israel",
                "Italy", "Japan", "Malaysia", "Mexico", "Netherlands", "New Zealand", 
                "Norway", "Philippines", "Poland", "Portugal", "Singapore", "South Africa",
                "South Korea", "Spain", "Sweden", "Switzerland", "Thailand", "Turkey",
                "United Arab Emirates", "United Kingdom", "United States", "Vietnam"
            ],
            default=st.session_state.form_data.get('geographic_focus', ["United States"])
        )
    
    pain_points = st.text_area(
        "Primary Customer Pain Points & Use Cases",
        value=st.session_state.form_data.get('pain_points', ''),
        placeholder="What specific problems does your solution solve? What use cases drive purchases?",
        height=80
    )
    
    # Store B2B data in session state
    st.session_state.form_data.update({
        'target_company_sizes': target_company_sizes,
        'target_industries': target_industries,
        'deal_size_range': deal_size_range,
        'sales_cycle_length': sales_cycle_length,
        'decision_maker_roles': decision_maker_roles,
        'pain_points': pain_points,
        'geographic_focus': geographic_focus
    })
    
    # Convert to enum format
    company_size_enums = []
    for size in target_company_sizes:
        if size == "Startup":
            company_size_enums.append(CompanySize.STARTUP)
        elif size == "Small/Medium Business":
            company_size_enums.append(CompanySize.SMB)
        elif size == "Mid-Market":
            company_size_enums.append(CompanySize.MID_MARKET)
        elif size == "Enterprise":
            company_size_enums.append(CompanySize.ENTERPRISE)
    
    return B2BInputs(
        target_company_sizes=company_size_enums,
        target_industries=target_industries,
        deal_size_range=deal_size_range,
        sales_cycle_length=sales_cycle_length,
        decision_maker_roles=decision_maker_roles,
        pain_points=pain_points,
        geographic_focus=geographic_focus
    )

def render_b2c_questions():
    """Render B2C specific questions"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_age_groups = st.multiselect(
            "Target Age Groups",
            options=[
                "Gen Z (18-27)", "Millennials (28-43)", "Gen X (44-59)",
                "Baby Boomers (60-78)", "Silent Generation (79+)"
            ],
            default=st.session_state.form_data.get('target_age_groups', ["Millennials (28-43)"])
        )
        
        gender_focus = st.selectbox(
            "Gender Focus",
            options=["All", "Primarily Male", "Primarily Female", "Non-binary"],
            index=st.session_state.form_data.get('gender_focus_index', 0)
        )
        
        income_brackets = st.multiselect(
            "Target Income Brackets",
            options=[
                "Under $25K", "$25K-$50K", "$50K-$75K", "$75K-$100K",
                "$100K-$150K", "$150K-$250K", "Over $250K"
            ],
            default=st.session_state.form_data.get('income_brackets', ["$50K-$75K", "$75K-$100K"])
        )
        
        product_category = st.selectbox(
            "Product Category",
            options=[
                "Consumer Electronics", "Fashion/Apparel", "Health/Beauty",
                "Home/Garden", "Food/Beverage", "Entertainment/Media",
                "Travel/Experience", "Education/Learning", "Fitness/Wellness",
                "Financial Services", "Software/Apps", "Other"
            ],
            index=st.session_state.form_data.get('product_category_index', 0)
        )
    
    with col2:
        geographic_markets = st.multiselect(
            "Geographic Markets",
            options=[
                "United States", "Canada", "United Kingdom", "Europe",
                "Australia", "Asia Pacific", "Latin America", "Global"
            ],
            default=st.session_state.form_data.get('geographic_markets', ["United States"])
        )
        
        purchase_frequency = st.selectbox(
            "Expected Purchase Frequency",
            options=[
                "One-time purchase", "Monthly", "Quarterly", "Bi-annually",
                "Annually", "As needed", "Subscription-based"
            ],
            index=st.session_state.form_data.get('purchase_frequency_index', 5)
        )
        
        customer_motivations = st.multiselect(
            "Primary Customer Motivations",
            options=[
                "Save money", "Save time", "Convenience", "Quality",
                "Status/Prestige", "Health/Wellness", "Self-improvement",
                "Entertainment", "Security/Safety", "Social connection",
                "Environmental impact", "Innovation/Technology"
            ],
            default=st.session_state.form_data.get('customer_motivations', ["Save time", "Convenience"])
        )
        
        lifestyle_categories = st.multiselect(
            "Lifestyle/Interest Categories",
            options=[
                "Tech Enthusiasts", "Health & Fitness", "Family-oriented",
                "Career-focused", "Outdoor/Adventure", "Creative/Artistic",
                "Social/Community", "Luxury/Premium", "Eco-conscious",
                "Budget-conscious", "Early adopters", "Traditional"
            ],
            default=st.session_state.form_data.get('lifestyle_categories', ["Tech Enthusiasts"])
        )
    
    # Store B2C data in session state
    st.session_state.form_data.update({
        'target_age_groups': target_age_groups,
        'gender_focus': gender_focus,
        'income_brackets': income_brackets,
        'geographic_markets': geographic_markets,
        'product_category': product_category,
        'purchase_frequency': purchase_frequency,
        'customer_motivations': customer_motivations,
        'lifestyle_categories': lifestyle_categories
    })
    
    return B2CInputs(
        target_age_groups=target_age_groups,
        gender_focus=gender_focus,
        income_brackets=income_brackets,
        geographic_markets=geographic_markets,
        product_category=product_category,
        purchase_frequency=purchase_frequency,
        customer_motivations=customer_motivations,
        lifestyle_categories=lifestyle_categories
    )