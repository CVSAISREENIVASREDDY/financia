import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def create_line_chart(df, metric, title):
    """Creates a line chart for a specific metric over the years."""
    if metric not in df.index:
        return None
    fig = px.line(
        x=df.columns,
        y=df.loc[metric],
        title=title,
        labels={'x': 'Year', 'y': metric}
    )
    fig.update_traces(mode='markers+lines')
    return fig

def create_bar_chart(df, metric, title):
    """Creates a bar chart for a specific metric over the years."""
    if metric not in df.index:
        return None
    fig = px.bar(
        x=df.columns,
        y=df.loc[metric],
        title=title,
        labels={'x': 'Year', 'y': metric}
    )
    return fig

def create_asset_liability_chart(df, title):
    """Creates a grouped bar chart comparing assets and liabilities."""
    metrics_to_plot = ['Total Assets', 'Total Liabilities']
    if not all(metric in df.index for metric in metrics_to_plot):
        return None

    plot_df = df.loc[metrics_to_plot].T # Transpose to get years as rows
    fig = go.Figure()
    for metric in metrics_to_plot:
        fig.add_trace(go.Bar(
            x=plot_df.index,
            y=plot_df[metric],
            name=metric
        ))
    fig.update_layout(
        title_text=title,
        barmode='group',
        xaxis_title='Year',
        yaxis_title='Value'
    )
    return fig

def create_growth_chart(df, metric, title):
    """Calculates and plots the year-over-year growth of a specific metric."""
    if metric not in df.index:
        return None

    data = df.loc[metric]
    growth = data.pct_change() * 100 # Calculate percentage growth
    growth = growth.dropna() # Remove the first year which has no growth value

    fig = px.bar(
        x=growth.index,
        y=growth.values,
        title=title,
        labels={'x': 'Year', 'y': 'YoY Growth (%)'}
    )
    fig.update_traces(texttemplate='%{y:.2f}%', textposition='outside')
    return fig