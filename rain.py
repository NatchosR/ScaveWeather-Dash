import pandas as pd
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc


def rain_stats(df):
    """
    return rain statistics as dictionnary
    """
    rain_stats = dict()

    # --- STATISTICS CALCULATIONS ---
    # 1.a) Days of rain: count days with rain_daily > 0 (group by date, take max)
    if 'rain_daily' not in df.columns:
        daily_rain = pd.Series(dtype=float)
        days_of_rain = 0
        total_days_in_month = 0
    else:
        daily_rain = df.groupby(pd.Grouper(key='datetime', freq='D'))['rain_daily'].max().dropna()
        days_of_rain = (daily_rain > 0).sum()
        total_days = len(daily_rain)

        rain_stats['rainy_days'] = days_of_rain
        rain_stats['total_days'] = total_days

    # 2) Monthly total: last value of rain_monthly (assuming cumulative)
    # temporary (debug)
    if 'rain_monthly' in df.columns:
        monthly_series = df['rain_monthly'].dropna()
        if len(monthly_series) > 0:
            monthly_total = monthly_series.iloc[-1]
        else:
            monthly_total = np.nan
    else:
        monthly_total = np.nan
    
    rain_stats['monthly_rainfall'] = monthly_total

    # 3) Total rain
    if 'rain_yearly' in df.columns:
        # Create year column
        df['year'] = df['datetime'].dt.year

        # Group by year, take last non-NaN value of rain_yearly for each year
        yearly_totals = df.groupby('year')['rain_yearly'].last()

        # Sum all yearly totals
        yearly_total = yearly_totals.sum()

        # If no data, return NaN
        if pd.isna(yearly_total):
            yearly_total = np.nan
    else:
        yearly_total = np.nan

    rain_stats['yearly_rainfall'] = yearly_total

    # 4) Top 3 rainy days: group by date, max rain_daily, sort, take top 3
    if 'rain_daily' in df.columns:
        top_rain_days = daily_rain.sort_values(ascending=False).head(3)
        top3_rainday = {}
        for date, value in top_rain_days.items():
            top3_rainday[date.strftime('%Y-%m-%d')] = value
            #top_rain_days_list.append((date.strftime('%Y-%m-%d'), f"{value:.1f}"))
    else:
        top3_rainday = {}

    rain_stats['top_rainy_days'] = top3_rainday


    # 5) Strongest rain rate: max rain_rate + corresponding time
    if 'rain_rate' in df.columns:
        max_rate_idx = df['rain_rate'].idxmax()
        strongest_rate = df.loc[max_rate_idx, 'rain_rate']
        strongest_rate_time = df.loc[max_rate_idx, 'datetime'].date()
    else:
        strongest_rate = np.nan
        strongest_rate_time = pd.NaT

    rain_stats['max_rain_rate'] = strongest_rate
    rain_stats['time_max_rain_rate'] = strongest_rate_time

    # 6) Average rain rate (excluding 0s)
    if 'rain_rate' in df.columns:
        avg_rate = df['rain_rate'][df['rain_rate'] > 0].mean()
    else:
        avg_rate = np.nan

    rain_stats['avg_rain_rate'] = avg_rate

    return rain_stats

# Component for main.py
def component_rainfall_stats(rain_stats, all_time_filter:bool):

    if all_time_filter == True:
        total_rain_period = rain_stats['yearly_rainfall']
    else:
        total_rain_period = rain_stats['monthly_rainfall']

    return dbc.Card([
    dbc.CardBody([
        html.H4([
            html.I(className="bi bi-droplet me-2"),
            "Rainfall"
        ], className="card-title text-center"),
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
            ], style={"textAlign": "center", "marginBottom": "0.5rem"}),
            html.Div([
                "Average rain rate: ",
                html.Span(f"{rain_stats['avg_rain_rate']:.1f} [mm/h]", style={"fontWeight": "bold"})
            ], style={"textAlign": "left", "marginBottom": "0.5rem"}),
            html.Div([
                "Strongest rain fall: ",
                html.Span(f"{rain_stats['max_rain_rate']:.1f} [mm/h] ", style={"fontWeight": "bold"}),
                html.Br(),
                f"on the {rain_stats['time_max_rain_rate']}"
            ], style={"textAlign": "left", "marginBottom": "1rem"}),
            html.Div([
                html.Strong("Top 3 Rainy Days:"),
                html.Ul([
                    html.Li(f"{day}: {value:.1f} [mm]")
                    for day, value in rain_stats['top_rainy_days'].items()
                ], style={"fontSize": "0.9rem", "paddingLeft": "0.5rem"})
            ], style={"textAlign": "left"})
        ], style={"marginTop": "1rem"}),
        dbc.Button("More Details", id="rainfall-btn", color="primary", href="/rainfall_graph", className="mt-2")
    ])
], className="h-100",style={"minHeight": "500px"}, color = 'rgba(64,224,208,1)')