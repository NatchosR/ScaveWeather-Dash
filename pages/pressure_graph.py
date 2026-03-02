# pages/rainfall_graph.py
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# Add the parent directory to Python path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import data_parser
from sun_pressure import pressure_stats, sun_stats

# Build horizontal statistics
def render_pressure_stats_horizontal(p_stats:dict, s_stats:dict):
    """
    Return styled pressure stats as Dash component in horizontal layout (for graph page)
    Layout: [Avg Pressure] [Type of weather + UV] [Solar Irradiance] 
    """
    return dbc.Row([

        # Left: Avg Pressure
        dbc.Col([
            html.Div([
                "Average Atmospheric Pressure: ",
                html.Br(),
                html.Span(f"{p_stats['avg_pressure']:.1f} [hPa]", style={"fontSize":"1.8rem","fontWeight": "bold"})
                ], style={"textAlign": "center", "marginBottom": "0.5rem"})         
        ], width=4, className="text-center"),

        # Center: Type of Weather and UV index
        dbc.Col([
            html.Div([
                "Type of Weather:",
                html.Br(),
                html.Span(f"{p_stats['weather_class']}", style={"fontSize":"1.8rem","fontWeight": "bold"})
                ], style={"textAlign": "center", "marginBottom": "0.5rem"})
        ], width=4, className="text-center"),

        # Right: Sun irradiance
        dbc.Col([
            html.Div([
                "Solar Irradiance:",
                html.Br(),
                html.Span(f"{s_stats['avg_solar']:.1f} [W/m2]", style={"fontWeight": "bold"}),
                html.Br(),
                "UV index:",
                html.Br(),
                html.Span(f"{s_stats['avg_uvi']:.1f}", style={"fontWeight": "bold"}),
                html.I(f" ({s_stats['uvi_text']})", style={"fontSize":"0.8rem","fontWeight": "bold"})
                ], style={"textAlign": "center", "marginBottom": "0.5rem"})
        ], width=4, className="text-center")
    ], className="mb-2")

# Build Graph
def create_pressure_graph(pressure_df):

    # Initialize figure
    fig = go.Figure()

    # Find max and min
    if 'pressure_relative' in pressure_df.columns:
        max_idx = pressure_df['pressure_relative'].idxmax()
        min_idx = pressure_df['pressure_relative'].idxmin()
        max_pressure = pressure_df.loc[max_idx, 'pressure_relative']
        min_pressure = pressure_df.loc[min_idx, 'pressure_relative']
        max_time = pressure_df.loc[max_idx, 'datetime']
        min_time = pressure_df.loc[min_idx, 'datetime']
    else:
        max_pressure = min_pressure = np.nan
        max_time = min_time = pd.NaT

    # --- START PLOT ---

    # Add pressure line
    if 'pressure_relative' in pressure_df.columns:
        fig.add_trace(
            go.Scatter(
                x=pressure_df['datetime'],
                y=pressure_df['pressure_relative'],
                mode='lines',
                name='Pressure',
                line=dict(color='black', width=2),
                hovertemplate='<b>%{x}</b><br>Pressure: %{y:.1f} hPa<extra></extra>'
            )
        )

    # Add average line (dashed)
    avg_pressure = pressure_df['pressure_relative'].mean()
    if not np.isnan(avg_pressure):
        fig.add_hline(
            y=avg_pressure,
            line=dict(color='gray', width=2, dash='dash'),
            annotation_text=f"avg: <b>{avg_pressure:.1f} hPa</b>",
            annotation_position="top right",
            annotation_font_size=16,
            annotation_font_color="gray"
        )

    # Add max point
    if not np.isnan(max_pressure):
        fig.add_trace(
            go.Scatter(
                x=[max_time],
                y=[max_pressure],
                mode='markers+text',
                marker=dict(color='red', size=8),
                text=f"<b> Max: {max_pressure:.1f}</b>",
                textfont=dict(size=12, color='red'),
                textposition='top right',
                hoverinfo='skip',
                showlegend=False
            )
        )

    # Add min point
    if not np.isnan(min_pressure):
        fig.add_trace(
            go.Scatter(
                x=[min_time],
                y=[min_pressure],
                mode='markers+text',
                marker=dict(color='blue', size=8),
                text=f"<b>Min: {min_pressure:.1f}</b>",
                textfont=dict(size=12, color='blue'),
                textposition='bottom right',
                hoverinfo='skip',
                showlegend=False
            )
        )

    # Update axes
    fig.update_xaxes(
        title_text="Time",
        showgrid=True,
        gridcolor='white',
        gridwidth=1,
        tickangle=45,
        tickformat="%Y-%m-%d"
    )
    """
    if 'pressure_relative' in pressure_df.columns:
        y_range = [pressure_df['pressure_relative'].min(), pressure_df['pressure_relative'].max()]
        y_margin = 0.3 * (y_range[1] - y_range[0])
        fig.update_yaxes(
            range=[y_range[0] - y_margin, y_range[1] + y_margin],
            title_text="Pressure (hPa)",
            showgrid=True,
            gridcolor='white',
            gridwidth=1
        )
    """
    # Update layout — REMOVE fixed height for Dash responsiveness
    fig.update_layout(
        #height=400,  # ← COMMENTED OUT — let Dash auto-fit
        xaxis_title="Time",
        yaxis_title="Pressure (hPa)",
        showlegend=False,
        margin=dict(t=50, b=50, l=50, r=50),
        plot_bgcolor='rgba(204,229,255,1)',
        font=dict(family="Arial", size=12)
    )

    return fig

# Register page
dash.register_page("pressure_graph", path="/pressure_graph", )

# Layout: Title → Horizontal Stats → Graph → Back Button
layout = html.Div([
    html.H2("Atmospheric Pressure", className="text-center mb-3"),

    # Back Button
    html.A("← Back to Dashboard", href="/", className="btn btn-outline-secondary mb-3"),

    # Filter
    html.Div([
        dbc.Col([
        html.Label("Select a Period:"),
        dcc.Dropdown(
            id="month-pressure-graph-filter",
            options=[
                {"label": "2025 - December", "value": "[2025, 12]"},
                {"label": "2026 - January", "value": "[2026, 1]"}
            ],
            value="[2026, 1]",  # Default
            clearable=False,
            className="mb-3"
            )
        ], width=6)
    ]),

    # Horizontal Stats Row
    html.Div(id="sun-pressure-stats-container"),

    # Graph
    dcc.Graph(id="pressure-graph", style={"height": "600px"})
])

# Callback: Compute stats and graph when page loads
@callback(
    Output("sun-pressure-stats-container", "children"),
    Output("pressure-graph", "figure"),
    Input("month-pressure-graph-filter", "value"),
    State("weather-data-store", "data")  #pass weather_df via State
)

def update_rainfall_page(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("No data loaded."), go.Figure()

    # Parse string "[2025, 12]" → list [2025, 12]
    try:
        time_period = eval(selected_month_str)  # Safe because we control the options
    except:
        time_period = [2026, 1]  # Fallback

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    sun_df = data_parser(weather_df, 'sun', time_period)
    pressure_df = data_parser(weather_df, 'pressure', time_period)
    p_stats = pressure_stats(pressure_df)
    s_stats = sun_stats(sun_df)

    fig = create_pressure_graph(pressure_df)

    return render_pressure_stats_horizontal(p_stats,s_stats), fig
