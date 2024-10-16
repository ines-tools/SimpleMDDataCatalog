import validators 
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD


def identifier_to_uri(identifier: str, namespace: Namespace) -> URIRef :
    # checks if identifier str is a valid uri and if it is not, turns it into a uri
    identifier= str(identifier)
    if validators.uri.uri(identifier):
        uri=identifier
    else :
        uri= namespace[identifier]
    return uri

def literal_or_uri(string = str):
    # checks if string is value or uri and returns as appropriate type
    string = str(string)
    if validators.uri.uri(string):
        value= URIRef(string)
    else :
        value = Literal(string) 

    return value   