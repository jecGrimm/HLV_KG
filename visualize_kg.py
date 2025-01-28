import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph
import networkx as nx
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO
from query_kg import num_labels
import os.path
from csv import DictReader
from collections import defaultdict
from matplotlib.lines import Line2D
import json
from rdflib.namespace import Namespace, RDFS, RDF, XSD
import re
from rdflib import URIRef, Literal
import numpy as np
from tqdm import tqdm

def inspect_instance(g, words):
    '''
    This function creates a visualization of the annotations for one word pair.
    
    @params
        g: graph
        words: list of the word pair
    @returns instance_graph_rdf: RDF-graph of the annotations for one word pair
    '''
    instance_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
    PREFIX hlv_word: <https:/hlv.org/word/>

    CONSTRUCT {{
        ?word1 rdfs:label "{words[0]}"^^xsd:string ;
            ?word1_p ?word1_o ;
            nif:annotation ?annotation ;
            nif:referenceContext ?sentence1 .

        ?word2 rdfs:label "{words[1]}"^^xsd:string ;
            ?word1_p ?word1_o ;
            nif:annotation ?annotation ;
            nif:referenceContext ?sentence2 .
        
        ?sentence1 ?sentence1_p ?sentence1_o .
        ?sentence2 ?sentence2_p ?sentence2_o .

        ?annotation ?annotation_p ?annotation_o .
    }}
    WHERE {{
        ?word1 rdfs:label "{words[0]}"^^xsd:string ;
            ?word1_p ?word1_o ;
            nif:annotation ?annotation ;
            nif:referenceContext ?sentence1 .

        ?word2 rdfs:label "{words[1]}"^^xsd:string ;
            ?word1_p ?word1_o ;
            nif:annotation ?annotation ;
            nif:referenceContext ?sentence2 .
        
        ?sentence1 ?sentence1_p ?sentence1_o .
        ?sentence2 ?sentence2_p ?sentence2_o .

        ?annotation ?annotation_p ?annotation_o .

    }}
    """
    instance_graph_rdf = g.query(instance_query)

    # create visualization
    rdf_grapher_vis(instance_graph_rdf.serialize(format="turtle"), f"./visualizations/instance/{'_'.join(words)}_dwug_en.png")
    return instance_graph_rdf

def rdf_grapher_vis(g, path):
    '''
    This function creates a visualization with RDF Grapher.

    @param 
        g: RDF-graph
        path: path where the visualization should be stored
    '''
    params = {"rdf": g, "from": "ttl", "to": "png"}
    url = f"http://www.ldf.fi/service/rdf-grapher"
    r = requests.post(url, params = params)

    # print status code because large graphs cannot be parsed (ok: 200)
    print("status code: ", r.status_code)

    # transform into image
    i = Image.open(BytesIO(r.content))
    i.show()
    i.save(path)

def create_annotation_subgraph(g):
    '''
    This function creates a graph of all annotations in the dataset.
    
    @param g: graph
    @returns annotation_graph_rdf: RDF-graph with all annotations
    '''
    annotation_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    CONSTRUCT {{
        ?annotation_lbl nif:category ?category.
    }}
    WHERE {{
        ?annotation rdfs:label ?annotation_lbl ;
            nif:category ?category.

        FILTER (isNumeric(?category))   
    }}
    """
    annotation_graph_rdf = g.query(annotation_query)

    return annotation_graph_rdf

def create_full_annotation_vis(g, pos, color_dict, color_mode = "distinct"):
    '''
    This function visualizes all annotations in the dataset.

    @params 
        g: graph
        full_pos: positions of all graph nodes in the visualization
        color_dict: colors of the nodes
        color_mode: kind of variation
    '''
    # collect data
    annotation_graph_rdf = create_annotation_subgraph(g)
    annotation_graph_nx = rdflib_to_networkx_graph(annotation_graph_rdf) 
    lbl2category = {triple[0]:int(triple[2]) for triple in annotation_graph_rdf}
    annotation_nodes = lbl2category.keys()
    
    # color code
    colors = [color_dict[str(lbl)] for lbl in annotation_nodes]

    # lower labels are closer to the center, higher labels further away
    scales = [0.25, 0.5, 0.75, 1, 1.25, 1.5]
    scaled_pos = defaultdict(tuple)
    for lbl, category in lbl2category.items():
        scaled_pos[lbl] = (pos[lbl][0] * scales[category], pos[lbl][1] * scales[category])

    # plot
    fig, ax = plt.subplots()
    fig.suptitle("Full annotation graph")

    nx.draw_networkx_nodes(annotation_graph_nx, ax=ax, pos=scaled_pos, nodelist = annotation_nodes, node_size=1, node_color=colors, margins=(0.8, 0.8))

    ax.margins(x=0.6, y=0.6)
    ax.axis('off')

    fig.legend(handles = get_legend_elements(color_mode), loc="upper right") 
    plt.tight_layout() 
    plt.savefig(f"./visualizations/full/full_annotations_{color_mode}_dwug_en.png", format="PNG", dpi=300)


def create_annotator_subgraph(g, annotator):
    '''
    This function creates a graph of the annotation for one annotator.
    
    @params
        g: graph
        annotator: the annotator of the returned annotations
    @returns annotator_graph_rdf: RDF-graph of the annotations for one annotator
    '''
    annotator_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    CONSTRUCT {{
        ?annotation_lbl rdaio:P40015 ?annotator .
    }}
    WHERE {{
        ?annotation rdaio:P40015 ?annotator ;
            rdfs:label ?annotation_lbl ;
            nif:category ?category.

        FILTER (isNumeric(?category))
        ?annotator rdfs:label "{annotator}"^^xsd:string .    
    }}
    """
    annotator_graph_rdf = g.query(annotator_query)
    return annotator_graph_rdf

def create_single_annotator_vis(g, annotator, pos, color_dict, color_mode = "distinct"):
    '''
    This function visualizes the annotations of one annotator.

    @params
        g: the full RDF-graph
        annotator: the annotator who has annotated the visualized annotations
        pos: the positions of the annotation nodes
        color_dict: the colors of the nodes in the full graph
        color_mode: 
            distinct: colors are defined by the amount of distinct labels for the annotations
            range: colors are defined by the range of distinct labels for the annotations
    '''
    fig, ax = plt.subplots()
    fig.suptitle(annotator)

    # collect data
    annotator_graph_rdf = create_annotator_subgraph(g, annotator)
    annotator_graph_nx = rdflib_to_networkx_graph(annotator_graph_rdf) 
    annotator_node = [node for node in annotator_graph_nx.nodes if color_dict[str(node)] == "#f20c1f" and str(node).split("/")[-1] == re.search("\d+", annotator).group()]
    annotation_nodes = list(set(annotator_graph_nx.nodes)-set(annotator_node)) # exlude annotator node
    
    # assign colors
    colors = [color_dict[str(node)] for node in annotation_nodes]

    # plot
    nx.draw_networkx_nodes(annotator_graph_nx, ax=ax, pos=pos, nodelist = annotation_nodes, node_size=1, node_color=colors, margins=(0.8, 0.8))
    nx.draw_networkx_nodes(annotator_graph_nx, ax=ax, pos = {annotator_node[0]:np.array([0,0])}, nodelist=annotator_node, node_size=5, node_color = "#f20c1f")

    ax.margins(x=0.6, y=0.6)
    ax.axis('off')

    fig.legend(handles = get_legend_elements(color_mode), loc="upper right") 
    plt.tight_layout() 
    plt.savefig(f"./visualizations/annotator/{color_mode}/{annotator}_{color_mode}_dwug_en.png", format="PNG", dpi=300)

def get_colors(g, color_mode = "distinct"):
    '''
    This function assigns the colors to the annotations.

    @params
        g: RDF-graph
        color_mode: 
            distinct: colors are defined by the amount of distinct labels for the annotations
            range: colors are defined by the range of distinct labels for the annotations
    @returns color_dict: dictionary mapping the nodes to their colors
    '''
    print(f"assigning {color_mode} colors...")
    if not os.path.isfile(f"./resources/color_dict_{color_mode}.json"):
        # get range and number of distinct categories
        num_lbls_file = "./query_results/num_labels.csv"
        if not os.path.isfile(num_lbls_file):
            num_labels(g)
        
        with open(num_lbls_file, "r", encoding="utf-8") as csv_file:
            csv_dict = DictReader(csv_file)
            color_dict = defaultdict(lambda: "#f20c1f") # red
            # map colors to the variation labels
            if color_mode != "range":
                for row in csv_dict:
                    if row["num_distinct_lbls"] == '1':
                        color_dict[row["annotation_lbl"]] = "#168ff2" # blue
                    elif row["num_distinct_lbls"] == '2':
                        color_dict[row["annotation_lbl"]] = "#ff7f00" # orange
                    elif row["num_distinct_lbls"] == '3':
                        color_dict[row["annotation_lbl"]] = "#1fed18" # green
                    elif row["num_distinct_lbls"] == '4':
                        color_dict[row["annotation_lbl"]] = "#f781bf" # pink
                    elif row["num_distinct_lbls"] == '5':
                        color_dict[row["annotation_lbl"]] = "#fafa43" # yellow
            else:
                # map color to the range of distinct labels
                for row in csv_dict:
                    if row["range"] == '0':
                        color_dict[row["annotation_lbl"]] = "#0730b8" # blue
                    elif row["range"] == '1':
                        color_dict[row["annotation_lbl"]] = "#9e4603" # orange
                    elif row["range"] == '2':
                        color_dict[row["annotation_lbl"]] = "#039c12" # green
                    elif row["range"] == '3':
                        color_dict[row["annotation_lbl"]] = "#cf086f" # pink 
                    elif row["range"] == '4':
                        color_dict[row["annotation_lbl"]] = "#9c038d" # purple

        # save the color_dict for computational reasons
        with open(f"./resources/color_dict_{color_mode}.json", 'w', encoding="utf-8") as color_file:
            json.dump(color_dict, color_file)
    else:
        # needs to be initialized to avoid key errors
        color_dict = defaultdict(lambda: "#f20c1f")
        with open(f"./resources/color_dict_{color_mode}.json", 'r', encoding="utf-8") as color_file:
            color_dict = json.load(color_file)
        
    return color_dict

def create_annotation_pos(g):
    '''
    This function determines the positions of the nodes in the visualizations.

    @param g: RDF-graph
    @returns graph_pos: dictionary mapping each node to its position
    '''
    print("assigning positions...")
    if not os.path.isfile("./resources/full_graph_pos.json"):
        # get annotations for the full graph
        NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
        RDAIO = Namespace("http://rdaregistry.info/Elements/i/object/")

        annotation_lbls = []
        for annotation_uri in g.subjects(RDF.type, NIF.Annotation):
            annotation_lbls += [annotation_lbl for annotation_lbl in g.objects(annotation_uri, RDFS.label)] # annotation label
            annotation_lbls += [annotator for annotator in g.objects(annotation_uri, RDAIO.P40015)]# annotators

        # assign positions
        graph_pos = nx.spring_layout(annotation_lbls, k=0.8, seed=0)
        graph_pos = {node: (p[0] * 2000, p[1] * 2000) for (node, p) in graph_pos.items()}

        with open("./resources/full_graph_pos.json", 'w', encoding="utf-8") as pos_file:
            json.dump(graph_pos, pos_file)
    else:
        # load positions if they are already available
        with open("./resources/full_graph_pos.json", 'r', encoding="utf-8") as pos_file:
            pos_json = json.load(pos_file)

            # create Literals and Uris to match the nodes in the subgraphs
            graph_pos = dict()
            for node, pos in pos_json.items():
                if "annotator" not in node:
                    graph_pos[Literal(node, datatype=XSD.string)] = pos
                else:
                    graph_pos[URIRef(node)] = pos
    return graph_pos

def get_legend_elements(color_mode = "distinct"):
    '''
    This function creates the elements of the legend for the visualization.

    @param color_mode: 
            distinct: colors are defined by the amount of distinct labels for the annotations
            range: colors are defined by the range of distinct labels for the annotations
    @returns legend_elements: list of the elements in the legend
    '''
    legend_elements = []
    if color_mode == "range":
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Annotator',markerfacecolor="#f20c1f", markersize=10),
            Line2D([0], [0], marker='o', color='w', label='Range 0',markerfacecolor="#0730b8", markersize=10),   
            Line2D([0], [0], marker='o', color='w', label='Range 1',markerfacecolor="#9e4603", markersize=10), 
            Line2D([0], [0], marker='o', color='w', label='Range 2',markerfacecolor="#039c12", markersize=10),   
            Line2D([0], [0], marker='o', color='w', label='Range 3',markerfacecolor="#cf086f", markersize=10),  
            Line2D([0], [0], marker='o', color='w', label='Range 4',markerfacecolor="#9c038d", markersize=10),      
        ]
    else:
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', label='Annotator',markerfacecolor="#f20c1f", markersize=10),
            Line2D([0], [0], marker='o', color='w', label='No distinct labels',markerfacecolor="#168ff2", markersize=10),   
            Line2D([0], [0], marker='o', color='w', label='2 distinct labels',markerfacecolor="#ff7f00", markersize=10),   
            Line2D([0], [0], marker='o', color='w', label='3 distinct labels',markerfacecolor="#1fed18", markersize=10),   
            Line2D([0], [0], marker='o', color='w', label='4 distinct labels',markerfacecolor="#f781bf", markersize=10), 
            Line2D([0], [0], marker='o', color='w', label='5 distinct labels',markerfacecolor="#fafa43", markersize=10)     
        ]
    return legend_elements

if __name__ == "__main__":
    g = rdflib.Graph()
    result = g.parse("./graphs/dwug_en.ttl", format='turtle').serialize(format="turtle")
    
    #examples
    # inspect a single instance
    words = ["circled_mag_1856_590750.txt-21-18","circling_fic_1849_7230.txt-2441-6"]
    inspect_instance(g, words)

    # Full visualization 
    pos = create_annotation_pos(g)
    color_mode = "range"
    color_dict = get_colors(g, color_mode)
    create_full_annotation_vis(g, pos, color_dict, color_mode)

    # Annotator visualization 
    for i in tqdm(range(13), desc="Creating annotator visualizations"):
        create_single_annotator_vis(g, f"annotator{i}", pos, color_dict, color_mode="distinct")
        create_single_annotator_vis(g, f"annotator{i}", pos, color_dict, color_mode="range")
