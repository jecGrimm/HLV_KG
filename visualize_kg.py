import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_graph
import networkx as nx
import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO

def full_vis(result):
    '''
    This method creates the visualization for the full knowledge graph.

    @param result: the serialized turtle string
    '''
    print("result:", result)
    params = {"rdf": result, "from": "ttl", "to": "png"}
    url = f"http://www.ldf.fi/service/rdf-grapher"
    r = requests.get(url, params = params)

    i = Image.open(BytesIO(r.content))
    i.show()

    i.save("full_dwug_en.png")

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
        ?annotation_lbl nif:annotation ?category .
    }}
    WHERE {{
        ?annotation rdaio:P40015 ?annotator ;
            rdfs:label ?annotation_lbl ;
            nif:category ?category.
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
    fig, axs = plt.subplots(len(annotators))
    fig.suptitle("Annotator comparison over the whole dataset")
    
    pos = nx.spring_layout(rdflib_to_networkx_graph(create_annotator_subgraph(g, annotators[0])))
    #print("pos:", pos)
    for i in range(len(annotators)):
        axs[i].set_title(annotators[i])
        annotator_graph_rdf = create_annotator_subgraph(g, annotators[i])

        annotator_graph_nx = rdflib_to_networkx_graph(create_annotator_subgraph(g, annotators[i])) 
        #print("\nannotator_graph_nx nodes", annotator_graph_nx.nodes) 
        
        #edge_labels = {tuple([triple[0], triple[2]]): f"property={triple[1]}" for triple in annotator_graph_rdf}
        edge_labels = {tuple([triple[0], triple[2]]): f"nif:category" for triple in annotator_graph_rdf}
        #print("\nedge labels:\n", edge_labels)
        nx.draw(annotator_graph_nx, ax=axs[i], pos = pos, with_labels=True, font_weight='normal', node_size=300, font_size=14)
        nx.draw_networkx_edge_labels(annotator_graph_nx, pos = pos,ax=axs[i], edge_labels=edge_labels, font_size=14)

        axs[i].margins(x=0.6, y=0.6)
    #plt.show()
    plt.savefig("annotator_dwug_en.png", format="PNG")


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
    # TODO: position edge labels
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
    plt.savefig("pos_dwug_en.png", format="PNG")

if __name__ == "__main__":
    g = rdflib.Graph()
    result = g.parse("./dwug_en.ttl", format='turtle').serialize(format="turtle")

    #full_vis(result)

    create_annotator_vis(g, ["annotator9", "annotator9"])

    #create_pos_vis(g, ["nn1", "nn1"])
