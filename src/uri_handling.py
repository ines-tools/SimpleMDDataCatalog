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

def str_abbrev_namespace_to_full_namespace(str_uri= str):
    split_at_colon= str_uri.split(":")
    namespace_dict={
        "owl":OWL,
        "xsd":XSD,
        "dcterms": DCTERMS,
        "dqv": "http://www.w3.org/ns/dqv#",
        "iso": "https://iso25000.com/index.php/en/iso-25000-standards/iso-25012/"
    }
    full_namespace_str= str(namespace_dict[split_at_colon[0]])+str(split_at_colon[1])
    full_namespace=URIRef(full_namespace_str)
    return full_namespace


str_uri= 'xsd:int'
str_abbrev_namespace_to_full_namespace(str_uri=str_uri)