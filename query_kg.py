import rdflib

def annotated_sentences(g):
    annotations_query = """
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT DISTINCT ?annotator ?token ?sentence
    WHERE {
        ?word nif:anchorOf ?token;
            nif:annotation ?annotation;
            nif:referenceContext/nif:isString ?sentence.    

        ?annotation rdaio:P40015/rdfs:label ?annotator.
    }
    ORDER BY ?annotator ?lemma"""

    qres = g.query(annotations_query)
    #print(qres)
    # store results in a csv file
    qres.serialize("annotated_sents.csv", encoding='utf-8', format='csv')

    # print results
    for row in qres:
        print(f"{row.annotator}: {row.token} - {row.sentence}")

def num_labels(g):
    num_labels_query = """
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT ?annotation_lbl ?category (COUNT(?category) as ?num_distinct_lbls)
    WHERE {
        ?annotation nif:category ?category ;
            rdfs:label ?annotation_lbl .
    }
    GROUP BY ?annotation_lbl
    ORDER BY ?annotation_lbl ?count ?category"""

    qres = g.query(num_labels_query)
    #print(qres)
    # store results in a csv file
    qres.serialize("num_labels.csv", encoding='utf-8', format='csv')

    # print results
    for row in qres:
        print(f"{row.annotation_lbl} - {row.category}: {row.num_distinct_lbls}")

def filter_variation(g, start, end = None):
    condition = ""
    if start == end:
        condition = f"HAVING (COUNT(?category) = {start})"
    elif end == None:
        condition = f"HAVING (COUNT(?category) >= {start})"
    else:
        condition = f"HAVING (COUNT(?category) >= {start} && COUNT(?category) <= {end})"

    num_variation_query = f"""
        PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
        PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
        PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
        PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX schema: <https://schema.org/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT ?annotation_lbl ?category (COUNT(?category) as ?num_distinct_lbls)
        WHERE {{
            ?annotation nif:category ?category ;
                rdfs:label ?annotation_lbl .
        }}
        GROUP BY ?annotation_lbl
        {condition}
        ORDER BY ?annotation_lbl ?count ?category"""

    qres = g.query(num_variation_query)
    #print(qres)
    # store results in a csv file
    qres.serialize(f"variations_{start}_{end}.csv", encoding='utf-8', format='csv')

    # print results
    for row in qres:
        print(f"{row.annotation_lbl}: {row.category}")

if __name__ == "__main__":
    g = rdflib.Graph()
    g.parse("./dwug_en.ttl", format='turtle').serialize(format="turtle")

    #annotated_sentences(g)
    #num_labels(g)
    #filter_variation(g, start = 1)
    #filter_variation(g, start = 1, end = 3)
    filter_variation(g, start = 3, end = 3)
