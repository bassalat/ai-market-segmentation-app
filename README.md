# AI Market Segmentation Web App

A Streamlit-based web application that leverages Claude AI to perform intelligent market segmentation for go-to-market strategies.

## Features

- **Dynamic Questionnaire**: Adaptive forms that adjust based on B2B/B2C selection
- **AI-Powered Analysis**: Claude Sonnet 4 analyzes your business and market data
- **Real-time Processing**: Live updates showing segmentation progress
- **Interactive Dashboard**: Visual segment cards with detailed personas
- **Professional Reports**: Downloadable PDF reports with implementation roadmaps
- **Web Search Integration**: Automatic market research and trend analysis
- **Enhanced Market Intelligence**: Industry growth factors, CAGR, commercial urgencies
- **Competitive Analysis**: Top 5 competitors with funding and solution specialties
- **Role-Specific Insights**: Pain points mapped to specific business roles
- **Use Case Mapping**: Practical applications for each market segment

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Project Structure

```
market_segmentation_app/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── components/
│   ├── questionnaire.py       # Dynamic form components
│   ├── results_dashboard.py   # Results visualization
│   └── export_handler.py      # PDF generation and export
├── services/
│   ├── claude_service.py      # Claude API integration
│   ├── search_service.py      # Web search functionality
│   └── segmentation_engine.py # Core segmentation logic
└── models/
    ├── user_inputs.py         # Input validation models
    └── segment_models.py      # Data models for segments
```

## Usage

1. **Landing Page**: Introduction and overview of the tool
2. **Questionnaire**: Fill out business details and target market information
3. **Processing**: AI analyzes your data and performs market research
4. **Results**: Interactive dashboard with segment cards and visualizations
5. **Export**: Download comprehensive PDF reports

## API Requirements

- **Anthropic API Key**: Required for Claude AI integration
- The application uses Claude Sonnet 4 for market analysis and segmentation

## Features by Business Model

### B2B Segmentation
- Target company sizes and industries
- Deal size and sales cycle analysis
- Decision maker role mapping
- Enterprise vs SMB segmentation

### B2C Segmentation
- Demographic and psychographic analysis
- Lifestyle and interest categorization
- Purchase behavior patterns
- Geographic market analysis

## Generated Reports Include

- Executive summary with market overview
- Comprehensive market analysis and industry trends
- Industry growth factors and CAGR projections
- Commercial urgencies and market pressures
- Top 5 competitor analysis with funding and specialties
- Detailed segment profiles with rich personas
- Role-specific pain points and buying triggers
- Use cases and practical applications
- Messaging recommendations and channel preferences
- Implementation roadmap with priority matrix
- Success metrics and KPI frameworks

## Technical Notes

- Built with Streamlit for rapid development and deployment
- Uses Plotly for interactive visualizations
- ReportLab for professional PDF generation
- Implements session state management for multi-step flows
- Includes error handling and retry logic for API calls

## Deployment

The application can be deployed on:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure
- Any platform supporting Python web applications

Make sure to set the `ANTHROPIC_API_KEY` environment variable in your deployment environment.

## License

This project is for demonstration purposes and follows the original instructions for an AI-powered market segmentation tool.