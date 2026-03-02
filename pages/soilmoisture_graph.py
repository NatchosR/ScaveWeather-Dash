from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
import dash
import plotly.graph_objects as go
import plotly.subplots as sp
import plotly.express as px
import numpy as np
import pandas as pd

# Add the parent directory to Python path
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils import data_parser
from soilmoisture import soilmoisture_stats

def disconnected_sensors_component(moisture_stats):

    return html.Div([
                html.Strong("Top 3 Disconnected Sensors:"),
                html.Ul([
                    html.Li(f"{sensor}: {count} times")
                    for sensor, count in moisture_stats['top3_missing_sensors']
                ], style={"fontSize": "0.9rem", "paddingLeft": "1.5rem", "marginTop": "0.5rem", "marginBottom": "0.5rem"})
            ], style={"textAlign": "left"})

# Subplot
def create_soilmoisture_graph(df):
    """
    Creates a 4-row subplot about soil moisture 
    Returns: plotly.graph_objects.Figure
    """

    # Define zone colors and name
    zone_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
    zone_names = ['3_ENEU', '4_ENES', '6_ESOS', '8_ESEU']
    sensor_pairs = [
        ('3ENEU_L_soil_moisture', '3ENEU_EL_soil_moisture'),  # Subplot 1
        ('4ENES_L_soil_moisture', '4ENES_EL_soil_moisture'),  # Subplot 2
        ('6ESOS_L_soil_moisture', '6ESOS_EL_soil_moisture'),  # Subplot 3
        ('8ESEU_L_soil_moisture', '7ESES_EL_soil_moisture'),  # Subplot 4 (note: 7ESES_EL)
    ]

    # Create subplot figure
    fig = sp.make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=zone_names
    )

    # Plot each subplot
    for i, (line_col, interline_col) in enumerate(sensor_pairs):
        row = i + 1
        color = zone_colors[i]
        zone_name = zone_names[i]
        
        # Plot line (plain)
        if line_col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df[line_col],
                    mode='lines',
                    name=f'{zone_name} - Line',
                    line=dict(color=color, width=2),
                    hovertemplate='<b>%{x}</b><br>Line: %{y:.1f} %<extra></extra>',
                    legendgroup=zone_name,
                    showlegend=True
                ),
                row=row, col=1
            )
        
        # Plot interline (condensed dashed — use 'dot' for closer to plain line)
        if interline_col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df[interline_col],
                    mode='lines',
                    name=f'{zone_name} - Interline',
                    line=dict(color=color, width=1.5, dash='dot'),  # 'dot' = condensed dash
                    hovertemplate='<b>%{x}</b><br>Interline: %{y:.1f} %<extra></extra>',
                    legendgroup=zone_name,
                    showlegend=True
                ),
                row=row, col=1
            )
        
        # ✅ Force y-axis to 0–100% — with autorange=False
        fig.update_yaxes(
            autorange=False,      # ← Critical: disable auto-scaling
            range=[0, 100],       # ← Set fixed range
            title_text="Soil Moisture (%)",
            row=row, col=1
        )

    # Update layout
    fig.update_layout(
        height=1500,
        title_text="Soil Moisture",
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, b=50, l=50, r=50)
    )

    # Update x-axis
    fig.update_xaxes(
        tickangle=45,
        tickformat="%Y-%m-%d",
        row=4, col=1
    )

    return fig

#Barchart
def create_monthly_moisture_barchart(df):
    """
    Create vertical bar chart with dual x-axes for precise positioning
    - Bottom x-axis: month-year labels
    - Top x-axis (hidden): for positioning (0 to N*3)
    - Two bars per month: Line + Interline
    - Horizontal outdoor temp line per month
    - Labels inside bars: "Line: xx%", "Interline: xx%"
    """

    # Group by year-month and compute mean for each sensor
    monthly_moist = df.groupby(df['datetime'].dt.to_period('M'), as_index=False).mean()

    # Extract month name and year (e.g., "Dec 2025")
    monthly_moist['month_label'] = monthly_moist['datetime'].dt.strftime('%b %Y')

    # Define sensor columns
    WET_line_col = ['3ENEU_L_soil_moisture', '8ESEU_L_soil_moisture']
    WET_interline_col = ['3ENEU_EL_soil_moisture', '7ESES_EL_soil_moisture']
    DRY_line_col = ['4ENES_L_soil_moisture', '6ESOS_L_soil_moisture']
    DRY_interline_col = ['4ENES_EL_soil_moisture', '6ESOS_EL_soil_moisture']

    # Compute Line and Interline averages per month (mean across sensors)
    monthly_moist['WET_line_moist'] = monthly_moist[WET_line_col].mean(axis=1)  # Mean across Line sensors
    monthly_moist['WET_IL_moist'] = monthly_moist[WET_interline_col].mean(axis=1)  # Mean across Interline sensors
    monthly_moist['WET_moist'] = monthly_moist[[*WET_line_col,*WET_interline_col]].mean(axis=1)  # Mean across Line sensors
    
    monthly_moist['DRY_line_moist'] = monthly_moist[DRY_line_col].mean(axis=1)  # Mean across Line sensors
    monthly_moist['DRY_IL_moist'] = monthly_moist[DRY_interline_col].mean(axis=1)  # Mean across Interline sensors
    monthly_moist['DRY_moist'] = monthly_moist[[*DRY_line_col,*DRY_interline_col]].mean(axis=1)  # Mean across Interline sensors

    # Create figure with dual x-axes
    fig = go.Figure()

    # Colors
    dry_color = 'rgba(0,255,127,0.5)'      # Brown for DRY
    wet_color = 'rgba(25,25,112,0.5)'     # Turquoise for WET
    line_color = 'rgba(176, 196, 222, 1)'      # steel blue for Line
    interline_color = 'rgba(230, 230, 250, 1)'  # lavender for Interline

    n = len(monthly_moist)
    for i, row in monthly_moist.iterrows():
        month = row['month_label']
        avg_DRY = row['DRY_moist']
        avg_WET = row['WET_moist']
        DRY_line = row['DRY_line_moist']
        DRY_IL = row['DRY_IL_moist']
        WET_line = row['WET_line_moist']
        WET_IL = row['WET_IL_moist']

        # Positioning: each month takes 3 units
        x_start = i * 2

        # Add DRY Zone Main Bar (0.5 to 1.5)
        # Add DRY Avg on top of main bar (centered)
        fig.add_trace(go.Bar(
            x=[x_start + 0.55],  # Center of DRY zone
            y=[avg_DRY],   # Slightly above
            width = 0.8,
            marker_color = dry_color,
            showlegend=False,
            xaxis='x2'
        ))

        fig.add_trace(go.Scatter(
            x=[x_start + 0.25],
            y=[avg_DRY + 0.2],
            mode='text',
            text=f"DRY ZONE: {avg_DRY:.1f}%",
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            textposition='top center',  # ← Left-align the text
            showlegend=False,
            xaxis='x2'
        ))

        # Sub Bar 1: Interline (0.5 to 1)
        fig.add_trace(go.Bar(
            x=[x_start + 0.40],  
            y=[DRY_IL],
            width=0.3,  # Bar width
            marker_color=interline_color,
            text=f"Interline:<br>{DRY_IL:.1f}%",
            textposition='inside',
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'
        ))

        # Sub Bar 2: Line (1 to 1.5)
        fig.add_trace(go.Bar(
            x=[x_start + 0.70],  # Center at 1.05
            y=[DRY_line],
            width=0.3,  # Bar width
            marker_color=line_color,
            text=f"Line:<br>{DRY_line:.1f}%",
            textposition='inside',
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'
        ))

        # Add WET Zone Main Bar (1.5 to 2.5)
        # Add WET Avg on top of main bar (centered)
        fig.add_trace(go.Bar(
            x=[x_start + 1.55],  # Center of WET zone
            y=[avg_WET],   # Slightly above
            width=0.8,
            marker_color=wet_color,
            showlegend=False,
            xaxis='x2'
        ))

        fig.add_trace(go.Scatter(
            x=[x_start + 1.2],
            y=[avg_WET + 0.2],
            mode='text',
            text=f"WET ZONE: {avg_WET:.1f}%",
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            textposition='top center',  # ← Left-align the text
            showlegend=False,
            xaxis='x2'
        ))

        # Sub Bar 1: Interline (1.5 to 2)
        fig.add_trace(go.Bar(
            x=[x_start + 1.40],  # Center at 1.75
            y=[WET_IL],
            width=0.3,  # Bar width
            marker_color=interline_color,
            text=f"Interline:<br>{WET_IL:.1f}%",
            textposition='inside',
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'
        ))

        # Sub Bar 2: Line (2 to 2.5)
        fig.add_trace(go.Bar(
            x=[x_start + 1.70],  # Center at 2.25
            y=[WET_line],
            width=0.3,  # Bar width
            marker_color=line_color,
            text=f"Line:<br>{WET_line:.1f}%",
            textposition='inside',
            textfont=dict(size=12, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'
        ))

        # Add vertical line at x_start+3 (end of month)
        if i < n - 1:  # Don't add after last month
            fig.add_shape(
                type="line",
                x0=x_start + 2,
                x1=x_start + 2,
                y0=0,
                y1=1,
                line=dict(color="gray", width=0.5, dash="dot"),
                xref="x2",
                yref="paper"
            )

    # Update layout
    fig.update_layout(
        xaxis=dict(
            title="",
            tickmode='array',
            tickvals=[],
            showgrid=False,
            showticklabels=False,
            overlaying='x',
            side='top',
            range=[0, n * 2]  # Range for positioning
        ),
        xaxis2=dict(
            title="Month",
            tickmode='array',
            tickvals=[i * 2 + 1 for i in range(n)],  # Center labels
            ticktext=monthly_moist['month_label'],
            tickfont=dict(size=14,
                          weight = 'bold'),
            tickangle=0,
            showgrid=False,
            gridcolor='lightgray',
            side='bottom'
        ),
        yaxis=dict(
            title="Soil Moisture (%)",
            showgrid=True,
            gridcolor='lightgray'
        ),
        barmode='overlay',
        margin=dict(t=50, b=50, l=50, r=50),
        title_font_size=20,
        plot_bgcolor='white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )

    return fig

# Register page
dash.register_page("soilmoisture_graph", path="/soilmoisture_graph", )

### LAYOUT ###
layout = html.Div([
    html.H2("Soil Moisture Graph", className="text-center mb-3"),
    dbc.Row([
        dbc.Col([
            # Back Button
            html.A("← Back to Dashboard", href="/", className="btn btn-outline-secondary mb-3"),

            # Filter
            html.Div([
                dbc.Col([
                html.Label("Select a Period:"),
                dcc.Dropdown(
                    id="month-soilmoisture-graph-filter",
                    options=[],
                    value=None,  # Default
                    clearable=False,
                    className="mb-3"
                    )
                ], width=6)
            ]),
        ], width=6),
        dbc.Col([
            html.Div(id="soilmoisture-stats-container")
        ], width={"offset": 2})
    ], style={"marginLeft": "0.5rem"}),
    
    # Subplot
    dcc.Graph(id="soilmoisture-graph", style={"height": "1500px"}),

    # Barchart
    html.H4("Soil Moisture Evolution", className="mt-2 mb-2"),
    dcc.Graph(id="monthly-soilmoisture-bar", style={"height": "400px"})
])

### CALLBACK ###

# MONTH_OPTIONS
@callback(
    Output("month-soilmoisture-graph-filter", "options"),
    Output("month-soilmoisture-graph-filter", "value"),
    Input("month-options-store", "data")  # ← Get MONTH_OPTIONS from store
)
def update_month_options(month_options):
    if not month_options:
        return [], None
    # Set default to last option (most recent)
    default_value = month_options[-1]["value"]
    return month_options, default_value

# GRAPH and STATS
@callback(
    Output("soilmoisture-stats-container", "children"),
    Output("soilmoisture-graph", "figure"),
    Input("month-soilmoisture-graph-filter", "value"),  
    State("weather-data-store", "data")  #pass weather_df via State
)

def update_soilmoisture_page(selected_month_str, weather_data_dict):
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
    soilmoisture_df = data_parser(weather_df, 'soilmoisture', time_period)
    moisture_stats = soilmoisture_stats(soilmoisture_df)
    fig = create_soilmoisture_graph(soilmoisture_df)

    return disconnected_sensors_component(moisture_stats), fig

# VERTICAL BARCHART
@callback(
    Output("monthly-soilmoisture-bar", "figure"),
    Input("monthly-soilmoisture-bar", "id"),  # Trigger on page load
    State("weather-data-store", "data")
)
def update_monthly_bar_chart(_, weather_data_dict):
    if not weather_data_dict:
        return px.bar()

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    time_period = None
    moist_df = data_parser(weather_df, 'soilmoisture', time_period)
    return create_monthly_moisture_barchart(moist_df)
