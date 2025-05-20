from dagster import repository, with_resources
from .resources import (
    metacritic_scraper_resource,
    steam_scraper_resource,
    data_cleaner_resource,
    data_merger_resource
)
from .assets import raw_metacritic_data, raw_steam_data, cleaned_data, video_games_dataset, video_games_job
from .schedules import daily_schedule, weekly_schedule

@repository
def video_games_repository():
    """Repository for the video games pipeline"""
    
    # Define resources
    resources = {
        "metacritic_scraper": metacritic_scraper_resource,
        "steam_scraper": steam_scraper_resource,
        "data_cleaner": data_cleaner_resource,
        "data_merger": data_merger_resource
    }
    
    # Apply resources to assets
    resource_assets = with_resources(
        [raw_metacritic_data, raw_steam_data, cleaned_data, video_games_dataset],
        resources
    )
    
    return [
        # Assets
        *resource_assets,
        
        # Jobs
        video_games_job,
        
        # Schedules
        daily_schedule,
        weekly_schedule
    ]