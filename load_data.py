import pandas as pd

def load_once_weather_data(path="./data/WEATHERDATA_ALL.csv"):
    """
    CORRECTED LOADER:
    1. Attempts strict ISO parsing (YYYY-MM-DD) first.
    2. Falls back to European parsing (DD/MM/YYYY) only for rows that failed step 1.
    3. Prevents 'dayfirst' ambiguity errors.
    """
    print(f"Loading weather data from {path}...")

    # Step 1: Force text loading
    try:
        weather_df = pd.read_csv(path, dtype={'datetime': str})
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return None

    # Step 2: Exclude 'Heap' columns if present
    if 'Heap' in weather_df.columns:
        heap_index = weather_df.columns.get_loc('Heap')
        weather_df = weather_df.iloc[:, :heap_index]

    # Step 3: Sanitize input
    raw_dates = weather_df['datetime'].astype(str).str.strip()
    total_rows = len(raw_dates)

    # --- SEQUENTIAL PARSING LOGIC ---

    # Attempt 1: Strict ISO Format (YYYY-MM-DD HH:MM:SS)
    # This catches '2025-12-13...' immediately without ambiguity.
    parsed_dates = pd.to_datetime(raw_dates, format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # Identify rows that failed ISO parsing
    mask_failed = parsed_dates.isna()
    
    if mask_failed.any():
        count_failed = mask_failed.sum()
        print(f"ℹ️  {count_failed} rows did not match ISO format. Trying European (DD/MM/YYYY)...")
        
        # Attempt 2: European Format on the failed rows only
        # We try a flexible European parser for the remaining rows
        eu_parsed = pd.to_datetime(raw_dates[mask_failed], dayfirst=True, errors='coerce')
        
        # Merge results: Keep ISO successes, fill with European successes
        parsed_dates.loc[mask_failed] = eu_parsed
        
        # Final Check
        remaining_failures = parsed_dates.isna().sum()
        if remaining_failures > 0:
            print(f"⚠️  WARNING: {remaining_failures} rows are still invalid after both attempts.")
            print("   Sample of truly bad data:", raw_dates[parsed_dates.isna()].head(3).tolist())
            
            # Drop unrecoverable rows
            weather_df = weather_df[~parsed_dates.isna()].copy()
            parsed_dates = parsed_dates.dropna()
        else:
            print("✅ Successfully parsed mixed formats (ISO + European).")
    else:
        print("✅ Successfully parsed all dates as ISO.")

    if len(weather_df) == 0:
        print("❌ CRITICAL: No valid data remaining.")
        return None

    # Assign clean dates
    weather_df['datetime'] = parsed_dates

    # Step 4: Sort and Clean
    weather_df = weather_df.sort_values('datetime').reset_index(drop=True)

    # Step 5: Convert to ISO String for storage
    weather_df['datetime'] = weather_df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Step 6: Numeric conversion
    for col in weather_df.columns:
        if col != 'datetime':
            weather_df[col] = pd.to_numeric(weather_df[col], errors='coerce')

    print(f"✅ Success: Loaded {len(weather_df)} valid records.")
    return weather_df