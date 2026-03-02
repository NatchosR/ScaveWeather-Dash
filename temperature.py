import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc

def temperature_stats(df):
    """
    Return air and soil temperature statistics as dictionary
    """
    temperature_stats = dict()

    # Define sensor pairs
    sensor_pairs = [
        ('3ENOU_L_soil_temperature', '3ENOU_EL_soil_temperature'),  # Wet
        ('4ENES_L_soil_temperature', '4ENES_EL_soil_temperature'),  # Dry
        ('6ESOS_L_soil_temperature', '6ESOS_EL_soil_temperature'),  # Dry
        ('8ESEU_L_soil_temperature', '8ESEU_EL_soil_temperature')   # Wet
    ]

    # Compute avg differences for each zone
    avg_temps_line = []
    avg_temps_inter = []
    avg_deltas = []

    for line_col, interline_col in sensor_pairs:
        avg_L = np.nan
        avg_I = np.nan
        avg_diff = np.nan

        if line_col in df.columns and interline_col in df.columns:
            temp_df = df[[line_col, interline_col]].copy()
            avg_L = temp_df[line_col].mean()
            avg_I = temp_df[interline_col].mean()
            diff = temp_df[line_col] - temp_df[interline_col]
            avg_diff = diff.mean()

        avg_temps_line.append(avg_L)
        avg_temps_inter.append(avg_I)
        avg_deltas.append(avg_diff)

    temperature_stats["avg_temps_line_list"] = avg_temps_line
    temperature_stats["avg_temps_inter_list"] = avg_temps_inter
    temperature_stats["avg_deltas_list"] = avg_deltas

    # Compute Dry Zone Averages (4 ENES, 6 ESOS)
    dry_line_cols = ['4ENES_L_soil_temperature', '6ESOS_L_soil_temperature']
    dry_inter_cols = ['4ENES_EL_soil_temperature', '6ESOS_EL_soil_temperature']
    dry_line_avg = df[dry_line_cols].mean().mean() if all(c in df.columns for c in dry_line_cols) else np.nan
    dry_inter_avg = df[dry_inter_cols].mean().mean() if all(c in df.columns for c in dry_inter_cols) else np.nan
    temperature_stats["dry_avg_temp_line"] = dry_line_avg
    temperature_stats["dry_avg_temp_inter"] = dry_inter_avg

    # Compute Wet Zone Averages (3 ENOU, 8 ESEU)
    wet_line_cols = ['3ENOU_L_soil_temperature', '8ESEU_L_soil_temperature']
    wet_inter_cols = ['3ENOU_EL_soil_temperature', '8ESEU_EL_soil_temperature']
    wet_line_avg = df[wet_line_cols].mean().mean() if all(c in df.columns for c in wet_line_cols) else np.nan
    wet_inter_avg = df[wet_inter_cols].mean().mean() if all(c in df.columns for c in wet_inter_cols) else np.nan
    temperature_stats["wet_avg_temp_line"] = wet_line_avg
    temperature_stats["wet_avg_temp_inter"] = wet_inter_avg

    # Air Temperature
    if 'temperature' in df.columns:
        temperature_stats['avg_temperature'] = df['temperature'].mean()
        temperature_stats['temperature_min_&time'] = (df['temperature'].min(), df.loc[df['temperature'].idxmin(), 'datetime'])
        temperature_stats['temperature_max_&time'] = (df['temperature'].max(), df.loc[df['temperature'].idxmax(), 'datetime'])
    else:
        temperature_stats['avg_temperature'] = np.nan
        temperature_stats['temperature_min_&time'] = (np.nan, "N/A")
        temperature_stats['temperature_max_&time'] = (np.nan, "N/A")

    # Find min/max of Outdoor Temperature
    temp_series = df['temperature'].dropna()
    max_idx_T = temp_series.idxmax()
    min_idx_T = temp_series.idxmin()

    max_time_T = df.loc[max_idx_T, 'datetime'].date()
    min_time_T = df.loc[min_idx_T, 'datetime'].date()
    max_val_T = temp_series.max()
    min_val_T = temp_series.min()

    # tuple [0] = value and [1] = date
    temperature_stats["temperature_max_&time"] = (max_val_T, max_time_T)
    temperature_stats["temperature_min_&time"] = (min_val_T, min_time_T)

    # Average temperature
    avg_temperature = df['temperature'].mean() if 'temperature' in df.columns else np.nan

    temperature_stats['avg_temperature'] = avg_temperature

    # Set the background color
    if avg_temperature < 20:
        bg_color = 'rgba(135,206,250,1)'
        bg_color_box = 'rgba(135,206,250,0.6)'
    elif avg_temperature <30:
        bg_color = 'rgba(255,160,122,1)'
        bg_color_box = 'rgba(255,160,122,0.6)'
    else:
        bg_color = 'rgba(255,0,0,1)'
        bg_color_box = 'rgba(255,0,0,0.6)'

    temperature_stats['bg_color'] = bg_color
    temperature_stats['bg_color_box'] = bg_color_box
    
    return temperature_stats


def component_temperature_stats(temperature_stats):
    """
    Return styled temperature stats as Dash component for main page (dashboard)
    """
    # Define zone groups
    dry_zones = [
        {"name": "4 ENES", "avg_L": temperature_stats['avg_temps_line_list'][1], "avg_I": temperature_stats['avg_temps_inter_list'][1]},
        {"name": "6 ESOS", "avg_L": temperature_stats['avg_temps_line_list'][2], "avg_I": temperature_stats['avg_temps_inter_list'][2]}
    ]
    wet_zones = [
        {"name": "3 ENOU", "avg_L": temperature_stats['avg_temps_line_list'][0], "avg_I": temperature_stats['avg_temps_inter_list'][0]},
        {"name": "8 ESEU", "avg_L": temperature_stats['avg_temps_line_list'][3], "avg_I": temperature_stats['avg_temps_inter_list'][3]}
    ]

    # Dry zone averages
    dry_avg_L = temperature_stats['dry_avg_temp_line']
    dry_avg_I = temperature_stats['dry_avg_temp_inter']

    # Wet zone averages
    wet_avg_L = temperature_stats['wet_avg_temp_line']
    wet_avg_I = temperature_stats['wet_avg_temp_inter']

    return dbc.Card([
        dbc.CardBody([
            html.H4([
                html.I(className="bi bi-thermometer-half me-2"),
                "Air and Soil Temperature"
            ], className="card-title text-center"),

           html.Div([
                "Air Temperature:",
                html.Br(),
                    dbc.Col([
                        html.Span(f"{temperature_stats['avg_temperature']:.1f} °C",
                            style={
                                "fontSize": "1.8rem",
                                "fontWeight": "bold",
                                "display": "block",
                            }
                        ),
                        html.Div([
                            "Min: ",
                            html.Span(f"{temperature_stats['temperature_min_&time'][0]:.1f} °C ", style={"fontWeight": "normal"}),
                            "|| Max: ",
                            html.Span(f"{temperature_stats['temperature_max_&time'][0]:.1f} °C", style={"fontWeight": "normal"})
                        ], style={"fontSize": "0.9rem", "marginBottom": "0.5rem"})
                    ], width="auto", className="justify-content-center"),  # ← Center the temperature value within its col

            ], style={"textAlign": "center", "marginBottom": "0.8rem"}),

            # Soil Temperature - Dry Zone Row
            html.H5("Dry Zones", className="text-center mb-2"),
            
            dbc.Row([
                # Col 1: 4 ENES
                dbc.Col([
                    html.H6(dry_zones[0]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{dry_zones[0]['avg_L']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{dry_zones[0]['avg_I']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center", "marginRight":"0.5rem"}),

                # Col 2: 6 ESOS
                dbc.Col([
                    html.H6(dry_zones[1]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{dry_zones[1]['avg_L']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{dry_zones[1]['avg_I']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center"}),

            ], className="justify-content-center mb-2"),

            # Soil Temperature - Wet Zone Row
            html.H5("Wet Zones", className="text-center mb-2"),
            dbc.Row([
                # Col 1: 3 ENOU
                dbc.Col([
                    html.H6(wet_zones[0]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{wet_zones[0]['avg_L']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{wet_zones[0]['avg_I']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center", "marginRight":"0.5rem"}),

                # Col 2: 8 ESEU
                dbc.Col([
                    html.H6(wet_zones[1]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{wet_zones[1]['avg_L']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{wet_zones[1]['avg_I']:.1f} °C", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center"}),

            ], className="justify-content-center gb-2"),

            # Button
            dbc.Button("More Details", id="temperature-btn", color="primary", href="/temperature_graph", className="mt-3")

        ])
    ], className="h-100",style={"minHeight": "500px"}, color=temperature_stats["bg_color"])
