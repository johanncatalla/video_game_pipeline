import requests
from bs4 import BeautifulSoup
import time
import csv
import os
import random
import json
from datetime import datetime

class SteamScraper:
    def __init__(self):
        self.search_url = "https://store.steampowered.com/search/"
        self.app_url = "https://store.steampowered.com/app/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        self.output_dir = os.path.join(os.getcwd(), "data", "raw")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def search_game(self, game_title):
        """Search for a game on Steam"""
        search_params = {
            'term': game_title,
            'category1': 998,  # Games category
        }
        
        try:
            response = requests.get(self.search_url, params=search_params, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to search for {game_title}. Status code: {response.status_code}")
                return None
                
            soup = BeautifulSoup(response.text, 'lxml')
            results = soup.select('#search_resultsRows a')
            
            if not results:
                print(f"No results found for {game_title}")
                return None
            
            # Take the first result (most relevant match)
            first_result = results[0]
            app_id = first_result['data-ds-appid']
            app_url = f"{self.app_url}{app_id}"
            
            result = {
                'search_term': game_title,
                'app_id': app_id,
                'app_url': app_url
            }
            
            return result
            
        except Exception as e:
            print(f"Error searching for {game_title}: {e}")
            return None
    
    def get_game_details(self, app_url):
        """Get detailed information about a game from its Steam page"""
        try:
            # Add age verification parameters to avoid age check page
            params = {
                'birthtime': 536457600,  # A timestamp for age verification
                'mature_content': 1
            }
            
            response = requests.get(app_url, params=params, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to fetch details for {app_url}. Status code: {response.status_code}")
                return {}
                
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract the game title
            title_elem = soup.select_one('.apphub_AppName')
            title = title_elem.text.strip() if title_elem else "N/A"
            
            # Extract current price
            price_elem = soup.select_one('.game_purchase_price')
            if not price_elem:
                price_elem = soup.select_one('.discount_final_price')  # Check for discounted price
            price = price_elem.text.strip() if price_elem else "N/A"
            
            # Extract discount percentage if available
            discount_elem = soup.select_one('.discount_pct')
            discount = discount_elem.text.strip() if discount_elem else "0%"
            
            # Extract user reviews
            review_elem = soup.select_one('.user_reviews_summary_row .game_review_summary')
            review_text = review_elem.text.strip() if review_elem else "N/A"
            
            # Try to extract review percentage
            review_count_elem = soup.select_one('.user_reviews_summary_row .responsive_hidden')
            review_count = "N/A"
            if review_count_elem:
                review_count = review_count_elem.text.strip().replace('(', '').replace(')', '')
            
            # Extract release date
            release_date_elem = soup.select_one('.release_date .date')
            release_date = release_date_elem.text.strip() if release_date_elem else "N/A"
            
            # Extract developer
            dev_elem = soup.select_one('#developers_list a')
            developer = dev_elem.text.strip() if dev_elem else "N/A"
            
            # Extract publisher from details block
            publisher = "N/A"
            details_block = soup.select('.details_block')
            for block in details_block:
                if 'Publisher:' in block.text:
                    publisher_links = block.select('a')
                    for link in publisher_links:
                        if block.text.find('Publisher:') < block.text.find(link.text):
                            publisher = link.text.strip()
                            break
            
            # Extract tags
            tags = []
            tags_elems = soup.select('.popular_tags a')
            for tag in tags_elems:
                tag_text = tag.text.strip()
                if tag_text:  # Skip empty tags
                    tags.append(tag_text)
            
            # Extract minimum system requirements
            sys_req = {}
            req_divs = soup.select('.game_area_sys_req')
            if req_divs:
                min_req_div = req_divs[0]  # First div should be minimum requirements
                req_list = min_req_div.select('li')
                for req in req_list:
                    req_text = req.text.strip()
                    if ':' in req_text:
                        key, value = req_text.split(':', 1)
                        sys_req[key.strip()] = value.strip()
            
            # Compile all details into a dictionary
            game_details = {
                'title': title,
                'app_url': app_url,
                'price': price,
                'discount': discount,
                'review_summary': review_text,
                'review_count': review_count,
                'release_date': release_date,
                'developer': developer,
                'publisher': publisher,
                'tags': ', '.join(tags) if tags else "N/A",
                'system_requirements': json.dumps(sys_req) if sys_req else "N/A"
            }
            
            return game_details
            
        except Exception as e:
            print(f"Error fetching details for {app_url}: {e}")
            return {}
    
    def process_game_list(self, game_titles):
        """Process a list of game titles to get Steam details"""
        steam_games = []
        
        for idx, title in enumerate(game_titles):
            print(f"Processing game {idx+1}/{len(game_titles)}: {title}")
            
            # Search for the game
            search_result = self.search_game(title)
            if not search_result:
                print(f"Could not find {title} on Steam")
                steam_games.append({'search_term': title, 'found': False})
                time.sleep(random.uniform(5.0, 7.0))  # Respect Steam's crawl-delay
                continue
                
            # Get detailed information
            app_url = search_result['app_url']
            game_details = self.get_game_details(app_url)
            
            # Combine search result and game details
            game_data = {
                **search_result,
                **game_details,
                'found': True
            }
            
            steam_games.append(game_data)
            
            # Respect Steam's crawl-delay: 5 directive
            time.sleep(random.uniform(5.0, 7.0))
        
        return steam_games
    
    def save_to_csv(self, games, filename=None):
        """Save scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"steam_games_{timestamp}.csv"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Determine fieldnames from all games
            fieldnames = set()
            for game in games:
                fieldnames.update(game.keys())
            
            fieldnames = sorted(list(fieldnames))
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(games)
            
        print(f"Saved {len(games)} games to {filepath}")
        return filepath
    
    def run(self, game_titles, output_filename=None):
        """Run the complete scraping process for a list of game titles"""
        print(f"Starting Steam scraper for {len(game_titles)} games")
        
        steam_games = self.process_game_list(game_titles)
        print(f"Processed {len(steam_games)} games")
        
        filepath = self.save_to_csv(steam_games, output_filename)
        return filepath

if __name__ == "__main__":
    # Test the scraper with a few game titles
    test_titles = ["Elden Ring", "Baldur's Gate 3", "Cyberpunk 2077"]
    scraper = SteamScraper()
    scraper.run(test_titles)