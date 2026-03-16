# UrbanTech Drinking Fountains

## Research Question: Where should new drinking fountains be installed in Berlin?

* Based on existing drinking fountain locations
* Types of land use (e.g., green spaces)
* Population distribution
* Public transport data
* Retail stores (that provide beverages)

## Existing Drinking Fountains and Green Spaces directly on the Geoportal Berlin map:

[Drinking fountains and green spaces together](https://gdi.berlin.de/viewer/main/?LAYERS=[{%22id%22:%22hintergrund_default_grau%22},{%22id%22:%22gruenanlagen:spielplaetze%22},{%22id%22:%22gruenanlagen:gruenanlagen%22},{%22id%22:%22trinkwasserbrunnen:trinkwasserbrunnen%22}])

---

# Data Sources

This project uses several publicly available datasets.  
The datasets are **not owned by this repository's author** and remain subject to their respective licenses and terms of use.

## Berlin Open Data

The following datasets were obtained from the Berlin Open Data portal:  
https://daten.berlin.de/datensaetze

### Drinking Fountains

Source dataset:  
https://daten.berlin.de/datensaetze/trinkwasserbrunnen-wfs-47dba2c3

The dataset provides the locations of public drinking fountains in Berlin.

### Land Use

Source dataset:  
https://daten.berlin.de/datensaetze/flachennutzung-umweltatlas-ab-2021-wfs-80589f72

This dataset contains land use classifications such as green spaces, residential areas, and other urban land categories.  
The dataset of year 2022 has been used here.

### Population Density

Source dataset:  
https://daten.berlin.de/datensaetze/einwohnerdichte-2023-umweltatlas-wfs-b4eb74c4

Population density was used to weight areas in order to estimate suitable locations for drinking fountains.   
The grid tiling is compatible with the land use dataset, so they can be merged.

## OpenStreetMap

Additional geospatial data such as **beverage shops** and **public transport stops** were derived from:

OpenStreetMap  
https://www.openstreetmap.org

© OpenStreetMap contributors  
OpenStreetMap data is licensed under the **Open Database License (ODbL)**:  
https://opendatacommons.org/licenses/odbl/

## License Notice

The **MIT License included in this repository applies only to the source code**.

All datasets remain subject to the licenses of their original providers:

- Berlin Open Data portal datasets  
- OpenStreetMap data (ODbL)

Users of this repository are responsible for complying with the licenses of the respective data providers.

---

# Calculating New Fountain Locations – Methodological Sources

### Weighted Linear Combination (WLC)

Idea: Weighting distances to public transport stops, beverage stores, etc. leads to a suitability score for each location.

`Score_i = w1 * distance_to_stop + w2 * distance_to_other_fountains + w3 * area_type + ...`

This is also the **method implemented in this project**.

### Maximal Covering Location Problem (MCLP)

Idea: With a limited budget (e.g., **50 new fountains**), maximize the population served within a radius **R**.

→ Useful for identifying coverage gaps and underserved areas.

[Link to paper – Church & ReVelle (1974)](https://www.scribd.com/document/986556159/05-Church-ReVelle-1974-The-maximal-covering-location-problem)

### Beverage Supply: Kernel Density Estimation (KDE)

Idea: Create a **supply gap map**. Areas that:

* Have only a few shops offering beverages
* Do not yet contain drinking fountains
* Include public transport stops
* And have a high population density

are good candidates for new fountains.

Calculation:
`Demand KDE − fountain & beverage KDE`

### Other notable approaches

→ Talen (1998) – *Visualizing Fairness* (Gini coefficient of service distribution)  
→ Boone et al. (2009) – *Environmental Justice*  
→ Jacek Malczewski (1999) – *GIS and Multicriteria Decision Analysis*

---

**Important note:** In Berlin, drinking fountains are generally considered more of a **“nice-to-have” amenity** rather than an essential service, and they are **only operational from April to October**.
