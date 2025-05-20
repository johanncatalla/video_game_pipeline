from dagster import ScheduleDefinition
from .assets import video_games_job

# Schedule to run the job daily at 01:00 AM
daily_schedule = ScheduleDefinition(
    job=video_games_job,
    cron_schedule="0 1 * * *",  # Run at 1:00 AM every day
    execution_timezone="America/New_York",
    name="video_games_daily_schedule",
)

# Schedule to run the job weekly on Sunday at 03:00 AM
weekly_schedule = ScheduleDefinition(
    job=video_games_job,
    cron_schedule="0 3 * * 0",  # Run at 3:00 AM every Sunday
    execution_timezone="America/New_York",
    name="video_games_weekly_schedule",
)