import json
import string
import webbrowser
import os

import folium
import pandas as pd
from fuzzywuzzy import process

from config import CONFIG

NUM_SHEETS = len(pd.ExcelFile(CONFIG['LOR_KEY']).sheet_names)
SAVE_FILE_NAME = 'results.html'

with open(CONFIG['GEO_JSON']) as f:
    gj = json.load(f)
BEZIRKSREGIONEN = [f['properties']['BZRNAME']for f in gj['features']]

def get_closest_name(s):
    """Takes bezirksregion name from the original excel file
       and finds the closest match in the geojson file,
       since the names are not exactly the same. This is needed
       for the choropleth map to render properly.

       For example:
       - Brunnenstr. Nord --> Brunnenstraße Nord
       - Gatow / Kladow --> Gatow/Kladow
       - Ost 1 - Reginhardstr. --> Ost 1

       TODO:

       Kölln. Vorstadt/ Spindlersf. gets incorrectly
       converted to Tempelhofer Vorstadt.

    """
    match = process.extractOne(s, BEZIRKSREGIONEN)
    return match[0]

def standardize_names(df):
    """
    Using the pre-defined function, get_closest_name,
    replaces the values of the 'Bezirksregion' column
    with the actual spelling defined in the GeoJSON file,
    in order to match the data with the polygon shapes
    on the choropleth map.
    """

    print('Standardizing Bezirkregion names...')
    bzr_matches = []
    for bzr in df['Bezirksregion'].values:
        if bzr not in BEZIRKSREGIONEN:
            match = get_closest_name(bzr)
            bzr_matches.append(match)
        else:
            bzr_matches.append(bzr)
    df['Bezirksregion'] = bzr_matches

    return df

def gen_migration_data(source):

    """
    From the Excel and CSV file, generate a combined DataFrame needed
    for analyzing geographic distribution of various ethic groups /
    nationalities across Berlin's neighborhoods.
    """

    print('Contructing dataframe from Excel and CSV files...')

    df = pd.read_csv(source, sep=';')

    df_list = []
    for sheet in range(1, NUM_SHEETS):
        key_xls = pd.read_excel(CONFIG['LOR_KEY'],
                                sheet_name=sheet,
                                skiprows=3,
                                usecols="B:C, E:F, H:I, K:L",
                                names=CONFIG['KEY_COLS']).fillna(method='ffill')
        df_list.append(key_xls)

    merged_key = pd.concat(df_list)
    merged_df = df.merge(merged_key, how='inner')
    merged_df.set_index('RAUMID', inplace=True)

    for new, old in zip(CONFIG['NEW_COLS'], CONFIG['OLD_COLS']):
        merged_df[f'{new}'] = round((merged_df[f'{old}']/merged_df['MH_E'])*100, 2)

    return merged_df

def generate_map(df, dem_group):
    """
    Taking in the dataframe that was organized, consolidated, and cleaned up
    from the previous functions, allows the user to specify the column
    name of the demographic group to plot a choropleth map of that
    group's representation in all of Berlin's districts, or Bezirksregionen.

    This function saves the map to an HTML file and opens it up
    automatically in Google Chrome.
    """

    print('Generating map...\n')

    plot_cols = ['Bezirksregion', '%EU15', '%EU28',
                 '%Poland', '%Form. Yug.', '%Form. USSR',
                 '%Turk', '%Arab', '%Other', '%Unclassified']
    df_avg = df[plot_cols].copy().groupby('Bezirksregion').mean().reset_index()

    bzrmap = folium.Map(location=[52.54, 13.36],
                        zoom_start=10,
                        tiles='CartoDB positron')

    folium.Choropleth(
        geo_data=CONFIG['GEO_JSON'],
        name='chloropleth',
        data=df_avg, #actual data to be displayed
        columns=['Bezirksregion', f'{dem_group}'],
        key_on='properties.Name',
        fill_color='YlOrRd',
        nan_fill_color='#ededed',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'{dem_group}',
        highlight=True).add_to(bzrmap)

    folium.LayerControl().add_to(bzrmap)
    bzrmap.save(SAVE_FILE_NAME)
    webbrowser.open('file://' + os.path.realpath(SAVE_FILE_NAME))
    print(f'HTML file generated and saved: {SAVE_FILE_NAME}')

def main(source, dem_group):
    """Primary function to wrap all previous functions"""
    df = gen_migration_data(source)
    df = standardize_names(df)
    generate_map(df, dem_group)

if __name__ == '__main__':

    prompt = '''
    From the following options, please select the letter corresponding to the
    ethnic group / geographic region for which you'd like to generate a map.\n
    '''

    print(prompt)

    letters = list(string.ascii_uppercase)
    letters = letters[:len(CONFIG['CLI_OPTIONS'])]

    for let, opt in zip(letters, CONFIG['CLI_OPTIONS']):
        print(f'{let}. {opt}')

    choice = input('\n\nEnter letter (no punctuation): ')
    choice = dict(zip(letters, CONFIG['NEW_COLS']))[choice.upper()]

    main(CONFIG['SOURCE_FILE'], choice)
