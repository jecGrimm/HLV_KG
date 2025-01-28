import rdflib

def category_stats(g):
    '''
    This functions queries the graph to collect information about the categories.

    This query answers the question: How often has a label been annotated?

    @param g: RDF-graph
    @returns qres: the result of the query
    '''
    category_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT DISTINCT ?category (COUNT(?category) as ?num_annotated) (COUNT(DISTINCT ?annotation_lbl) as ?num_distinct_sentence_pairs) (COUNT(DISTINCT ?annotator) as ?num_annotators) (GROUP_CONCAT(DISTINCT ?annotator; separator=" | ") as ?annotators)
    WHERE {{
        ?annotation nif:category ?category ;
            rdfs:label ?annotation_lbl ;
            rdaio:P40015/rdfs:label ?annotator .

        FILTER(isNumeric(?category))
    }} 
    GROUP BY ?category
    ORDER BY ?category ?annotators
    """
    qres = g.query(category_query)

    # store results in a csv file
    qres.serialize(f"./query_results/category_stats.csv", encoding='utf-8', format='csv')
    return qres

def annotations_per_annotator(g, annotator):
    '''
    This functions queries the graph to collect all annotation of one annotator.

    This query answers the question: Which annotations has a annotator done?

    @params 
        g: RDF-graph
        annotator: the annotator for which the annotations are collected
    @returns qres: the result of the query
    '''
    annotations_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT DISTINCT ?annotation_lbl (GROUP_CONCAT(?category) as ?categories) (GROUP_CONCAT(?sentencestr; separator=" || ") as ?sentences)
    WHERE {{
        ?annotation rdaio:P40015/rdfs:label "{annotator}"^^xsd:string;
            rdfs:label ?annotation_lbl ;
            nif:category ?category .
        
        ?word nif:annotation ?annotation ;
            nif:referenceContext ?sentence .

        ?sentence rdfs:label ?sentenceid ;
            nif:isString ?sentencestr .

    }} 
    GROUP BY ?sentencestr
    ORDER BY ?annotation_lbl ?categories ?sentences
    """
    qres = g.query(annotations_query)

    # store results in a csv file
    qres.serialize(f"./query_results/annotator/{annotator}.csv", encoding='utf-8', format='csv')
    return qres

def num_labels(g):
    '''
    This functions queries the graph to collect information about the variation of the annotations.

    This query answers the question: How many distinct labels has a annotation and how much do they differ from each other?
    
    @param g: RDF-graph
    @returns qres: the result of the query
    '''
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
    qres = g.query(num_labels_query)

    # store results in a csv file
    qres.serialize("./query_results/num_labels.csv", encoding='utf-8', format='csv')
    return qres

def filter_variation(g, start, end = None):
    '''
    This query returns all annotations with at least a number of <start> distinct labels and a maximum of <end> distinct labels.

    It is a more fine-grained duplicate of num_labels().

    @param g: RDF-graph
    @returns qres: the result of the query
    '''
    condition = ""
    if start == end:
        condition = f"HAVING (COUNT(DISTINCT ?category) = {start})"
    elif end == None:
        condition = f"HAVING (COUNT(DISTINCT ?category) >= {start})"
    else:
        condition = f"HAVING (COUNT(DISTINCT ?category) >= {start} && COUNT(DISTINCT ?category) <= {end})"

    num_variation_query = f"""
    PREFIX nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> 
    PREFIX rdaa: <http://rdaregistry.info/Elements/a/> 
    PREFIX rdai: <http://rdaregistry.info/Elements/i/> 
    PREFIX rdaio: <http://rdaregistry.info/Elements/i/object/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
    PREFIX schema: <https://schema.org/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 

    SELECT ?annotation_lbl (COUNT(DISTINCT ?category) as ?num_distinct_lbls) (COUNT(?annotation_lbl)/2 as ?num_total_lbls) (MAX(?category) - MIN(?category) as ?range)
    WHERE {{
        ?annotation nif:category ?category ;
            rdfs:label ?annotation_lbl .

        ?word1 nif:annotation ?annotation ;
            nif:lemma ?lemma ;
            nif:referenceContext/rdfs:label ?sentence1ID .
        ?word2 nif:annotation ?annotation ;
            nif:referenceContext/rdfs:label ?sentence2ID .

        FILTER (isNumeric(?category))
        FILTER (?sentence1ID != ?sentence2ID)
    }}
    GROUP BY ?annotation_lbl
    {condition}
    ORDER BY ?num_distinct_lbls ?num_total_lbls ?range ?annotation_lbl
    """

    qres = g.query(num_variation_query)

    # store results in a csv file
    qres.serialize(f"./query_results/variation/variations_{start}_{end}.csv", encoding='utf-8', format='csv')
    return qres

def get_pos_tags(g):
    '''
    This query lists the used POS-tags in the graph.

    It answers the question: Which POS-tags are used in the dataset?

    @param g: RDF-graph
    @returns qres: the result of the query
    '''
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

    # store results in a csv file
    qres.serialize(f"./query_results/pos_tags.csv", encoding='utf-8', format='csv')
    return qres


if __name__ == "__main__":
    g = rdflib.Graph()
    g.parse("./graphs/dwug_en.ttl", format='turtle').serialize(format="turtle")

    # some examples
    #category_stats(g)
    annotations_per_annotator(g, annotator="annotator1") # get annotated sentences per annotator
    #num_labels(g) # get all instances with variation count
    #filter_variation(g, start = 2) # get high variation
    #filter_variation(g, start = 1, end=1) # get no variation
    #get_pos_tags(g) # all pos tags in the dataset

