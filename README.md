# Video Game Data Pipeline and Analytics Dashboard

## Project Overview
This project implements an end-to-end data pipeline for collecting, processing, and analyzing video game data from Metacritic and Steam. The pipeline uses Dagster for orchestration and includes a React-based analytics dashboard for data visualization.

## Project Structure
```
video_game_pipeline/
├── data/                      # Data storage directory
│   └── final/                # Processed data files
├── dagster_pipeline/         # Dagster pipeline configuration
├── processors/               # Data processing modules
│   ├── data_cleaner.py      # Data cleaning operations
│   └── data_merger.py       # Data merging operations
├── scrapers/                 # Web scraping modules
│   ├── metacritic_scraper.py # Metacritic data scraper
│   └── steam_scraper.py      # Steam data scraper
├── App.js                    # React dashboard application
├── requirements.txt          # Python dependencies
└── workspace.yaml           # Dagster workspace configuration
```

## Components

### 1. Web Scraping
The project includes two web scrapers:

#### Metacritic Scraper
- Extracts game information from Metacritic including:
  - Game title
  - Metascore
  - Platform
  - Release date
  - Developer
  - Publisher
  - Genres

#### Steam Scraper
- Extracts game information from Steam including:
  - Game title
  - Price
  - Discount
  - Review summary
  - Review count
  - Release date
  - Developer
  - Publisher
  - Tags

### 2. Data Processing
The data processing pipeline includes:

#### Data Cleaning
- Standardizes game titles
- Normalizes dates
- Handles missing values
- Removes duplicates
- Validates data types

#### Data Merging
- Matches games between Metacritic and Steam
- Calculates match confidence scores
- Combines complementary data
- Generates unified dataset

### 3. Dagster Pipeline
The Dagster pipeline orchestrates the entire process:

- Schedules regular data collection
- Executes data quality checks
- Manages data processing steps
- Saves results to CSV

### 4. Analytics Dashboard
A React-based dashboard visualizes the collected data:

#### Features
- Overview statistics
- Genre distribution
- Price analysis
- Review score trends
- Developer/publisher insights

[SCREENSHOT_PLACEHOLDER_1: Dashboard Overview]
[SCREENSHOT_PLACEHOLDER_2: Genre Distribution Chart]
[SCREENSHOT_PLACEHOLDER_3: Price Analysis Graph]
[SCREENSHOT_PLACEHOLDER_4: Review Score Trends]

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Installation Steps

1. Clone the repository:
```bash
git clone [repository-url]
cd video_game_pipeline
```

2. Set up Python environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install frontend dependencies:
```bash
npm install
```

4. Configure environment variables:
Create a `.env` file with necessary API keys and configuration.

## Usage

### Running the Pipeline
1. Start the Dagster UI:
```bash
dagster dev
```

2. Access the Dagster UI at `http://localhost:3000`

3. Trigger the pipeline manually or wait for scheduled execution

### Running the Dashboard
1. Start the React development server:
```bash
npm start
```

2. Access the dashboard at `http://localhost:3000`

## Data Quality Checks
The pipeline includes several data quality checks:
- Title matching confidence threshold
- Required field validation
- Date format verification
- Price range validation

## Scheduling
The pipeline is configured to run:
- Daily at midnight
- Manual trigger option available
- Configurable through Dagster UI

## Challenges and Solutions

### Challenges
1. Rate Limiting
   - Implemented delays between requests
   - Respects robots.txt rules

2. Data Matching
   - Developed fuzzy matching algorithm
   - Confidence scoring system

3. Data Consistency
   - Standardized data formats
   - Comprehensive cleaning pipeline

### Solutions
- Implemented request throttling
- Created robust error handling
- Developed data validation checks

## Future Improvements
1. Additional data sources
2. Enhanced matching algorithms
3. Real-time data updates
4. Advanced analytics features
5. User authentication system

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
[Specify License]

## Contact
[Your Contact Information]
