import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta

class WebDataScraper:
    """
    A class to scrape voter registration data from the North Carolina State Board of Elections website, 
    process it, and merge it with additional county information.

    Attributes:
        date_str (str): A date string in the format 'MM/DD/YY'. If not provided, the most recent Saturday is used.
        most_recent_saturday (str): The most recent Saturday date in 'MM/DD/YYYY' format.
        url (str): The URL for fetching the voter registration data.
        json_data (str): The JSON data extracted from the webpage.
    """

    def __init__(self, date_str=None):
        self.date_str = date_str
        self.most_recent_saturday = self.get_most_recent_saturday()
        self.url = f'https://vt.ncsbe.gov/RegStat/Results/?date={self.most_recent_saturday}'
        self.json_data = ""

    def get_most_recent_saturday(self):
        """
        Get the most recent Saturday date based on the provided or current date.

        Returns:
            str: The most recent Saturday date in 'MM/DD/YYYY' format.
        """
        if self.date_str:
            try:
                provided_date = datetime.strptime(self.date_str, '%m/%d/%y')
                offset = (provided_date.weekday() + 2) % 7
                recent_saturday = provided_date - timedelta(days=offset)
            except ValueError:
                raise ValueError("Date must be in the format MM/DD/YY")
        else:
            today = datetime.now()
            offset = (today.weekday() + 2) % 7
            recent_saturday = today - timedelta(days=offset)
        
        return recent_saturday.strftime('%m/%d/%Y')

    def fetch_data(self):
        """
        Fetch the voter registration data from the website.

        Raises:
            ValueError: If JSON data is not found in the webpage.
        """
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'SetupGrid' in script.string:
                script_content = script.string
                start_index = script_content.find("var data = ")
                end_index = script_content.find("// initialize the igGrid control")
                if start_index != -1 and end_index != -1:
                    self.json_data = script_content[start_index + len("var data = "):end_index].strip()
                    break

        if self.json_data:
            self.json_data = self.json_data.rstrip(',')
        else:
            raise ValueError("JSON data not found.")

    def parse_json(self):
        """
        Parse the JSON data into a DataFrame, clean it, and merge with additional datasets.

        Returns:
            pd.DataFrame: The processed and merged DataFrame.
        """
        if not self.json_data:
            raise ValueError("No JSON data to parse.")

        data = json.loads(self.json_data)
        df = pd.DataFrame(data)

        # Drop the 'AppVersion' column if it exists
        if 'AppVersion' in df.columns:
            df = df.drop(columns=['AppVersion'])

        # Add the 'Week Ending' column with the most recent Saturday's date
        df['Week Ending'] = self.most_recent_saturday

        # Capitalize the first letter of each county name
        df['CountyName'] = df['CountyName'].str.capitalize()

        # Merge FIPS with scraped dataframe
        df_fips = pd.read_csv('FIPS.csv')
        df_fips['FIPS'] = df_fips['FIPS'].astype(str).str.zfill(3)
        merged_df = pd.merge(df, df_fips, left_on='CountyName', right_on='County', how='inner')

        # Drop the 'CountyName' column
        merged_df = merged_df.drop(columns=['CountyName'])
        df = merged_df

        # Load in County Populations
        df_pop = pd.read_csv('CountyPopulations.csv')
        merged_df = pd.merge(df, df_pop, left_on='County', right_on='County', how='inner')

        # Calculate Total Voters per capita
        merged_df['TotalVotersPerCapita'] = merged_df['Total'] / merged_df['Population']

        # Reorder columns to put 'County', 'FIPS', 'Population' at the front
        columns_order = ['County', 'FIPS', 'Population','Total','TotalVotersPerCapita','Week Ending'] + \
                        [col for col in merged_df.columns if col not in ['County', 'FIPS', 'Population','Total','TotalVotersPerCapita','Week Ending']]
        merged_df = merged_df[columns_order]
        df = merged_df

        # Capitalize everything in the 'County' column
        df['County'] = df['County'].str.upper()

        return df

    def get_dataframe(self):
        """
        Fetch and process the data, returning the final DataFrame.

        Returns:
            pd.DataFrame: The final processed DataFrame.
        """
        self.fetch_data()
        return self.parse_json()

# Help Section
if __name__ == "__main__":
    help(WebDataScraper)
