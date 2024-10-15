import rdflib

def parse_catalog(input_file: str):
    graph = Graph()

    if input_file != None :
        graph.parse(input_file)  

    dataset_query= """select distinct ?dataset  ?title ?license ?identifier ?publisher ?contactPoint ?hasCurrentVersion ?theme ?distribution ?spatial ?temporal where {{

        ?dataset a dcat:Dataset .
        OPTIONAL{{
            ?dataset dcterms:title ?title .
            ?dataset dcterms:license ?license .
            ?dataset dcterms:identifier ?identifier .
            ?dataset dcterms:publisher ?publisher .
            ?dataset dcat:contactPoint ?contactPoint .
            ?dataset dcat:hashasCurrentVersion ?hasCurrentVersion .
            ?dataset dcat:theme ?theme .
            ?dataset dcat:distribution ?distribution .
            ?dataset dcterms:spatial ?spatial .
            ?dataset dcterms:temporal ?temporal .
        }}

    }}"""    



#### testing


