from rdflib import Graph, Literal, RDF, URIRef, BNode
from rdflib.namespace import FOAF , XSD, SDO, Namespace, RDFS
import csv
import re
import os
from explore_data import full
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
    # dataset node
    dataset_uri = URIRef(dataset_name, base = HLV)

    g.add((dataset_uri, RDF.type, SDO.Dataset))

    return dataset_uri

def model_words(g, dataset_uri, word, start_pos, end_pos, lemma, pos_tag, language):
    word_uri = URIRef(f"{word}_{start_pos}_{end_pos}", base = HLV_Word)
    g.add((word_uri, RDF.type, NIF.Word))
    g.add((word_uri, NIF.sourceUrl, dataset_uri))
    g.add((word_uri, RDFS.label, Literal(f"{word}_{start_pos}_{end_pos}", datatype=XSD.string)))
    # from uses
    g.add((word_uri, NIF.anchorOf, Literal(word, lang="en")))
    g.add((word_uri, NIF.lemma, Literal(lemma, datatype=XSD.string)))
    g.add((word_uri, NIF.posTag, Literal(pos_tag, datatype=XSD.string)))
    g.add((word_uri, NIF.beginIndex, Literal(start_pos, datatype=XSD.integer)))
    g.add((word_uri, NIF.endIndex, Literal(end_pos, datatype=XSD.integer)))

    return word_uri

def model_sentences(g, sentence_id, sentence, language, year, start_pos, end_pos, word_uri):
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
    # judgements
    annotation_uri = URIRef(idx, base = HLV_Annotation)
    g.add((annotation_uri, RDF.type, NIF.Annotation))
    # Item
    g.add((annotation_uri, RDF.type, RDAI.P40080))
    g.add((annotation_uri, RDFS.label, Literal(f"{g.value(word1_uri, NIF.lemma)}_{g.value(word1_uri, NIF.beginIndex)}_{g.value(word1_uri, NIF.endIndex)}_{g.value(word2_uri, NIF.beginIndex)}_{g.value(word2_uri, NIF.endIndex)}", datatype=XSD.string)))

    g.add((word1_uri, NIF.annotation, annotation_uri))
    g.add((word2_uri, NIF.annotation, annotation_uri))
    g.add((annotation_uri, NIF.category, Literal(category, datatype=XSD.integer)))
    # comment
    g.add((annotation_uri, RDAI.P40064, Literal(comment, lang=language)))

    return annotation_uri

def model_annotator(g, annotator, annotation_uri):
    annotator_uri = URIRef(re.search("\d+", annotator).group(), base=HLV_Annotator)
    # Agent
    g.add((annotator_uri, RDF.type, RDAA.P50157))
    g.add((annotator_uri, RDFS.label, Literal(annotator, datatype=XSD.string)))

    # has annotator
    g.add((annotation_uri, RDAIO.P40015, annotator_uri))
    return annotator_uri

def read_csv(path):
    csvfile = open(path)
    reader = csv.DictReader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE,strict=True)
    return csvfile, list(reader)

def create_kg(data_path = "./dwug_en/data", dataset_name = "dwug_en", annotated_words = full, language="en"):
    g = Graph(bind_namespaces="rdflib")
    bind_namespaces(g)
    dataset_uri = model_dataset(g, dataset_name)
    annotation_idx = 1
    # Iterate through single csv files
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
            word1_uri = model_words(g, dataset_uri, token1, start1, end1, annotated_word, uses1_row["pos"], language)
            model_sentences(g, sentence1_id, uses1_row["context"], language, uses1_row["date"], start1_sent, end1_sent, word1_uri)
            
            # second word
            sentence2_id = judgment_row["identifier2"]

            uses2_rows = [row for row in uses_dict if row["identifier"] == sentence2_id]
            uses2_row = uses2_rows[0]
            token2 = uses2_row["context_tokenized"].split(" ")[int(uses2_row["indexes_target_token_tokenized"])]
            start2, end2 = uses2_row["indexes_target_token"].split(":")
            start2_sent, end2_sent = uses2_row["indexes_target_sentence"].split(":")
            word2_uri = model_words(g, dataset_uri, token2, start2, end2, annotated_word, uses2_row["pos"], language)
            model_sentences(g, sentence2_id, uses2_row["context"], language, uses2_row["date"], start2_sent, end2_sent, word2_uri)

            # annotation
            annotation_uri = model_annotation(g, str(annotation_idx), word1_uri, word2_uri, judgment_row["judgment"], judgment_row["comment"], language)
            annotation_idx += 1
            model_annotator(g, judgment_row["annotator"], annotation_uri)

        judgment_file.close()
        uses_file.close()
        
    # Print out the entire Graph in the RDF Turtle format
    #g.serialize(destination = f"{dataset_name}.ttl", encoding="utf-8", format="turtle")

    g.serialize(destination = f"{dataset_name}.ttl", encoding="utf-8", format="turtle")
    return g

# Iterate over triples in store and print them out.
# print("--- printing raw triples ---")
# for s, p, o in g:
#     print((s, p, o))

# For each foaf:Person in the store, print out their mbox property's value.
#print("--- printing mboxes ---")
# for person in g.subjects(RDF.type, FOAF.Person):
#     for mbox in g.objects(person, FOAF.mbox):
#         print(mbox)
if __name__ == "__main__":
    # Create a Graph
    g = create_kg()