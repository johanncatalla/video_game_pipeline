import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import random
from datetime import datetime

class MetacriticScraper:
    def __init__(self, base_url="https://www.metacritic.com/browse/game/pc/all/all-time/metascore/"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.output_dir = os.path.join(os.getcwd(), "data", "raw")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def get_game_list(self, num_pages=2):
        """Scrape multiple pages of game listings"""
        all_games = []
        
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}?page={page}"
            print(f"Scraping page {page}: {url}")
            
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch page {page}. Status code: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'lxml')
            game_elements = soup.select('.c-finderProductCard')
            
            for game in game_elements:
                try:
                    title_elem = game.select_one('.c-finderProductCard_title')
                    title = title_elem.text.strip() if title_elem else "N/A"
                    
                    link_elem = game.select_one('a.c-finderProductCard_container')
                    game_url = f"https://www.metacritic.com{link_elem['href']}" if link_elem else "N/A"
                    
                    metascore_elem = game.select_one('.c-siteReviewScore')
                    metascore = metascore_elem.text.strip() if metascore_elem else "N/A"
                    
                    release_elem = game.select_one('.c-finderProductCard_meta span')
                    release_date = release_elem.text.strip() if release_elem else "N/A"
                    
                    platform = "PC"  # Since we're specifically scraping PC games
                    
                    game_data = {
                        'title': title,
                        'url': game_url,
                        'metascore': metascore,
                        'platform': platform,
                        'release_date': release_date
                    }
                    
                    all_games.append(game_data)
                except Exception as e:
                    print(f"Error parsing game: {e}")
            
            # Respect website by adding delay between requests
            time.sleep(random.uniform(1.5, 3.0))
            
        return all_games
    
    def get_game_details(self, games_list):
        """Fetch detailed information for each game"""
        detailed_games = []
        
        for idx, game in enumerate(games_list):
            try:
                print(f"Fetching details for game {idx+1}/{len(games_list)}: {game['title']}")
                
                response = requests.get(game['url'], headers=self.headers)
                if response.status_code != 200:
                    print(f"Failed to fetch details for {game['title']}. Status code: {response.status_code}")
                    detailed_games.append(game)  # Add the basic info we already have
                    continue
                
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Extract user score
                user_score_elem = soup.select_one('.c-siteReviewScore_user')
                user_score = user_score_elem.text.strip() if user_score_elem else "N/A"
                
                # Extract critic reviews count
                critic_count_elem = soup.select_one('.c-siteReviewScore_title span')
                critic_count = critic_count_elem.text.strip().replace('Critic Reviews', '').strip() if critic_count_elem else "N/A"
                
                # Extract user reviews count
                user_count_elem = soup.select_one('.c-siteReviewScore_user + .c-siteReviewScore_title span')
                user_count = user_count_elem.text.strip().replace('User Ratings', '').strip() if user_count_elem else "N/A"
                
                # Extract developer
                developer_elem = soup.select_one('.c-gameDetails_Developer .c-gameDetails_listItem a')
                developer = developer_elem.text.strip() if developer_elem else "N/A"
                
                # Extract publisher
                publisher_elem = soup.select_one('.c-gameDetails_Distributor a')
                publisher = publisher_elem.text.strip() if publisher_elem else "N/A"
                
                # Extract genres
                genre_elems = soup.select('.c-genreList_item .c-globalButton_label')
                genres = [g.text.strip() for g in genre_elems] if genre_elems else []
                
                # Update game data with detailed information
                detailed_game = {
                    **game,
                    'user_score': user_score,
                    'critic_count': critic_count,
                    'user_count': user_count,
                    'developer': developer,
                    'publisher': publisher,
                    'genres': ', '.join(genres) if genres else "N/A"
                }
                
                detailed_games.append(detailed_game)
                
                # Respect website by adding delay between requests
                time.sleep(random.uniform(1.5, 3.0))
                
            except Exception as e:
                print(f"Error fetching details for {game['title']}: {e}")
                detailed_games.append(game)  # Add the basic info we already have
        
        return detailed_games
    
    def save_to_csv(self, games, filename=None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metacritic_games_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Determine fieldnames from the first game with the most fields
            fieldnames = []
            for game in games:
                if len(game.keys()) > len(fieldnames):
                    fieldnames = list(game.keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games)
            
        print(f"Saved {len(games)} games to {filepath}")
        return filepath
    
    def run(self, num_pages=2, output_filename=None):
        """Run the complete scraping process"""
        print(f"Starting Metacritic scraper for {num_pages} pages")
        games_list = self.get_game_list(num_pages)
        print(f"Found {len(games_list)} games in list pages")
        
        detailed_games = self.get_game_details(games_list)
        print(f"Processed {len(detailed_games)} games with details")
        
        filepath = self.save_to_csv(detailed_games, output_filename)
        return filepath

if __name__ == "__main__":
    # Test the scraper
    scraper = MetacriticScraper()
    scraper.run(num_pages=1)  # Scrape just 1 page for testing