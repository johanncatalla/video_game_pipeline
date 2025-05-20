from dagster import resource, InitResourceContext

@resource
def metacritic_scraper_resource(context):
    """Resource for the Metacritic scraper"""
    from scrapers.metacritic_scraper import MetacriticScraper
    return MetacriticScraper()

@resource
def steam_scraper_resource(context):
    """Resource for the Steam scraper"""
    from scrapers.steam_scraper import SteamScraper
    return SteamScraper()

@resource
def data_cleaner_resource(context):
    """Resource for the data cleaner"""
    from processors.data_cleaner import DataCleaner
    return DataCleaner()

@resource
def data_merger_resource(context):
    """Resource for the data merger"""
    from processors.data_merger import DataMerger
    return DataMerger()