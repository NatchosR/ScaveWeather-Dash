import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc

def soilmoisture_stats(df):
    """
    Return soil moisture statistics as dictionary
    Handles NaN values correctly.
    """
    moisture_stats = dict()

    # Define zone names and sensor pairs
    zone_names = ['3_ENEU', '4_ENES', '6_ESOS', '8_ESEU']
    sensor_pairs = [
        ('3ENEU_L_soil_moisture', '3ENEU_EL_soil_moisture'),  # Subplot 1
        ('4ENES_L_soil_moisture', '4ENES_EL_soil_moisture'),  # Subplot 2
        ('6ESOS_L_soil_moisture', '6ESOS_EL_soil_moisture'),  # Subplot 3
        ('8ESEU_L_soil_moisture', '7ESES_EL_soil_moisture'),  # Subplot 4 (note: 7ESES_EL)
    ]

    # Initialize lists
    avg_moist_line = []
    avg_moist_inter = []
    avg_deltas = []

    # Compute avg differences for each zone
    for line_col, interline_col in sensor_pairs:
        avg_L = np.nan
        avg_I = np.nan
        avg_diff = np.nan

        if line_col in df.columns and interline_col in df.columns:
            # Drop rows where both are NaN — or handle per column
            moist_df = df[[line_col, interline_col]].copy()
            # Compute mean ignoring NaN
            avg_L = moist_df[line_col].mean()
            avg_I = moist_df[interline_col].mean()
            # Compute difference only where both are not NaN
            diff = moist_df[line_col] - moist_df[interline_col]
            avg_diff = diff.mean()

        avg_moist_line.append(avg_L)
        avg_moist_inter.append(avg_I)
        avg_deltas.append(avg_diff)

    moisture_stats["avg_moist_line_list"] = avg_moist_line
    moisture_stats["avg_moist_inter_list"] = avg_moist_inter
    moisture_stats["avg_deltas_list"] = avg_deltas

    # Avg soil moisture across all 8 sensors (ignoring NaN)
    all_sensors = [
        '3ENEU_L_soil_moisture', '3ENEU_EL_soil_moisture',
        '4ENES_L_soil_moisture', '4ENES_EL_soil_moisture',
        '6ESOS_L_soil_moisture', '6ESOS_EL_soil_moisture',
        '8ESEU_L_soil_moisture', '7ESES_EL_soil_moisture'
    ]

    # Compute overall avg (ignoring NaN)
    overall_avg = df[all_sensors].mean().mean()  # Mean of means — or use .stack().mean()
    moisture_stats["overall_avg_moisture"] = overall_avg

    # Avg moisture in wet zones: '3_ENEU', '8_ESEU'
    wet_sensors = [
        '3ENEU_L_soil_moisture', '3ENEU_EL_soil_moisture',
        '8ESEU_L_soil_moisture', '7ESES_EL_soil_moisture'
    ]
    wet_avg_L = df[wet_sensors[0::2]].mean().mean()  # Line sensors
    wet_avg_I = df[wet_sensors[1::2]].mean().mean()  # Interline sensors
    wet_avg = df[wet_sensors].mean().mean()
    moisture_stats["wet_avg_line"] = wet_avg_L
    moisture_stats["wet_avg_inter"] = wet_avg_I
    moisture_stats["wet_avg"] = wet_avg

    # Avg moisture in dry zones: '4_ENES', '6_ESOS'
    dry_sensors = [
        '4ENES_L_soil_moisture', '4ENES_EL_soil_moisture',
        '6ESOS_L_soil_moisture', '6ESOS_EL_soil_moisture'
    ]
    dry_avg_L = df[dry_sensors[0::2]].mean().mean()  # Line sensors
    dry_avg_I = df[dry_sensors[1::2]].mean().mean()  # Interline sensors
    dry_avg = df[dry_sensors].mean().mean()
    moisture_stats["dry_avg_line"] = dry_avg_L
    moisture_stats["dry_avg_inter"] = dry_avg_I
    moisture_stats["dry_avg"] = dry_avg

    # Count missing data per sensor
    missing_counts = {}
    for sensor in all_sensors:
        if sensor in df.columns:
            missing_counts[sensor] = df[sensor].isna().sum()
        else:
            missing_counts[sensor] = np.nan

    moisture_stats["missing_counts"] = missing_counts

    # Top 3 sensors with most missing data
    sorted_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)
    moisture_stats["top3_missing_sensors"] = sorted_missing[:3]

    return moisture_stats


def component_soilmoisture_stats(moisture_stats):
    """
    Return styled soil moisture stats as Dash component for main page (dashboard)
    """
    # Define zone groups
    dry_zones = [
        {"name": "4 ENES", "avg_L": moisture_stats['avg_moist_line_list'][1], "avg_I": moisture_stats['avg_moist_inter_list'][1]},
        {"name": "6 ESOS", "avg_L": moisture_stats['avg_moist_line_list'][2], "avg_I": moisture_stats['avg_moist_inter_list'][2]}
    ]
    wet_zones = [
        {"name": "3 ENOU", "avg_L": moisture_stats['avg_moist_line_list'][0], "avg_I": moisture_stats['avg_moist_inter_list'][0]},
        {"name": "8 ESEU", "avg_L": moisture_stats['avg_moist_line_list'][3], "avg_I": moisture_stats['avg_moist_inter_list'][3]}
    ]

    # Dry zone averages
    dry_avg_L = moisture_stats['dry_avg_line']
    dry_avg_I = moisture_stats['dry_avg_inter']
    dry_avg = moisture_stats['dry_avg']

    # Wet zone averages
    wet_avg_L = moisture_stats['wet_avg_line']
    wet_avg_I = moisture_stats['wet_avg_inter']
    wet_avg = moisture_stats['wet_avg']

    return dbc.Card([
        dbc.CardBody([
            html.H4([
                html.I(className="bi bi-moisture me-2"),
                "Soil Moisture"
            ], className="card-title text-center"),

            # General Soil Moisture
            html.Div([
                html.Div([
                    "General Soil Moisture (avg 8 sensors):",
                    html.Br(),
                    html.Span(f"{moisture_stats['overall_avg_moisture']:.1f} %",
                        style={
                            "fontSize": "1.8rem",
                            "fontWeight": "bold",
                            "display": "block",
                            "textAlign": "center",
                            "marginBottom": "0.5rem"
                        }
                    )
                ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
            ], style={"marginTop": "1rem"}),

            # Dry Zone Row
            dbc.Row([
                html.Span([
                    html.H5("Dry Zones",  style={"fontSize": "1.2rem", "display": "inline", "marginRight": "0.5rem"}, className="text-center"),
                    "avg: ",
                    html.Span(f"{dry_avg:.1f} %", style={"fontWeight": "bold", "display": "inline"})
                ],  style={"fontSize": "0.8rem", "display": "inline-block", "textAlign": "center"})
            ], className="justify-content-center mb-2"),          

            dbc.Row([
                # Col 1: 4 ENES Line
                dbc.Col([
                    html.H6(dry_zones[0]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{dry_zones[0]['avg_L']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{dry_zones[0]['avg_I']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center", "marginRight":"0.5rem"}),

                # Col 2: 6 ESOS Line
                dbc.Col([
                    html.H6(dry_zones[1]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{dry_zones[1]['avg_L']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{dry_zones[1]['avg_I']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center"}),
            ], className="justify-content-center mb-2"),

            # Wet Zone Row
            dbc.Row([
                html.Span([
                    html.H5("Wet Zones", style={"fontSize": "1.2rem", "display": "inline", "marginRight": "0.5rem"}, className="text-center"),
                    "avg: ",
                    html.Span(f"{wet_avg:.1f} % ", style={"fontWeight": "bold", "display": "inline"}),
                ], style={"fontSize": "0.8rem", "display": "inline-block", "textAlign": "center"})
            ], className="justify-content-center mb-2"),          

            dbc.Row([
                # Col 1: 3 ENOU Line
                dbc.Col([
                    html.H6(wet_zones[0]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{wet_zones[0]['avg_L']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{wet_zones[0]['avg_I']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center", "marginRight":"0.5rem"}),

                # Col 2: 8 ESEU Line
                dbc.Col([
                    html.H6(wet_zones[1]["name"], className="text-center mb-1", style={"fontWeight": "bold"}),
                    html.Div([
                        "Line: ",
                        html.Span(f"{wet_zones[1]['avg_L']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"}),
                    html.Div([
                        "Interline: ",
                        html.Span(f"{wet_zones[1]['avg_I']:.1f} %", style={"fontWeight": "bold"})
                    ], style={"fontSize": "0.9rem", "marginBottom": "0.2rem"})
                ], width=4, style={"border": "1px solid #FFFFFF", "borderRadius": "8px", "padding": "10px", "textAlign": "center"}),

            ], className="justify-content-center mb-2"),

            # Button
            dbc.Button("More Details", id="soilmoisture-btn", color="primary", href="/soilmoisture_graph", className="mt-3")
            ])
    ], className="h-100",style={"minHeight": "500px"}, color='rgba(210,105,30,1)')
