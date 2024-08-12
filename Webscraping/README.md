# WebDataScraper

## Overview

`WebDataScraper` is a Python class designed to scrape voter registration data from the North Carolina State Board of Elections website, process the data, and merge it with additional county information. The class handles data extraction, transformation, and loading into a pandas DataFrame for further analysis.

## Features

- Fetches voter registration data from a specified or most recent Saturday.
- Parses JSON data extracted from the website's HTML.
- Cleans and processes the data, including merging with FIPS and population datasets.
- Calculates voter registration statistics per capita.
- Returns a processed DataFrame with a standardized format.

## Installation

Ensure you have the following Python packages installed:

- `requests`
- `beautifulsoup4`
- `pandas`

You can install these using pip:

```sh
pip install requests beautifulsoup4 pandas
```

## Usage

### Importing and Initializing

```python
from web_data_scraper import WebDataScraper

# Initialize with an optional date string in 'MM/DD/YY' format
scraper = WebDataScraper(date_str='08/03/24')
```

### Fetch and Process Data

```python
# Fetch and process the data, returning a pandas DataFrame
df = scraper.get_dataframe()

# Display the DataFrame
print(df.head())
```

### Methods

- `__init__(self, date_str=None)`: Initializes the scraper with an optional date string. Defaults to the most recent Saturday if not provided.
- `get_most_recent_saturday(self)`: Calculates the most recent Saturday based on the provided date or current date.
- `fetch_data(self)`: Fetches the voter registration data from the website.
- `parse_json(self)`: Parses the JSON data, processes it, and merges it with additional datasets.
- `get_dataframe(self)`: Combines the fetching and processing methods to return the final DataFrame.

## Example

```python
from web_data_scraper import WebDataScraper

# Create an instance of WebDataScraper
scraper = WebDataScraper()

# Fetch and process the data
dataframe = scraper.get_dataframe()

# Print the processed DataFrame
print(dataframe)
```

## Data Sources

- `FIPS.csv`: A CSV file containing FIPS codes for counties.
- `CountyPopulations.csv`: A CSV file containing population data for counties.

Ensure these files are in the same directory as the script or provide the appropriate path to them.

## Error Handling

- `ValueError`: Raised if the date format is incorrect or if JSON data is not found.
