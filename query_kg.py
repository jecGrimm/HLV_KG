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
    qres.serialize("./query_results/annotated_sents.csv", encoding='utf-8', format='csv')

    # print results
    # for row in qres:
    #     print(f"{row.annotator}: {row.token} - {row.sentence}")

def num_labels(g):
    '''
    This query answers the question: How many distinct labels has a annotation?
    '''
    # TODO: Filter category for integer
    num_labels_query = """
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT ?annotation_lbl (COUNT(DISTINCT ?category) as ?num_distinct_lbls) (COUNT(?annotation_lbl)/2 as ?num_total_lbls) (MAX(?category) - MIN(?category) as ?range)
    WHERE {
        ?annotation nif:category ?category ;
            rdfs:label ?annotation_lbl .

        ?word1 nif:annotation ?annotation ;
            nif:lemma ?lemma ;
            nif:referenceContext/rdfs:label ?sentence1ID .
        ?word2 nif:annotation ?annotation ;
            nif:referenceContext/rdfs:label ?sentence2ID .

        FILTER (isNumeric(?category))
        FILTER (?sentence1ID != ?sentence2ID)
    }
    GROUP BY ?annotation_lbl
    ORDER BY ?num_distinct_lbls ?num_total_lbls ?range ?annotation_lbl"""
    #FILTER (DATATYPE(?category)==xsd:integer)
    qres = g.query(num_labels_query)
    #print(qres)
    # store results in a csv file
    qres.serialize("./query_results/num_labels.csv", encoding='utf-8', format='csv')

    # print results
    # for row in qres:
    #     print(f"{row.annotation_lbl} - {row.category}: {row.num_distinct_lbls}")

def filter_variation(g, start, end = None):
    '''
    This query returns all annotations with at least a number of <start> distinct labels and a maximum of <end> distinct labels.
    '''
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

        SELECT ?annotation_lbl (COUNT(DISTINCT ?category) as ?num_distinct_lbls)
        WHERE {{
            ?annotation nif:category ?category ;
                rdfs:label ?annotation_lbl .

            ?word1 nif:annotation ?annotation ;
                nif:lemma ?lemma ;
                nif:referenceContext/rdfs:label ?sentence1ID .
            ?word2 nif:annotation ?annotation ;
                nif:referenceContext/rdfs:label ?sentence2ID .

            FILTER (?sentence1ID != ?sentence2ID)
        }}
        GROUP BY ?annotation_lbl
        {condition}
        ORDER BY ?annotation_lbl ?num_distinct_lbls"""

    qres = g.query(num_variation_query)
    #print(qres)
    # store results in a csv file
    qres.serialize(f"./query_results/variations_{start}_{end}.csv", encoding='utf-8', format='csv')

    # print results
    # for row in qres:
    #     print(f"{row.annotation_lbl}: {row.category}")

def get_pos_tags(g):
    pos_query = f"""
        PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
        PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
        PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
        PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        PREFIX schema: <https://schema.org/> 
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

        SELECT DISTINCT ?pos
        WHERE {{
            ?word nif:posTag ?pos .
        }}
        ORDER BY ?pos"""

    qres = g.query(pos_query)
    #print(qres)
    # store results in a csv file
    qres.serialize(f"./query_results/pos_tags.csv", encoding='utf-8', format='csv')

    # print results
    # for row in qres:
    #     print(f"{row.pos}")
    
    return qres


if __name__ == "__main__":
    g = rdflib.Graph()
    #g.parse("./graphs/dwug_en.ttl", format='turtle').serialize(format="turtle")
    g.parse("./graphs/test_dwug_en.ttl", format='turtle').serialize(format="turtle")
    
    # annotated_sentences(g) # get annotated sentences per annotator
    num_labels(g) # get all instances with variation count
    #filter_variation(g, start = 2) # get high variation
    #filter_variation(g, start = 1, end=1) # get no variation
    #get_pos_tags(g) # all pos tags in the dataset

