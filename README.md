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

## Quellen:

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

## Übersicht Bevölkerung:
**Quelle**: [Statistik Einwohner](https://www.statistik-berlin-brandenburg.de/a-i-5-hj)  
**Wichtige Tabelle**: T11 – Einwohner nach Bezirken und Unter-Bezirken, auch nach Alter.
