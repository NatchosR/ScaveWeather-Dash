import dash
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash import page_registry, register_page, callback, Input, Output, State
import pandas as pd
from io import StringIO
import ast

from load_data import load_once_weather_data
from utils import data_parser
from rain import component_rainfall_stats, rain_stats
from humidity import component_humidity_stats, humidity_stats
from sun_pressure import component_sun_stats, sun_stats, pressure_stats
from temperature import component_temperature_stats, temperature_stats
from wind import component_wind_stats, wind_stats
from soilmoisture import component_soilmoisture_stats, soilmoisture_stats

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

### === APP LAYOUT === ###
main_layout = dbc.Container([

    # Title + Data Info (1 row, 2 cols)
    dbc.Row([
        dbc.Col(html.H1("Weather Dashboard", className="text-left mb-2"), width={"size": 6, "order": 1, "offset": 0}, md=6, xs=12),
        dbc.Col([
            html.Div(id="data-info")
        ], width={"size": 6, "order": 2, "offset": 0}, md=6, xs=12),
    ], className="g-2 mb-2"),

    # Filters (1 row, 1 col on mobile, 1/2 on desktop)
    dbc.Row([
        dbc.Col([
            html.Label("Select a Period:"),
            dcc.Dropdown(
                id="month-filter",
                options=[],
                value=None,
                clearable=False,
                className="mb-2"
            )
        ], width={"size": 6, "order": 1, "offset": 0}, md=4, xs=12),
        
        dbc.Col([
            html.Br(),
            dcc.Download(id="download-weather-data"),
            dbc.Button("Download Weather Data", id="download-btn", color="secondary", className="mt-2")
        ], width="auto")
        

    ], className="g-2 mb-2"),

    # Stat Cards (1 row, 6 cards — responsive: 1 col on mobile, 3 cols on desktop)
    dbc.Row([
        dbc.Col(html.Div(id="rain-card-container"), width={"size": 4, "order": 1, "offset": 0}, md=4, xs=12),
        dbc.Col(html.Div(id="temperature-card-container"), width={"size": 4, "order": 3, "offset": 0}, md=4, xs=12),
        dbc.Col(html.Div(id="soilmoisture-card-container"), width={"size": 4, "order": 4, "offset": 0}, md=4, xs=12),
        dbc.Col(html.Div(id="humidity-card-container"), width={"size": 4, "order": 2, "offset": 0}, md=4, xs=12),
        dbc.Col(html.Div(id="wind-card-container"), width={"size": 4, "order": 5, "offset": 0}, md=4, xs=12),
        dbc.Col(html.Div(id="sun-pressure-card-container"), width={"size": 4, "order": 6, "offset": 0}, md=4, xs=12),
    ], className="g-2 mb-2"),

], fluid=True)

### === PAGES === ###

# Register main page manually
dash.register_page("index", path="/", layout=main_layout)  # main page

# Import pages explicitly
from pages.rainfall_graph import layout as rainfall_layout
dash.register_page("rainfall_graph", path="/rainfall_graph", layout=rainfall_layout)
from pages.pressure_graph import layout as pressure_layout
dash.register_page("pressure_graph", path="/pressure_graph", layout=pressure_layout)
from pages.temperature_graph import layout as temperature_layout
dash.register_page("temperature_graph", path="/temperature_graph", layout=temperature_layout)
from pages.soilmoisture_graph import layout as soilmoisture_layout
dash.register_page("soilmoisture_graph", path="/soilmoisture_graph", layout=soilmoisture_layout)

# Use dcc.Location to detect URL changes and render correct layout
app.layout = html.Div([
    html.Link(
        rel="stylesheet",
        href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css"
    ),
    dcc.Store(id="weather-data-store"), 
    dcc.Store(id="month-options-store"),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

### === CALLBACKS === ###

#----------------- app configuration -----------------------

# Load data once and store in dcc.Store
@callback(
    Output("weather-data-store", "data"),
    Input("url", "pathname")  # ← Trigger on page load
)
def load_data_on_startup(pathname):
    print("Loading data...")  
    weather_df = load_once_weather_data()
    return weather_df.to_dict('records')

@callback(
    Output("month-options-store", "data"),
    Input("weather-data-store", "data")
)
def compute_month_options(weather_data_dict):
    if not weather_data_dict:
        return [{"label": "No data", "value": "[0, 0]"}]

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    weather_df = weather_df.dropna(subset=['datetime'])

    # Compute available months
    available_months = weather_df['datetime'].dt.to_period('M').unique()
    available_periods = [[p.year, p.month] for p in available_months]
    available_periods.sort()

    MONTH_OPTIONS = [
        {"label": "All Time", "value": "None"}
    ]

    MONTH_OPTIONS.extend([
        {"label": f"{year} - {pd.to_datetime(f'{year}-{month:02d}-01').strftime('%B')}", "value": f"[{year}, {month}]"}
        for year, month in available_periods
    ])

    return MONTH_OPTIONS

@callback(
    Output("month-filter", "options"),
    Output("month-filter", "value"),
    Input("month-options-store", "data")
)
def update_month_options(month_options):
    if not month_options:
        return [], None
    # Set default to last option (most recent)
    default_value = month_options[-1]["value"]
    return month_options, default_value

@callback(
    Output("data-info", "children"),
    Input("weather-data-store", "data")
)

def update_data_info(weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)
    weather_df = weather_df.dropna(subset=['datetime'])

    min_date = weather_df['datetime'].min().strftime("%d %B %Y")
    max_date = weather_df['datetime'].max().strftime("%d %B %Y")

    return html.Div([
        "Data Available",
        html.Br(),
        "from: ",
        html.Span(min_date, style={"fontSize": "0.8rem", "fontWeight": "bold"}),
        html.Br(),
        "until: ",
        html.Span(max_date, style={"fontSize": "0.8rem", "fontWeight": "bold"}),
    ], style={"textAlign": "left"})

# Callback to render page based on URL
@callback(Output('page-content', 'children'),
          Input('url', 'pathname'))
def display_page(pathname):

    if pathname == "/rainfall_graph":
        return page_registry["rainfall_graph"]["layout"]
    if pathname == "/pressure_graph":
        return page_registry["pressure_graph"]["layout"]
    if pathname == "/temperature_graph":
        return page_registry["temperature_graph"]["layout"]
    if pathname == "/soilmoisture_graph":
        return page_registry["soilmoisture_graph"]["layout"]
    else:
        return page_registry["index"]["layout"]
    
# ------------------------- CARDS -----------------------------

# === RAIN FALL === #
@callback(
    Output("rain-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_rain_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")
    
    if selected_month_str == "None":
        time_period = None  # ← Pass None to data_parser
    else:
        try:
            time_period = eval(selected_month_str)  # e.g., [2025, 12]
        except:
            time_period = None  # Fallback

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    rain_df = data_parser(weather_df, 'rain', time_period)
    r_stats = rain_stats(rain_df)
    if selected_month_str == "None":
        return component_rainfall_stats(r_stats, True)
    else:
        return component_rainfall_stats(r_stats, False)

# === HUMIDITY === #

@callback(
    Output("humidity-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_humidity_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")
    
    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Use month-filter if it's not "None"
    if selected_month_str and selected_month_str != "None":
        try:
            time_period = ast.literal_eval(selected_month_str)  # ✅ Safe replacement for eval
        except (ValueError, SyntaxError, TypeError):
            time_period = None
        humidity_df = data_parser(weather_df, 'humidity', time_period=time_period)
    else:
        humidity_df = data_parser(weather_df, 'humidity')  # No filter — note: fixed typo 'humidtiy' → 'humidity'


    h_stats = humidity_stats(humidity_df)
    return component_humidity_stats(h_stats)

# === SUN & PRESSURE === #

@callback(
    Output("sun-pressure-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_sun_pressure_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Use month-filter if it's not "None"
    if selected_month_str and selected_month_str != "None":
        try:
            time_period = ast.literal_eval(selected_month_str)  # ✅ Safe replacement
            # Optional: Validate it's a list of 2 integers
            if not isinstance(time_period, list) or len(time_period) != 2 or not all(isinstance(x, int) for x in time_period):
                time_period = None
        except (ValueError, SyntaxError, TypeError):
            time_period = None

        sun_df = data_parser(weather_df, 'sun', time_period=time_period)
        pressure_df = data_parser(weather_df, 'pressure', time_period=time_period)
    else:
        sun_df = data_parser(weather_df, 'sun')      # No filter
        pressure_df = data_parser(weather_df, 'pressure')  # No filter

    s_stats = sun_stats(sun_df)
    p_stats = pressure_stats(pressure_df)
    return component_sun_stats(s_stats, p_stats)

# === WIND === #

@callback(
    Output("wind-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_wind_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Use month-filter if it's not "None"
    if selected_month_str and selected_month_str != "None":
        try:
            time_period = ast.literal_eval(selected_month_str)  # ✅ Safe replacement for eval
        except (ValueError, SyntaxError, TypeError):
            time_period = None
        wind_df = data_parser(weather_df, 'wind', time_period=time_period)
    else:
        wind_df = data_parser(weather_df, 'wind')  # No filter — note: fixed typo 'humidtiy' → 'humidity'

    w_stats = wind_stats(wind_df)
    #print("Wind Arrow:", repr(w_stats['wind_arrow']))
    return component_wind_stats(w_stats)

# === TEMPERATURE === #
@callback(
    Output("temperature-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_temperature_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")
    
    if selected_month_str == "None":
        time_period = None  # ← Pass None to data_parser
    else:
        try:
            time_period = ast.literal_eval(selected_month_str)  # e.g., [2025, 12]
            # Optional: Validate it's a list of 2 integers
            if not isinstance(time_period, list) or len(time_period) != 2 or not all(isinstance(x, int) for x in time_period):
                time_period = None
        except (ValueError, SyntaxError, TypeError):
            time_period = None  # Fallback

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    temperature_df = data_parser(weather_df, 'temperature', time_period)
    t_stats = temperature_stats(temperature_df)
    return component_temperature_stats(t_stats)

# === SOILMOISTURE === #

@callback(
    Output("soilmoisture-card-container", "children"),
    Input("month-filter", "value"),
    State("weather-data-store", "data")
)
def update_soilmoisture_card(selected_month_str, weather_data_dict):
    if not weather_data_dict:
        return html.Div("Loading...")
    
    if selected_month_str == "None":
        time_period = None  # ← Pass None to data_parser
    else:
        try:
            time_period = ast.literal_eval(selected_month_str)  # e.g., [2025, 12]
            # Optional: Validate it's a list of 2 integers
            if not isinstance(time_period, list) or len(time_period) != 2 or not all(isinstance(x, int) for x in time_period):
                time_period = None
        except (ValueError, SyntaxError, TypeError):
            time_period = None  # Fallback

    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    moisture_df = data_parser(weather_df, 'soilmoisture', time_period)
    sm_stats = soilmoisture_stats(moisture_df)
    return component_soilmoisture_stats(sm_stats)


# DOWNLOAD DATA
@callback(
    Output("download-weather-data", "data"),
    Input("download-btn", "n_clicks"),
    State("month-filter", "value"),
    State("weather-data-store", "data"),
    prevent_initial_call=True
)
def download_weather_data(n_clicks, selected_month_str, weather_data_dict):
    if not n_clicks or not weather_data_dict:
        return None

    # Convert to DataFrame
    weather_df = pd.DataFrame(weather_data_dict)
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Apply filter
    if selected_month_str and selected_month_str != "None":
        try:
            time_period = ast.literal_eval(selected_month_str)  # ✅ Safer than eval
            weather_df = weather_df[
                (weather_df['datetime'].dt.year == time_period[0]) &
                (weather_df['datetime'].dt.month == time_period[1])
            ].copy()
        except:
            pass  # Fallback to no filter

    # Generate CSV
    csv_buffer = StringIO()
    weather_df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()

    # Return for download
    return dict(content=csv_string, filename="weather_data.csv")

# Run app
if __name__ == "__main__":
    app.run(debug=True)