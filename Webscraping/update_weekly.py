import os
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from datetime import datetime, timedelta

class UpdateWeekly:
    def __init__(self, date_str=None):
        self.date_str = date_str
        self.most_recent_saturday = self.get_most_recent_saturday()
        self.url = f'https://vt.ncsbe.gov/RegStat/Results/?date={self.most_recent_saturday}'
        self.json_data = ""

    def get_most_recent_saturday(self):
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
        if not self.json_data:
            raise ValueError("No JSON data to parse.")

        data = json.loads(self.json_data)
        df = pd.DataFrame(data)

        if 'AppVersion' in df.columns:
            df = df.drop(columns=['AppVersion'])

        df['Week Ending'] = self.most_recent_saturday
        df['CountyName'] = df['CountyName'].str.capitalize()

        df_fips = pd.read_csv('FIPS.csv')
        df_fips['FIPS'] = df_fips['FIPS'].astype(str).str.zfill(3)
        merged_df = pd.merge(df, df_fips, left_on='CountyName', right_on='County', how='inner')

        merged_df = merged_df.drop(columns=['CountyName'])
        df = merged_df

        df_pop = pd.read_csv('CountyPopulations.csv')
        merged_df = pd.merge(df, df_pop, left_on='County', right_on='County', how='inner')

        merged_df['TotalVotersPerCapita'] = merged_df['Total'] / merged_df['Population']

        columns_order = ['County', 'FIPS', 'Population','Total','TotalVotersPerCapita','Week Ending'] + \
                        [col for col in merged_df.columns if col not in ['County', 'FIPS', 'Population','Total','TotalVotersPerCapita','Week Ending']]
        merged_df = merged_df[columns_order]
        df = merged_df

        df['County'] = df['County'].str.upper()

        return df

    def get_dataframe(self):
        self.fetch_data()
        return self.parse_json()

def update_combined_data():
    scraper = UpdateWeekly()
    new_data = scraper.get_dataframe()

    combined_data_path = "../combined_data.csv"
    
    if os.path.exists(combined_data_path):
        combined_data = pd.read_csv(combined_data_path)
    else:
        combined_data = pd.DataFrame()

    if scraper.most_recent_saturday in combined_data['Week Ending'].values:
        print("Data for this date already exists. No update needed.")
    else:
        combined_data = pd.concat([combined_data, new_data])
        combined_data.to_csv(combined_data_path, index=False)
        print("Data updated successfully.")

if __name__ == "__main__":
    update_combined_data()
