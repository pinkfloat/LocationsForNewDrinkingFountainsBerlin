# UrbanTech Drinking Fountains
## Fragestellung: Wo sollten neue Trinkbrunnen aufgestellt werden?

- Anhand von bisherigen Brunnenstandorten
- Grünanlagen
- ÖPNV-Daten
- Kaufläden (die Getränke bereitstellen)
- Bevölkerungsdichte

Eventuell weitere hilfreiche Datensätze:  
[Fußwege in Berlin](https://daten.berlin.de/datensaetze/fussgangernetz-wfs-f1995e5e)  
[Straßennetz](https://daten.berlin.de/datensaetze/detailnetz-berlin-wfs-4f2045ef)

## Trinkbrunnen und Grünanlagen direkt auf Geoportal Berlin Karte:
[Trinkbrunnen und Grünanlagen zusammen](<https://gdi.berlin.de/viewer/main/?LAYERS=[{%22id%22:%22hintergrund_default_grau%22},{%22id%22:%22gruenanlagen:spielplaetze%22},{%22id%22:%22gruenanlagen:gruenanlagen%22},{%22id%22:%22trinkwasserbrunnen:trinkwasserbrunnen%22}]>)

---

## Daten Quellen:

### Trinkbrunnen (unter HTML Ressource):
[Trinkbrunnen GeoJSON Datei](https://daten.berlin.de/datensaetze/trinkwasserbrunnen-wfs-47dba2c3)

### Flächennutzung 2022 (Grünanlagen, Wohngebiete, etc., unter HTML Ressource)
[Flächennutzung GeoJSON Datei](https://daten.berlin.de/datensaetze/flachennutzung-umweltatlas-ab-2021-wfs-80589f72)

Dazu passend Einwohnerdichte 2023 (zu 2022 gab's kein geojson):  
[Einwohnerdichte in identischer Kachelung](https://daten.berlin.de/datensaetze/einwohnerdichte-2023-umweltatlas-wfs-b4eb74c4)  
Die Anzahl der Einwohner sollte helfen Gebiete für Trinkbrunnen zu Gewichten.

### Grünanlagen (WFS Datei - deprecated wenn Flächennutzung verwendet wird):
[Grünanlagen WFS Datei](https://daten.berlin.de/datensaetze/grunanlagenbestand-berlin-einschliesslich-der-offentlichen-spielplatze-wfs-737fd0a4)

**Achtung unvollständig!!**
- Z.Bsp.: "Friedhof Baumschulenweg" nicht als Grünanlage markiert.
- Extraktionen aus Open Street Map haben aber bisher deutlich schlechtere Qualität.
  - Code manuell nachbessern könnte helfen, um evtl. weitere Grünflächen hinzuzufügen.
  - Alle Ergebnisse haben ansonsten ähnlich viele Zeilen (ca. 2500-2700) – also ähnliche Datenmenge.
  - [OpenStreetMap Park Beispiel](https://www.openstreetmap.org/way/4413796#map=17/52.492887/13.310092)

**Weitere Erweiterungsmöglichkeiten**
- **Wälder**: [Grunewald auf OpenStreetMap](https://www.openstreetmap.org/relation/3410#map=13/52.46898/13.25672)
- **Friedhöfe**: Hier ließen sich eventuell auch weitere Datensätze auf der Berlin Website finden.

### Openstreetmap
Für Getränkeläden und Haltestellen.

---

## Berechnung neuer Brunnen - Quellen für Ansätze:

### Maximal Covering Location Problem (MCLP)
Idee: Bei begrenztem Budget (z.B. 30 neue Brunnen) maximiere die versorgte Bevölkerung innerhalb eines Radius R.  
-> Zum Versorgungslücken berechnen und unterversorgte Gebiete identifizieren  
[Link zu Paper - Church & ReVelle (1974)](https://www.scribd.com/document/986556159/05-Church-ReVelle-1974-The-maximal-covering-location-problem)

### Weighted Linear Combination (WLC)
Idee: Gewichtung von Distanzen zu Halestellen, Getränkeläden etc. führt zu Location.  
`Scorei ​= w1​ * Haltestellen-Distanz + w2​ * weitere Trinkbrunnen-Distanz + w3 * Area-Typ + ...`

### Getränke-Versorgung: Kernel Density Estimation (KDE)
Idee: Versorgungslückenkarte - Flächen wo:
- Es nur wenige Shops gibt die Getränke anbieten
- bisher keine Brunnen besitzen
- Haltestellen beinhalten
- Und eine hohe Einwohnerdichte haben  
eignen sich für neue Brunnen.  
Berechnung: `Nachfrage-KDE − Brunnen & Getränke-KDE`

### Weitere namhafte Ansätze
-> Talen (1998) – Visualizing Fairness (Gini-Koeffizient der Versorgung)  
-> Boone et al. (2009) – Environmental Justice  
-> Jacek Malczewski (1999) – GIS and Multicriteria Decision Analysis

**Wichtige Anmerkung:** Trinkbrunnen sind in Berlin eher ein "nice to have" als  
eine zwingende Versorgung und ohnehin nur von April bis Oktober freigegeben.
