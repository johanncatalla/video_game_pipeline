from dagster import asset, AssetExecutionContext, define_asset_job, AssetIn, AssetsDefinition
import pandas as pd
import os

@asset(
    required_resource_keys={"metacritic_scraper"},
    description="Raw Metacritic data scraped from the website"
)
def raw_metacritic_data(context: AssetExecutionContext) -> str:
    """Scrape data from Metacritic"""
    context.log.info("Starting Metacritic scraping asset")
    
    # Get the number of pages to scrape from config (default to 10)
    num_pages = (context.op_config or {}).get("num_pages", 10)
    
    # Call the scraper
    filepath = context.resources.metacritic_scraper.run(num_pages=num_pages)
    
    context.log.info(f"Metacritic scraping complete. Data saved to {filepath}")
    return filepath

@asset(
    required_resource_keys={"steam_scraper"},
    deps=["raw_metacritic_data"],
    description="Raw Steam data scraped from the website"
)
def raw_steam_data(context: AssetExecutionContext, raw_metacritic_data: str) -> str:
    """Extract game titles and scrape data from Steam"""
    context.log.info(f"Starting Steam scraping asset using data from {raw_metacritic_data}")
    
    # Read the Metacritic CSV to get game titles
    df = pd.read_csv(raw_metacritic_data)
    
    # Extract unique titles
    titles = df['title'].unique().tolist()
    
    # Limit the number of titles to avoid overloading Steam
    max_titles = (context.op_config or {}).get("max_titles", 240)
    titles = titles[:min(len(titles), max_titles)]
    
    context.log.info(f"Extracted {len(titles)} game titles for Steam search")
    
    # Call the scraper
    filepath = context.resources.steam_scraper.run(titles)
    
    context.log.info(f"Steam scraping complete. Data saved to {filepath}")
    return filepath

@asset(
    required_resource_keys={"data_cleaner"},
    deps=["raw_metacritic_data", "raw_steam_data"],
    description="Cleaned Metacritic and Steam data"
)
def cleaned_data(context: AssetExecutionContext, raw_metacritic_data: str, raw_steam_data: str) -> dict:
    """Clean and standardize the data"""
    context.log.info("Starting data cleaning asset")
    
    # Call the cleaner
    result = context.resources.data_cleaner.run(raw_metacritic_data, raw_steam_data)
    
    context.log.info("Data cleaning complete")
    return {
        'metacritic_filepath': result['metacritic']['filepath'],
        'steam_filepath': result['steam']['filepath'],
        'metacritic_df': result['metacritic']['dataframe'],
        'steam_df': result['steam']['dataframe']
    }

@asset(
    required_resource_keys={"data_merger"},
    deps=["cleaned_data"],
    description="Final merged dataset of video games"
)
def video_games_dataset(context: AssetExecutionContext, cleaned_data: dict) -> str:
    """Merge the datasets"""
    context.log.info("Starting data merging asset")
    
    # Output filename
    output_filename = (context.op_config or {}).get("output_filename", "videogames_final.csv")
    
    # Call the merger
    filepath, _ = context.resources.data_merger.run(
        cleaned_data['metacritic_df'], 
        cleaned_data['steam_df'], 
        output_filename
    )
    
    context.log.info(f"Data merging complete. Final data saved to {filepath}")
    
    # Validate the final dataset
    df = pd.read_csv(filepath)
    
    # Check if file exists and is not empty
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        context.log.error("Validation failed: Final file is empty or doesn't exist")
        raise ValueError("Final dataset validation failed")
    
    # Check if we have at least some rows
    min_rows = (context.op_config or {}).get("min_rows", 5)
    if len(df) < min_rows:
        context.log.error(f"Validation failed: Final dataset has only {len(df)} rows, expected at least {min_rows}")
        raise ValueError("Final dataset validation failed")
    
    # Check if we have matched games (where data from both sources was merged)
    matched_games = df[df.get('is_matched', False) == True]
    min_matched = (context.op_config or {}).get("min_matched", 3)
    if len(matched_games) < min_matched:
        context.log.error(f"Validation failed: Only {len(matched_games)} games were matched across both sources, expected at least {min_matched}")
        raise ValueError("Final dataset validation failed")
    
    context.log.info(f"Data validation passed. Final dataset has {len(df)} rows with {len(matched_games)} matched games.")
    return filepath

# Define an asset job for the pipeline
video_games_job = define_asset_job(name="video_games_pipeline_job", selection=["video_games_dataset"])