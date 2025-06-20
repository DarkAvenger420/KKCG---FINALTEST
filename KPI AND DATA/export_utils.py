import pandas as pd
import io
from datetime import datetime
import json
import base64

def export_dataset_csv(df):
    """
    Export the complete dataset as CSV
    
    Args:
        df: DataFrame with demand data
    
    Returns:
        CSV string data
    """
    return df.to_csv(index=False)

def create_insights_report_text(insights, insight_texts, recommendations):
    """
    Create a comprehensive insights report in text format
    
    Args:
        insights: Dictionary with computed insights
        insight_texts: List of insight text strings
        recommendations: List of recommendation strings
    
    Returns:
        Formatted text report
    """
    
    report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    KODI KURA CHITTI GAARE                       ║
║                  DEMAND ANALYTICS REPORT                        ║
║                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                    ║
╚══════════════════════════════════════════════════════════════════╝

📊 EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════

🏆 TOP PERFORMING DISH: {insights['top_dish']}
   Total Demand: {insights['top_dish_demand']:,} units
   
🏢 LEADING OUTLET: {insights['top_outlet']}
   Total Demand: {insights['top_outlet_demand']:,} units
   
⚖️ MOST VARIABLE DISH: {insights['most_unbalanced_dish']}
   Coefficient of Variation: {insights['unbalance_coefficient']}
   
📅 PEAK PERFORMANCE DAY: {insights['peak_day'].strftime('%A, %B %d, %Y')}
   Peak Day Demand: {insights['peak_day_demand']:,} units

📈 OPERATIONAL METRICS
═══════════════════════════════════════════════════════════════════

• Total Dishes Analyzed: {insights['total_dishes']}
• Total Outlets: {insights['total_outlets']}
• Average Demand per Dish: {insights['avg_demand_per_dish']} units
• Most Consistent Performer: {insights['most_consistent_dish']}
• Analysis Period: {insights['date_range']['start']} to {insights['date_range']['end']}

🎯 OUTLET CHAMPIONS
═══════════════════════════════════════════════════════════════════
"""
    
    for outlet, data in insights['best_dish_per_outlet'].items():
        report += f"• {outlet}: {data['dish']} ({data['demand']:,} demand)\n"
    
    report += f"""
💡 KEY BUSINESS INSIGHTS
═══════════════════════════════════════════════════════════════════

"""
    
    for i, insight in enumerate(insight_texts, 1):
        # Remove markdown formatting for plain text
        clean_insight = insight.replace('**', '').replace('*', '')
        report += f"{i}. {clean_insight}\n\n"
    
    report += f"""🚀 ACTIONABLE RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════

"""
    
    for i, recommendation in enumerate(recommendations, 1):
        # Remove markdown formatting for plain text
        clean_rec = recommendation.replace('**', '').replace('*', '')
        report += f"{i}. {clean_rec}\n\n"
    
    report += f"""
📋 PERFORMANCE MATRIX
═══════════════════════════════════════════════════════════════════

BEST PERFORMERS BY OUTLET:
"""
    
    for outlet, data in insights['best_dish_per_outlet'].items():
        report += f"  {outlet:15} → {data['dish']} ({data['demand']:,})\n"
    
    report += f"""
WORST PERFORMERS BY OUTLET:
"""
    
    for outlet, data in insights['worst_dish_per_outlet'].items():
        report += f"  {outlet:15} → {data['dish']} ({data['demand']:,})\n"
    
    report += f"""

═══════════════════════════════════════════════════════════════════
Report generated by Kodi Kura Chitti Gaare Analytics Dashboard
Built with Streamlit • Plotly • Pandas
═══════════════════════════════════════════════════════════════════
"""
    
    return report

def create_insights_report_json(insights, df):
    """
    Create a structured JSON report with insights and summary statistics
    
    Args:
        insights: Dictionary with computed insights
        df: DataFrame with demand data
    
    Returns:
        JSON string with structured data
    """
    
    # Calculate additional summary statistics
    outlet_summary = df.groupby('outlet').agg({
        'predicted_demand': ['sum', 'mean', 'std']
    }).round(2)
    outlet_summary.columns = ['total_demand', 'avg_demand', 'std_demand']
    
    dish_summary = df.groupby('dish').agg({
        'predicted_demand': ['sum', 'mean', 'std']
    }).round(2)
    dish_summary.columns = ['total_demand', 'avg_demand', 'std_demand']
    
    # Top 10 dishes
    top_dishes = dish_summary.nlargest(10, 'total_demand')
    
    report_data = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "report_type": "demand_analytics_insights",
            "data_period": {
                "start_date": insights['date_range']['start'].isoformat(),
                "end_date": insights['date_range']['end'].isoformat(),
                "total_days": (insights['date_range']['end'] - insights['date_range']['start']).days + 1
            }
        },
        "executive_summary": {
            "top_dish": {
                "name": insights['top_dish'],
                "total_demand": insights['top_dish_demand']
            },
            "leading_outlet": {
                "name": insights['top_outlet'],
                "total_demand": insights['top_outlet_demand']
            },
            "most_variable_dish": {
                "name": insights['most_unbalanced_dish'],
                "coefficient_of_variation": insights['unbalance_coefficient']
            },
            "peak_day": {
                "date": insights['peak_day'].isoformat(),
                "total_demand": insights['peak_day_demand']
            },
            "most_consistent_dish": insights['most_consistent_dish'],
            "average_demand_per_dish": insights['avg_demand_per_dish'],
            "total_dishes_analyzed": insights['total_dishes'],
            "total_outlets": insights['total_outlets']
        },
        "outlet_performance": {
            outlet: {
                "total_demand": int(data['total_demand']),
                "average_demand": float(data['avg_demand']),
                "demand_std_dev": float(data['std_demand']),
                "champion_dish": insights['best_dish_per_outlet'][outlet]['dish'],
                "champion_dish_demand": insights['best_dish_per_outlet'][outlet]['demand']
            }
            for outlet, data in outlet_summary.iterrows()
        },
        "top_dishes": [
            {
                "rank": i + 1,
                "dish_name": dish,
                "total_demand": int(data['total_demand']),
                "average_demand": float(data['avg_demand']),
                "demand_std_dev": float(data['std_demand'])
            }
            for i, (dish, data) in enumerate(top_dishes.iterrows())
        ],
        "performance_insights": {
            "outlet_champions": insights['best_dish_per_outlet'],
            "underperformers": insights['worst_dish_per_outlet']
        }
    }
    
    return json.dumps(report_data, indent=2, default=str)

def create_download_link(data, filename, mime_type="text/plain"):
    """
    Create a download link for data
    
    Args:
        data: Data to download (string)
        filename: Name of the file
        mime_type: MIME type of the file
    
    Returns:
        Base64 encoded download link
    """
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'

def create_executive_summary_csv(insights):
    """
    Create a CSV with executive summary metrics
    
    Args:
        insights: Dictionary with computed insights
    
    Returns:
        CSV string with executive summary
    """
    
    summary_data = {
        'Metric': [
            'Top Performing Dish',
            'Top Dish Demand',
            'Leading Outlet',
            'Leading Outlet Demand',
            'Most Variable Dish',
            'Variability Coefficient',
            'Peak Day',
            'Peak Day Demand',
            'Most Consistent Dish',
            'Average Demand per Dish',
            'Total Dishes Analyzed',
            'Total Outlets',
            'Analysis Start Date',
            'Analysis End Date'
        ],
        'Value': [
            insights['top_dish'],
            insights['top_dish_demand'],
            insights['top_outlet'],
            insights['top_outlet_demand'],
            insights['most_unbalanced_dish'],
            insights['unbalance_coefficient'],
            insights['peak_day'].strftime('%Y-%m-%d'),
            insights['peak_day_demand'],
            insights['most_consistent_dish'],
            insights['avg_demand_per_dish'],
            insights['total_dishes'],
            insights['total_outlets'],
            insights['date_range']['start'].strftime('%Y-%m-%d'),
            insights['date_range']['end'].strftime('%Y-%m-%d')
        ]
    }
    
    df = pd.DataFrame(summary_data)
    return df.to_csv(index=False)

def get_export_formats():
    """
    Get available export formats
    
    Returns:
        Dictionary with format options
    """
    return {
        "CSV - Full Dataset": "csv_full",
        "CSV - Executive Summary": "csv_summary", 
        "TXT - Insights Report": "txt_insights",
        "JSON - Structured Data": "json_insights"
    }

def generate_export_data(df, insights, insight_texts, recommendations, export_format):
    """
    Generate export data based on selected format
    
    Args:
        df: DataFrame with demand data
        insights: Computed insights dictionary
        insight_texts: List of insight texts
        recommendations: List of recommendations
        export_format: Selected export format
    
    Returns:
        Tuple of (data, filename, mime_type)
    """
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if export_format == "csv_full":
        data = export_dataset_csv(df)
        filename = f"kkcg_demand_data_{timestamp}.csv"
        mime_type = "text/csv"
        
    elif export_format == "csv_summary":
        data = create_executive_summary_csv(insights)
        filename = f"kkcg_executive_summary_{timestamp}.csv"
        mime_type = "text/csv"
        
    elif export_format == "txt_insights":
        data = create_insights_report_text(insights, insight_texts, recommendations)
        filename = f"kkcg_insights_report_{timestamp}.txt"
        mime_type = "text/plain"
        
    elif export_format == "json_insights":
        data = create_insights_report_json(insights, df)
        filename = f"kkcg_structured_data_{timestamp}.json"
        mime_type = "application/json"
        
    else:
        raise ValueError(f"Unknown export format: {export_format}")
    
    return data, filename, mime_type 