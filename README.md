# HLV_KG
This repository provides a tool to turn [DWUG EN: Diachronic Word Usage Graphs for English](https://zenodo.org/records/7387261) (Schlechtweg et al. 2024) into a knowledge graph to visualize and query the variation of the annotations in the dataset.

## Usage
### Environment
The needed packages are stored in `environment.yml`. Please create a conda environment with the following command:

`conda env create -f environment.yml`

## Structure
### dwug_en
This folder contains the dataset [DWUG EN: Diachronic Word Usage Graphs for English](https://zenodo.org/records/7387261) (Schlechtweg et al. 2021). Please click on the link to see the documentation of the dataset.

### graphs
This folder contains the turtle files of the created knowledge graphs.

#### dwug_en.ttl
The full knowledge graph of the dataset [DWUG EN: Diachronic Word Usage Graphs for English](https://zenodo.org/records/7387261) (Schlechtweg et al. 2021).

#### test_dwug_en.ttl
A small sample of three words of the dataset [DWUG EN: Diachronic Word Usage Graphs for English](https://zenodo.org/records/7387261) (Schlechtweg et al. 2021) in turtle format for testing purposes.

### query_results
This folder contains the results for the executed SPARQL-SELECT queries.

#### annotator
This folder contains the annotator queries.

#### variation
This folder contains the variation queries.

### resources
This folder contains the assigned positions and colors of the nodes as json-files. Please node that this folder is not pushed to GitHub due to file size limitations.

#### full_graph_pos.json
This file contains the positions of the nodes for the full knowledge graph. 

#### color_dict_{color_mode}.json
This file contains the colors of the nodes for the full knowledge graph. The colors depend on the `color_mode`. If the mode is `distinct`, the colors define the number of distinct categories. If the mode is `range`, the colors define the range of distinct categories.

### visualizations
This folder contains the created visualizations.

### annotator
This folder contains the created visualizations per annotator.

### full 
This folder contains the created visualizations for the full graph. The positions of the nodes are re-scaled. Each ring of nodes represents one category.

first ring (= the closest to the center): category `0` = `Undecidable` = No annotation possible <br>
second ring: category `1` = `Unrelated` = Homonymy <br>
third ring: category `2` = `Distantly Related` = Polysemy <br>
fourth ring: category `3` = `Closely Related` = Context Variance <br>
fifth ring: category `4` = `Identical` = Identity <br>

### instance
This folder contains the created visualizations for one word pair. It resembles the structure of the knowledge graph.

### create_kg.py
This script creates the RDF-graph from the csv-files in the dataset [DWUG EN: Diachronic Word Usage Graphs for English](https://zenodo.org/records/7387261) (Schlechtweg et al. 2024).

The knowledge graph has the following nodes and relations: <br>
`dataset`: The dataset node which collects meta information about the dataset and connects all words to each other. <br>
`word`: The word nodes which collect information about the token occurence. Each word is connected to its reference sentence and the annotation it occurs in. <br>
`sentence`: The sentence nodes which collect information about the occurence. Each sentence is connected to a word. <br>
`annotation`: The annotation nodes which collect information about the annotation. Each annotation is connected to two annotated words and its annotator. <br>
`annotator`: The annotator nodes which collect information about the annotators. Each annotator is connected to the annotations they have annotated. <br>

The knowledge graph relies mainly on the classes and properties on the [NIF 2.0 Core Ontology](https://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core/nif-core.html) which has been built for NLP tools, resources and annotations. The [RDA](http://rdaregistry.info/) namespace is for missing properties and classes from NIF (e.g. annotators). The `dataset` node is defined as a `Dataset` object of [schema.org](https://schema.org/Dataset).  

### explore_data.py
This script entails functions that query the original dataset, e.g. extracting the words from the dataset that are annotated by all annotators.

### main.py
This script creates the data stored in the folders `graphs`, `query_results`, and `visualizations`. It can be seen as an example pipeline for the provided scripts. 

### query_kg.py
This script contains the SPARQL queries to parse the RDF-graph. Available queries are:

`category_stats`: How often has a label been annotated? <br>
`annotations_per_annotator`: Which annotations has a annotator done? <br>
`num_labels`: How many distinct labels has a annotation and how much do they differ from each other? This query is used to create the annotator and full graph visualizations.<br>
`filter_variation`: This query is a more refined version of `num_labels`, because one can decide how high the range of the number of distinct labels should be.<br>
`get_pos_tags`: Which POS-tags are used in the dataset?<br>

### visualize_kg.py
This script creates the visualizations of the RDF-graph on three different levels. Available visualizations are:

instance: A visualization of the annotations of a word pair via [RDF Grapher](https://www.ldf.fi/service/rdf-grapher) <br>
annotator: A visualization of the annotaions of one annotator via [NetworkX](https://networkx.org/) <br>
full: A visualization of all annotations in the graph via [NetworkX](https://networkx.org/) <br>

## References
Schlechtweg, D. and Dubossarsky, H. and Hengchen, S. and McGillivray, B. and Tahmasebi, N. 2024. DWUG EN: Diachronic Word Usage Graphs for English (3.0.0).