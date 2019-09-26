
import pandas as pd
import numpy as np
from fuzzywuzzy import process
import webbrowser
import json
import folium

SOURCE_FILE = 'data/EWRMIGRA201712H_Matrix.csv'
CHROME_PATH = 'open -a /Applications/Google\ Chrome.app %s'

LOR_KEY = 'data/LOR-Schluesselsystematik.xls'
#filefrom Berlin govt website to translate numbers to meaningful location names
KEY_COLS = ['BEZ', 'Bezirk', 'PGR', 'Prognoseraum',
               'BZR', 'Bezirksregion', 'PLR', 'Planungsraum']
NUM_SHEETS = len(pd.ExcelFile(LOR_KEY).sheet_names)

OLD_COLS = ['HK_EU15', 'HK_EU28', 'HK_Polen', 'HK_EheJug', 'HK_EheSU',
            'HK_Turk', 'HK_Arab', 'HK_Sonst', 'HK_NZOrd']
NEW_COLS = ['%EU15', '%EU28', '%Poland', '%Form. Yug.',
            '%Form. USSR', '%Turk', '%Arab', '%Other', '%Unclassified']

with open('data/LOR-Bezirksregionen.geojson') as f:
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

    print('Contructing dataframe from Excel and CSV files...')

    df = pd.read_csv(source, sep=';')

    df_list = []
    for sheet in range(1, NUM_SHEETS):
        key_xls = pd.read_excel(LOR_KEY,
                                sheet_name = sheet,
                                skiprows = 3,
                                usecols = "B:C, E:F, H:I, K:L",
                                names = KEY_COLS).fillna(method='ffill')
        df_list.append(key_xls)

    merged_key = pd.concat(df_list)

    merged_df = df.merge(merged_key, how='inner')
    #combine/merge data with the key, in order to map demographic groups to location
    merged_df.set_index('RAUMID', inplace = True)

    for new, old in zip(NEW_COLS, OLD_COLS):
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

    print('Generating map...')

    plot_cols = ['Bezirksregion', '%EU15','%EU28',
                 '%Poland', '%Form. Yug.', '%Form. USSR',
                 '%Turk', '%Arab', '%Other', '%Unclassified']
    df_avg = df[plot_cols].copy().groupby('Bezirksregion').mean().reset_index()

    bzrmap = folium.Map(location=[52.54, 13.36],
                        zoom_start=10,
                        tiles='CartoDB positron')

    folium.Choropleth(
        geo_data='data/LOR-Bezirksregionen.geojson',
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
    bzrmap.save('results/demo_map.html')
    webbrowser.get(CHROME_PATH).open('results/demo_map.html')

def main(source, dem_group):
    """Primary function to wrap all previous functions"""
    df = gen_migration_data(source)
    df = standardize_names(df)
    generate_map(df, dem_group)

if __name__ == '__main__':

    main(SOURCE_FILE, '%Form. USSR')
