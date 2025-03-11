import pandas as pd
from validators import uri
import validators
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD, TIME
from SimpleMDDataCatalog.uri_handling import literal_or_uri, identifier_to_uri, str_abbrev_namespace_to_full_namespace #SimpleMDDataCatalog.
import pathlib

def spreadsheet_to_ld_catalog(uri: str, output_graph: str= 'docs/catalog.ttl', input_sheet: str='catalog.xlsx') -> Graph:
    path = pathlib.Path("docs/")
    path.mkdir(parents=True, exist_ok=True)

    uri=Namespace(uri)
    datasets_df = pd.read_excel(input_sheet, 'Datasets', 
                                converters={'dcterms:identifier': str, 
                                            'prov:wasDerivedFrom':str, 
                                            'dcat:distrbution':str, 
                                            'dcterms:temporal/time:hasBeginning': str,
                                            'dcterms:temporal/time:hasEnd': str, 
                                            'dcterms:publisher': str })
    distributions_df = pd.read_excel(input_sheet, 'Distributions')
    concepts_df= pd.read_excel(input_sheet, 'Concepts')
    metrics_df= pd.read_excel(input_sheet, 'Metrics')
    quality_measurements_df = pd.read_excel(input_sheet, 'QualityMeasurements')
    data_catalog_df =pd.read_excel(input_sheet, 'DataCatalog')
    dataset_series_df = pd.read_excel(input_sheet, 'DatasetSeries')
    odrl_ns=Namespace('http://www.w3.org/ns/odrl/2/')

    ns=Namespace(uri)

    data_catalog = Graph()
    VCARD=Namespace('http://www.w3.org/2006/vcard/ns#')
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    data_catalog.bind("adms", Namespace(adms_ns))
    data_catalog.bind("dqv", dqv_ns)
    data_catalog.bind("vcard", VCARD)
    data_catalog.bind('odrl', odrl_ns)
    
    # start with concepts so we can rely on rdf graph navigation to match themes
    for n, row in concepts_df.iterrows():
        if str(row['dcterms:identifier'])=='nan':
            raise Exception("Concepts must have an identifier")
        if str(row['skos:prefLabel'])=='nan':
            raise Exception("Concepts must have a prefLabel")
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
    
    # adding data catalog
    if len(data_catalog_df.index)>1:
        print("WARNING: Spreadsheet contains more than 1 entry for data catalog, only the first entry is used")
       
    identifier= data_catalog_df.iloc[0]['dcterms:identifier']
    if identifier=='nan':
        raise Exception("error: the data catalog must have an identifier")
    
    catalog_uri= identifier_to_uri(identifier=identifier, namespace= ns)
    title= data_catalog_df.iloc[0]['dcterms:title']
    if title=='nan':
        raise Exception("error: the data catalog must have a title")
    description= data_catalog_df.iloc[0]['dcterms:description']
    license =data_catalog_df.iloc[0]['dcterms:license']
    publisher= str(data_catalog_df.iloc[0]['dcterms:publisher'])
    
    themes= data_catalog_df.iloc[0]['dcat:theme']

    data_catalog.add((catalog_uri, RDF.type, DCAT.Catalog))
    data_catalog.add((catalog_uri, DCTERMS.title, Literal(title)))
    data_catalog.add((catalog_uri, DCTERMS.description, Literal(description)))
            # add publisher, it its is a uri, add it, if its a name, create a blank node and add properties
    publisher_bnode=BNode()
    if str(publisher)!= 'nan':
        if validators.uri.uri(str(publisher)):
            data_catalog.add((catalog_uri,
                        DCTERMS.publisher, 
                        literal_or_uri(publisher)))
        else:
            data_catalog.add((catalog_uri, DCTERMS.publisher, publisher_bnode))
            data_catalog.add((publisher_bnode, RDF.type, FOAF.Agent))
            data_catalog.add((publisher_bnode, FOAF.name, Literal(publisher, datatype=str)))

    if str(license)!= 'nan':
            license_bnode=BNode()
            
            if validators.uri.uri(str(license)):
                data_catalog.add((dataset_uri,
                        DCTERMS.license, 
                        literal_or_uri(str(license))))
            else :
                data_catalog.add((catalog_uri, DCTERMS.license, license_bnode))
                data_catalog.add((license_bnode, RDF.type, DCTERMS.LicenseDocument))
                data_catalog.add((license_bnode, DCTERMS.title, Literal(license)))    
    
    theme_list= list(themes.split(","))
    for j in theme_list:
        j= j.lstrip()
        theme= literal_or_uri(j)
        if type(theme)==Literal:
            theme_uri=data_catalog.value(predicate= SKOS.prefLabel, object=theme)
            
            if theme_uri==None:
                print('Warning: \''+ theme +'\' has not been defined in the concepts and will be ignored as a theme')
            else :
                data_catalog.add((catalog_uri, DCAT.theme, theme_uri))     
        elif type(theme)==URIRef:
            data_catalog.add((catalog_uri, DCAT.theme, theme))   

    for i, row in datasets_df.iterrows():

        if str(row['dcterms:identifier'])=='nan':
            raise Exception("ERROR: Datasets must have an identifier")
        dataset_uri= identifier_to_uri(row['dcterms:identifier'],ns)

        # add that this dataset is in the catalog
        data_catalog.add((catalog_uri, DCAT.resource, dataset_uri))

        # declare dataset
        data_catalog.add((dataset_uri,RDF.type, DCAT.Dataset))

        #add identifier

        data_catalog.add((dataset_uri, DCTERMS.identifier, Literal(row['dcterms:identifier'])))

        # add title
        if str(row['dcterms:title'])=='nan':
            raise Exception("ERROR: Datasets must have a Title")
        data_catalog.add((dataset_uri,
                        DCTERMS.title, 
                        Literal(row['dcterms:title'])))
        # add description
        data_catalog.add((dataset_uri,
                        DCTERMS.description, 
                        Literal(row['dcterms:description'])))
        # add publisher, it its is a uri, add it, if its a name, create a blank node and add properties
        publisher_bnode=BNode()

        if row['dcterms:publisher']!= 'nan':
            if validators.uri.uri(str(row['dcterms:publisher'])):
                data_catalog.add((dataset_uri,
                            DCTERMS.publisher, 
                            literal_or_uri(row['dcterms:publisher'])))
            else:
                data_catalog.add((dataset_uri, DCTERMS.publisher, publisher_bnode))
                data_catalog.add((publisher_bnode, RDF.type, FOAF.Agent))
                data_catalog.add((publisher_bnode , FOAF.name, Literal(row['dcterms:publisher'])))    
        # add  contactPoint
        cp=BNode()
        if row['dcat:contactPoint'] !='nan':
            if validators.uri.uri(str(row['dcat:contactPoint'])):
                data_catalog.add((dataset_uri,
                        DCAT.contactPoint, 
                        Literal(row['dcat:contactPoint'] )))
            else:
                data_catalog.add((dataset_uri, DCAT.contactPoint, cp))
                data_catalog.add((cp,RDF.type, VCARD.Kind))
                data_catalog.add((cp, VCARD.hasEmail, Literal(row['dcat:contactPoint']) ))

        # data_catalog.add((dataset_uri,
        #                 DCAT.contactPoint, 
        #                 literal_or_uri(row['dcat:contactPoint'])))
        
        # add license

        if str(row['dcterms:license'])!= 'nan':
            license_bnode=BNode()
            
            if validators.uri.uri(str(row['dcterms:license'])):
                data_catalog.add((dataset_uri,
                        DCTERMS.license, 
                        literal_or_uri(str(row['dcterms:license']))))
            else :
                data_catalog.add((dataset_uri, DCTERMS.license, license_bnode))
                data_catalog.add((license_bnode, RDF.type, DCTERMS.LicenseDocument))
                data_catalog.add((license_bnode, DCTERMS.title, Literal(row['dcterms:license'])))    
        # add version

        if str(row['dcat:version'])!='nan':
            data_catalog.add((dataset_uri,
                        DCAT.version, 
                        literal_or_uri(row['dcat:version'])))
        # add themes
        
        if str(row['dcat:theme'])!= 'nan':
            theme_list= list((str(row['dcat:theme']).split(",")))
        
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
        if str(row['dcterms:spatial']) != 'nan':
            

            if validators.uri.uri(str(row['dcterms:spatial'])):
                data_catalog.add((dataset_uri,
                                  DCTERMS.spatial, 
                                  URIRef(row['dcterms:spatial'])))
                data_catalog.add((URIRef(row['dcterms:spatial'],
                                         RDF.type, DCTERMS.Location)))
            else :    
                # create blank node give it type location and a preflabel
                sbn=BNode() 
                data_catalog.add((dataset_uri,DCTERMS.spatial, sbn)) 
                data_catalog.add((sbn, RDF.type, DCTERMS.Location))
                
                data_catalog.add((sbn, SKOS.prefLabel, 
                            Literal(row['dcterms:spatial'])))

        # add temporal 
        tbn= BNode()
        if str(row['dcterms:temporal/time:hasBeginning']) != 'nan':
            data_catalog.add((dataset_uri,
                        DCTERMS.temporal, 
                        tbn))
            data_catalog.add((tbn, RDF.type, DCTERMS.PeriodOfTime))
            data_catalog.add((tbn, TIME.hasBeginning, Literal(str(row['dcterms:temporal/time:hasBeginning']))))
        if str(row['dcterms:temporal/time:hasEnd']) != 'nan':
            data_catalog.add((dataset_uri,
                        DCTERMS.temporal, 
                        tbn))
            data_catalog.add((tbn, RDF.type, DCTERMS.PeriodOfTime))
            data_catalog.add((tbn, TIME.hasEnd, Literal(row['dcterms:temporal/time:hasEnd'])))

        # add status
        if str(row['adms:status']) != 'nan':
            data_catalog.add((dataset_uri,
                        adms_ns.status, 
                        literal_or_uri(row['adms:status'])))
        
        # add modified

        if str(row['dcterms:modified']) != 'NaT':
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
        # add distributions this one will be deprecated, and be replaced by a relationship defined in the distributions
        if 'dcat:distribution' in row:
            dist =str(row['dcat:distribution'])
            dist_list= list(dist.split(","))
            for l in dist_list:
                if l != "nan" :
                    dist_uri= identifier_to_uri(identifier= l.strip(), 
                                                namespace= uri )
                    data_catalog.add((dataset_uri, DCAT.distribution, dist_uri))

        if 'dcat:inSeries' in row:
            data_catalog.add((dataset_uri, DCAT.inSeries, identifier_to_uri(row['dcat:inSeries'], namespace=ns)))

        if 'odrl:hasPolicy' in row:
            pbn = BNode() #add blank node for policy
            data_catalog.add((dataset_uri, odrl_ns, pbn))
            data_catalog.add((pbn, RDF.type, odrl_ns.Policy))
            data_catalog.add((pbn, DCTERMS.title, row['odrl:hasPolicy']))




    for m, row in distributions_df.iterrows():
        distribution_uri= identifier_to_uri(row['dcterms:identifier'],ns)

        # declare distribution
        data_catalog.add((distribution_uri, 
                        RDF.type, DCAT.Distribution))
        
        # add identifier
        data_catalog.add((distribution_uri, DCTERMS.identifier, Literal(str(row['dcterms:identifier']))))

        # add title
        if str(row['dcterms:title']) != 'nan':
            data_catalog.add((distribution_uri, DCTERMS.title,Literal(str(row['dcterms:title']))))

        # add description
        if str(row['dcterms:description']) != 'nan':
            data_catalog.add((distribution_uri, DCTERMS.title,Literal(str(row['dcterms:description']))))    

        
        # add accessURL
        if str(row['dcat:accessURL']) != 'nan':
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
        
        # add distributions

        if 'inv-dcat:distribution' in row:
            data_catalog.add((URIRef(identifier_to_uri(identifier=row['inv-dcat:distribution'],namespace=ns)),DCAT.distribution, distribution_uri))
        

        
    for n , row in metrics_df.iterrows():
        
        identifier= row['dcterms:identifier']
        metrics_uri= identifier_to_uri(identifier, ns)
        data_catalog.add((metrics_uri,RDF.type, dqv_ns.Metric))
        data_catalog.add((metrics_uri, DCTERMS.identifier, Literal(identifier)))
        data_catalog.add((metrics_uri,SKOS.prefLabel, Literal(row['skos:prefLabel'])))
        data_catalog.add((metrics_uri, SKOS.definition, Literal(row['skos:definition'])))
        
        datatype=URIRef(str_abbrev_namespace_to_full_namespace(row['dqv:expectedDataType']))
        data_catalog.add((metrics_uri, dqv_ns.expectedDataType, datatype))
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


    for n, row in dataset_series_df.iterrows():
        if str(row['dcterms:identifier'])=='nan':
            raise Exception("ERROR: DataSeries must have an identifier")
        series_uri = identifier_to_uri(row['dcterms:identifier'], ns)

        # declare DataSeries
        data_catalog.add((series_uri, RDF.type, DCAT.DatasetSeries))

        # add identifier
        data_catalog.add((series_uri, DCTERMS.identifier, Literal(row['dcterms:identifier'])))

        # add title
        if str(row['dcterms:title'])=='nan':
            raise Exception("ERROR: DataSeries must have a Title")
        data_catalog.add((series_uri, DCTERMS.title, Literal(row['dcterms:title'])))

        # add description
        if str(row['dcterms:description'])!='nan':
            data_catalog.add((series_uri, DCTERMS.description, Literal(row['dcterms:description'])))

        # add publisher (if applicable)
        publisher_bnode = BNode()
        if row['dcterms:publisher'] != 'nan':
            if validators.uri.uri(str(row['dcterms:publisher'])):
                data_catalog.add((series_uri, DCTERMS.publisher, literal_or_uri(row['dcterms:publisher'])))
            else:
                data_catalog.add((series_uri, DCTERMS.publisher, publisher_bnode))
                data_catalog.add((publisher_bnode, RDF.type, FOAF.Agent))
                data_catalog.add((publisher_bnode, FOAF.name, Literal(row['dcterms:publisher'])))

        cp=BNode()
        if row['dcat:contactPoint'] !='nan':
  
            if validators.uri.uri(str(row['dcat:contactPoint'])):
                data_catalog.add((series_uri,
                        DCAT.contactPoint, 
                        Literal(row['dcat:contactPoint'] )))
            else:
                data_catalog.add((series_uri, DCAT.contactPoint, cp))
                data_catalog.add((cp,RDF.type, VCARD.Kind))
                data_catalog.add((cp, VCARD.hasEmail, Literal(row['dcat:contactPoint']) ))

        # data_catalog.add((dataset_uri,
        #                 DCAT.contactPoint, 
        #                 literal_or_uri(row['dcat:contactPoint'])))
        
        # add license

        if str(row['dcterms:license'])!= 'nan':
            license_bnode=BNode()
            
            if validators.uri.uri(str(row['dcterms:license'])):
                data_catalog.add((series_uri,
                        DCTERMS.license, 
                        literal_or_uri(str(row['dcterms:license']))))
            else :
                data_catalog.add((series_uri, DCTERMS.license, license_bnode))
                data_catalog.add((license_bnode, RDF.type, DCTERMS.LicenseDocument))
                data_catalog.add((license_bnode, DCTERMS.title, Literal(row['dcterms:license'])))   


        if str(row['dcat:theme']) != 'nan':
            # Convert the theme string to a list of themes, splitting by commas
            theme_list = [str(item).strip() for item in str(row['dcat:theme']).split(",")]

            for j in theme_list:
                # Strip any leading whitespace from each theme
                j = j.lstrip()

                # Determine if the theme is a literal or URI reference
                theme = literal_or_uri(j)

                # Check if the theme is a Literal
                if isinstance(theme, Literal):
                    # Look up the URI for the theme using its preferred label
                    theme_uri = data_catalog.value(predicate=SKOS.prefLabel, object=theme)

                    # If the theme URI is not found, print a warning and ignore it as a theme
                    if theme_uri is None:
                        print('Warning: \'' + str(theme) + '\' has not been defined in the concepts and will be ignored as a theme')
                    else:
                        # Add the theme URI to the data catalog for the given series
                        data_catalog.add((series_uri, DCAT.theme, theme_uri))

                # Check if the theme is a URI reference
                elif isinstance(theme, URIRef):
                    # If it is a URI reference, directly add it as a theme to the data catalog
                    data_catalog.add((series_uri, DCAT.theme, theme))

    data_catalog.serialize(destination= output_graph, format = 'ttl') 


    return data_catalog

