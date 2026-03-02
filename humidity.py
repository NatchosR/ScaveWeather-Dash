import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc




def humidity_stats(df):

    """
   return humidity statistics as dictionnary
    """
    humidity_stats = dict()
    ## --- STATISTICS CALCULATIONS --- ##

    avg_humidity = df['humidity'].mean() if 'humidity' in df.columns else np.nan
    humidity_25 = df['humidity'].quantile(0.25) if 'humidity' in df.columns else np.nan
    humidity_75 = df['humidity'].quantile(0.75) if 'humidity' in df.columns else np.nan

    avg_vpd = df['vpd'].mean() if 'vpd' in df.columns else np.nan

    # Set background color based on AVG VPD
    if avg_vpd < 0.5:
        bg_color = "rgba(200,255,200,0.8)"  # Light green
    elif avg_vpd <= 0.75:
        bg_color = "rgba(255,220,150,0.8)"  # Light orange
    else:
        bg_color = "rgba(255,200,200,0.8)"  # Light red

    if avg_vpd < 0.5:
        stress_text = "LOW"
        color_stress = 'rgba(0,128,0,1)'
    elif avg_vpd <= 0.75:
        stress_text = "HIGH"
        color_stress = 'rgba(255,128,0,1)'
    else:
        stress_text = "CRITICAL"
        color_stress = 'rgba(255,0,0,1)'

    humidity_stats["avg_humidity"] = avg_humidity
    humidity_stats["humidity_25"] = humidity_25
    humidity_stats["humidity_75"] = humidity_75
    humidity_stats["avg_vpd"] = avg_vpd
    humidity_stats["bg_color"] =bg_color
    humidity_stats["stress_text"] = stress_text
    humidity_stats["color_stress"] = color_stress

    return humidity_stats

def component_humidity_stats(humidity_stats):
    """
    Return styled humidity stats as Dash component for main page (dashboard)
    """
    
    return dbc.Card([
    dbc.CardBody([
        html.H4([
            html.I(className="bi bi-cloud me-2"),
            "Humidity & Pressure"
        ], className="card-title text-center"),
        html.Div([
            html.Div([
                "Air Humidity:",
                html.Br(),
                html.Span(f"{humidity_stats['avg_humidity']:.1f} %",
                    style={
                        "fontSize": "1.8rem",
                        "fontWeight": "bold",
                        "display": "block",
                        "textAlign": "center",
                        "marginBottom": "0.5rem"
                    }
                )
            ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
            html.Div([
                "25th percentile:  ",
                html.Span(f"{humidity_stats['humidity_25']} %", style={"fontWeight": "bold"}),
                " | 75th percentile: ",
                html.Span(f"{humidity_stats['humidity_75']} %", style={"fontWeight": "bold"})
            ], style={"fontSize": "0.9rem", "textAlign": "center", "marginBottom": "1.5rem"}),
            html.Div([
                "Vapour Pressure Deficit (VPD) ",
                html.Br(),
                html.Span(f"{humidity_stats['avg_vpd']:.1f} [kPa]", style={"fontSize": "1.8rem", "fontWeight": "bold", "color":humidity_stats["color_stress"]})
            ], style={"textAlign": "center", "marginBottom": "1rem"}),
            html.Div([
                "Plant Stress: ",
                html.Br(),
                html.Span(f"{humidity_stats['stress_text']}", style={"fontSize": "1.8rem", "fontWeight": "bold", "color":humidity_stats["color_stress"]})
            ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
        ], style={"marginTop": "0.5rem"}),
        #dbc.Button("coming soon ...", id="humidity-btn", color="danger", href="/", className="mt-3")
    ])
], className="h-100", style={"minHeight": "350px"}, color = humidity_stats["bg_color"])
