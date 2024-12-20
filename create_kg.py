from rdflib import Graph, Literal, RDF, URIRef, BNode
from rdflib.namespace import FOAF , XSD, SDO

# Create a Graph
g = Graph()

hlv = URIRef("http://hlv.org/")
# dataset node
dices_350 = URIRef("dices_350", base = hlv)

# Prefixes
g.bind("hlv", hlv)

g.add((dices_350, RDF.type, SDO.Dataset))

# donna = URIRef("http://example.org/donna")

# # Add triples using store's add() method.
# g.add((donna, RDF.type, FOAF.Person))
# g.add((donna, FOAF.nick, Literal("donna", lang="en")))
# g.add((donna, FOAF.name, Literal("Donna Fales")))
# g.add((donna, FOAF.mbox, URIRef("mailto:donna@example.org")))

# # Add another person
# ed = URIRef("http://example.org/edward")

# # Add triples using store's add() method.
# g.add((ed, RDF.type, FOAF.Person))
# g.add((ed, FOAF.nick, Literal("ed", datatype=XSD.string)))
# g.add((ed, FOAF.name, Literal("Edward Scissorhands")))
# g.add((ed, FOAF.mbox, Literal("e.scissorhands@example.org", datatype=XSD.anyURI)))

# Iterate over triples in store and print them out.
# print("--- printing raw triples ---")
# for s, p, o in g:
#     print((s, p, o))

# For each foaf:Person in the store, print out their mbox property's value.
#print("--- printing mboxes ---")
# for person in g.subjects(RDF.type, FOAF.Person):
#     for mbox in g.objects(person, FOAF.mbox):
#         print(mbox)

# Bind the FOAF namespace to a prefix for more readable output
g.bind("foaf", FOAF)

# Print out the entire Graph in the RDF Turtle format
print(g.serialize(format="turtle"))