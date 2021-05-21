# What is this?
Project for scraping tweets related to climate change and central banks.

# Setup
- clone from gitlab and navigate to project folder.
- Setup environment by running setup.bat

# How to run
- Navigate to project folder and start environment with venv\Scripts\activate
- Scrape Twitter data with download_central_bank_tweets.py. This takes a good while and might crash on connection issues and such. Simply relaunching the script should make it automatically figure out how to pick up where it left off.
- Compute aggregate monthly data on mentions of central banks and climate change by running aggregate_climate_data.py. Aggregate data are saved in data folder, and if possible on network drive.