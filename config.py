CONFIG = {
          'SOURCE_FILE' : 'data/EWRMIGRA201712H_Matrix.csv',
          'LOR_KEY' : 'data/LOR-Schluesselsystematik.xls',
          'GEO_JSON' : 'data/LOR-Bezirksregionen.geojson',
          'KEY_COLS' : ['BEZ', 'Bezirk', 'PGR', 'Prognoseraum',
                        'BZR', 'Bezirksregion', 'PLR', 'Planungsraum'],
          'OLD_COLS' : ['HK_EU15', 'HK_EU28', 'HK_Polen',
                        'HK_EheJug', 'HK_EheSU', 'HK_Turk',
                        'HK_Arab', 'HK_Sonst', 'HK_NZOrd'],
          'NEW_COLS' : ['%EU15', '%EU28', '%Poland',
                        '%Form. Yug.', '%Form. USSR', '%Turk',
                        '%Arab', '%Other', '%Unclassified'],
          'CLI_OPTIONS' : ['EU-15 Nations', 'EU-28 Nations', 'Poland',
                           'Balkans (i.e. former Yugoslavia)',
                           'Russia / Former USSR', 'Turkey',
                           'Arab Nations', 'Other', 'Unclassified']
                        }
