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


def create_temperature_subplot(temperature_df):
    # Define zone colors and names
    zone_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']  # Blue, Orange, Green, Red
    zone_names = ['3_ENOU','4_ENES', '6_ESOS', '8_ESEU']
    sensor_pairs = [
        ('3ENOU_L_soil_temperature', '3ENOU_EL_soil_temperature'),
        ('4ENES_L_soil_temperature', '4ENES_EL_soil_temperature'),
        ('6ESOS_L_soil_temperature', '6ESOS_EL_soil_temperature'),
        ('8ESEU_L_soil_temperature', '8ESEU_EL_soil_temperature')   
    ]

    # Create subplot with updated titles
    fig = sp.make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles= "Air & Soil Temperature"
    )

    # Create subplot figure — 5 rows
    fig = sp.make_subplots(
        rows=5, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles= ["Air Temperature"] + zone_names
    )

    # Collect all temperature values for global y-limits
    all_temps = []
    for line_col, interline_col in sensor_pairs:
        if line_col in temperature_df.columns:
            all_temps.extend(temperature_df[line_col].dropna().values)
        if interline_col in temperature_df.columns:
            all_temps.extend(temperature_df[interline_col].dropna().values)
    if 'temperature' in temperature_df.columns:
        all_temps.extend(temperature_df['temperature'].dropna().values)
    if 'temperature_low' in temperature_df.columns:
        all_temps.extend(temperature_df['temperature_low'].dropna().values)
    if 'temperature_high' in temperature_df.columns:
        all_temps.extend(temperature_df['temperature_high'].dropna().values)

    # Compute global y-limits with 10% margin
    if all_temps:
        y_min = min(all_temps)
        y_max = max(all_temps)
        margin = 0.1 * (y_max - y_min)
        y_min -= margin
        y_max += margin
    else:
        y_min, y_max = 0, 1  # Fallback

    # === ROW 1: Outdoor Temperature ===
    row = 1
    if 'temperature' in temperature_df.columns and not temperature_df['temperature'].dropna().empty:
        fig.add_trace(
            go.Scatter(
                x=temperature_df['datetime'],
                y=temperature_df['temperature'],
                mode='lines',
                name='Outdoor Temp',
                line=dict(color='black', width=1),
                hovertemplate='<b>%{x}</b><br>Outdoor: %{y:.1f} °C<extra></extra>',
                legendgroup='outdoor',
                showlegend=False
            ),
            row=row, col=1
        )

        # Find min/max of Outdoor Temperature
        temp_series = temperature_df['temperature'].dropna()
        max_idx_T = temp_series.idxmax()
        min_idx_T = temp_series.idxmin()

        max_time_T = temperature_df.loc[max_idx_T, 'datetime']
        min_time_T = temperature_df.loc[min_idx_T, 'datetime']
        max_val_T = temp_series.max()
        min_val_T = temp_series.min()

        # Add max point marker
        fig.add_trace(
            go.Scatter(
                x=[max_time_T],
                y=[max_val_T],
                mode='markers+text',
                marker=dict(color='red', size=6),
                text=f"Temp: {max_val_T:.1f}°C",
                textposition='top right',
                hoverinfo='skip',
                showlegend=False
            ),
            row=1, col=1
        )

        # Add min point marker
        fig.add_trace(
            go.Scatter(
                x=[min_time_T],
                y=[min_val_T],
                mode='markers+text',
                marker=dict(color='blue', size=6),
                text=f"Temp: {min_val_T:.1f}°C",
                textposition='bottom left',
                hoverinfo='skip',
                showlegend=False
            ),
            row=1, col=1
        )

    # Add temperature range (low/high)
    if 'temperature_low' in temperature_df.columns and 'temperature_high' in temperature_df.columns:
        fig.add_trace(
            go.Scatter(
                x=temperature_df['datetime'],
                y=temperature_df['temperature_high'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ),
            row=row, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=temperature_df['datetime'],
                y=temperature_df['temperature_low'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.6)',
                name='Temp Range',
                hoverinfo='skip',
                legendgroup='outdoor',
                showlegend=False
            ),
            row=row, col=1
        )

    # Add 0°C line
    fig.add_hline(y=0, line_color="black", line_width=1, row=row, col=1)

    # Update legend for outdoor plot
    fig.update_layout(
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
    )

    # === ROWS 2-5: Zones ===
    for i, (line_col, interline_col) in enumerate(sensor_pairs):
        row = i + 2
        color = zone_colors[i]
        zone_name = zone_names[i]

        # Plot line (plain)
        if line_col in temperature_df.columns and not temperature_df[line_col].dropna().empty:
            fig.add_trace(
                go.Scatter(
                    x=temperature_df['datetime'],
                    y=temperature_df[line_col],
                    mode='lines',
                    name=f'{zone_name} - Line',
                    line=dict(color=color, width=2),
                    hovertemplate='<b>%{x}</b><br>Line: %{y:.1f} °C<extra></extra>',
                    legendgroup=zone_name,
                    showlegend=True
                ),
                row=row, col=1
            )

            # Find min/max of line
            line_series = temperature_df[line_col].dropna()
            max_idx = line_series.idxmax()
            min_idx = line_series.idxmin()

            max_time = temperature_df.loc[max_idx, 'datetime']
            min_time = temperature_df.loc[min_idx, 'datetime']
            max_val = line_series.max()
            min_val = line_series.min()

            # Get interline value at same time
            max_interline = temperature_df.loc[max_idx, interline_col] if interline_col in temperature_df.columns else np.nan
            min_interline = temperature_df.loc[min_idx, interline_col] if interline_col in temperature_df.columns else np.nan

            # Add max point marker
            fig.add_trace(
                go.Scatter(
                    x=[max_time],
                    y=[max_val],
                    mode='markers+text',
                    marker=dict(color='red', size=6),
                    text=f"Line: {max_val:.1f}°C",
                    textposition='bottom left',
                    hoverinfo='skip',
                    showlegend=False
                ),
                row=row, col=1
            )

            # Add min point marker
            fig.add_trace(
                go.Scatter(
                    x=[min_time],
                    y=[min_val],
                    mode='markers+text',
                    marker=dict(color='blue', size=6),
                    text=f"Line: {min_val:.1f}°C",
                    textposition='top right',
                    hoverinfo='skip',
                    showlegend=False
                ),
                row=row, col=1
            )

            # Add interline value as text below max/min
            if not np.isnan(max_interline):
                fig.add_annotation(
                    x=max_time,
                    y=max_val,
                    text=f"Interline: {max_interline:.1f}°C",
                    showarrow=False,
                    yshift=20,
                    font=dict(size=10, color='gray'),
                    row=row, col=1
                )
            if not np.isnan(min_interline):
                fig.add_annotation(
                    x=min_time,
                    y=min_val,
                    text=f"Interline: {min_interline:.1f}°C",
                    showarrow=False,
                    yshift=-20,
                    font=dict(size=10, color='gray'),
                    row=row, col=1
                )

        # Plot interline (dotted)
        if interline_col in temperature_df.columns and not temperature_df[interline_col].dropna().empty:
            fig.add_trace(
                go.Scatter(
                    x=temperature_df['datetime'],
                    y=temperature_df[interline_col],
                    mode='lines',
                    name=f'{zone_name} - Interline',
                    line=dict(color=color, width=1.5, dash='dot'),
                    hovertemplate='<b>%{x}</b><br>Interline: %{y:.1f} °C<extra></extra>',
                    legendgroup=zone_name,
                    showlegend=True
                ),
                row=row, col=1
            )

        # Add 0°C line
        fig.add_hline(y=0, line_color="black", line_width=1, row=row, col=1)

        # Update legend for this subplot
        fig.update_layout(
            legend=dict(
                x=0.98,
                y=0.98,
                xanchor="right",
                yanchor="top",
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="black",
                borderwidth=1
            )
        )

    # Update Layout (legend particulary)
    fig.update_layout(
        showlegend=True,
        margin=dict(t=50, b=50, l=50, r=50),
        title_font_size=30,
        legend=dict(
            orientation="h",        # ← Horizontal legend
            yanchor="bottom",       # ← Anchor to bottom of legend area
            y=1.02,               # ← Position just above the plot (1.0 = top of plot, >1.0 = above)
            xanchor="center",       # ← Center horizontally
            x=0.5,                # ← Center the legend
            bgcolor="rgba(255,255,255,0.8)",  # Optional: semi-transparent background
            bordercolor="Black",
            borderwidth=1
        )
    )

    # Update y-axis for all subplots
    for i in range(1, 6):
        fig.update_yaxes(
            range=[y_min, y_max],
            title_text="Temp °C",
            row=i, col=1
        )

    # Update x-axis (only for last row)
    fig.update_xaxes(
        tickangle=45,
        tickformat="%Y-%m-%d",
        row=5, col=1
    )

    return fig

def create_monthly_temperature_barchart(df):
    """
    Create vertical bar chart with dual x-axes for precise positioning
    - Bottom x-axis: month-year labels
    - Top x-axis (hidden): for positioning (0 to N*3)
    - Two bars per month: Line + Interline
    - Horizontal outdoor temp line per month
    - Labels inside bars: "Line: xx°C", "Interline: xx°C"
    """

    # Group by year-month and compute mean for each sensor
    monthly_temp = df.groupby(df['datetime'].dt.to_period('M'), as_index=False).mean()

    # Convert to timestamp for plotting
    #monthly_temp['datetime'] = monthly_temp['datetime'].to_timestamp()

    # Extract month name and year (e.g., "Dec 2025")
    monthly_temp['month_label'] = monthly_temp['datetime'].dt.strftime('%b %Y')

    # Define sensor columns
    line_col = ['3ENOU_L_soil_temperature', '4ENES_L_soil_temperature', '6ESOS_L_soil_temperature', '8ESEU_L_soil_temperature']
    interline_col = ['3ENOU_EL_soil_temperature', '4ENES_EL_soil_temperature', '6ESOS_EL_soil_temperature', '8ESEU_EL_soil_temperature']

    # Compute Line and Interline averages per month (mean across sensors)
    monthly_temp['avg_line_T'] = monthly_temp[line_col].mean(axis=1)  # Mean across Line sensors
    monthly_temp['avg_interline_T'] = monthly_temp[interline_col].mean(axis=1)  # Mean across Interline sensors
    monthly_temp['avg_T'] = monthly_temp['temperature']  # Outdoor air temp

    # Create figure with dual x-axes
    fig = go.Figure()

    # Colors
    line_color = 'rgba(176, 192, 222, 1)'      # steel blue for Line
    interline_color = 'rgba(230, 230, 250, 1)'  # lavender for Interline
    outdoor_color = 'rgba(119, 136, 153, 1)'     # gray for Outdoor

    # Add bars and lines
    n = len(monthly_temp)
    for i, row in monthly_temp.iterrows():
        month = row['month_label']
        avg_line = row['avg_line_T']
        avg_interline = row['avg_interline_T']
        avg_T = row['avg_T']

        # Positioning: each month takes 3 units
        x_start = i * 1

        # Add Line bar (0.5 to 1.5)
        fig.add_trace(go.Bar(
            x=[x_start + 0.3],  # Center at 1.0
            y=[avg_line],
            width=0.4,  # Bar width
            marker_color=line_color,
            text=f"Line:<br>{avg_line:.1f} °C",
            textposition='inside',
            textfont=dict(size=14, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'  # Use top x-axis for positioning
        ))

        # Add Interline bar (1.5 to 2.5)
        fig.add_trace(go.Bar(
            x=[x_start + 0.7],  # Center at 2.0
            y=[avg_interline],
            width=0.4,  # Bar width
            marker_color=interline_color,
            text=f"Interline:<br>{avg_interline:.1f} °C",
            textposition='inside',
            textfont=dict(size=14, family='Arial', color='black', weight='bold'),
            showlegend=False,
            xaxis='x2'  # Use top x-axis for positioning
        ))

        # Add horizontal outdoor temp line (x_start to x_start+3)
        fig.add_trace(go.Scatter(
            x=[x_start, x_start + 1],
            y=[avg_T, avg_T],
            mode='lines',
            line=dict(color=outdoor_color, width=3),
            showlegend=False,
            xaxis='x2'  # Use top x-axis for positioning
        ))

        # Add text on top of the line (centered)
        fig.add_trace(go.Scatter(
            x=[x_start],
            y=[avg_T - 0.3],   # Slightly above the line
            mode='text',
            text=f"AVG outdoor T°: <br>{avg_T:.1f}°C",
            textfont=dict(size=12, family='Arial', color=outdoor_color, weight='bold'),
            textposition='bottom right',
            showlegend=False,
            xaxis='x2'
        ))

        # Add vertical line at x_start+3 (end of month)
        if i < n - 1:  # Don't add after last month
            fig.add_shape(
                type="line",
                x0=x_start + 1,
                x1=x_start + 1,
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
            range=[0, n * 1]  # Range for positioning
        ),
        xaxis2=dict(
            title="Month",
            tickmode='array',
            tickvals=[i * 1 + 0.5 for i in range(n)],  # Center labels
            ticktext=monthly_temp['month_label'],
            tickfont=dict(size=14,
                          weight = 'bold'),
            tickangle=0,
            showgrid=False,
            gridcolor='lightgray',
            side='bottom'
        ),
        yaxis=dict(
            title="Temperature (°C)",
            showgrid=True,
            gridcolor='rgba(211,211,211,0.6)',
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
dash.register_page("temperature_graph", path="/temperature_graph", )

# Layout: Title → Horizontal Stats → Graph → Back Button
layout = html.Div([
    html.H2("Temperature Graph", className="text-center mb-3"),

    dbc.Row([
        dbc.Col([
            # Back Button
            html.A("← Back to Dashboard", href="/", className="btn btn-outline-secondary mb-3"),

            # Filter
            html.Div([
                dbc.Col([
                html.Label("Select a Period:"),
                dcc.Dropdown(
                    id="month-temperature-graph-filter",
                    options=[],
                    value=None,
                    clearable=False,
                    className="mb-3"
                    )
                ], width=6)
            ]),
        ], width=6),
    ], style={"marginLeft": "0.5rem"}),
    
    # Graph
    dcc.Graph(id="temperature-graph", style={"height": "1500px"}),

    # Vertical Bar Chart (All Time)
    html.H4("Soil Temperature Evolution", className="mt-4 mb-2"),
    dcc.Graph(id="monthly-temperature-bar", style={"height": "400px"})
])

### CALLBACKS ###

# MONTH_OPTIONS
@callback(
    Output("month-temperature-graph-filter", "options"),
    Output("month-temperature-graph-filter", "value"),
    Input("month-options-store", "data")  # ← Get MONTH_OPTIONS from store
)
def update_month_options(month_options):
    if not month_options:
        return [], None
    # Set default to last option (most recent)
    default_value = month_options[-1]["value"]
    return month_options, default_value

# GRAPH
@callback(
    Output("temperature-graph", "figure"),
    Input("month-temperature-graph-filter", "value"),
    State("weather-data-store", "data")  #pass weather_df via State
)

def update_temperature_page(selected_month_str, weather_data_dict):
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
    temperature_df = data_parser(weather_df, 'temperature', time_period)
    fig = create_temperature_subplot(temperature_df)

    return fig

# VERTICAL BARCHART
@callback(
    Output("monthly-temperature-bar", "figure"),
    Input("monthly-temperature-bar", "id"),  # Trigger on page load
    State("weather-data-store", "data")
)
def update_monthly_bar_chart(_, weather_data_dict):
    if not weather_data_dict:
        return px.bar()

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    time_period = None
    temp_df = data_parser(weather_df, 'temperature', time_period)
    return create_monthly_temperature_barchart(temp_df)
