from rdflib import Graph, Literal, RDF, URIRef
from rdflib.namespace import XSD, SDO, Namespace, RDFS
import csv
import re
import os
from explore_data import find_variation_words
from tqdm import tqdm

NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
HLV_Word = Namespace("https://hlv.org/word/")
HLV_Sentence = Namespace("https://hlv.org/sentence/")
HLV_Annotation = Namespace("https://hlv.org/annotation/")
HLV_Annotator = Namespace("https://hlv.org/annotator/")

HLV = Namespace("http://hlv.org/")
RDAI = Namespace("http://rdaregistry.info/Elements/i/")
RDAIO = Namespace("http://rdaregistry.info/Elements/i/object/")
RDAA = Namespace("http://rdaregistry.info/Elements/a/")

def bind_namespaces(g):
    '''
    This function binds the namespaces to the graph.

    @param g: RDF-graph
    '''
    # Prefixes
    g.bind("hlv", HLV)
    g.bind("nif", NIF)
    g.bind("rdai", RDAI)
    g.bind("rdaio", RDAIO)
    g.bind("rdaa", RDAA)
    g.bind("hlv_word", HLV_Word)
    g.bind("hlv_sentence", HLV_Sentence)
    g.bind("hlv_annotation", HLV_Annotation)
    g.bind("hlv_annotator", HLV_Annotator)

def model_dataset(g, dataset_name):
    '''
    This function adds the dataset node.

    @params
        g: RDF-graph
        dataset_name: name of the dataset
    @returns dataset_uri: URI of the dataset node 
    '''
    # dataset node
    dataset_uri = URIRef(dataset_name, base = HLV)

    g.add((dataset_uri, RDF.type, SDO.Dataset))

    return dataset_uri

def model_words(g, dataset_uri, word, sentence_id, start_pos, end_pos, lemma, pos_tag, language):
    '''
    This function adds the word nodes.

    @params
        g: RDF-graph
        dataset_uri: URI of the dataset node
        word: annotated token
        sentence_id: id of the annotated sentence
        start_pos: starting position of the word in the sentence string
        end_pos: end position of the word in the sentence string
        lemma: lemma of the word
        pos_tag: POS tag of the word
        language: language of the word
    @returns word_uri: URI of the word node 
    '''
    word_uri = URIRef(f"{word}_{sentence_id}", base = HLV_Word)
    g.add((word_uri, RDF.type, NIF.Word))
    g.add((word_uri, NIF.sourceUrl, dataset_uri))
    g.add((word_uri, RDFS.label, Literal(f"{word}_{sentence_id}", datatype=XSD.string)))
    # from uses
    g.add((word_uri, NIF.anchorOf, Literal(word, lang=language)))
    g.add((word_uri, NIF.lemma, Literal(lemma, datatype=XSD.string)))
    g.add((word_uri, NIF.posTag, Literal(pos_tag, datatype=XSD.string)))
    g.add((word_uri, NIF.beginIndex, Literal(start_pos, datatype=XSD.integer)))
    g.add((word_uri, NIF.endIndex, Literal(end_pos, datatype=XSD.integer)))

    return word_uri

def model_sentences(g, sentence_id, sentence, language, year, start_pos, end_pos, word_uri):
    '''
    This function adds the sentence nodes.

    @params
        g: RDF-graph
        sentence_id: id of the annotated sentence
        sentence: string of the annotated sentence
        language: language of the word
        year: year of the sentence
        start_pos: starting position of the sentence string (should be 0)
        end_pos: end position of the sentence string
        word_uri: URI of the annotated token
    @returns sentence_uri: URI of the sentence node 
    '''
    sentence_uri = URIRef(sentence_id, base = HLV_Sentence)
    g.add((sentence_uri, RDF.type, NIF.Context))
    g.add((sentence_uri, RDF.type, SDO.Observation))
    g.add((sentence_uri, RDFS.label, Literal(sentence_id, datatype=XSD.string)))
    g.add((sentence_uri, NIF.isString, Literal(sentence, lang=language)))
    g.add((sentence_uri, SDO.observationDate, Literal(year, datatype=XSD.gYear)))
    g.add((sentence_uri, NIF.beginIndex, Literal(start_pos, datatype=XSD.integer)))
    g.add((sentence_uri, NIF.endIndex, Literal(end_pos, datatype=XSD.integer)))

    g.add((word_uri, NIF.referenceContext, sentence_uri))

    return sentence_uri

def model_annotation(g, idx, word1_uri, word2_uri, category, comment, language):
    '''
    This function adds the annotation nodes.

    @params
        g: RDF-graph
        idx: id of the annotation
        word1_uri: URI of the first annotated token
        word2_uri: URI of the second annotated token
        category: annotation label (integer)
        comment: comment of the annotation
        language: language of the annotated word
    @returns annotation_uri: URI of the annotation node 
    '''
    idx2lbl = {'0':"Undecidable", '1':"Unrelated", '2':"Distantly Related", '3':"Closely Related", '4':"Identical"}

    # judgements
    annotation_uri = URIRef(idx, base = HLV_Annotation)
    g.add((annotation_uri, RDF.type, NIF.Annotation))
    # Item
    g.add((annotation_uri, RDF.type, RDAI.P40080))
    g.add((annotation_uri, RDFS.label, Literal(f"{g.value(word1_uri, RDFS.label)}_{g.value(word2_uri, RDFS.label)}", datatype=XSD.string)))

    g.add((word1_uri, NIF.annotation, annotation_uri))
    g.add((word2_uri, NIF.annotation, annotation_uri))
    g.add((annotation_uri, NIF.category, Literal(category, datatype=XSD.integer)))
    g.add((annotation_uri, NIF.category, Literal(idx2lbl[category], datatype=XSD.string)))
    # comment
    g.add((annotation_uri, RDAI.P40064, Literal(comment, lang=language)))

    return annotation_uri

def model_annotator(g, annotator, annotation_uri):
    '''
    This function adds the annotator nodes.

    @params
        g: RDF-graph
        annotator: name of the annotator
        annotation_uri: URI of the annotation
    @returns annotator_uri: URI of the annotator node 
    '''
    annotator_uri = URIRef(re.search("\d+", annotator).group(), base=HLV_Annotator)
    # Agent
    g.add((annotator_uri, RDF.type, RDAA.P50157))
    g.add((annotator_uri, RDFS.label, Literal(annotator, datatype=XSD.string)))

    # has annotator
    g.add((annotation_uri, RDAIO.P40015, annotator_uri))
    return annotator_uri

def read_csv(path):
    '''
    This function reads a csv file.

    @param path: path of the csv file
    @returns 
        csvfile: open csv file
        list(reader): the csv file as a list
    '''
    csvfile = open(path)
    reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE,strict=True)
    return csvfile, list(reader)

def create_kg(data_path = "./dwug_en/data", dataset_name = "dwug_en", annotated_words = find_variation_words(), language="en"):    
    '''
    This file creates the knowledge graph.

    @params
        data_path: path to the data folder
        dataset_name: name of the dataset
        annotated_words: list of words that should be included
        language: language of the dataset
    @returns g: RDF-graph
    '''
    g = Graph(bind_namespaces="rdflib")
    bind_namespaces(g)
    dataset_uri = model_dataset(g, dataset_name)
    annotation_idx = 1

    # Iterate through single csv files for the specified words
    for annotated_word in tqdm(set(annotated_words).intersection(set(os.listdir(data_path))), desc="Processing data"):
        judgment_file, judgment_dict = read_csv(f"{data_path}/{annotated_word}/judgments.csv")
        uses_file, uses_dict = read_csv(f"{data_path}/{annotated_word}/uses.csv")
        
        for judgment_row in judgment_dict:
            # first word
            sentence1_id = judgment_row["identifier1"]
            uses1_rows = [row for row in uses_dict if row["identifier"] == sentence1_id]
            uses1_row = uses1_rows[0]
            token1 = uses1_row["context_tokenized"].split(" ")[int(uses1_row["indexes_target_token_tokenized"])]
            start1, end1 = uses1_row["indexes_target_token"].split(":")
            start1_sent, end1_sent = uses1_row["indexes_target_sentence"].split(":")
            word1_uri = model_words(g=g, dataset_uri=dataset_uri, word=token1, sentence_id=sentence1_id, start_pos=start1, end_pos=end1, lemma=annotated_word, pos_tag=uses1_row["pos"], language=language)
            model_sentences(g=g, sentence_id=sentence1_id, sentence=uses1_row["context"], language=language, year=uses1_row["date"], start_pos=start1_sent, end_pos=end1_sent, word_uri=word1_uri)
            
            # second word
            sentence2_id = judgment_row["identifier2"]

            uses2_rows = [row for row in uses_dict if row["identifier"] == sentence2_id]
            uses2_row = uses2_rows[0]
            token2 = uses2_row["context_tokenized"].split(" ")[int(uses2_row["indexes_target_token_tokenized"])]
            start2, end2 = uses2_row["indexes_target_token"].split(":")
            start2_sent, end2_sent = uses2_row["indexes_target_sentence"].split(":")
            word2_uri = model_words(g=g, dataset_uri=dataset_uri, word=token2, sentence_id=sentence2_id, start_pos=start2, end_pos=end2, lemma=annotated_word, pos_tag=uses2_row["pos"], language=language)
            model_sentences(g=g, sentence_id=sentence2_id, sentence=uses2_row["context"], language=language, year=uses2_row["date"], start_pos=start2_sent, end_pos=end2_sent, word_uri=word2_uri)

            # annotation
            annotation_uri = model_annotation(g=g, idx=str(annotation_idx), word1_uri=word1_uri, word2_uri=word2_uri, category=judgment_row["judgment"], comment=judgment_row["comment"], language=language)
            annotation_idx += 1
            model_annotator(g=g, annotator=judgment_row["annotator"], annotation_uri=annotation_uri)

        judgment_file.close()
        uses_file.close()
        
    # Store the entire Graph in the RDF Turtle format
    g.serialize(destination = f"./graphs/{dataset_name}.ttl", encoding="utf-8", format="turtle")
    return g

if __name__ == "__main__":
    # Create a Graph
    g = create_kg()