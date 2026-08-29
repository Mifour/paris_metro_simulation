# Paris Metro Simulation

# Français

Une visualisation dans le navigateur du trafic du métro parisien tout au long d'une journée type, reconstituée à partir des données de horaires des transports en commun.

La simulation prétraite les données GTFS d'Île-de-France Mobilités pour créer un ensemble compact de trajectoires de trains en 2D et les restitue dans le navigateur à l'aide de PixiJS et WebGL.

## Données

La simulation s'appuie sur le jeu de données GTFS d'Île-de-France Mobilités publié le 26 août 2026.

**Source :**

[https://transport.data.gouv.fr/resources/80921](https://transport.data.gouv.fr/resources/80921)

**Date du jeu de données :**

26-08-2026

**Licence :**

Licence Mobilités

L'archive GTFS d'origine utilisée pour générer la simulation est incluse dans ce dépôt sous le dossier `data/`.

Le jeu de données de simulation généré (`dist/keyframes.json`) est dérivé de ces données de mobilité et est distribué sous la Licence Mobilités.

## Logiciel

Le pipeline de prétraitement et l'application web sont des logiciels originaux et sont publiés sous la licence MIT.

Cela comprend :

* `preprocessing/` — pipeline de prétraitement des données
* `dist/index.html` — application web
* Le code de visualisation JavaScript
* Les outils de prétraitement en Rust, le cas échéant

Consultez le fichier `LICENSE` pour la licence MIT complète ainsi que pour obtenir des informations sur la licence distincte s'appliquant aux données de mobilité.

## Relancer le pipeline de traitement ETL

Le script ETL est écrit en Python 3.14 pur et peut être exécuté directement :

```
python ./preprocessing/etl.py IDFM-gtfs/ 2026-08-26 dist/keyframes.json

```

## Exécution en local

La simulation générée est une application web entièrement statique.

```bash
cd dist
python -m http.server 8000

```

Puis ouvrez :

[http://localhost:8000](http://localhost:8000)

## Remerciements

Données fournies par Île-de-France Mobilités.

Source :
[https://transport.data.gouv.fr/resources/80921](https://transport.data.gouv.fr/resources/80921)


----
# English

A browser-based visualization of Paris Metro traffic throughout a typical
day, reconstructed from scheduled public transport data.

The simulation preprocesses Île-de-France Mobilités GTFS data into a compact
set of 2D train trajectories and renders them in the browser using PixiJS
and WebGL.

## Data

The simulation is based on the Île-de-France Mobilités GTFS dataset published
on August 26, 2026.

**Source:**  
https://transport.data.gouv.fr/resources/80921

**Dataset date:**  
2026-08-26

**License:**  
Licence Mobilités

The original GTFS archive used to generate the simulation is included in this
repository under `data/`.

The generated simulation dataset (`dist/keyframes.json`) is derived from
these mobility data and is distributed under the Licence Mobilités.

## Software

The preprocessing pipeline and web application are original software and are
released under the MIT License.

This includes:

- `preprocessing/` — data preprocessing pipeline
- `dist/index.html` — web application
- JavaScript visualization code
- Rust preprocessing tools, where applicable

See `LICENSE` for the full MIT License and information regarding the
separate licensing of mobility data.

## Rerun the ETL processing pipeline
The ETL script is in pure python 3.14 and can run directly: 

```
python ./preprocessing/etl.py IDFM-gtfs/ 2026-08-26 dist/keyframes.json
```

## Running locally

The generated simulation is a completely static web application.

```bash
cd dist
python -m http.server 8000
```

Then open:

[http://localhost:8000](http://localhost:8000)

## Acknowledgements

Data provided by Île-de-France Mobilités.

Source:
[https://transport.data.gouv.fr/resources/80921](https://transport.data.gouv.fr/resources/80921)


[1]: https://wiki.lafabriquedesmobilites.fr/wiki/Licence_Mobilit%C3%A9s "Licence Mobilités - Communauté de la Fabrique des Mobilités"
