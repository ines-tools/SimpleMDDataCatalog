import pandas as pd
import validators 
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD
import validators.uri

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

uri="https://datacatalog.github.io/test_this#"
uri=Namespace(uri)

input_sheet= './tests/example_spreadsheet.xlsx'


datasets_df = pd.read_excel(input_sheet, 'Datasets', converters={'dcterms:identifier': str, 'prov:wasDerivedFrom':str, 'dcat:distrbution':str})
distributions_df = pd.read_excel(input_sheet, 'Distributions')

ns=Namespace(uri)

data_catalog = Graph()
adms_ns= Namespace("http://www.w3.org/ns/adms#")
data_catalog.bind("adms", Namespace(adms_ns))

for i, row in datasets_df.iterrows():
    dataset_uri= identifier_to_uri(row['dcterms:identifier'],ns)

    # declare dataset
    data_catalog.add((dataset_uri,RDF.type, DCAT.Dataset))
    # add title
    data_catalog.add((dataset_uri,
                      DCTERMS.title, 
                      Literal(row['dcterms:title'])))
    # add description
    data_catalog.add((dataset_uri,
                      DCTERMS.description, 
                      Literal(row['dcterms:description'])))
    # add publisher
    data_catalog.add((dataset_uri,
                      DCTERMS.publisher, 
                      literal_or_uri(row['dcterms:publisher'])))
    # add  contactPoint
    data_catalog.add((dataset_uri,
                      DCAT.contactPoint, 
                      literal_or_uri(row['dcat:contactPoint'])))
    
    # add license
    data_catalog.add((dataset_uri,
                      DCTERMS.license, 
                      literal_or_uri(row['dcterms:license'])))
    # add version
    data_catalog.add((dataset_uri,
                      DCAT.hasCurrentVersion, 
                      literal_or_uri(row['dcat:hasCurrentVersion'])))
    # add themes
    theme_list= list(row['dcat:theme'].split(","))
    for j in theme_list:
        data_catalog.add((dataset_uri,
                          DCAT.theme,
                          literal_or_uri(j.strip())))
    
    # add spatial 
    data_catalog.add((dataset_uri,
                      DCTERMS.spatial, 
                      literal_or_uri(row['dcterms:spatial'])))

    # add temporal 
    data_catalog.add((dataset_uri,
                      DCTERMS.temporal, 
                      literal_or_uri(row['dcterms:temporal'])))
    # add status
    data_catalog.add((dataset_uri,
                      adms_ns.status, 
                      literal_or_uri(row['adms:status'])))
    
    # add provenance
    prov =str(row['prov:wasDerivedFrom'])
    prov_list= list(prov.split(","))
    for k in prov_list:
        if k != "nan" :
            prov_uri= identifier_to_uri(identifier= k.strip(), 
                                        namespace= uri )
            data_catalog.add((dataset_uri, PROV.wasDerivedFrom, prov_uri))
    # add distributions
    dist =str(row['prov:wasDerivedFrom'])
    dist_list= list(prov.split(","))
    for l in dist_list:
        if l != "nan" :
            dist_uri= identifier_to_uri(identifier= k.strip(), 
                                        namespace= uri )
            data_catalog.add((dataset_uri, DCAT.distribution, dist_uri))

for m, row in distributions_df.iterrows():
    distribution_uri= identifier_to_uri(row['dcterms:identifier'],ns)

    # declare distribution
    data_catalog.add((distribution_uri, 
                      RDF.type, DCAT.Distribution))
    
    # add accessURL
    data_catalog.add((distribution_uri, DCAT.accessURL, URIRef(row['dcat:accessURL'])))

    # add format
    data_catalog.add((distribution_uri, DCTERMS.format, literal_or_uri(row['dcterms:format'])))

    # add version
    data_catalog.add((distribution_uri,
                      DCAT.hasCurrentVersion, 
                      literal_or_uri(row['dcat:hasCurrentVersion'])))
    # add modified
    data_catalog.add((distribution_uri,
                      DCTERMS.modified, 
                      Literal(row['dcterms:modified'],datatype= XSD.date)))




data_catalog.serialize(destination= './tests/datacatalog.ttl', format = 'ttl')    

# print(validators.uri.uri("www.example.com"))