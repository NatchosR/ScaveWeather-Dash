# utils.py
import pandas as pd

def data_parser(df, parameter: str, time_period:list = None, date1=None, date2=None):
    if time_period:
        df = df[(df['datetime'].dt.year == time_period[0]) & (df['datetime'].dt.month == time_period[1])].copy()
   
    if parameter == 'rain':
        rain_col = ['datetime', 'rain_rate', 'rain_daily', 'rain_event', 'rain_hourly', 'rain_24h', 'rain_weekly', 'rain_monthly', 'rain_yearly']
        return df[rain_col].copy()

    if parameter == 'wind':
        wind_col = ['datetime','wind_speed', 'wind_gust', 'wind_direction', '10_minute_avg_wind_direction']
        return df[wind_col].copy()

    if parameter == 'sun':
        sun_col = ['datetime', 'solar', 'uvi']
        return df[sun_col].copy()

    if parameter == 'humidity':
        humidity_col = ['datetime','humidity', 'humidity_low', 'humidity_high', 'vpd']
        return df[humidity_col].copy()

    if parameter == 'soilmoisture':
        soilmoisutre_col = ['datetime','4ENES_EL_soil_moisture','4ENES_L_soil_moisture','6ESOS_L_soil_moisture',
                         '8ESEU_L_soil_moisture', '6ESOS_EL_soil_moisture', '7ESES_EL_soil_moisture',
                         '3ENEU_EL_soil_moisture', '3ENEU_L_soil_moisture']
        return df[soilmoisutre_col].copy()

    if parameter == 'temperature':
        temperature_col = ['datetime','temperature', 'temperature_low', 'temperature_high', 'feels_like', 'dew_point',
                         '4ENES_EL_soil_temperature', '4ENES_L_soil_temperature', '8ESEU_EL_soil_temperature',
                         '8ESEU_L_soil_temperature', '6ESOS_EL_soil_temperature', '6ESOS_L_soil_temperature',
                         '3ENOU_EL_soil_temperature', '3ENOU_L_soil_temperature']
        return df[temperature_col].copy()

    if parameter == 'pressure':
        pressure_col = ['datetime', 'pressure_relative', 'pressure_relative_low', 'pressure_relative_high', 'pressure_absolute']
        return df[pressure_col].copy()

    return df.copy()