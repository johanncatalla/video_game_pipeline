import pandas as pd
from dagster import op, In, Out, OpExecutionContext
import os

@op(
    ins={
        "context": In(None),
    },
    out=Out(str),
    required_resource_keys={"metacritic_scraper"}
)
def scrape_metacritic(context: OpExecutionContext) -> str:
    """Scrape data from Metacritic"""
    context.log.info("Starting Metacritic scraping operation")
    
    # Get the number of pages to scrape from config (default to 2)
    num_pages = context.op_config.get("num_pages", 2)
    
    # Call the scraper
    filepath = context.resources.metacritic_scraper.run(num_pages=num_pages)
    
    context.log.info(f"Metacritic scraping complete. Data saved to {filepath}")
    return filepath

@op(
    ins={
        "metacritic_filepath": In(str),
    },
    out=Out(list),
    required_resource_keys={"steam_scraper"}
)
def extract_game_titles(context: OpExecutionContext, metacritic_filepath: str) -> list:
    """Extract game titles from Metacritic data for Steam search"""
    context.log.info(f"Extracting game titles from {metacritic_filepath}")
    
    # Read the Metacritic CSV
    df = pd.read_csv(metacritic_filepath)
    
    # Extract unique titles
    titles = df['title'].unique().tolist()
    
    # Limit the number of titles to avoid overloading Steam
    max_titles = context.op_config.get("max_titles", 20)
    titles = titles[:min(len(titles), max_titles)]
    
    context.log.info(f"Extracted {len(titles)} game titles for Steam search")
    return titles

@op(
    ins={
        "game_titles": In(list),
    },
    out=Out(str),
    required_resource_keys={"steam_scraper"}
)
def scrape_steam(context: OpExecutionContext, game_titles: list) -> str:
    """Scrape data from Steam"""
    context.log.info(f"Starting Steam scraping operation for {len(game_titles)} games")
    
    # Call the scraper
    filepath = context.resources.steam_scraper.run(game_titles)
    
    context.log.info(f"Steam scraping complete. Data saved to {filepath}")
    return filepath

@op(
    ins={
        "metacritic_filepath": In(str),
        "steam_filepath": In(str),
    },
    out={
        "metacritic_cleaned": Out(str),
        "steam_cleaned": Out(str),
        "metacritic_df": Out(pd.DataFrame),
        "steam_df": Out(pd.DataFrame),
    },
    required_resource_keys={"data_cleaner"}
)
def clean_data(context: OpExecutionContext, metacritic_filepath: str, steam_filepath: str):
    """Clean and standardize the data"""
    context.log.info("Starting data cleaning operation")
    
    # Call the cleaner
    result = context.resources.data_cleaner.run(metacritic_filepath, steam_filepath)
    
    context.log.info("Data cleaning complete")
    return (
        result['metacritic']['filepath'],
        result['steam']['filepath'],
        result['metacritic']['dataframe'],
        result['steam']['dataframe']
    )

@op(
    ins={
        "metacritic_df": In(pd.DataFrame),
        "steam_df": In(pd.DataFrame),
    },
    out=Out(str),
    required_resource_keys={"data_merger"}
)
def merge_data(context: OpExecutionContext, metacritic_df: pd.DataFrame, steam_df: pd.DataFrame) -> str:
    """Merge the datasets"""
    context.log.info("Starting data merging operation")
    
    # Output filename
    output_filename = context.op_config.get("output_filename", "videogames_final.csv")
    
    # Call the merger
    filepath, _ = context.resources.data_merger.run(metacritic_df, steam_df, output_filename)
    
    context.log.info(f"Data merging complete. Final data saved to {filepath}")
    return filepath

@op(
    ins={
        "final_filepath": In(str),
    },
    out=Out(bool)
)
def validate_data(context: OpExecutionContext, final_filepath: str) -> bool:
    """Validate the final dataset"""
    context.log.info(f"Validating final dataset at {final_filepath}")
    
    # Read the final CSV
    df = pd.read_csv(final_filepath)
    
    # Check if file exists and is not empty
    if not os.path.exists(final_filepath) or os.path.getsize(final_filepath) == 0:
        context.log.error("Validation failed: Final file is empty or doesn't exist")
        return False
    
    # Check if we have at least some rows
    min_rows = context.op_config.get("min_rows", 5)
    if len(df) < min_rows:
        context.log.error(f"Validation failed: Final dataset has only {len(df)} rows, expected at least {min_rows}")
        return False
    
    # Check if we have matched games (where data from both sources was merged)
    matched_games = df[df.get('is_matched', False) == True]
    min_matched = context.op_config.get("min_matched", 3)
    if len(matched_games) < min_matched:
        context.log.error(f"Validation failed: Only {len(matched_games)} games were matched across both sources, expected at least {min_matched}")
        return False
    
    # Check for required columns
    required_columns = [
        'mc_title', 'mc_metascore', 'mc_genres', 'mc_developer',
        'steam_title', 'steam_price_numeric', 'steam_tags'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        context.log.error(f"Validation failed: Missing required columns: {missing_columns}")
        return False
    
    context.log.info(f"Data validation passed. Final dataset has {len(df)} rows with {len(matched_games)} matched games.")
    return True