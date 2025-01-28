# HLV_KG
This repository provides a tool to visualize annotations of non-aggregated datasets.

## TODOS:
1. Create KG
2. Visualizations
- einzelne Instanzen: rdf-grapher (sonst SPARQL)
3. Queries
- lbl query
4. Code cleanup
- num_labels und filter_variations zusammenlegen
- Löschen, was nicht gebraucht wird
- Dokumentation
- Parameter mit Name übergeben
5. Code alles neu laufen lassen
5. Schreiben

Additional:
- Connect Dataset entity to metadata from ZENO
- CLI for visualizations
- function call mit category=uses["category"] für bessere Lesbarkeit
- nicht gebrauchte imports löschen
- Dateien in Ordnern organisieren
- andere Sprachen
- color coding für visualisierungen
- variations query: wichtige daten hinzufügen
- 1 environment für alles
- max Unterschied
- full kg: rdfgraph submodule
- Interaktivität
- einzelne Instanzen: kleineren Graph mit rdf-grapher darstellen
- vollen kg darstellen
- Nicht genutzte sub-modules weg
- nicht genutzte funktionen weg
- color dict in json-datei speichern
- pos visualization
- annotator range vis
- alle möglichen visualisierungen
- CLIs
- eine pipeline-Datei erstellen

Offene Fragen:
- Was nutzen die für POS-tags?

## Installation
git clone --recurse-submodules

## Usage
### Environment
trust mit numpy = 2.0.2
trust_viz mit numpy = 1.26.4 (weil sonst networkx mit großen Dateien nicht läuft)
