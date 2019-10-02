# Project Description

### Background and Sources

The government of Berlin, Germany hosts a large collection
of interesting publicly available data sets on the *Berlin
Open Data* portal (https://daten.berlin.de/), on topics
such as education, demographics, economy, health, culture,
transportation, environment, sports, etc.

One topic of interest was the data regarding demographics
of Berliners; in particular, in which regions of the city
do certain ethnic groups live? Since the city is so
multi-cultural and certain districts are known to be home
to different demographic / ethnic groups, it would be
interesting to visualize these patterns on a map.

The data being used comes directly from the *Berlin Open
Data* site, under the name, **Einwohnerinnen und Einwohner
mit Migrationshintergrund in Berlin in LOR-Planungsräumen
nach Herkunftsgebieten am 31.12.2017; Melderechtlich
registrierte Einwohner mit Hauptwohnsitz**.

In english, this translates to "**Berlin residents with a
migrant background (by region of origin),
sorted by LOR Planning Areas (i.e. defined geographical
sub-regions, used for statistical purposes),
as of December 31, 2017;
Registered residents with main residence (in Berlin)**".

`Source:`
https://daten.berlin.de/datensaetze/einwohnerinnen-und-einwohner-mit-migrationshintergrund-berlin-lor-planungsr%C3%A4umen-1
*(includes data in .csv format,
as well as a description of the metadata in .pdf format)*

`Other Resoures`:
Definition of "LOR Planning Area boundaries" (as of 2009):
https://earthworks.stanford.edu/catalog/tufts-berlin-planungsraum-planningareas-09

**Note**: The raw dataset used in the analysis for 2017
(as well as the data for other years before and after 2017)
is included in the [data/](data/) sub-folder of this
repository.

### The Challenge

While the data provided by Berlin is publicly available as
CSV files, they are admittedly a bit difficult to decipher.

For example, the column names detailing the nationalities / ethnic origins are not clear, so they must be interpreted from the data description pdf file, [data/Beschreibung_MIGRA_Datenpool-2018.pdf](data/Beschreibung_MIGRA_Datenpool-2018.pdf).

Also, all demographic statistics in the CSV files are linked to geographical regions of Berlin, designated by a **RAUMID**, roughly translated to an "Area ID". This ID is composed of smaller numbers; namely, the **Bezirk (BZR)**, the **Prognoseraum (PGR)**, the **Bezirksregion (BZR)**, and the **Planungsraum (PLR)**.
In order to understand how these numbers map to actual names of areas in Berlin, they need to be merged with the data in the so-called "key- and name catalog" spreadsheet:
[data/LOR-Schluesselsystematik.xls](data/LOR-Schluesselsystematik.xls).

For example, the RAUMID of `1011303` translates to:
The *Bezirk* of `Mitte` *(1)*, the *Prognoseraum* of `Zentrum` *(01)*, the *Bezirksregion* of `Alexanderplatz` *(13)*, and the *Planungsraum* of	`Alexanderplatzviertel` *(03)*.

Finally, the translated, "human-readable" geographic regions need to be associated with their corresponding names found in the GeoJSON file ([data/LOR-Bezirksregionen.geojson](data/LOR-Bezirksregionen.geojson)) so that the data can actually be plotted in a map using the `Folium` library in Python.

For names that aren't spelled exactly the same in both files (e.g. Brunnenstr. Nord --> Brunnenstraße Nord), the fuzzy string matching library in Python, `fuzzywuzzy`, was quite useful.

`Sources:`
- https://www.stadtentwicklung.berlin.de/planen/basisdaten_stadtentwicklung/lor/ (for naming key)
- https://data.technologiestiftung-berlin.de (for GeoJSON file)
