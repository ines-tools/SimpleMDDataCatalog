import pandas as pd
from validators import uri
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD
from uri_handling import literal_or_uri, identifier_to_uri, str_abbrev_namespace_to_full_namespace



def spreadsheet_to_ld_catalog(input_sheet: str, uri: str, output_graph) -> Graph:

    uri=Namespace(uri)
    datasets_df = pd.read_excel(input_sheet, 'Datasets', converters={'dcterms:identifier': str, 'prov:wasDerivedFrom':str, 'dcat:distrbution':str})
    distributions_df = pd.read_excel(input_sheet, 'Distributions')
    concepts_df= pd.read_excel(input_sheet, 'Concepts')
    metrics_df= pd.read_excel(input_sheet, 'Metrics')
    quality_measurements_df = pd.read_excel(input_sheet, 'QualityMeasurements')

    ns=Namespace(uri)

    data_catalog = Graph()
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    data_catalog.bind("adms", Namespace(adms_ns))
    data_catalog.bind("dqv", dqv_ns)

    # start with concepts so we can rely on rdf graph navigation to match themes
    for n, row in concepts_df.iterrows():
        identifier= row['dcterms:identifier']
        concept_uri= identifier_to_uri(identifier, ns)
        data_catalog.add((concept_uri, RDF.type, SKOS.Concept))
        data_catalog.add((concept_uri, DCTERMS.identifier, Literal(identifier)))
        pref_label= row['skos:prefLabel']
        data_catalog.add((concept_uri, SKOS.prefLabel, Literal(pref_label)))
        definition= row["skos:definition"]
        data_catalog.add((concept_uri, SKOS.definition, Literal(definition)))

        example = row['skos:example']
        if type(example)== str: # this is hacky
            data_catalog.add((concept_uri, SKOS.example, Literal(example)))


    for i, row in datasets_df.iterrows():
        dataset_uri= identifier_to_uri(row['dcterms:identifier'],ns)

        # declare dataset
        data_catalog.add((dataset_uri,RDF.type, DCAT.Dataset))

        #add identifier

        data_catalog.add((dataset_uri, DCTERMS.identifier, Literal(row['dcterms:identifier'])))

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
                        DCAT.version, 
                        literal_or_uri(row['dcat:version'])))
        # add themes
        theme_list= list(row['dcat:theme'].split(","))
        for j in theme_list:
            j= j.lstrip()
            theme= literal_or_uri(j)
            if type(theme)==Literal:
                theme_uri=data_catalog.value(predicate= SKOS.prefLabel, object=theme)
                
                if theme_uri==None:
                    print('Warning: \''+ theme +'\' has not been defined in the concepts and will be ignored as a theme')
                else :
                    data_catalog.add((dataset_uri, DCAT.theme, theme_uri))     
            elif type(theme)==URIRef:
                data_catalog.add((dataset_uri, DCAT.theme, theme)) 


            # data_catalog.add((dataset_uri,
            #                 DCAT.theme,
            #                 literal_or_uri(j.strip())))
        
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
        
        # add modified
        data_catalog.add((dataset_uri,
                        DCTERMS.modified, 
                        Literal(row['dcterms:modified'],datatype= XSD.date)))
        
        # add provenance
        prov =str(row['prov:wasDerivedFrom'])
        prov_list= list(prov.split(","))
        for k in prov_list:
            if k != "nan" :
                prov_uri= identifier_to_uri(identifier= k.strip(), 
                                            namespace= uri )
                data_catalog.add((dataset_uri, PROV.wasDerivedFrom, prov_uri))
        # add distributions
        dist =str(row['dcat:distribution'])
        dist_list= list(dist.split(","))
        for l in dist_list:
            if l != "nan" :
                dist_uri= identifier_to_uri(identifier= l.strip(), 
                                            namespace= uri )
                data_catalog.add((dataset_uri, DCAT.distribution, dist_uri))

    for m, row in distributions_df.iterrows():
        distribution_uri= identifier_to_uri(row['dcterms:identifier'],ns)

        # declare distribution
        data_catalog.add((distribution_uri, 
                        RDF.type, DCAT.Distribution))
        
        # add identifier
        data_catalog.add((distribution_uri, DCTERMS.identifier, Literal(str(row['dcterms:identifier']))))
        
        # add accessURL
        data_catalog.add((distribution_uri, DCAT.accessURL, Literal(row['dcat:accessURL'])))

        # add format
        data_catalog.add((distribution_uri, DCTERMS.format, literal_or_uri(row['dcterms:format'])))

        # add version
        data_catalog.add((distribution_uri,
                        DCAT.version, 
                        literal_or_uri(row['dcat:version'])))
        # add modified
        data_catalog.add((distribution_uri,
                        DCTERMS.modified, 
                        Literal(row['dcterms:modified'],datatype= XSD.date)))
        
    for n , row in metrics_df.iterrows():
        # print(row['dcterms:identifier'])
        metrics_uri= identifier_to_uri(row['dcterms:identifier'], ns)
        data_catalog.add((metrics_uri,RDF.type, dqv_ns.Metric))
        data_catalog.add((metrics_uri,SKOS.prefLabel, Literal(row['skos:prefLabel'])))
        data_catalog.add((metrics_uri, SKOS.definition, Literal(row['skos:definition'])))
        # print(row['dqv:expectedDataType'])
        datatype=URIRef(str_abbrev_namespace_to_full_namespace(row['dqv:expectedDataType']))
        data_catalog.add((metrics_uri, dqv_ns.expectedDataType,datatype))
        quality_dimension=URIRef(str_abbrev_namespace_to_full_namespace(row['dqv:inDimension']))
        data_catalog.add((metrics_uri, dqv_ns.inDimension, quality_dimension))

    for o, row in quality_measurements_df.iterrows():
        qm_uri= identifier_to_uri(row['dcterms:identifier'], ns)
        data_catalog.add((qm_uri,RDF.type, dqv_ns.QualityMeasurement))
        data_catalog.add((qm_uri, dqv_ns.computedOn , identifier_to_uri(row['dqv:computedOn'],ns) ))
        metric_uri=identifier_to_uri(row['dqv:isMeasurementOf'], ns)
        data_catalog.add((qm_uri, dqv_ns.isMeasurementOf, metric_uri))
        data_catalog.add((qm_uri, dqv_ns.value, Literal(row['dqv:value']))) # ,datatype= data_catalog.value(metric_uri, dqv_ns.expectedDataType) the datatype is obtained by looking at the expected datatype of the metric
        data_catalog.add((qm_uri, PROV.generatedAtTime, Literal(row['prov:generatedAtTime'], datatype= 'xsd:dateTime')))




    data_catalog.serialize(destination= output_graph, format = 'ttl') 


    return data_catalog


uri="https://datacatalog.github.io/test_this#"
input_sheet= './tests/example_spreadsheet.xlsx'
output_graph= './tests/datacatalog.ttl'
spreadsheet_to_ld_catalog(input_sheet=input_sheet, uri=uri, output_graph=output_graph)