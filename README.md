# Video Game Data Pipeline

A data pipeline for collecting, processing, and analyzing video game data from Metacritic and Steam platforms. This project uses Dagster for orchestration and provides a comprehensive dataset of video game information including reviews, ratings, and metadata.

## Project Structure

```
video_game_pipeline/
├── data/               # Data storage
│   ├── raw/           # Raw scraped data
│   └── final/         # Processed and merged datasets
├── processors/         # Data processing modules
├── scrapers/          # Web scraping modules
├── dagster_pipeline/  # Dagster pipeline definitions
├── requirements.txt   # Python dependencies
└── workspace.yaml     # Dagster workspace configuration
```

## Features

- Web scraping of video game data from Metacritic and Steam
- Data processing and cleaning
- Intelligent matching of games across platforms
- Combined scoring system
- Dagster-based pipeline orchestration

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Git

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd video_game_pipeline
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Dagster UI:
```bash
dagster dev
```

2. Access the Dagster UI at `http://localhost:3000`

3. Run the pipeline:
   - Navigate to the "Launchpad" in the Dagster UI
   - Select the pipeline you want to run
   - Configure any necessary parameters
   - Click "Launch Run"

## Data Processing

The pipeline performs the following steps:

1. **Data Collection**
   - Scrapes game data from Metacritic
   - Scrapes game data from Steam
   - Stores raw data in CSV format

2. **Data Processing**
   - Cleans and standardizes game titles
   - Matches games across platforms
   - Calculates combined scores
   - Generates final dataset

## Output

The final dataset includes:
- Game titles
- Developer information
- Metacritic scores
- Steam review scores
- Combined weighted scores
- Platform availability
- Release dates
- URLs for both platforms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
