import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import json
import plotly.express as px

# Load the CSV file as a DataFrame
csv_file_path = 'combined_data.csv'
df = pd.read_csv(csv_file_path)

# Ensure the 'Week Ending' column is in datetime format
df['Week Ending'] = pd.to_datetime(df['Week Ending'])

# Ensure FIPS codes are strings and zero-padded
df['FIPS'] = df['FIPS'].astype(str).str.zfill(3).str.strip()

# Extract unique dates for the date dropdown menu
dates = df['Week Ending'].dt.strftime('%Y-%m-%d').unique()

# Extract column names for the data type dropdown menu
data_columns = ['Total', 'Democrats', 'Republicans', 'Unaffiliated', 'White', 'Black', 'Hispanic', 'Male', 'Female']

# Load GeoJSON data
with open('north_carolina.geojson') as f:
    geojson_data = json.load(f)

# Extract FIPS codes from GeoJSON
geo_fips = {feature['properties']['FIPS'] for feature in geojson_data['features']}

# Function to calculate weekly changes for the selected column
def calculate_weekly_changes(df, column):
    df['Week Ending'] = pd.to_datetime(df['Week Ending'], format='%m/%d/%Y')
    df = df.sort_values(by=['County', 'Week Ending'])
    df['Weekly Change'] = df.groupby('County')[column].diff().fillna(0)
    return df

# Function to format numbers with K and decimal points
def format_number(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return str(value)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(style={'font-family': 'Calibri'}, children=[
    html.H1("North Carolina Voter Registration Dashboard 2024"),

    # KPI Box
    html.Div([
        html.H3(id='kpi-date-title', style={'text-align': 'left', 'padding': '10px'}),
        html.Div(id='kpi-box', style={'display': 'flex', 'justify-content': 'space-evenly', 'padding': '10px'})
    ], style={'margin-bottom': '20px'}),

    # Container for the map and graph
    html.Div([
        # Left side for map
        html.Div([
            dcc.Graph(id='choropleth-map'),
            html.Div([
                dcc.Dropdown(
                    id='date-dropdown',
                    options=[{'label': date, 'value': date} for date in dates],
                    value=dates[0],  # Set the default value to the first date
                    style={'width': '200px', 'margin': '0 auto'}
                ),
                dcc.Dropdown(
                    id='data-dropdown',
                    options=[{'label': col, 'value': col} for col in data_columns],
                    value='Total',  # Set the default value to 'Total'
                    style={'width': '200px', 'margin': '10px auto'}
                ),
            ], style={'text-align': 'center'})
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        # Right side for graph
        html.Div([
            dcc.Graph(id='weekly-change-graph'),
            html.Div([
                dcc.Dropdown(
                    id='county-dropdown',
                    options=[{'label': 'All Counties', 'value': 'All'}] + [{'label': county, 'value': county} for county in sorted(df['County'].unique())],
                    value='All',
                    clearable=False,
                    style={'width': '200px', 'margin': '10px auto'}
                ),
                dcc.Dropdown(
                    id='column-dropdown',
                    options=[{'label': col, 'value': col} for col in data_columns],
                    value='Total',
                    clearable=False,
                    style={'width': '200px', 'margin': '0 auto'}
                ),
            ], style={'text-align': 'center'})
        ], style={'width': '48%', 'display': 'inline-block', 'float': 'right'})
    ], style={'display': 'flex'}),
])

# Define a callback to update the KPIs, map, and graph
@app.callback(
    [Output('kpi-date-title', 'children'),
     Output('kpi-box', 'children'),
     Output('choropleth-map', 'figure'),
     Output('weekly-change-graph', 'figure')],
    [Input('date-dropdown', 'value'),
     Input('data-dropdown', 'value'),
     Input('county-dropdown', 'value'),
     Input('column-dropdown', 'value')]
)
def update_content(selected_date, selected_column, selected_county, selected_column_graph):
    # Calculate KPIs for the most recent date
    most_recent_date = df['Week Ending'].max()
    latest_data = df[df['Week Ending'] == most_recent_date]

    total_voters = format_number(latest_data['Total'].sum())
    democrats = format_number(latest_data['Democrats'].sum())
    republicans = format_number(latest_data['Republicans'].sum())
    unaffiliated = format_number(latest_data['Unaffiliated'].sum())

    kpi_box = html.Div([
        html.Div([
            html.H3("Total Registered Voters:"),
            html.P(total_voters, style={'fontSize': 24})
        ], style={'width': '24%', 'display': 'inline-block', 'text-align': 'center'}),
        
        html.Div([
            html.H3("Democrats:"),
            html.P(democrats, style={'fontSize': 24})
        ], style={'width': '24%', 'display': 'inline-block', 'text-align': 'center'}),
        
        html.Div([
            html.H3("Republicans:"),
            html.P(republicans, style={'fontSize': 24})
        ], style={'width': '24%', 'display': 'inline-block', 'text-align': 'center'}),
        
        html.Div([
            html.H3("Unaffiliated:"),
            html.P(unaffiliated, style={'fontSize': 24})
        ], style={'width': '24%', 'display': 'inline-block', 'text-align': 'center'}),
    ], style={'display': 'flex', 'justify-content': 'space-evenly', 'padding': '10px', 'width': '100%'})

    kpi_date_title = f"As of {most_recent_date.strftime('%Y-%m-%d')}"

    # Update the map
    filtered_df = df[df['Week Ending'].dt.strftime('%Y-%m-%d') == selected_date]
    
    if filtered_df.empty:
        map_fig = px.choropleth()
    else:
        df_with_changes = calculate_weekly_changes(df, selected_column)
        filtered_df_changes = df_with_changes[df_with_changes['Week Ending'].dt.strftime('%Y-%m-%d') == selected_date]
        filtered_fips = set(filtered_df_changes['FIPS'])
        missing_fips = geo_fips - filtered_fips
        
        if missing_fips:
            print(f"Missing FIPS codes for {selected_date}: {missing_fips}")

        map_fig = px.choropleth(
            filtered_df_changes,
            geojson=geojson_data,
            locations='FIPS',
            featureidkey="properties.FIPS",
            color='Weekly Change',
            color_continuous_scale="Viridis",
            range_color=(filtered_df_changes['Weekly Change'].min(), filtered_df_changes['Weekly Change'].max()),
            scope="usa",
            labels={'Weekly Change': 'Weekly Change'},
            hover_name='County',
            hover_data={'FIPS': False, selected_column: True}
        )
        map_fig.update_geos(fitbounds="locations", visible=False)
        map_fig.update_layout(title=f"Weekly Changes in {selected_column} by County")

    # Update the graph
    if selected_county == 'All':
        aggregated_df = df.groupby('Week Ending').agg({selected_column_graph: 'sum'}).reset_index()
        aggregated_df['Weekly Change'] = aggregated_df[selected_column_graph].diff().fillna(0)
        graph_fig = px.line(aggregated_df,
                            x='Week Ending',
                            y='Weekly Change',
                            title=f'Weekly Changes in {selected_column_graph} (All Counties)',
                            labels={'Weekly Change': f'Change in {selected_column_graph}'},
                            line_shape='linear')
    else:
        filtered_df = df[df['County'] == selected_county]
        filtered_df = calculate_weekly_changes(filtered_df, selected_column_graph)
        graph_fig = px.line(filtered_df,
                            x='Week Ending',
                            y='Weekly Change',
                            title=f'Weekly Changes in {selected_column_graph} for {selected_county}',
                            labels={'Weekly Change': f'Change in {selected_column_graph}'},
                            line_shape='linear')

    graph_fig.update_layout(
        xaxis_title='Date',
        yaxis_title=f'Change in {selected_column_graph}',
        xaxis=dict(
            tickformat="%b %Y",
            dtick="M1",
            tickangle=-45
        )
    )

    return kpi_date_title, kpi_box, map_fig, graph_fig

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))  # Default to 8050 if PORT is not set
    app.run_server(host='0.0.0.0', port=port)
