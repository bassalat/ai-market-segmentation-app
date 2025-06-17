import pandas as pd
import PyPDF2
import io
import streamlit as st
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re
import openpyxl
from models.segment_models import DataSource, ContentType, SourceQuality

class DocumentProcessor:
    """Process uploaded documents (PDF, CSV, Excel) to extract context for market analysis"""
    
    def __init__(self):
        self.supported_formats = {
            'pdf': ['application/pdf'],
            'csv': ['text/csv', 'application/csv'],
            'excel': ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 
                     'application/vnd.ms-excel']
        }
        
    def process_uploaded_files(self, uploaded_files: List[Any]) -> Dict[str, Any]:
        """Process all uploaded files and extract relevant context"""
        
        if not uploaded_files:
            return {
                'has_context': False,
                'processed_content': {},
                'summary': "No additional context files provided.",
                'file_count': 0
            }
        
        processed_content = {
            'text_content': [],
            'structured_data': [],
            'key_insights': [],
            'data_sources': [],
            'file_summaries': []
        }
        
        for uploaded_file in uploaded_files:
            file_info = self._process_single_file(uploaded_file)
            if file_info:
                processed_content['text_content'].extend(file_info.get('text_content', []))
                processed_content['structured_data'].extend(file_info.get('structured_data', []))
                processed_content['key_insights'].extend(file_info.get('key_insights', []))
                processed_content['data_sources'].append(file_info.get('data_source'))
                processed_content['file_summaries'].append(file_info.get('summary', ''))
        
        # Generate comprehensive summary
        summary = self._generate_context_summary(processed_content, len(uploaded_files))
        
        return {
            'has_context': True,
            'processed_content': processed_content,
            'summary': summary,
            'file_count': len(uploaded_files),
            'content_length': sum(len(text) for text in processed_content['text_content']),
            'data_points': len(processed_content['structured_data'])
        }
    
    def _process_single_file(self, uploaded_file: Any) -> Optional[Dict[str, Any]]:
        """Process a single uploaded file based on its type"""
        
        try:
            file_type = self._detect_file_type(uploaded_file)
            
            if file_type == 'pdf':
                return self._process_pdf(uploaded_file)
            elif file_type == 'csv':
                return self._process_csv(uploaded_file)
            elif file_type == 'excel':
                return self._process_excel(uploaded_file)
            else:
                st.warning(f"Unsupported file type: {uploaded_file.name}")
                return None
                
        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            return None
    
    def _detect_file_type(self, uploaded_file: Any) -> str:
        """Detect file type from file extension and MIME type"""
        
        file_name = uploaded_file.name.lower()
        
        if file_name.endswith('.pdf'):
            return 'pdf'
        elif file_name.endswith('.csv'):
            return 'csv'
        elif file_name.endswith(('.xlsx', '.xls')):
            return 'excel'
        else:
            # Fallback to MIME type detection
            if hasattr(uploaded_file, 'type'):
                mime_type = uploaded_file.type
                for file_type, mime_types in self.supported_formats.items():
                    if mime_type in mime_types:
                        return file_type
        
        return 'unknown'
    
    def _process_pdf(self, uploaded_file: Any) -> Dict[str, Any]:
        """Extract text and insights from PDF files"""
        
        try:
            # Read PDF content
            pdf_content = uploaded_file.read()
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            text_content = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append({
                            'page': page_num + 1,
                            'content': page_text.strip(),
                            'length': len(page_text)
                        })
                except Exception as e:
                    st.warning(f"Could not extract text from page {page_num + 1}: {str(e)}")
            
            # Extract key insights from text
            all_text = ' '.join([page['content'] for page in text_content])
            key_insights = self._extract_insights_from_text(all_text)
            
            # Create data source
            data_source = DataSource(
                url=f"uploaded_file:{uploaded_file.name}",
                title=uploaded_file.name,
                organization="User Provided Document",
                content_type=ContentType.INDUSTRY_REPORT,
                source_quality=SourceQuality.TIER_2,  # User documents get Tier 2 quality
                confidence_score=0.8,
                relevance_score=1.0,  # User documents are highly relevant
                data_quality_rating=0.8
            )
            
            return {
                'file_name': uploaded_file.name,
                'file_type': 'PDF',
                'text_content': text_content,
                'structured_data': [],
                'key_insights': key_insights,
                'data_source': data_source,
                'summary': f"PDF document with {len(text_content)} pages and {len(all_text)} characters of content.",
                'page_count': len(text_content),
                'total_characters': len(all_text)
            }
            
        except Exception as e:
            st.error(f"Error processing PDF {uploaded_file.name}: {str(e)}")
            return None
    
    def _process_csv(self, uploaded_file: Any) -> Dict[str, Any]:
        """Extract data and insights from CSV files"""
        
        try:
            # Read CSV content
            df = pd.read_csv(uploaded_file)
            
            # Basic dataset information
            dataset_info = {
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data_types': df.dtypes.to_dict()
            }
            
            # Extract structured data insights
            structured_data = []
            
            # Identify potential market data columns
            market_columns = self._identify_market_columns(df.columns.tolist())
            
            for column in market_columns:
                if column in df.columns:
                    try:
                        # Extract statistics for numeric columns
                        if pd.api.types.is_numeric_dtype(df[column]):
                            stats = {
                                'column': column,
                                'type': 'numeric',
                                'mean': float(df[column].mean()) if df[column].notna().any() else None,
                                'median': float(df[column].median()) if df[column].notna().any() else None,
                                'min': float(df[column].min()) if df[column].notna().any() else None,
                                'max': float(df[column].max()) if df[column].notna().any() else None,
                                'count': int(df[column].count())
                            }
                            structured_data.append(stats)
                        else:
                            # Extract category distributions for categorical columns
                            value_counts = df[column].value_counts().head(10)
                            stats = {
                                'column': column,
                                'type': 'categorical',
                                'top_values': value_counts.to_dict(),
                                'unique_count': df[column].nunique(),
                                'count': int(df[column].count())
                            }
                            structured_data.append(stats)
                    except Exception as e:
                        st.warning(f"Could not analyze column {column}: {str(e)}")
            
            # Generate text summary
            text_summary = self._generate_csv_summary(df, dataset_info, structured_data)
            
            # Extract key insights
            key_insights = self._extract_insights_from_structured_data(structured_data, dataset_info)
            
            # Create data source
            data_source = DataSource(
                url=f"uploaded_file:{uploaded_file.name}",
                title=uploaded_file.name,
                organization="User Provided Data",
                content_type=ContentType.MARKET_RESEARCH,
                source_quality=SourceQuality.TIER_2,
                confidence_score=0.9,  # Structured data gets high confidence
                relevance_score=1.0,
                data_quality_rating=0.9
            )
            
            return {
                'file_name': uploaded_file.name,
                'file_type': 'CSV',
                'text_content': [{'content': text_summary, 'length': len(text_summary)}],
                'structured_data': structured_data,
                'key_insights': key_insights,
                'data_source': data_source,
                'summary': f"CSV dataset with {dataset_info['rows']:,} rows and {dataset_info['columns']} columns.",
                'dataset_info': dataset_info
            }
            
        except Exception as e:
            st.error(f"Error processing CSV {uploaded_file.name}: {str(e)}")
            return None
    
    def _process_excel(self, uploaded_file: Any) -> Dict[str, Any]:
        """Extract data and insights from Excel files"""
        
        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(uploaded_file)
            sheet_names = excel_file.sheet_names
            
            all_structured_data = []
            all_text_content = []
            combined_insights = []
            
            for sheet_name in sheet_names:
                try:
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                    
                    # Process each sheet like a CSV
                    sheet_info = {
                        'sheet_name': sheet_name,
                        'rows': len(df),
                        'columns': len(df.columns),
                        'column_names': df.columns.tolist()
                    }
                    
                    # Extract structured data for this sheet
                    market_columns = self._identify_market_columns(df.columns.tolist())
                    sheet_structured_data = []
                    
                    for column in market_columns:
                        if column in df.columns:
                            try:
                                if pd.api.types.is_numeric_dtype(df[column]):
                                    stats = {
                                        'sheet': sheet_name,
                                        'column': column,
                                        'type': 'numeric',
                                        'mean': float(df[column].mean()) if df[column].notna().any() else None,
                                        'median': float(df[column].median()) if df[column].notna().any() else None,
                                        'min': float(df[column].min()) if df[column].notna().any() else None,
                                        'max': float(df[column].max()) if df[column].notna().any() else None,
                                        'count': int(df[column].count())
                                    }
                                    sheet_structured_data.append(stats)
                            except Exception:
                                continue
                    
                    all_structured_data.extend(sheet_structured_data)
                    
                    # Generate sheet summary
                    sheet_summary = f"Sheet '{sheet_name}': {sheet_info['rows']:,} rows, {sheet_info['columns']} columns"
                    if sheet_structured_data:
                        sheet_summary += f", {len(sheet_structured_data)} analyzed columns"
                    
                    all_text_content.append({
                        'sheet': sheet_name,
                        'content': sheet_summary,
                        'length': len(sheet_summary)
                    })
                    
                except Exception as e:
                    st.warning(f"Could not process sheet '{sheet_name}': {str(e)}")
            
            # Generate overall insights
            key_insights = []
            if all_structured_data:
                key_insights = self._extract_insights_from_structured_data(all_structured_data, {
                    'sheets': len(sheet_names),
                    'total_columns': sum(len(data.get('column_names', [])) for data in all_structured_data)
                })
            
            # Create data source
            data_source = DataSource(
                url=f"uploaded_file:{uploaded_file.name}",
                title=uploaded_file.name,
                organization="User Provided Data",
                content_type=ContentType.MARKET_RESEARCH,
                source_quality=SourceQuality.TIER_2,
                confidence_score=0.9,
                relevance_score=1.0,
                data_quality_rating=0.9
            )
            
            return {
                'file_name': uploaded_file.name,
                'file_type': 'Excel',
                'text_content': all_text_content,
                'structured_data': all_structured_data,
                'key_insights': key_insights,
                'data_source': data_source,
                'summary': f"Excel workbook with {len(sheet_names)} sheets and structured data analysis.",
                'sheet_count': len(sheet_names),
                'sheet_names': sheet_names
            }
            
        except Exception as e:
            st.error(f"Error processing Excel {uploaded_file.name}: {str(e)}")
            return None
    
    def _identify_market_columns(self, column_names: List[str]) -> List[str]:
        """Identify columns that likely contain market-relevant data"""
        
        market_keywords = [
            'revenue', 'sales', 'price', 'cost', 'profit', 'market', 'size', 'growth',
            'share', 'segment', 'customer', 'user', 'acquisition', 'retention',
            'conversion', 'engagement', 'satisfaction', 'nps', 'churn', 'ltv',
            'cac', 'mrr', 'arr', 'volume', 'units', 'quantity', 'amount',
            'value', 'worth', 'budget', 'spend', 'investment', 'funding',
            'geography', 'region', 'country', 'industry', 'vertical', 'sector'
        ]
        
        relevant_columns = []
        
        for column in column_names:
            column_lower = column.lower()
            if any(keyword in column_lower for keyword in market_keywords):
                relevant_columns.append(column)
        
        # If no specific market columns found, include all columns (up to 10)
        if not relevant_columns:
            relevant_columns = column_names[:10]
        
        return relevant_columns
    
    def _extract_insights_from_text(self, text: str) -> List[str]:
        """Extract key insights from text content"""
        
        insights = []
        
        # Look for market size mentions
        market_size_patterns = [
            r'\$(\d+(?:\.\d+)?)\s*(billion|million|trillion)',
            r'market\s+size.*?\$(\d+(?:\.\d+)?)\s*(billion|million|trillion)',
            r'(\d+(?:\.\d+)?)\s*(billion|million|trillion).*?market'
        ]
        
        for pattern in market_size_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:3]:  # Top 3 market size mentions
                if isinstance(match, tuple) and len(match) >= 2:
                    insights.append(f"Market size reference: ${match[0]} {match[1]}")
        
        # Look for growth rate mentions
        growth_patterns = [
            r'(\d+(?:\.\d+)?)\s*%.*?growth',
            r'growth.*?(\d+(?:\.\d+)?)\s*%',
            r'CAGR.*?(\d+(?:\.\d+)?)\s*%'
        ]
        
        for pattern in growth_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:2]:  # Top 2 growth mentions
                insights.append(f"Growth rate reference: {match}%")
        
        # Look for competitor mentions
        competitor_patterns = [
            r'competitors?\s+include\s+([^.]+)',
            r'market\s+leaders?\s+([^.]+)',
            r'vs\.?\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)'
        ]
        
        for pattern in competitor_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:2]:  # Top 2 competitor mentions
                insights.append(f"Competitor reference: {match}")
        
        # Look for segment mentions
        segment_patterns = [
            r'segment[s]?\s+include\s+([^.]+)',
            r'customer\s+types?\s+([^.]+)',
            r'target\s+market[s]?\s+([^.]+)'
        ]
        
        for pattern in segment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:2]:  # Top 2 segment mentions
                insights.append(f"Segment reference: {match}")
        
        return insights[:10]  # Return top 10 insights
    
    def _extract_insights_from_structured_data(self, structured_data: List[Dict], dataset_info: Dict) -> List[str]:
        """Extract insights from structured/tabular data"""
        
        insights = []
        
        for data in structured_data:
            if data['type'] == 'numeric':
                column = data['column']
                
                # Revenue/sales insights
                if any(keyword in column.lower() for keyword in ['revenue', 'sales', 'income']):
                    if data['mean']:
                        insights.append(f"Average {column.lower()}: ${data['mean']:,.0f}")
                    if data['max']:
                        insights.append(f"Maximum {column.lower()}: ${data['max']:,.0f}")
                
                # Growth rate insights
                elif any(keyword in column.lower() for keyword in ['growth', 'rate', 'percent']):
                    if data['mean']:
                        insights.append(f"Average {column.lower()}: {data['mean']:.1f}%")
                
                # Customer/user insights
                elif any(keyword in column.lower() for keyword in ['customer', 'user', 'client']):
                    if data['count']:
                        insights.append(f"Total {column.lower()}: {data['count']:,}")
                
                # General numeric insights
                else:
                    if data['mean'] and data['count'] > 1:
                        insights.append(f"{column} analysis: {data['count']} data points, average {data['mean']:.2f}")
            
            elif data['type'] == 'categorical':
                column = data['column']
                top_values = data.get('top_values', {})
                
                if top_values:
                    top_category = list(top_values.keys())[0]
                    top_count = list(top_values.values())[0]
                    insights.append(f"Top {column.lower()}: {top_category} ({top_count} occurrences)")
        
        # Add dataset summary insights
        if 'rows' in dataset_info and 'columns' in dataset_info:
            insights.append(f"Dataset contains {dataset_info['rows']:,} records across {dataset_info['columns']} dimensions")
        
        return insights[:8]  # Return top 8 insights
    
    def _generate_csv_summary(self, df: pd.DataFrame, dataset_info: Dict, structured_data: List[Dict]) -> str:
        """Generate a text summary of CSV data"""
        
        summary_parts = []
        
        # Basic dataset info
        summary_parts.append(f"Dataset Analysis: {dataset_info['rows']:,} rows and {dataset_info['columns']} columns")
        
        # Column information
        if structured_data:
            numeric_cols = [d for d in structured_data if d['type'] == 'numeric']
            categorical_cols = [d for d in structured_data if d['type'] == 'categorical']
            
            if numeric_cols:
                summary_parts.append(f"Numeric columns analyzed: {', '.join([d['column'] for d in numeric_cols])}")
            
            if categorical_cols:
                summary_parts.append(f"Categorical columns analyzed: {', '.join([d['column'] for d in categorical_cols])}")
        
        # Data quality info
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            summary_parts.append(f"Data completeness varies by column (some missing values detected)")
        else:
            summary_parts.append("Complete dataset with no missing values")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_context_summary(self, processed_content: Dict, file_count: int) -> str:
        """Generate overall summary of uploaded context"""
        
        summary_parts = []
        
        # File count and types
        summary_parts.append(f"Processed {file_count} user-provided document(s)")
        
        # Content statistics
        total_text_length = sum(len(text.get('content', '')) for text in processed_content['text_content'])
        if total_text_length > 0:
            summary_parts.append(f"extracted {total_text_length:,} characters of text content")
        
        data_points = len(processed_content['structured_data'])
        if data_points > 0:
            summary_parts.append(f"analyzed {data_points} structured data points")
        
        insights_count = len(processed_content['key_insights'])
        if insights_count > 0:
            summary_parts.append(f"identified {insights_count} key insights")
        
        # Create final summary
        if len(summary_parts) > 1:
            return ". ".join(summary_parts) + ". This context will inform the market segmentation analysis."
        else:
            return "User context documents processed and ready for analysis integration."
    
    def format_context_for_claude(self, processed_context: Dict[str, Any]) -> str:
        """Format processed context for inclusion in Claude prompts"""
        
        if not processed_context.get('has_context', False):
            return ""
        
        content = processed_context['processed_content']
        formatted_parts = []
        
        # Add document summary
        formatted_parts.append("USER-PROVIDED CONTEXT:")
        formatted_parts.append(f"Summary: {processed_context['summary']}")
        formatted_parts.append("")
        
        # Add key insights
        if content['key_insights']:
            formatted_parts.append("KEY INSIGHTS FROM USER DOCUMENTS:")
            for insight in content['key_insights']:
                formatted_parts.append(f"- {insight}")
            formatted_parts.append("")
        
        # Add structured data insights
        if content['structured_data']:
            formatted_parts.append("STRUCTURED DATA ANALYSIS:")
            for data in content['structured_data'][:10]:  # Top 10 data points
                if data['type'] == 'numeric':
                    formatted_parts.append(f"- {data['column']}: Mean {data.get('mean', 'N/A')}, Count {data.get('count', 'N/A')}")
                else:
                    top_values = data.get('top_values', {})
                    if top_values:
                        top_item = list(top_values.items())[0]
                        formatted_parts.append(f"- {data['column']}: Top value '{top_item[0]}' ({top_item[1]} times)")
            formatted_parts.append("")
        
        # Add relevant text excerpts
        if content['text_content']:
            formatted_parts.append("RELEVANT TEXT CONTENT:")
            for text_item in content['text_content'][:5]:  # Top 5 text items
                content_text = text_item.get('content', '')
                if len(content_text) > 300:
                    content_text = content_text[:300] + "..."
                formatted_parts.append(f"- {content_text}")
            formatted_parts.append("")
        
        formatted_parts.append("Please incorporate this user-provided context into your market analysis and segmentation.")
        
        return "\n".join(formatted_parts)