import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_graph
import networkx as nx
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO
from query_kg import get_pos_tags, num_labels
import matplotlib.colors as mcolors
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

def inspect_instance(g, words, path):
    '''
    This function creates a visualization of all annotations in the dataset.
    
    @params
        g: graph
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
    #hlv_word:{words[0]}

    instance_graph_rdf = g.query(instance_query)
    print("number of triples", len(instance_graph_rdf))
    # for row in instance_graph_rdf:
    #     print(row)
    #     print("\n")

    rdf_grapher_vis(instance_graph_rdf.serialize(format="turtle"), path)
    return instance_graph_rdf

def rdf_grapher_vis(g, path):
    '''
    This method creates the visualization for the full knowledge graph.

    @param result: the serialized turtle string
    '''
    #print("result:", result)
    params = {"rdf": g, "from": "ttl", "to": "png"}
    url = f"http://www.ldf.fi/service/rdf-grapher"
    #r = requests.get(url, params = params)
    r = requests.post(url, params = params)
    print("status code: ", r.status_code)
    i = Image.open(BytesIO(r.content))
    i.show()

    i.save(path)

def create_annotation_subgraph(g):
    '''
    This function creates a visualization of all annotations in the dataset.
    
    @params
        g: graph
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
    #annotator_query.format(annotator_label=annotator)

    annotation_graph_rdf = g.query(annotation_query)
    # for row in annotation_graph_rdf:
    #     print(row)
    #     print("\n")
    return annotation_graph_rdf

def create_full_annotation_vis(g, pos, color_dict, color_mode = "distinct"):
    '''
    This function visualizes all annotations.

    @params 
        g: graph
        full_pos: positions of all graph nodes in the visualization
        color_dict: colors of the nodes
        color_mode: kind of variation
    '''
    annotation_graph_rdf = create_annotation_subgraph(g)
    annotation_graph_nx = rdflib_to_networkx_graph(annotation_graph_rdf) 
    lbl2category = {triple[0]:int(triple[2]) for triple in annotation_graph_rdf}
    annotation_nodes = lbl2category.keys()
    
    colors = [color_dict[str(lbl)] for lbl in annotation_nodes]

    scales = [0.25, 0.5, 0.75, 1, 1.25, 1.5]
    for lbl, category in lbl2category.items():
        pos[lbl] = (pos[lbl][0] * scales[category], pos[lbl][1] * scales[category])

    fig, ax = plt.subplots()
    fig.suptitle("Full annotation graph")

    nx.draw_networkx_nodes(annotation_graph_nx, ax=ax, pos=pos, nodelist = annotation_nodes, node_size=1, node_color=colors, margins=(0.8, 0.8))

    ax.margins(x=0.6, y=0.6)
    ax.axis('off')

    fig.legend(handles = get_legend_elements(color_mode), loc="upper right") 
    plt.tight_layout() 
    #plt.show()
    plt.savefig(f"./visualizations/full/full_annotations_{color_mode}_dwug_en.png", format="PNG", dpi=300)


def create_annotator_subgraph(g, annotator):
    '''
    This function creates a visualization of the annotator behaviour over the full dataset.
    
    @params
        g: graph
        annotator: the annotator that should be visualized
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
    #annotator_query.format(annotator_label=annotator)

    annotator_graph_rdf = g.query(annotator_query)
    # for row in annotator_graph_rdf:
    #     print(row)
    #     print("\n")
    return annotator_graph_rdf

def create_annotator_vis(g, annotators):
    # TODO: cluster?
    # TODO: Titel überlappen -> ausstellen?
    # TODO: runder machen -> gitter statt untereinander
    # TODO: All data
    # TODO: subplots mouseover=True?
    fig, axs = plt.subplots(len(annotators), 1)
    fig.suptitle("Annotator comparison over the whole dataset")
    #plt.title("Annotator comparison over the whole dataset")


    # get colors
    color_dict = get_colors(g)
    #axs[0].plot([0], [0], color="#f20c1f", label = "Annotator")
    for i in range(len(annotators)):
        axs[i].set_title(annotators[i])
        annotator_graph_rdf = create_annotator_subgraph(g, annotators[i])

        annotator_graph_nx = rdflib_to_networkx_graph(annotator_graph_rdf) 
        #annotator_graph_nx = transform_edge_weights(annotator_graph_nx, transformation=lambda x: (x ** 6))
        pos = nx.spring_layout(annotator_graph_nx, k=0.8, seed=0)
        pos = {node: (p[0] * 2000, p[1] * 2000) for (node, p) in pos.items()}
        #print("pos:", pos)

        colors = [color_dict[str(node)] for node in pos.keys()]
        annotators = [node for node in pos.keys() if color_dict[str(node)] == "#f20c1f"]
        annotator_graph_nx = nx.ego_graph(annotator_graph_nx, annotator)

        nx.draw_networkx_nodes(annotator_graph_nx, ax=axs[i], pos=pos, node_size=1, node_color=colors, margins=(0.8, 0.8))
        nx.draw_networkx_edges(annotator_graph_nx, ax=axs[i], pos = pos, edge_color="#94918f") # grey
        nx.draw_networkx_nodes(annotator_graph_nx, ax=axs[i], pos = pos, nodelist=[annotator], node_size=5, node_color = "#f20c1f")
        #nx.draw(annotator_graph_nx, ax=axs[i], pos = pos, with_labels=True, font_weight='normal', node_size=300, font_size=14)
        #nx.draw(annotator_graph_nx, ax=axs[i], pos = pos, with_labels=False, font_weight='normal', node_size=300, font_size=14)

        #edge_labels = {tuple([triple[0], triple[2]]): f"nif:category" for triple in annotator_graph_rdf}
        #nx.draw_networkx_edge_labels(annotator_graph_nx, pos = pos,ax=axs[i], edge_labels=edge_labels, font_size=14)

        axs[i].margins(x=0.6, y=0.6)
        axs[i].axis('off')
        #axs[i].plot([0], [0], color="#f20c1f", label = "Annotator axis i")
            
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Annotator',markerfacecolor="#f20c1f", markersize=10),
        Line2D([0], [0], marker='o', color='w', label='No distinct labels',markerfacecolor="#168ff2", markersize=10),   
        Line2D([0], [0], marker='o', color='w', label='2 distinct labels',markerfacecolor="#ff7f00", markersize=10), # "#ff7f00"  
        Line2D([0], [0], marker='o', color='w', label='3 distinct labels',markerfacecolor="#1fed18", markersize=10), # "#ff7f00"  
        Line2D([0], [0], marker='o', color='w', label='4 distinct labels',markerfacecolor="#f781bf", markersize=10), # "#ff7f00"     
    ]
    # plt.legend(handles = legend_elements, loc = 'upper right')
    fig.legend(handles = legend_elements, loc="upper right") 
    plt.tight_layout() # witd nicht angewendet
    plt.show()
    #plt.savefig("annotator_dwug_en.png", format="PNG", dpi=300)

def create_single_annotator_vis(g, annotator, pos, color_dict, color_mode = "distinct"):
    fig, ax = plt.subplots()
    fig.suptitle(annotator)

    annotator_graph_rdf = create_annotator_subgraph(g, annotator)
    annotator_graph_nx = rdflib_to_networkx_graph(annotator_graph_rdf) 
    
    annotator_node = [node for node in annotator_graph_nx.nodes if color_dict[str(node)] == "#f20c1f" and str(node).split("/")[-1] == re.search("\d+", annotator).group()]
    annotation_nodes = list(set(annotator_graph_nx.nodes)-set(annotator_node)) # exlude annotator node
    colors = [color_dict[str(node)] for node in annotation_nodes]

    #annotator_graph_nx = nx.ego_graph(annotator_graph_nx, annotator_node[0])

    nx.draw_networkx_nodes(annotator_graph_nx, ax=ax, pos=pos, nodelist = annotation_nodes, node_size=1, node_color=colors, margins=(0.8, 0.8))
    #nx.draw_networkx_edges(annotator_graph_nx, ax=ax, pos = pos, edge_color="#94918f") # grey
    nx.draw_networkx_nodes(annotator_graph_nx, ax=ax, pos = {annotator_node[0]:np.array([0,0])}, nodelist=annotator_node, node_size=5, node_color = "#f20c1f")

    ax.margins(x=0.6, y=0.6)
    ax.axis('off')

    fig.legend(handles = get_legend_elements(color_mode), loc="upper right") 
    plt.tight_layout() 
    #plt.show()
    plt.savefig(f"./visualizations/annotator/{annotator}_{color_mode}_dwug_en.png", format="PNG", dpi=300)

def get_colors(g, color_mode = "distinct"):
    # read num of distinct lbls
    print("assigning colors...")
    if not os.path.isfile(f"./resources/color_dict_{color_mode}.json"):
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


        with open(f"./resources/color_dict_{color_mode}.json", 'w', encoding="utf-8") as color_file:
            json.dump(color_dict, color_file)
    else:
        with open(f"./resources/color_dict_{color_mode}.json", 'r', encoding="utf-8") as color_file:
            color_dict = json.load(color_file)
        
    return color_dict

def create_pos_subgraph(g, pos):
    '''
    This function creates a visualization of the annotator behaviour over the full dataset.
    
    @params
        g: graph
        annotator: the annotator that should be visualized
    '''
    pos_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    CONSTRUCT {{
        ?annotation_lbl nif:annotation ?category .
    }}
    WHERE {{
        ?annotation rdfs:label ?annotation_lbl ;
            nif:category ?category .

        ?token nif:posTag "{pos}"^^xsd:string ;
            nif:annotation ?annotation .
        

    }}
    """
    # print("subgraph: ", g.query(pos_query))
    # for row in g.query(pos_query):
    #     print(row)
    #     print("\n")
    return g.query(pos_query)

def create_pos_vis(g, pos_tags):
    fig, axs = plt.subplots(len(pos_tags))
    
    fig.suptitle("POS-tag comparison over the whole dataset")
    
    # outside of the loop to keep positions between graphs
    pos = nx.spring_layout(rdflib_to_networkx_graph(create_pos_subgraph(g, pos_tags[0])))
    #print("pos:", pos)
    for i in range(len(pos_tags)):
        axs[i].set_title(pos_tags[i])
        pos_graph_rdf = create_pos_subgraph(g, pos_tags[i])

        pos_graph_nx = rdflib_to_networkx_graph(create_pos_subgraph(g, pos_tags[i])) 
        #print("\nannotator_graph_nx nodes", pos_graph_nx.nodes) 
        
        #edge_labels = {tuple([triple[0], triple[2]]): f"property={triple[1]}" for triple in annotator_graph_rdf}
        edge_labels = {tuple([triple[0], triple[2]]): f"nif:category" for triple in pos_graph_rdf}
        #print("\nedge labels:\n", edge_labels)
        # font_size=8, font_weight='normal', verticalalignment="bottom"
       
        nx.draw(pos_graph_nx, ax=axs[i], pos = pos, with_labels=True, font_weight='normal', node_size=300, font_size=14)
        nx.draw_networkx_edge_labels(pos_graph_nx, pos = pos,ax=axs[i], edge_labels=edge_labels, font_size=14)
        axs[i].margins(x=0.6, y=0.6)

    #plt.show()
    plt.savefig("./visualizations/pos/pos_dwug_en.png", format="PNG")

def create_annotation_pos(g):
    print("assigning positions...")
    if not os.path.isfile("./resources/full_graph_pos.json"):
        # create annotations for the full graph
        NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
        RDAIO = Namespace("http://rdaregistry.info/Elements/i/object/")

        annotation_lbls = []
        for annotation_uri in g.subjects(RDF.type, NIF.Annotation):
            annotation_lbls += [annotation_lbl for annotation_lbl in g.objects(annotation_uri, RDFS.label)] # annotation label
            annotation_lbls += [annotator for annotator in g.objects(annotation_uri, RDAIO.P40015)]# annotators


        graph_pos = nx.spring_layout(annotation_lbls, k=0.8, seed=0)
        graph_pos = {node: (p[0] * 2000, p[1] * 2000) for (node, p) in graph_pos.items()}

        with open("./resources/full_graph_pos.json", 'w', encoding="utf-8") as pos_file:
            json.dump(graph_pos, pos_file)
    else:
        with open("./resources/full_graph_pos.json", 'r', encoding="utf-8") as pos_file:
            pos_json = json.load(pos_file)

            # create Literals and Uris
            #HLV_Annotator = Namespace("https://hlv.org/annotator/")
            graph_pos = dict()
            for node, pos in pos_json.items():
                if "annotator" not in node:
                    graph_pos[Literal(node, datatype=XSD.string)] = pos
                else:
                    graph_pos[URIRef(node)] = pos
    return graph_pos

def get_legend_elements(color_mode = "distinct"):
    legend_elements = []
    if color_mode == "range":
        # change colors and labels
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
    #result = g.parse("./graphs/dwug_en.ttl", format='turtle').serialize(format="turtle")
    result = g.parse("./graphs/test_dwug_en.ttl", format='turtle').serialize(format="turtle")
    
    words = ["circled_mag_1856_590750.txt-21-18","circling_fic_1849_7230.txt-2441-6"]
    inspect_instance(g, words, f"./visualizations/instance/{'_'.join(words)}_dwug_en.png")

    # Annotator visualization 
    # with rdf-grapher

    # with networkx
    # pos = create_annotation_pos(g)
    # color_mode = "range"
    # color_dict = get_colors(g, color_mode)
    # create_full_annotation_vis(g, pos, color_dict, color_mode)

    # test
    #create_single_annotator_vis(g, f"annotator1", pos, color_dict, color_mode="range")

    # for i in tqdm(range(13), desc="Creating annotator visualizations"):
    #     create_single_annotator_vis(g, f"annotator{i}", pos, color_dict)
