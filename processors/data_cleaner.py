import pandas as pd
import os
import re
from datetime import datetime

class DataCleaner:
    def __init__(self):
        self.processed_dir = os.path.join(os.getcwd(), "data", "processed")
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def clean_metacritic_data(self, filepath):
        """Clean and standardize Metacritic data"""
        print(f"Cleaning Metacritic data from {filepath}")
        
        # Read the CSV
        df = pd.read_csv(filepath)
        
        # Remove any duplicate entries based on title and URL
        df = df.drop_duplicates(subset=['title', 'url'])
        
        # Clean and standardize Metascore
        df['metascore'] = df['metascore'].apply(lambda x: pd.to_numeric(str(x).strip(), errors='coerce'))
        
        # Clean and standardize User Score
        df['user_score'] = df['user_score'].apply(
            lambda x: pd.to_numeric(re.sub(r'[^\d.]', '', str(x)) if x not in ['N/A', 'tbd', ''] else None, errors='coerce'))
        
        # Clean and standardize Critic Count
        df['critic_count'] = df['critic_count'].apply(
            lambda x: pd.to_numeric(re.sub(r'[^\d]', '', str(x)) if x not in ['N/A', ''] else None, errors='coerce'))
        
        # Clean and standardize User Count
        df['user_count'] = df['user_count'].apply(
            lambda x: pd.to_numeric(re.sub(r'[^\d]', '', str(x)) if x not in ['N/A', ''] else None, errors='coerce'))
        
        # Standardize release date format
        df['release_date'] = df['release_date'].apply(self._standardize_date)
        
        # Extract release year
        df['release_year'] = df['release_date'].apply(
            lambda x: int(x.split('-')[0]) if isinstance(x, str) and '-' in x else None)
        
        # Save the cleaned data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filepath = os.path.join(self.processed_dir, f"metacritic_cleaned_{timestamp}.csv")
        df.to_csv(output_filepath, index=False)
        
        print(f"Saved cleaned Metacritic data to {output_filepath}")
        return output_filepath, df
    
    def clean_steam_data(self, filepath):
        """Clean and standardize Steam data"""
        print(f"Cleaning Steam data from {filepath}")
        
        # Read the CSV
        df = pd.read_csv(filepath)
        
        # Remove any duplicate entries based on app_id
        df = df.drop_duplicates(subset=['app_id'])
        
        # Clean and standardize price
        df['price_numeric'] = df['price'].apply(self._extract_price)
        
        # Clean and standardize discount
        df['discount_percent'] = df['discount'].apply(
            lambda x: pd.to_numeric(re.sub(r'[^\d]', '', str(x)) if x not in ['N/A', '0%', ''] else 0, errors='coerce'))
        
        # Standardize review count
        df['review_count_numeric'] = df['review_count'].apply(
            lambda x: pd.to_numeric(re.sub(r'[^\d]', '', str(x)) if x not in ['N/A', ''] else None, errors='coerce'))
        
        # Map review summary to a numeric score (very rough approximation)
        review_map = {
            'Overwhelmingly Positive': 95,
            'Very Positive': 85,
            'Positive': 75,
            'Mostly Positive': 65,
            'Mixed': 50,
            'Mostly Negative': 35,
            'Negative': 25,
            'Very Negative': 15,
            'Overwhelmingly Negative': 5
        }
        df['review_score_approx'] = df['review_summary'].apply(
            lambda x: review_map.get(str(x).strip(), None))
        
        # Standardize release date format
        df['release_date'] = df['release_date'].apply(self._standardize_date)
        
        # Extract release year
        df['release_year'] = df['release_date'].apply(
            lambda x: int(x.split('-')[0]) if isinstance(x, str) and '-' in x else None)
        
        # Save the cleaned data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filepath = os.path.join(self.processed_dir, f"steam_cleaned_{timestamp}.csv")
        df.to_csv(output_filepath, index=False)
        
        print(f"Saved cleaned Steam data to {output_filepath}")
        return output_filepath, df
    
    def _extract_price(self, price_str):
        """Extract numeric price value from string"""
        if not isinstance(price_str, str):
            return None
            
        price_str = price_str.strip()
        if price_str in ['N/A', 'Free', 'Free to Play', '']:
            return 0.0
            
        # Extract numeric value using regex
        price_match = re.search(r'[\d.,]+', price_str)
        if price_match:
            # Remove non-numeric chars except decimal point
            price_numeric = re.sub(r'[^\d.]', '', price_match.group())
            try:
                return float(price_numeric)
            except:
                return None
        return None
    
    def _standardize_date(self, date_str):
        """Convert various date formats to YYYY-MM-DD"""
        if not isinstance(date_str, str) or date_str in ['N/A', 'TBA', '']:
            return None
            
        # Remove extra information in parentheses
        date_str = re.sub(r'\(.*?\)', '', date_str).strip()
        
        # Try different date formats
        date_formats = [
            '%b %d, %Y',     # Jan 01, 2020
            '%B %d, %Y',     # January 01, 2020
            '%d %b, %Y',     # 01 Jan, 2020
            '%d %B, %Y',     # 01 January, 2020
            '%d %b %Y',      # 01 Jan 2020
            '%d %B %Y',      # 01 January 2020
            '%b %d %Y',      # Jan 01 2020
            '%B %d %Y',      # January 01 2020
            '%Y-%m-%d',      # 2020-01-01
            '%m/%d/%Y',      # 01/01/2020
            '%d/%m/%Y',      # 01/01/2020
            '%Y',            # 2020 (year only)
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                # Return in ISO format (YYYY-MM-DD)
                if fmt == '%Y':
                    # For year-only, set to January 1st
                    return f"{date_obj.year}-01-01"
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        # If we couldn't parse the date, check if it's just a year
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return f"{year_match.group()}-01-01"
            
        # If all parsing attempts failed
        return None

    def run(self, metacritic_filepath, steam_filepath):
        """Run the complete cleaning process"""
        metacritic_output, metacritic_df = self.clean_metacritic_data(metacritic_filepath)
        steam_output, steam_df = self.clean_steam_data(steam_filepath)
        
        return {
            'metacritic': {
                'filepath': metacritic_output,
                'dataframe': metacritic_df
            },
            'steam': {
                'filepath': steam_output,
                'dataframe': steam_df
            }
        }

if __name__ == "__main__":
    # Test the cleaner
    cleaner = DataCleaner()
    # These paths would need to be actual file paths from your previous scraping
    # cleaner.run("data/raw/metacritic_games_20230101_120000.csv", "data/raw/steam_games_20230101_120000.csv")