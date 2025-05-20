import pandas as pd
import os
from datetime import datetime
from difflib import SequenceMatcher
import re

class DataMerger:
    def __init__(self):
        self.final_dir = os.path.join(os.getcwd(), "data", "final")
        os.makedirs(self.final_dir, exist_ok=True)
    
    def string_similarity(self, a, b):
        """Calculate string similarity between two strings"""
        if not isinstance(a, str) or not isinstance(b, str):
            return 0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def clean_game_title(self, title):
        """Remove numbering and clean game titles"""
        if not isinstance(title, str):
            return title
        
        # Remove numbering pattern like "235. " from the start of the title
        title = re.sub(r'^\d+\.\s*', '', title)
        
        # Remove any extra whitespace
        title = title.strip()
        
        return title
    
    def merge_datasets(self, metacritic_df, steam_df):
        """Merge Metacritic and Steam datasets based on game title and developer"""
        print("Merging Metacritic and Steam datasets")
        
        # Create a copy of dataframes to avoid modifying originals
        metacritic = metacritic_df.copy()
        steam = steam_df.copy()
        
        # Clean game titles
        metacritic['title'] = metacritic['title'].apply(self.clean_game_title)
        steam['title'] = steam['title'].apply(self.clean_game_title)
        
        # Filter out rows without titles
        metacritic = metacritic[metacritic['title'].notna() & (metacritic['title'] != '')]
        steam = steam[steam['title'].notna() & (steam['title'] != '')]
        
        # Ensure consistent column names
        metacritic = metacritic.rename(columns={
            'title': 'game_title',
            'url': 'metacritic_url',
            'metascore': 'metascore',
            'platform': 'platform',
            'release_date': 'release_date',
            'developer': 'developer',
            'publisher': 'publisher',
            'genres': 'genres'
        })
        
        steam = steam.rename(columns={
            'title': 'game_title',
            'app_url': 'steam_url',
            'price': 'price',
            'discount': 'discount',
            'review_summary': 'steam_review_summary',
            'review_count': 'steam_review_count',
            'release_date': 'steam_release_date',
            'developer': 'steam_developer',
            'publisher': 'steam_publisher',
            'tags': 'steam_tags'
        })
        
        # Create a merged dataframe
        merged_df = pd.DataFrame()
        
        # For each Metacritic game, find the best matching Steam game
        for idx, mc_game in metacritic.iterrows():
            best_match = None
            best_score = 0
            
            mc_title = mc_game['game_title']
            mc_developer = mc_game['developer']
            
            for _, steam_game in steam.iterrows():
                steam_title = steam_game['game_title']
                steam_developer = steam_game['steam_developer']
                
                # Calculate title similarity
                title_sim = self.string_similarity(mc_title, steam_title)
                
                # If developers are available, calculate developer similarity
                if isinstance(mc_developer, str) and isinstance(steam_developer, str) and mc_developer != 'N/A' and steam_developer != 'N/A':
                    dev_sim = self.string_similarity(mc_developer, steam_developer)
                    # Weighted score (title is more important)
                    match_score = title_sim * 0.7 + dev_sim * 0.3
                else:
                    # If developer info not available, use only title similarity
                    match_score = title_sim
                
                # Check if this is the best match so far
                if match_score > best_score and match_score > 0.7:  # 0.7 threshold for confidence
                    best_score = match_score
                    best_match = steam_game
            
            # If we found a good match, add it to the merged dataframe
            if best_match is not None:
                # Create a standardized row with all possible columns
                merged_row = {
                    'game_title': mc_title,
                    'metacritic_url': mc_game['metacritic_url'],
                    'metascore': mc_game['metascore'],
                    'platform': mc_game['platform'],
                    'release_date': mc_game['release_date'],
                    'developer': mc_game['developer'],
                    'publisher': mc_game['publisher'],
                    'genres': mc_game['genres'],
                    'steam_url': best_match['steam_url'],
                    'price': best_match['price'],
                    'discount': best_match['discount'],
                    'steam_review_summary': best_match['steam_review_summary'],
                    'steam_review_count': best_match['steam_review_count'],
                    'steam_release_date': best_match['steam_release_date'],
                    'steam_developer': best_match['steam_developer'],
                    'steam_publisher': best_match['steam_publisher'],
                    'steam_tags': best_match['steam_tags'],
                    'match_confidence': best_score,
                    'is_matched': True
                }
                merged_df = pd.concat([merged_df, pd.DataFrame([merged_row])], ignore_index=True)
        
        # Add the Metacritic games that weren't matched
        matched_mc_titles = set(merged_df['game_title'])
        unmatched_mc = metacritic[~metacritic['game_title'].isin(matched_mc_titles)]
        
        # Create standardized rows for unmatched Metacritic games
        for _, mc_game in unmatched_mc.iterrows():
            unmatched_row = {
                'game_title': mc_game['game_title'],
                'metacritic_url': mc_game['metacritic_url'],
                'metascore': mc_game['metascore'],
                'platform': mc_game['platform'],
                'release_date': mc_game['release_date'],
                'developer': mc_game['developer'],
                'publisher': mc_game['publisher'],
                'genres': mc_game['genres'],
                'steam_url': None,
                'price': None,
                'discount': None,
                'steam_review_summary': None,
                'steam_review_count': None,
                'steam_release_date': None,
                'steam_developer': None,
                'steam_publisher': None,
                'steam_tags': None,
                'match_confidence': 0,
                'is_matched': False
            }
            merged_df = pd.concat([merged_df, pd.DataFrame([unmatched_row])], ignore_index=True)
        
        # Add the Steam games that weren't matched
        matched_steam_titles = set(merged_df['game_title'])
        unmatched_steam = steam[~steam['game_title'].isin(matched_steam_titles)]
        
        # Create standardized rows for unmatched Steam games
        for _, steam_game in unmatched_steam.iterrows():
            unmatched_row = {
                'game_title': steam_game['game_title'],
                'metacritic_url': None,
                'metascore': None,
                'platform': None,
                'release_date': None,
                'developer': None,
                'publisher': None,
                'genres': None,
                'steam_url': steam_game['steam_url'],
                'price': steam_game['price'],
                'discount': steam_game['discount'],
                'steam_review_summary': steam_game['steam_review_summary'],
                'steam_review_count': steam_game['steam_review_count'],
                'steam_release_date': steam_game['steam_release_date'],
                'steam_developer': steam_game['steam_developer'],
                'steam_publisher': steam_game['steam_publisher'],
                'steam_tags': steam_game['steam_tags'],
                'match_confidence': 0,
                'is_matched': False
            }
            merged_df = pd.concat([merged_df, pd.DataFrame([unmatched_row])], ignore_index=True)
        
        # Filter out any rows that don't have a game title
        merged_df = merged_df[merged_df['game_title'].notna() & (merged_df['game_title'] != '')]
        
        # Add a combined score for matched games
        merged_df['combined_score'] = None
        mask = (merged_df['is_matched'] == True) & (merged_df['metascore'].notna()) & (merged_df['steam_review_summary'].notna())
        
        if mask.any():
            # Convert metascore to float and steam review to numeric value
            merged_df.loc[mask, 'metascore'] = pd.to_numeric(merged_df.loc[mask, 'metascore'], errors='coerce')
            merged_df.loc[mask, 'steam_review_score'] = pd.to_numeric(
                merged_df.loc[mask, 'steam_review_summary'].str.extract(r'(\d+)')[0], 
                errors='coerce'
            )
            
            merged_df.loc[mask, 'combined_score'] = (
                merged_df.loc[mask, 'metascore'] * 0.6 + 
                merged_df.loc[mask, 'steam_review_score'] * 0.4
            )
        
        return merged_df
    
    def save_merged_data(self, merged_df, filename=None):
        """Save merged data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"videogames_merged_{timestamp}.csv"
        
        filepath = os.path.join(self.final_dir, filename)
        merged_df.to_csv(filepath, index=False)
        
        print(f"Saved merged data to {filepath}")
        return filepath
    
    def run(self, metacritic_df, steam_df, output_filename=None):
        """Run the complete merging process"""
        merged_df = self.merge_datasets(metacritic_df, steam_df)
        filepath = self.save_merged_data(merged_df, output_filename)
        
        print(f"Merger complete. {len(merged_df)} total games in the final dataset.")
        return filepath, merged_df
