import pandas as pd

def load_once_weather_data(path="./data/WEATHERDATA_ALL.csv"):
    """
    Loads and cleans weather data based on template column names.
    Returns a cleaned DataFrame ready for plotting.
    """
    print("Loading data for the first time...")

    # Step 1: Load weather data
    weather_df = pd.read_csv(path)

    # Step 2: Exclude all columns from 'Heap' onwards (inclusive)
    if 'Heap' in weather_df.columns:
        heap_index = weather_df.columns.get_loc('Heap')
        weather_df = weather_df.iloc[:, :heap_index]

    # Step 3: Convert 'time' column to datetime
    weather_df['datetime'] = pd.to_datetime(weather_df['datetime'], errors='coerce')
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Step 3.5: Convert back to string in ISO format for safe storage in Store
    weather_df['datetime'] = weather_df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Step 4: Convert all non-datetime columns to numeric (if possible)
    for col in weather_df.columns:
        if col != 'datetime':  # Skip datetime column
            weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')

    print("Data loaded successfully.")


    return weather_df
