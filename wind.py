import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc

def wind_stats(df):
    """
    return wind statistics as dictionnary
    """
    wind_stats = dict()

    ##  STATISTICS CALCULATIONS ##

    # Convert degrees to radians
    if '10_minute_avg_wind_direction' in df.columns:
        valid_dirs = df['10_minute_avg_wind_direction'].dropna()
        if len(valid_dirs) > 0:
            radians = np.deg2rad(valid_dirs)
            # Convert to x,y
            x = np.cos(radians)
            y = np.sin(radians)
            # Mean x,y
            mean_x = np.mean(x)
            mean_y = np.mean(y)
            # Back to degrees
            mean_angle_rad = np.arctan2(mean_y, mean_x)
            mean_angle_deg = np.rad2deg(mean_angle_rad) % 360  # 0–360°

            # Convert to cardinal point
            cardinals = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
            index = int((mean_angle_deg + 22.5) // 45) % 8
            dominant_cardinal = cardinals[index]
        else:
            mean_angle_deg = np.nan
            dominant_cardinal = "N/A"
    else:
        mean_angle_deg = np.nan
        dominant_cardinal = "N/A"
    
    wind_stats['avg_wind_direction'] = mean_angle_deg
    wind_stats['avg_wind_direction_cardinal'] = dominant_cardinal
    wind_stats['wind_icon'] = deg_to_bootstrap_icon(mean_angle_deg)
    # --- Calculate Wind Stats ---

    # Avg wind speed and  max wind gust
    if 'wind_gust' in df.columns:
        max_gust_idx = df['wind_gust'].idxmax()
        max_gust = df.loc[max_gust_idx, 'wind_gust']
        day_max_gust = df.loc[max_gust_idx, 'datetime'].date()
    else:
        max_gust = np.nan
        day_max_gust = pd.NaT

    wind_stats['max_wind_gust'] = max_gust
    wind_stats['day_max_gust'] = day_max_gust

    avg_speed = df['wind_speed'].mean() if 'wind_speed' in df.columns else np.nan

    wind_stats['avg_wind_speed'] = avg_speed
    
    # Group by date, get row with max wind_speed per day
    daily_max = df.groupby(pd.Grouper(key='datetime', freq='D'))[['datetime','wind_speed', 'wind_gust']].max().dropna().reset_index(drop=True)

    # Get top 3 days by max wind_speed
    top_days = daily_max.nlargest(3, 'wind_speed').copy()

    # Build top3 list
    top3_windyday = []
    for _, row in top_days.iterrows():
        top3_windyday.append({
            'day': row['datetime'].strftime('%Y-%m-%d'),
            'speed': row['wind_speed'],
            'gust': row['wind_gust']
        })

    wind_stats['top3'] = top3_windyday


    return wind_stats

def deg_to_bootstrap_icon(deg):
    deg = deg % 360
    if 337.5 <= deg or deg < 22.5:
        return "bi-arrow-up"
    elif 22.5 <= deg < 67.5:
        return "bi-arrow-up-right"
    elif 67.5 <= deg < 112.5:
        return "bi-arrow-right"
    elif 112.5 <= deg < 157.5:
        return "bi-arrow-down-right"
    elif 157.5 <= deg < 202.5:
        return "bi-arrow-down"
    elif 202.5 <= deg < 247.5:
        return "bi-arrow-down-left"
    elif 247.5 <= deg < 292.5:
        return "bi-arrow-left"
    elif 292.5 <= deg < 337.5:
        return "bi-arrow-up-left"
    return "bi-arrow-right"


def component_wind_stats(wind_stats):
    """
    Return styled wind stats as Dash component for main page (dashboard)
    """

    return dbc.Card([
    dbc.CardBody([
        html.Div([
        html.H4([
            html.I(className="bi bi-wind me-2"),
            "Wind"
        ], className="card-title text-center"),

        # Top line: avg speed + arrow + cardinal + degrees
        html.Div([
            html.Span(
                f"{wind_stats['avg_wind_speed']:.1f} km/h",
                style={
                    "fontSize": "1.8rem",
                    "fontWeight": "bold",
                    "marginRight": "1rem",
                    "display": "inline-block"
                }
            ),
             html.I(
                className=f"bi {wind_stats['wind_icon']} me-2",
                style={
                    "fontSize": "3rem",
                    "fontWeight": "bold",
                    "color": "rgba(46,139,87,1)",
                    "display": "inline-block"
                }
            ),
            html.Span(
                f"{wind_stats['avg_wind_direction_cardinal']} ({wind_stats['avg_wind_direction']:.0f}°)",
                style={
                    "fontSize": "1rem",
                    "fontWeight": "normal",
                    "display": "inline-block"
                }
            )
        ], style={"textAlign": "center", "marginBottom": "0.5rem"}),

        html.Div([
                "Strongest wind gust: ",
                html.Span(f"{wind_stats['max_wind_gust']:.1f} [km/h] ", style={"fontWeight": "bold"}),
                html.Br(),
                f"on the {wind_stats['day_max_gust']}"
            ], style={"textAlign": "left", "marginBottom": "1rem"}),

        # Top 3 Windy Days
        html.Div([
            html.Strong("Top 3 Windy Days:"),
            html.Ul([
                html.Li([
                    html.Span(
                        item['day'],
                        style={
                            "textDecoration": "underline",
                            "fontWeight": "normal",
                            "marginRight": "0.5rem"
                        }
                    ),
                    html.Span(
                        f"{item['speed']:.1f} km/h",
                        style={"fontWeight": "bold", "marginRight": "0.5rem"}
                    ),
                    html.I(f"({item['gust']:.1f} km/h)")
                ], style={"fontSize": "0.9rem", "paddingLeft": "1.5rem"})
                for item in wind_stats['top3']
            ])
        ], style={"textAlign": "left", "marginTop": "1rem"})
    ])
        
    ])
], className="h-100", style={"minHeight": "350px"}, color = 'rgba(143,188,143,1)')