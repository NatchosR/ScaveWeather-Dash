import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc

def sun_stats(df):

    sun_stats = dict()

    # FILTER: Keep only 08:00, 12:00
    # IMPORTANT NOTE: Data are aggregated to the maximum value in a 4h window 08:00 data correspond to the max value
    # recorded between 08:00 and 12:00. The 12:00 data correspond to the maximum value recorded between 12:00 and 16:00
    weather_df_day = df.copy()
    uvi_index = weather_df_day.columns.get_loc('uvi')
    weather_df_day = weather_df_day.iloc[:, :uvi_index+1]
    weather_df_day['hour'] = weather_df_day['datetime'].dt.hour
    weather_df_day = weather_df_day[weather_df_day['hour'].isin([8, 12])]

    ## --- BASIC STATISTICS CALCULATIONS --- ##

    avg_solar = weather_df_day['solar'].mean() if 'solar' in weather_df_day.columns else np.nan
    avg_uvi = weather_df_day['uvi'].mean() if 'uvi' in weather_df_day.columns else np.nan
    solar_25 = weather_df_day['solar'].quantile(0.25) if 'solar' in weather_df_day.columns else np.nan
    solar_75 = weather_df_day['solar'].quantile(0.75) if 'solar' in weather_df_day.columns else np.nan
    uvi_25 = weather_df_day['uvi'].quantile(0.25) if 'uvi' in weather_df_day.columns else np.nan
    uvi_75 = weather_df_day['uvi'].quantile(0.75) if 'uvi' in weather_df_day.columns else np.nan

    sun_stats["avg_solar"] = avg_solar
    sun_stats["avg_uvi"] = avg_uvi
    sun_stats["solar_25"] = solar_25
    sun_stats["solar_75"] = solar_75
    sun_stats["uvi_25"] = uvi_25
    sun_stats["uvi_75"] = uvi_75

    ## --- QUALITATIVE STATISTICS --- ##

    # UV index based on WHO (https://www.who.int/news-room/questions-and-answers/item/radiation-the-ultraviolet-(uv)-index)
    if avg_uvi <= 2:
        uv_txt = "LOW"
        uv_col = "rgba(0,128,0,1)"
    elif avg_uvi <= 5:
        uv_txt = "MODERATE"
        uv_col = "rgba(128,128,128,1)"
    elif avg_uvi <= 7:
        uv_txt = "HIGH"
        uv_col = "rgba(255,165,0,1)"
    elif avg_uvi <= 10:
        uv_txt = "VERY HIGH"
        uv_col = "rgba(255,0,0,1)"
    else:
        uv_txt = "EXTREME"
        uv_col = "rgba(255,105,180,1)"

    sun_stats["uvi_text"] = uv_txt
    sun_stats["uvi_color"] = uv_col

    return sun_stats

def pressure_stats(df):

    pressure_stats = dict()

    # --- STATISTICS CALCULATIONS ---
    avg_pressure = df['pressure_relative'].mean() if 'pressure_relative' in df.columns else np.nan

    # Classify weather based on average pressure
    if avg_pressure < 1000:
        weather_class = "Stormy and unsettled"
    elif avg_pressure <= 1015:
        weather_class = "Normal"
    else:
        weather_class = "Clear and stable"

    pressure_stats["avg_pressure"] = avg_pressure
    pressure_stats["weather_class"] = weather_class

    return pressure_stats
    

def component_sun_stats(sun_stats, pressure_stats):
    """
    Return styled sun stats as Dash component for main page (dashboard)
    """
    
    return dbc.Card([
    dbc.CardBody([
        html.H4([
            html.I(className="bi bi-sun me-2"),
            "Sun Exposure"
        ], className="card-title text-center"),
        html.Div([
            html.Div([
                "Sun Irradiance: (avg)",
                html.Br(),
                html.Span(f"{sun_stats['avg_solar']:.1f} W/m2",
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
                html.Span(f"{sun_stats['solar_25']:.1f} W/m2", style={"fontWeight": "bold"}),
                " | 75th percentile: ",
                html.Span(f"{sun_stats['solar_75']:.1f} W/m2", style={"fontWeight": "bold"})
            ], style={"fontSize": "0.9rem", "textAlign": "center", "marginBottom": "1rem"}),
            html.Div([
                "UV index: (avg)",
                html.Br(),
                html.Span(f"{sun_stats['avg_uvi']:.1f}", style={"fontSize": "1.8rem", "fontWeight": "bold","color":sun_stats["uvi_color"]}),
                html.I(f" ({sun_stats['uvi_text']})", style={"fontSize": "1rem", "fontWeight": "bold", "color":sun_stats["uvi_color"]})
            ], style={"textAlign": "center", "marginBottom": "1rem"}),
            html.Div([
                "Type of weather:",
                html.Br(),
                html.Span(f"{pressure_stats['weather_class']} ", style={"fontSize": "1.2rem", "fontWeight": "bold"}),
                html.Br(),
                html.Span(f"{pressure_stats['avg_pressure']:.1f} [hPA]", style={"fontSize": "0.9rem"})
            ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
        ], style={"marginTop": "0.5rem"}),
        #dbc.Button("Atmospheric Pressure", id="pressure-btn", color="secondary", href="/pressure_graph", className="mt-3")
    ])
], className="h-100", style={"minHeight": "350px"} , color = "rgba(255,255,0,1)")
