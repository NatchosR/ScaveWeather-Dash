# pages/rainfall_graph.py
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Add the parent directory to Python path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import data_parser
from rain import rain_stats

# Build horizontal statistics
def render_rain_stats_horizontal(rain_stats, all_time_filter:bool):

    if all_time_filter == True:
        total_rain_period = rain_stats['yearly_rainfall']
    else:
        total_rain_period = rain_stats['monthly_rainfall']

    return dbc.Row([

        # Left: Avg + Strongest Rain Rate
        dbc.Col([
            html.Div([
                html.Div([
                    "Average rain rate: ",
                    html.Span(f"{rain_stats['avg_rain_rate']:.1f} [mm/h]", style={"fontWeight": "bold"})
                ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
                html.Div([
                    "Strongest rain fall: ",
                    html.Span(f"{rain_stats['max_rain_rate']:.1f} [mm/h] ", style={"fontWeight": "bold"}),
                    html.Br(),
                    f"on the {rain_stats['time_max_rain_rate']}"
                ], style={"textAlign": "center", "marginBottom": "0.5rem"})
            ], style={"marginTop": "1rem"})
        ], width=4, className="text-center"),

        # Left: Center Rainfall
        dbc.Col([
            html.Div([
                html.Span(
                    f"{total_rain_period:.1f} [mm]",
                    style={
                        "fontSize": "1.8rem",
                        "fontWeight": "bold",
                        "display": "block",
                        "textAlign": "center",
                        "marginBottom": "0.5rem"
                    }
                ),
                html.Div([
                    "Days of rain ",
                    html.Span(f"{rain_stats['rainy_days']}", style={"fontWeight": "bold"}),
                    " (",
                    html.I(f"out of {rain_stats['total_days']}", style={"fontSize": "0.9rem"}),
                    ")"
                ], style={"textAlign": "center", "marginBottom": "0.5rem"})
            ], style={"marginTop": "1rem"})
        ], width=4, className="text-center"),

        # Right: Top 3 Rainy Days
        dbc.Col([
            html.Div([
                html.Strong("Top 3 Rainy Days:"),
                html.Ul([
                    html.Li(f"{day}: {value:.1f} [mm]")
                    for day, value in rain_stats['top_rainy_days'].items()
                ], style={"fontSize": "0.9rem", "paddingLeft": "1.5rem", "textAlign": "center"})
            ], style={"marginTop": "1rem"})
        ], width=4, className="text-center")
    ], className="mb-2")

# Build line graph
def create_rainfall_graph(df):
    # Build graph
    fig = px.line(
        x=df["datetime"],
        y=df["rain_daily"],
        labels={"x": "Date", "y": "Rainfall (mm)"},
        title="Daily Rainfall Over Time"
    )
    fig.update_layout(xaxis_tickangle=-45)

    return fig

# Build vertical bar chart
def create_monthly_rainfall_bar_chart(df):
    """
    Create a horizontal bar chart showing total rainfall per month (all time)
    """
    # # Ensure datetime is parsed
    # df = df.copy()
    # df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    # df = df.dropna(subset=['datetime'])

    # Group by year-month and sum rain_daily
    monthly_rain = df.groupby(df['datetime'].dt.to_period('M'))['rain_monthly'].max().reset_index()
    monthly_rain['datetime'] = monthly_rain['datetime'].dt.to_timestamp()  # Convert to datetime for plotting

    # Extract month name and year (e.g., "Dec 2025")
    monthly_rain['month_label'] = monthly_rain['datetime'].dt.strftime('%b %Y')

    # Create vertical bar chart
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly_rain['month_label'],  # Month-Year on x-axis
        y=monthly_rain['rain_monthly'],  # Rainfall on y-axis
        marker_color='rgba(64,224,208,0.7)',
        text=monthly_rain['rain_monthly'].round(1).astype(str) + " [mm]",  # Show value on bar
        textposition='auto',
        # Style text
        textfont={
            'size': 26,        # Larger font
            'family': 'Arial', # Optional: change font
            'color': 'black',  # Optional: change color
            'weight': 'bold'   # Bold text
        },
        hovertemplate="<b>%{x}</b><br>Rainfall: %{y:.1f} mm<extra></extra>",
        insidetextanchor='middle'
    ))

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Rainfall (mm)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40),
        height=400,
        xaxis_tickangle=-45,  # Rotate labels if many months
        yaxis=dict(range=[0, None])  # Ensure 0 at bottom
    )

    return fig

# Register page
dash.register_page("rainfall_graph", path="/rainfall_graph", )

# Layout: Title → Stats → Graph → Back Button
layout = html.Div([
    html.H2("Rainfall Details", className="text-center mb-3"),
    
    dbc.Row([
        dbc.Col([
            # Back Button
            html.A("← Back to Dashboard", href="/", className="btn btn-outline-secondary mb-3"),
    
            # Filter
            html.Div([
                dbc.Col([
                html.Label("Select a Period:"),
                dcc.Dropdown(
                    id="month-rain-graph-filter",
                    options=[],  # ← Will be updated by callback
                    value=None,  # ← You can set a default or use State to set it
                    clearable=False,
                    className="mb-3"
                )
                ], width=6)
            ]),
        ], width=6),
    ], style={"marginLeft": "0.5rem"}),

    
    # Statistics
    html.Div(id="rain-stats-container"),  # Will be filled by callback
    
    # Line Plot
    dcc.Graph(id="rainfall-graph", style={"height": "600px"}),

    # Vertical Bar Chart (All Time)
    html.H4("Monthly Rainfall Totals", className="mt-4 mb-2"),
    dcc.Graph(id="monthly-rainfall-bar", style={"height": "400px"})
])

### CALLBACKS ###

# MONTH_OPTIONS
@callback(
    Output("month-rain-graph-filter", "options"),
    Output("month-rain-graph-filter", "value"),
    Input("month-options-store", "data")  # ← Get MONTH_OPTIONS from store
)
def update_month_options(month_options):
    if not month_options:
        return [], None
    # Set default to last option (most recent)
    default_value = month_options[-1]["value"]
    return month_options, default_value

# GRAPH AND STATS
@callback(
    Output("rain-stats-container", "children"),
    Output("rainfall-graph", "figure"),
    Input("month-rain-graph-filter", "value"),
    State("weather-data-store", "data")  #pass weather_df via State
)

def update_rainfall_page(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("No data loaded."), px.line()
    
    # Parse string "[2025, 12]" → list [2025, 12]
    try:
        time_period = eval(selected_month_str)  # Safe because we control the options
    except:
        time_period = [2026, 1]  # Fallback

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    rain_df = data_parser(weather_df, 'rain', time_period)
    stats = rain_stats(rain_df)

    fig = create_rainfall_graph(rain_df)

    if selected_month_str == "None":
        return render_rain_stats_horizontal(stats, True), fig
    else:
        return render_rain_stats_horizontal(stats, False), fig

# VERTICAL BARCHART
@callback(
    Output("monthly-rainfall-bar", "figure"),
    Input("monthly-rainfall-bar", "id"),  # Trigger on page load
    State("weather-data-store", "data")
)
def update_monthly_bar_chart(_, weather_data_dict):
    if not weather_data_dict:
        return px.bar()

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    time_period = None
    rain_df = data_parser(weather_df, 'rain', time_period)
    return create_monthly_rainfall_bar_chart(rain_df)