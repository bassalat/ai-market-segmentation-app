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
        
        # Document Upload Section
        st.markdown("---")
        st.markdown("### 📄 Additional Context (Optional)")
        st.markdown("Upload documents to provide additional context for your market analysis:")
        
        # Create expandable section for document upload
        with st.expander("📁 Upload Documents (PDF, CSV, Excel)", expanded=False):
            st.markdown("""
            **Supported file types:**
            - **PDF**: Market reports, research documents, business plans
            - **CSV**: Customer data, market data, survey results  
            - **Excel**: Financial data, market analysis, competitor data
            
            **How this helps:**
            - Provides specific context about your market and customers
            - Incorporates your existing data into the analysis
            - Creates more accurate and personalized market segments
            - Uses your internal insights to validate external research
            """)
            
            uploaded_files = st.file_uploader(
                "Choose files to upload",
                type=['pdf', 'csv', 'xlsx', 'xls'],
                accept_multiple_files=True,
                help="Upload relevant documents that contain information about your market, customers, or business data"
            )
            
            # Process uploaded files
            document_context = None
            if uploaded_files:
                from services.document_processor import DocumentProcessor
                
                with st.spinner("Processing uploaded documents..."):
                    processor = DocumentProcessor()
                    processed_result = processor.process_uploaded_files(uploaded_files)
                    
                    if processed_result['has_context']:
                        document_context = processed_result
                        
                        # Show processing results
                        st.success(f"✅ Successfully processed {processed_result['file_count']} file(s)")
                        
                        # Display summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Files Processed", processed_result['file_count'])
                        with col2:
                            st.metric("Content Length", f"{processed_result['content_length']:,} chars")
                        with col3:
                            st.metric("Data Points", processed_result['data_points'])
                        
                        # Show summary
                        st.info(f"📋 **Context Summary:** {processed_result['summary']}")
                        
                        # Show file details
                        if st.checkbox("Show detailed file analysis", key="show_file_details"):
                            for i, file_summary in enumerate(processed_result['processed_content']['file_summaries']):
                                st.write(f"**File {i+1}:** {file_summary}")
                            
                            if processed_result['processed_content']['key_insights']:
                                st.write("**Key Insights Extracted:**")
                                for insight in processed_result['processed_content']['key_insights']:
                                    st.write(f"• {insight}")
        
        # Store document context in session state
        st.session_state.form_data['document_context'] = document_context
        
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
            
            # Create document context object if available
            doc_context = None
            if document_context:
                from models.user_inputs import DocumentContext
                doc_context = DocumentContext(
                    has_context=document_context['has_context'],
                    processed_content=document_context['processed_content'],
                    summary=document_context['summary'],
                    file_count=document_context['file_count'],
                    content_length=document_context['content_length'],
                    data_points=document_context['data_points']
                )
            
            user_inputs = UserInputs(
                basic_info=basic_info,
                b2b_inputs=b2b_inputs,
                b2c_inputs=b2c_inputs,
                document_context=doc_context
            )
            
            return user_inputs
    
    return None

def render_b2b_questions():
    """Render B2B specific questions per PRD specifications"""
    
    st.markdown("**Complete the following to generate comprehensive B2B market segments:**")
    st.markdown("*Questions marked with ⭐⭐⭐ are critical for accurate segmentation*")
    
    # Industry & Target Customer Section (⭐⭐⭐ Priority)
    st.markdown("#### 🏢 Industry & Target Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        target_company_types = st.text_input(
            "⭐⭐⭐ What type of companies do you want to sell to?",
            value=st.session_state.form_data.get('target_company_types', ''),
            placeholder="e.g., fintech, HR tech, retail, healthcare SaaS, manufacturing",
            help="This anchors use case and pain point mapping"
        )
        
        target_company_sizes = st.multiselect(
            "⭐⭐⭐ Company sizes you're targeting",
            options=["Startup", "Small/Medium Business", "Mid-Market", "Enterprise"],
            default=st.session_state.form_data.get('target_company_sizes', ["Small/Medium Business", "Mid-Market"]),
            help="Determines deal complexity and pricing strategy"
        )
    
    with col2:
        geographic_focus = st.multiselect(
            "⭐⭐ Geographic focus",
            options=[
                "Global", "North America", "Europe", "Asia Pacific", "Latin America", "Middle East", "Africa",
                "United States", "Canada", "United Kingdom", "Germany", "France", "Australia", 
                "India", "China", "Japan", "Singapore", "Brazil", "Mexico", "UAE", "Saudi Arabia", "Pakistan"
            ],
            default=st.session_state.form_data.get('geographic_focus', ["United States"]),
            help="Shapes compliance, channel, and GTM rollout"
        )
        
        target_industries = st.multiselect(
            "Target Industries (if specific)",
            options=[
                "Technology/SaaS", "Healthcare", "Financial Services", "Manufacturing",
                "Retail/E-commerce", "Education", "Government", "Media", "Real Estate",
                "Professional Services", "Non-profit", "Logistics", "Energy", "Other"
            ],
            default=st.session_state.form_data.get('target_industries', [])
        )
    
    # Buyer Roles Section (⭐⭐⭐ Priority)
    st.markdown("#### 👥 Buyer Roles & Decision Making")
    
    decision_maker_roles = st.multiselect(
        "⭐⭐⭐ Who typically makes the decision to buy your product?",
        options=[
            "CEO/Founder", "CTO/VP Engineering", "CMO/VP Marketing", "CFO/Finance",
            "VP Sales", "Operations Manager", "HR Director", "CISO/Security",
            "Procurement", "Department Manager", "End Users", "IT Administrator"
        ],
        default=st.session_state.form_data.get('decision_maker_roles', ["CEO/Founder"]),
        help="Essential for persona development and messaging fit"
    )
    
    # Pain Points & Use Cases Section (⭐⭐⭐ Priority)
    st.markdown("#### 🎯 Pain Points & Use Cases")
    
    col1, col2 = st.columns(2)
    
    with col1:
        main_problem_solved = st.text_area(
            "⭐⭐⭐ What's the main problem your product solves for customers?",
            value=st.session_state.form_data.get('main_problem_solved', ''),
            placeholder="Describe the core problem your solution addresses...",
            height=80,
            help="Essential for segmentation and value props"
        )
    
    with col2:
        practical_use_cases = st.text_area(
            "⭐⭐ Describe 1-2 practical ways your customers use the product",
            value=st.session_state.form_data.get('practical_use_cases', ''),
            placeholder="Specific use cases and scenarios...",
            height=80,
            help="Helps generate segment-specific use cases"
        )
    
    # Deal Dynamics Section (⭐⭐ Priority)
    st.markdown("#### 💰 Deal Dynamics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        deal_size_range = st.selectbox(
            "⭐⭐ Typical deal size range",
            options=[
                "Under $1K", "$1K - $10K", "$10K - $50K", "$50K - $100K",
                "$100K - $500K", "$500K - $1M", "Over $1M"
            ],
            index=st.session_state.form_data.get('deal_size_index', 2),
            help="Pricing + market sizing anchor"
        )
    
    with col2:
        sales_cycle_length = st.selectbox(
            "⭐⭐ How long does it usually take to close a deal?",
            options=[
                "Less than 1 month", "1-3 months", "3-6 months", 
                "6-12 months", "Over 12 months"
            ],
            index=st.session_state.form_data.get('sales_cycle_index', 1),
            help="GTM design (sales-led vs. PLG)"
        )
    
    # Tool Fit Section (⭐⭐ Priority)
    st.markdown("#### 🔧 Tool Integration & Fit")
    
    integration_requirements = st.text_area(
        "⭐⭐ Does your product need to integrate with tools your customers already use?",
        value=st.session_state.form_data.get('integration_requirements', ''),
        placeholder="List key integrations: CRM (Salesforce, HubSpot), productivity tools (Slack, Microsoft), etc.",
        height=80,
        help="Filters segments by compatibility"
    )
    
    # Triggers & Timing Section (⭐⭐ Priority)
    st.markdown("#### ⏰ Triggers & Timing")
    
    buying_triggers = st.text_area(
        "⭐⭐ When are customers more likely to buy?",
        value=st.session_state.form_data.get('buying_triggers', ''),
        placeholder="e.g., after funding, org change, new compliance requirements, security breach, rapid growth",
        height=80,
        help="Drives timing of GTM and campaigns"
    )
    
    # Lead Source & Budget Section (⭐⭐ Priority)
    st.markdown("#### 📈 Lead Sources & Budget")
    
    col1, col2 = st.columns(2)
    
    with col1:
        current_lead_sources = st.multiselect(
            "⭐⭐ Where do your best leads come from right now?",
            options=["Outbound sales", "Inbound marketing", "Referrals", "Partnerships", "Events", "Content marketing", "Paid ads", "Social media"],
            default=st.session_state.form_data.get('current_lead_sources', ["Inbound marketing"]),
            help="Affects channel mix and targeting"
        )
    
    with col2:
        customer_budget_sensitivity = st.selectbox(
            "⭐⭐ Customer budget characteristics",
            options=[
                "Tight budgets, very price-sensitive",
                "Budget-conscious but will pay for clear value",
                "Willing to pay premium for quality solutions",
                "Budget is rarely a constraint"
            ],
            index=st.session_state.form_data.get('budget_sensitivity_index', 1),
            help="Used for pricing sensitivity segmentation"
        )
    
    # Store all B2B data in session state
    st.session_state.form_data.update({
        'target_company_types': target_company_types,
        'target_company_sizes': target_company_sizes,
        'target_industries': target_industries,
        'geographic_focus': geographic_focus,
        'decision_maker_roles': decision_maker_roles,
        'main_problem_solved': main_problem_solved,
        'practical_use_cases': practical_use_cases,
        'deal_size_range': deal_size_range,
        'sales_cycle_length': sales_cycle_length,
        'integration_requirements': integration_requirements,
        'buying_triggers': buying_triggers,
        'current_lead_sources': current_lead_sources,
        'customer_budget_sensitivity': customer_budget_sensitivity
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
        target_company_types=[target_company_types] if target_company_types else [],
        target_company_sizes=company_size_enums,
        target_industries=target_industries,
        geographic_focus=geographic_focus,
        decision_maker_roles=decision_maker_roles,
        main_problem_solved=main_problem_solved,
        practical_use_cases=practical_use_cases,
        pain_points=f"{main_problem_solved} | {practical_use_cases}",  # Combine for backward compatibility
        deal_size_range=deal_size_range,
        sales_cycle_length=sales_cycle_length,
        integration_requirements=integration_requirements,
        buying_triggers=buying_triggers,
        current_lead_sources=current_lead_sources,
        customer_budget_sensitivity=customer_budget_sensitivity
    )

def render_b2c_questions():
    """Render B2C specific questions per PRD specifications"""
    
    st.markdown("**Complete the following to generate comprehensive B2C market segments:**")
    st.markdown("*Questions marked with ⭐⭐⭐ are critical for accurate segmentation*")
    
    # Target Customer Section (⭐⭐⭐ Priority)
    st.markdown("#### 👤 Target Customer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        primary_target_customer = st.text_input(
            "⭐⭐⭐ Who is your product primarily for?",
            value=st.session_state.form_data.get('primary_target_customer', ''),
            placeholder="e.g., students, working professionals, freelancers, mothers, Gen Z",
            help="Anchors all downstream segmentation and persona work"
        )
        
        target_age_groups = st.multiselect(
            "⭐⭐⭐ What age range do they usually fall in?",
            options=[
                "Gen Z (18-27)", "Millennials (28-43)", "Gen X (44-59)",
                "Baby Boomers (60-78)", "Silent Generation (79+)"
            ],
            default=st.session_state.form_data.get('target_age_groups', ["Millennials (28-43)"]),
            help="Informs creative tone and channel mix"
        )
    
    with col2:
        gender_focus = st.selectbox(
            "Gender Focus",
            options=["All", "Primarily Male", "Primarily Female", "Non-binary"],
            index=st.session_state.form_data.get('gender_focus_index', 0)
        )
        
        geographic_markets = st.multiselect(
            "⭐⭐ Are they mainly in a specific country, city, or region?",
            options=[
                "United States", "Canada", "United Kingdom", "Germany", "France", "Australia", 
                "India", "Brazil", "Mexico", "Japan", "South Korea", "Global", "Europe", "Asia Pacific", "Latin America"
            ],
            default=st.session_state.form_data.get('geographic_markets', ["United States"]),
            help="Affects cultural fit, timing, and localization"
        )
    
    # Buying Behavior Section (⭐⭐⭐ Priority)
    st.markdown("#### 🛒 Buying Behavior")
    
    col1, col2 = st.columns(2)
    
    with col1:
        purchase_frequency = st.selectbox(
            "⭐⭐⭐ How often do people usually buy your product?",
            options=[
                "One-time purchase", "Monthly", "Quarterly", "Bi-annually",
                "Annually", "Seasonally", "As needed", "Subscription-based"
            ],
            index=st.session_state.form_data.get('purchase_frequency_index', 6),
            help="Determines retention strategy and lifetime value"
        )
    
    with col2:
        purchase_context = st.selectbox(
            "⭐⭐ Is it usually something they buy for themselves, or as a gift or for others?",
            options=[
                "Primarily for themselves",
                "Mix of personal and gift purchases", 
                "Primarily as gifts for others",
                "For their family/household",
                "For their business/work"
            ],
            index=st.session_state.form_data.get('purchase_context_index', 0),
            help="Impacts messaging tone and triggers"
        )
    
    # Purchase Triggers Section (⭐⭐⭐ Priority)
    st.markdown("#### ⚡ Purchase Triggers")
    
    buying_triggers = st.text_area(
        "⭐⭐⭐ What are common situations or events when people decide to buy?",
        value=st.session_state.form_data.get('buying_triggers', ''),
        placeholder="e.g., holiday, stress, travel, life milestone, new job, moving, health concerns",
        height=80,
        help="Helps predict intent timing and campaign focus"
    )
    
    # Motivations & Lifestyle Section (⭐⭐⭐ Priority)
    st.markdown("#### 💭 Motivations & Lifestyle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        customer_priorities = st.text_area(
            "⭐⭐⭐ What do your customers care about most?",
            value=st.session_state.form_data.get('customer_priorities', ''),
            placeholder="e.g., convenience, looking good, saving money, feeling healthy, status, family time",
            height=80,
            help="Drives message resonance and emotional hooks"
        )
    
    with col2:
        price_vs_quality_focus = st.selectbox(
            "⭐⭐ Would you describe them as more price-conscious or quality-focused?",
            options=[
                "Very price-conscious, always looking for deals",
                "Price-conscious but will pay for clear value", 
                "Balanced between price and quality",
                "Quality-focused, willing to pay premium",
                "Premium buyers, price is rarely a factor"
            ],
            index=st.session_state.form_data.get('price_quality_index', 2),
            help="Important for pricing, bundling, and discounting"
        )
    
    # Product Fit Section (⭐⭐ Priority)
    st.markdown("#### 📦 Product Fit")
    
    col1, col2 = st.columns(2)
    
    with col1:
        product_type = st.selectbox(
            "⭐⭐ Is your product physical, digital, or a mix of both?",
            options=["Physical product", "Digital product/service", "Mix of physical and digital", "Service-based"],
            index=st.session_state.form_data.get('product_type_index', 1),
            help="Determines logistics and channel distribution"
        )
    
    with col2:
        discovery_channels = st.multiselect(
            "⭐⭐⭐ Where do your customers usually find out about products like yours?",
            options=[
                "Instagram", "TikTok", "Facebook", "YouTube", "Google Search", 
                "Friends/Word of mouth", "Email", "Influencers", "Traditional ads", "Retail stores", "Amazon", "Other online stores"
            ],
            default=st.session_state.form_data.get('discovery_channels', ["Google Search", "Instagram"]),
            help="Informs acquisition channels"
        )
    
    # Competitive Context Section (⭐⭐ Priority)
    st.markdown("#### 🏆 Competitive Context")
    
    existing_alternatives = st.text_area(
        "⭐⭐ Are there any popular alternatives or brands your customer might already be using or considering?",
        value=st.session_state.form_data.get('existing_alternatives', ''),
        placeholder="List key competitors, alternative solutions, or brands in your space...",
        height=80,
        help="Positions your product in the customer's mental landscape"
    )
    
    # Additional Demographics
    st.markdown("#### 📊 Additional Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
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
        customer_motivations = st.multiselect(
            "Customer Motivations (select all that apply)",
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
    
    # Store all B2C data in session state
    st.session_state.form_data.update({
        'primary_target_customer': primary_target_customer,
        'target_age_groups': target_age_groups,
        'gender_focus': gender_focus,
        'geographic_markets': geographic_markets,
        'purchase_frequency': purchase_frequency,
        'purchase_context': purchase_context,
        'buying_triggers': buying_triggers,
        'customer_priorities': customer_priorities,
        'price_vs_quality_focus': price_vs_quality_focus,
        'product_type': product_type,
        'discovery_channels': discovery_channels,
        'existing_alternatives': existing_alternatives,
        'income_brackets': income_brackets,
        'product_category': product_category,
        'customer_motivations': customer_motivations,
        'lifestyle_categories': lifestyle_categories
    })
    
    return B2CInputs(
        primary_target_customer=primary_target_customer,
        target_age_groups=target_age_groups,
        gender_focus=gender_focus,
        geographic_markets=geographic_markets,
        purchase_frequency=purchase_frequency,
        purchase_context=purchase_context,
        buying_triggers=buying_triggers,
        customer_priorities=customer_priorities,
        price_vs_quality_focus=price_vs_quality_focus,
        product_type=product_type,
        discovery_channels=discovery_channels,
        existing_alternatives=existing_alternatives,
        income_brackets=income_brackets,
        product_category=product_category,
        customer_motivations=customer_motivations,
        lifestyle_categories=lifestyle_categories
    )