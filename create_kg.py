from rdflib import Graph, Literal, RDF, URIRef, BNode
from rdflib.namespace import FOAF , XSD, SDO, Namespace, RDFS
#@prefix nif: <http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#> .
NIF = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
HLV_Word = Namespace("https://hlv.org/word/")
HLV_Sentence = Namespace("https://hlv.org/sentence/")
HLV_Annotation = Namespace("https://hlv.org/annotation/")
HLV_Annotator = Namespace("https://hlv.org/annotator/")

HLV = Namespace("http://hlv.org/")
RDAI = Namespace("http://rdaregistry.info/Elements/i/")
RDAIO = Namespace("http://rdaregistry.info/Elements/i/object/")
RDAA = Namespace("http://rdaregistry.info/Elements/a/")
# Create a Graph
g = Graph(bind_namespaces="rdflib")
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

# dataset node
dwug_en = URIRef("dwug_en", base = HLV)

g.add((dwug_en, RDF.type, SDO.Dataset))

attack_43_49 = URIRef("attack_43_49", base = HLV_Word)
g.add((attack_43_49, RDF.type, NIF.Word))
g.add((attack_43_49, NIF.sourceUrl, dwug_en))
g.add((attack_43_49, RDFS.label, Literal("attack_43_49", datatype=XSD.string)))
# from uses
g.add((attack_43_49, NIF.anchorOf, Literal("attack", datatype=XSD.string)))
g.add((attack_43_49, NIF.lemma, Literal("attack_nn", datatype=XSD.string)))
g.add((attack_43_49, NIF.posTag, Literal("nn1", datatype=XSD.string)))
g.add((attack_43_49, NIF.beginIndex, Literal("43", datatype=XSD.integer)))
g.add((attack_43_49, NIF.endIndex, Literal("49", datatype=XSD.integer)))

sentence1 = URIRef("fic_1835_7016.txt-2023-9", base = HLV_Sentence)
g.add((sentence1, RDF.type, NIF.Context))
g.add((sentence1, RDF.type, SDO.Observation))
g.add((sentence1, RDFS.label, Literal("fic_1835_7016.txt-2023-9", datatype=XSD.string)))
g.add((sentence1, NIF.isString, Literal("As the stranger fell to the earth under an attack so impetuous and unexpected, he uttered an exclamation in which Juan recognized the language of Mexico.", lang="en")))
g.add((sentence1, SDO.observationDate, Literal("1835", datatype=XSD.gYear)))
g.add((sentence1, NIF.beginIndex, Literal("0", datatype=XSD.integer)))
g.add((sentence1, NIF.endIndex, Literal("153", datatype=XSD.integer)))

g.add((attack_43_49, NIF.referenceContext, sentence1))

attack_250_256 = URIRef("attack_250_256", base = HLV_Word)
g.add((attack_250_256, RDF.type, NIF.Word))
g.add((attack_250_256, NIF.sourceUrl, dwug_en))
g.add((sentence1, RDFS.label, Literal("attack_250_256", datatype=XSD.string)))

# from uses
g.add((attack_250_256, NIF.anchorOf, Literal("attack", lang="en")))
g.add((attack_250_256, NIF.lemma, Literal("attack_nn", datatype=XSD.string)))
g.add((attack_250_256, NIF.posTag, Literal("nn1", datatype=XSD.string)))
g.add((attack_250_256, NIF.beginIndex, Literal("250", datatype=XSD.integer)))
g.add((attack_250_256, NIF.endIndex, Literal("256", datatype=XSD.integer)))

sentence2 = URIRef("mag_1834_554263.txt-306-48", base = HLV_Sentence)
g.add((sentence2, RDF.type, NIF.Context))
g.add((sentence2, RDF.type, SDO.Observation))
g.add((sentence2, RDFS.label, Literal("mag_1834_554263.txt-306-48", datatype=XSD.string)))
g.add((sentence2, NIF.isString, Literal("The great object with each party seemed to be to make the other begin the attack: the English would not do this, because they saw that their artillery was rapidly thinning the ranks of their enemies; and Charles was under the necessity of making the attack.", lang="en")))
g.add((sentence2, SDO.observationDate, Literal("1834", datatype=XSD.gYear)))
g.add((sentence2, NIF.beginIndex, Literal("0", datatype=XSD.integer)))
g.add((sentence2, NIF.endIndex, Literal("257", datatype=XSD.integer)))

g.add((attack_250_256, NIF.referenceContext, sentence2))

# judgements
annotation1 = URIRef("1", base = HLV_Annotation)
g.add((annotation1, RDF.type, NIF.Annotation))
# Item
g.add((annotation1, RDF.type, RDAI.P40080))
g.add((annotation1, RDFS.label, Literal("attack_nn_43_49_250_256", datatype=XSD.string)))

g.add((attack_43_49, NIF.annotation, annotation1))
g.add((attack_250_256, NIF.annotation, annotation1))
g.add((annotation1, NIF.category, Literal("0", datatype=XSD.integer)))
# comment
g.add((annotation1, RDAI.P40064, Literal("", lang="en")))

annotator9 = URIRef("9", base=HLV_Annotator)
# Agent
g.add((annotator9, RDF.type, RDAA.P50157))
g.add((annotator9, RDFS.label, Literal("annotator9", datatype=XSD.string)))

# has annotator
g.add((annotation1, RDAIO.P40015, annotator9))


# Iterate over triples in store and print them out.
# print("--- printing raw triples ---")
# for s, p, o in g:
#     print((s, p, o))

# For each foaf:Person in the store, print out their mbox property's value.
#print("--- printing mboxes ---")
# for person in g.subjects(RDF.type, FOAF.Person):
#     for mbox in g.objects(person, FOAF.mbox):
#         print(mbox)

# Print out the entire Graph in the RDF Turtle format
g.serialize(destination = "dwug_en.ttl", encoding="utf-8", format="turtle")