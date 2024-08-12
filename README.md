# North Carolina Voter Registration Dashboard 2024

## Overview

The **North Carolina Voter Registration Dashboard 2024** is a web application designed to visualize voter registration data for North Carolina. Built using Dash and Plotly, this dashboard provides insights into weekly changes in voter registrations across various demographics and political affiliations. The application allows users to interactively explore data through choropleth maps and line graphs.

<img width="1491" alt="image" src="https://github.com/user-attachments/assets/59ed4a1c-3938-4d36-95ca-6ac1476cc520">

## Features

- **Interactive Choropleth Map:** Visualize weekly changes in voter registrations by county with a color-coded map.
- **Dynamic Line Graphs:** View trends in voter registration changes over time for selected counties and demographics.
- **Key Performance Indicators (KPIs):** Display current totals for registered voters, Democrats, Republicans, and unaffiliated voters with formatting for readability.

## Installation

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/jaredbach/NC-Voter-Reg-Dash.git
    cd NC-Voter-Reg-Dash
    ```

2. **Create a Virtual Environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Prepare Your Data:**
   Ensure you have a CSV file named `combined_data.csv` in the root directory with the following columns:
   - `Week Ending`
   - `County`
   - `Total`
   - `Democrats`
   - `Republicans`
   - `Unaffiliated`
   - `White`
   - `Black`
   - `Hispanic`
   - `Male`
   - `Female`

2. **Run the Application:**

    ```bash
    python app.py
    ```

    The app will start running on `http://127.0.0.1:8050/`. Open this URL in your web browser to view the dashboard.

## Configuration

- **CSV File Path:** Update the `csv_file_path` variable in `app.py` to point to your CSV file if it is located elsewhere.
- **GeoJSON File:** Ensure you have the required GeoJSON file for North Carolina boundaries. Update the `geojson` path in the `update_dashboard` function if needed.

## Development

Feel free to contribute to this project! If you have suggestions or improvements, please fork the repository and create a pull request. For any issues or questions, open an issue on GitHub or contact me directly.


## Acknowledgments

- **Dash:** A productive Python framework for building web applications.
- **Plotly:** An open-source graphing library for Python.
