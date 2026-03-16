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

### Drinking Fountains (available under the HTML resource)

[Drinking fountains GeoJSON file](https://daten.berlin.de/datensaetze/trinkwasserbrunnen-wfs-47dba2c3)

### Land Use 2022 (green spaces, residential areas, etc., under HTML resource)

[Land use GeoJSON file](https://daten.berlin.de/datensaetze/flachennutzung-umweltatlas-ab-2021-wfs-80589f72)

Additionally, **population density for 2023** (no GeoJSON was available for 2022):  
[Population density GeoJSON file with identical grid tiling](https://daten.berlin.de/datensaetze/einwohnerdichte-2023-umweltatlas-wfs-b4eb74c4)

The number of residents should help to **weight areas to determine suitable locations for drinking fountains**.  
As they were sharing keys, I combined the land use and population dataset into one.

### OpenStreetMap

Used to retrieve beverage shops and public transport stops.

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
