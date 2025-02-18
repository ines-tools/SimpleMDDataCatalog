from rdflib import Graph, Namespace, URIRef, Literal, BNode, paths
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD, TIME
# from dcat_model import Dataset, Distribution, Resource
# from typing import List, Union
from validators import uri
import validators
from mdutils.mdutils import MdUtils
from mdutils import Html
from mdutils.tools.Table import Table
from mdutils.tools.Html import Html
import os
import pandas as pd
from SimpleMDDataCatalog.analysis_functions import was_derived_from_graphic, get_data_quality, supply_chain_analysis, create_theme_word_cloud
import pathlib

def extract_org_repo(repo_url=str):
    split_up_list = repo_url.split("/")
    
    org_name = split_up_list[len(split_up_list)-2]
    repo_name= split_up_list[len(split_up_list)-1]

    return org_name, repo_name
        
def anything_known(catalog_graph: Graph, uri=URIRef):
    # checks if any aditional information is known about this resource
    # this will help determine if there will be a dedicated resource to this page
    # or if it will just be a hyperref
    something_is_known= (uri, None, None) in catalog_graph

    return something_is_known

def create_index(catalog_graph: Graph, output_dir: str, repo_url :str = None):
    path = pathlib.Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    catalogs= catalog_graph.subjects(RDF.type, DCAT.Catalog)
    catalog_file_path = output_dir+'catalog.ttl'
    # catalog_graph.serialize(destination=catalog_file_path)
    
    for cat in catalogs:
        catalog_uri=cat
        # print(catalog_uri)


    catalog_title=str(catalog_graph.value(catalog_uri, DCTERMS.title))
    catalog_description=str(catalog_graph.value(catalog_uri, DCTERMS.description))
    index_md = MdUtils(
            file_name=output_dir+'index.md',
            title=catalog_title)
    
    # add description
    index_md.new_header(level=1, title="Description")
    index_md.new_paragraph(text=catalog_description)

    index_md.new_line(index_md.new_inline_link(link= catalog_file_path[5:],text= "The machine readable version of the catalog (ttl) can be found here." ))
    # add publisher
    index_md.new_header(level=2, title="Publisher")
    publisher= catalog_graph.value(catalog_uri, DCTERMS.publisher)
    if type(publisher)==BNode:
        publisher=catalog_graph.value(catalog_uri, DCTERMS.publisher/FOAF.name)
    
    index_md.new_line(str(publisher))
        
        
    # add license
    index_md.new_header(level=2, title="License")
    
    license =catalog_graph.value(catalog_uri, DCTERMS.license)
    
    if type(license)==BNode:
        license=catalog_graph.value(catalog_uri, DCTERMS.license/DCTERMS.title) 



    index_md.new_line(str(license))
    
        



    theme = catalog_graph.objects(catalog_uri, DCAT.theme)
    theme_list= [''] # first entry has to be empty for table to look nice
    for th in theme:
        theme_list.append(get_local_link(th,property=DCTERMS.identifier, label= SKOS.prefLabel, catalog_graph=catalog_graph)) 
    if len(theme_list) == 1:
        theme_list.append('no information available')
    index_md.new_header(level= 2, title='keywords')
    index_md.new_table(columns=1, 
                         rows= len(theme_list),
                         text=theme_list,
                         text_align='left')

        
    

    # datasets per theme
    themes= catalog_graph.subjects(RDF.type, SKOS.Concept)
    
    index_md.new_header(level=1, title= "Datasets organized by theme")
    index_md.new_line("the word cloud gives a sense of the themes that are covered by the datasets in this data catalog.")
    word_cloud= create_theme_word_cloud(catalog_graph=catalog_graph)
    word_cloud_path=str(word_cloud)[5:]
    index_md.new_line(index_md.new_inline_image(text="word cloud of dataset themes and their occurrences",
                                                path=word_cloud_path))
    index_md.new_line('Here you will find datasets organized by theme. The headers of each theme are links you can click to learn more about the definition')
    
    for th in themes :
       
        title = catalog_graph.value(th, SKOS.prefLabel)
        title=get_local_link(th, property=DCTERMS.identifier, label=SKOS.prefLabel, catalog_graph=catalog_graph)
        index_md.new_header(level= 2, title= 'theme: '+title)

        this_themes_datasets= catalog_graph.subjects(DCAT.theme, th)

        for th_ds in this_themes_datasets:
            index_md.new_line(text=get_local_link(uri=th_ds, property=DCTERMS.identifier, label=DCTERMS.title, catalog_graph=catalog_graph))

    index_md.new_header(level=2, title= "About this catalog")

    index_md.new_line("This catalog was generated using the SimpleMDDataCatalog package that is is maintained [here](https://github.com/uuidea/SimpleMDDataCatalog).")
    index_md.new_table_of_contents(depth=2,)
    index_md.create_md_file()

def get_local_link(uri: URIRef, property: URIRef, label: URIRef, catalog_graph= Graph):
    # uri = the uri of the object
    # property = the value upon which the local file's name is based
    #               e.g. for datasets, the local file is named after the dcterms:identifier
    # label  = the value upon which the name of the link is to be based
    #          e.g. for datasets, the local file is named after the dcterms:title 
    #           while for skos:concepts the title is based on skos:prefLabel        
    ds_identifier = str(catalog_graph.value(uri, property))
    ds_title= str(catalog_graph.value(uri, label))
    link= "["+ds_title+"]"+"("+ds_identifier+".md)"
    return link


def parse_catalog(input_file: str):
    catalog_graph = Graph()
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    VCARD=Namespace('http://www.w3.org/2006/vcard/ns#')
    catalog_graph.bind("adms", Namespace(adms_ns))
    catalog_graph.bind("dqv", dqv_ns)
    catalog_graph.bind("vcard",VCARD)

    if input_file != None :
        catalog_graph.parse(input_file)

    return catalog_graph    

def create_dataset_pages(catalog_graph: Graph, output_dir: str):
    graph=catalog_graph
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    VCARD=Namespace('http://www.w3.org/2006/vcard/ns#')
    graph.bind("adms", Namespace(adms_ns))
    catalog_graph.bind("vcard",VCARD)
    for s, p, o in graph.triples((None, RDF.type, DCAT.Dataset)):
        
        identifier = graph.value(s, DCTERMS.identifier)
        title = graph.value(s, DCTERMS.title)
        description = graph.value(s,DCTERMS.description)
       
        # initiate md object
        mdFile = MdUtils(
            file_name=output_dir+identifier,
            title=title)
        # title and description
        mdFile.new_header(level=1  ,title= 'description')
        mdFile.new_line(description)

        mdFile= add_publishing_info(graph=catalog_graph, page=mdFile, resource=s)
        mdFile= add_about_data(graph=catalog_graph, page=mdFile, resource=s)
        
        # data quality
        mdFile=add_data_quality_info(graph=catalog_graph, page=mdFile, resource=s)

        # data lineage
        mdFile= add_lineage_info(graph=catalog_graph, page=mdFile, resource=s)

        # Distributions
        mdFile.new_header(level=2, title='Distributions')
        dist_list= ['identifier', 'format', 'version', 'last modified', 'access url']

        for dist in graph.objects(s, DCAT.distribution):
            access_url= graph.value(dist, DCAT.accessURL)
            
            dist_list= dist_list+ [
                graph.value(dist, DCTERMS.identifier),
                graph.value(dist, DCTERMS.format),
                graph.value(dist, DCAT.version),
                graph.value(dist, DCTERMS.modified),
                "["+ str(access_url)+"]("+str(access_url)+")",
            ]

        mdFile.new_table(columns=5, rows= int(len(dist_list)/5), text= dist_list)

        mdFile.create_md_file()

def create_concept_pages(catalog_graph=Graph,output_dir=str):
    concepts= catalog_graph.subjects(RDF.type, SKOS.Concept)

    for c in concepts:
        title = catalog_graph.value(c, SKOS.prefLabel)
        filename = catalog_graph.value(c, DCTERMS.identifier)
        concept_file = MdUtils(
             file_name=output_dir+filename,
             title=title)
        concept_file.new_header(level= 1, title= 'Preferred Label')
        concept_file.new_line(catalog_graph.value(c, SKOS.prefLabel))
        
        concept_file.new_header(level=1, title= 'uri')
        concept_file.new_line(str(c))


        concept_file.new_header(level= 1, title= 'Definition')
        concept_file.new_line(catalog_graph.value(c, SKOS.definition))

        concept_file.new_header(level= 1, title= 'Examples')
        examples= catalog_graph.objects(c, SKOS.example)
        for e in examples:
            concept_file.new_paragraph(e)

        ## list datasets that have this as a theme

        concept_file.new_header(level= 1, title= 'Datasets that have this concept as a theme')
        datasets = catalog_graph.subjects(DCAT.theme, c)
        for ds in datasets:
            concept_file.new_line(get_local_link(uri=ds, property=DCTERMS.identifier, label= DCTERMS.title, catalog_graph=catalog_graph))
        
        concept_file.create_md_file()


# create datasetseries pages        

def create_metric_pages(catalog_graph=Graph,output_dir=str):
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")

    metrics= catalog_graph.subjects(RDF.type, dqv_ns.Metric)
    for m in metrics:
        m=URIRef(m)
        title = str(catalog_graph.value(m, SKOS.prefLabel))
        filename = str(catalog_graph.value(m, DCTERMS.identifier))
        concept_file = MdUtils(
             file_name=output_dir+filename,
             title=title)
        
        definition= str(catalog_graph.value(m,SKOS.definition))
        
        concept_file.new_header(level=1, title="definition")
        concept_file.new_paragraph(text=definition)
        
        datatype= str(catalog_graph.value(m, dqv_ns.expectedDataType )) 
        dimension= catalog_graph.objects(m, dqv_ns.inDimension)
        dimension_str=str()
        for dim in dimension:
            if len(dimension_str)== 0:
                dimension_str=dimension_str+str(dim)
            else:
                dimension_str=dimension_str+", "+str(dim)
        metrics_list=[
            "expected datatype: "+datatype, 
            "quality dimensions: "+ str(dimension_str)
            ]
        concept_file.new_list(metrics_list)
        

        concept_file.create_md_file()
        

    
def get_lineage(catalog_graph: Graph, dataset=URIRef):
    ds_uri_str=str("<"+dataset+">")

    indirect_lineage_query=("""
    SELECT DISTINCT ?lineage
    WHERE{
        %s prov:wasDerivedFrom* ?lineageds
    }
    """ % (ds_uri_str))

    indirect_lineage=catalog_graph.query(indirect_lineage_query)
    
    
    return indirect_lineage
            
def create_datasetseries_pages(catalog_graph: Graph, output_dir: str):
    """Creates markdown pages for each dataset series in the catalog."""

    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    VCARD=Namespace('http://www.w3.org/2006/vcard/ns#')
    catalog_graph.bind("adms", Namespace(adms_ns))
    catalog_graph.bind("dqv", dqv_ns)
    catalog_graph.bind("vcard",VCARD)

    for s, p, o in catalog_graph.triples((None, RDF.type, DCAT.DatasetSeries)):

        identifier = catalog_graph.value(s, DCTERMS.identifier)
        title = catalog_graph.value(s, DCTERMS.title)
        description = catalog_graph.value(s,DCTERMS.description)
        license = catalog_graph.value(s, DCTERMS.license)
       

        # initiate md object
        mdFile = MdUtils(
            file_name=output_dir+identifier,
            title=title)

        # title and description
        mdFile.new_header(level=1  ,title= 'description')
        mdFile.new_line(description)

        # publisher info

        mdFile= add_publishing_info(graph=catalog_graph, page=mdFile, resource=s)

        # themes
        mdFile= add_themes(graph=catalog_graph, page=mdFile, resource=s)       

       
        # Datasets in series
        mdFile.new_header(level=2, title='Datasets in this Series')
        datasets = catalog_graph.subjects(DCAT.inSeries, s)
        dataset_list=[] 
        for ds in datasets:
            dataset_list.append(get_local_link(uri=ds, property=DCTERMS.identifier, label= DCTERMS.title, catalog_graph=catalog_graph))

        mdFile.new_table(columns=1, 
                         rows= len(dataset_list),
                         text=dataset_list,
                         text_align='left')


        mdFile.create_md_file()


def add_publishing_info(graph= Graph, page= MdUtils, resource= URIRef)-> MdUtils :
    VCARD=Namespace('http://www.w3.org/2006/vcard/ns#')
    # creates a header and a table with publisher and contact info and license 
    license = graph.value(resource, DCTERMS.license)
    if type(license)==BNode:
        license=graph.value(resource, DCTERMS.license/DCTERMS.title)
    publisher = graph.value(resource,DCTERMS.publisher)
    if type(publisher)==BNode:
        publisher=graph.value(resource,DCTERMS.publisher/FOAF.name)
    contactPoint = graph.value(resource ,DCAT.contactPoint)
    if type(contactPoint)==BNode:
        contactPoint=graph.value(resource,DCAT.contactPoint/VCARD.hasEmail)
    
    if publisher ==None:
        publisher= 'unknown'
    if license ==None:
        license= 'unknown'    
    page.new_header(level=2, title='Publisher')
    publisher_list = [
        "", "",
        'Publisher', publisher,
        'Contact', contactPoint,
        'license', license
    ]
    page.new_table(columns=2, 
                    rows= 4, 
                    text=publisher_list,
                    text_align='left')

    return page
   

def add_themes(graph= Graph, page= MdUtils, resource= URIRef)->MdUtils:

    theme = graph.objects(resource, DCAT.theme)
    theme_list= [''] # first entry has to be empty for table to look nice
    for th in theme:
        theme_list.append(get_local_link(th,property=DCTERMS.identifier, label= SKOS.prefLabel, catalog_graph=graph)) 
    if len(theme_list) == 1:
        theme_list.append('no information available')
    page.new_header(level=2, title='keywords')
    page.new_table(columns=1, 
                     rows= len(theme_list),
                     text=theme_list,
                     text_align='left')

    return page

def add_about_data(graph= Graph, page= MdUtils, resource= URIRef)->MdUtils:
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    version = graph.value(resource,DCAT.version)
    status = graph.value(resource,adms_ns.status)
    modified = graph.value(resource,DCTERMS.modified)
    spatial = graph.value(resource,DCTERMS.spatial)
    if type(spatial)== BNode:
        spatial=spatial = graph.value(resource,DCTERMS.spatial/SKOS.prefLabel)
        
    
    temporal_begin = graph.value(resource,DCTERMS.temporal/TIME.hasBeginning)
    temporal_end= graph.value(resource,DCTERMS.temporal/TIME.hasEnd)

    # about dataset
    about_list= ["", "",]

    if modified!=None:
        about_list.extend(["last modified", str(modified) ])
    if spatial != None :
        about_list.extend(["spatial cover", str(spatial)])
    if temporal_begin== None:
        temporal_begin="unknown"
    if temporal_end== None:
        temporal_end="unknown"
    about_list.extend(["temporal cover", str(str(temporal_begin)+ " - "+str(temporal_end))])    
    if version!= None:
        about_list.extend(["version", str(version)])
    if status !=None:
        about_list.extend(["status", str(status)])

    page.new_header(level=2, title='About the data')
    print(about_list)
    
    page.new_table(columns=2, 
                     rows=int(len(about_list)/2), 
                     text=about_list,
                     text_align='left')

    return page

def add_lineage_info(graph= Graph, page= MdUtils, resource= URIRef)->MdUtils:
    wasDerivedFrom = graph.objects(resource,PROV.wasDerivedFrom)
    wdf_list = ['was derived from'] # first entry has to be empty for table to look nice
    has_lineage=True #assume lineage is known
    
    for wdf in wasDerivedFrom:
        
        if anything_known(catalog_graph=graph, uri=wdf):
            wdf_list.append(get_local_link(uri=wdf, property=DCTERMS.identifier, label=DCTERMS.title, catalog_graph=graph))
            
        else :
            wdf_list.append(str(wdf)+': No additional information this dataset was provided.')    
    if len(wdf_list) == 1:
        wdf_list.append('no lineage information available')
        has_lineage=False # lineage is not known
        
    page.new_header(level= 2, title='Data lineage')
    page.new_table(columns=1, 
                     rows= len(wdf_list), 
                     text=wdf_list,
                     text_align='left')
    if len(wdf_list)>1:
        image_path=was_derived_from_graphic(catalog_graph=graph, uri=resource)[5:]
        print(image_path)
        page.new_line(page.new_inline_image(text="Lineage overview", path=image_path))

    if has_lineage:

        page.new_header(level=2, title="supply chain analysis")
        pie_file=supply_chain_analysis(catalog_graph=graph,dataset_uri=resource)
        page.new_line(page.new_inline_image(text="supply chain analysis",path=str(pie_file)[5:]))    

    return page

def add_data_quality_info(graph= Graph, page= MdUtils, resource= URIRef)->MdUtils:
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    page.new_header(level=2, title="Data Quality")
    qm_list= [ "metric", "value", "time of evaluation", "dimension"]
    quality_measurements= get_data_quality(catalog_graph=graph, dataset_uri=resource)
    for qm in quality_measurements:
        metric_link= get_local_link(
            uri= graph.value(qm, dqv_ns.isMeasurementOf), 
            property=DCTERMS.identifier, 
            label= SKOS.prefLabel,
            catalog_graph=graph)
        value= str(graph.value(qm, dqv_ns.value))
        time= str(graph.value(qm, PROV.generatedAtTime))
        dimensions= graph.objects(qm, dqv_ns.isMeasurementOf/dqv_ns.inDimension)
        dimension=str()
        for dim in dimensions:
            
            if len(dimension)==0:
                dimension= dimension+str(dim)
            else:
                dimension= dimension+", "+str(dim)
            
        qm_list= qm_list +[ 
            metric_link,
            value,
            time,
            dimension
        ]
    page.new_table(columns=4, rows= int(len(qm_list)/4), text= qm_list)

    return page

#### testing

# input_file= './tests/datacatalog.ttl'
# output_dir = './docs/'
# repo_url= "https://github.com/uuidea/SimpleMDDataCatalog"
# dataset= URIRef("https://datacatalog.github.io/test_this#73956")


# catalog_graph= parse_catalog(input_file=input_file)
# create_index(catalog_graph= catalog_graph, output_dir=output_dir, repo_url=repo_url)
# create_dataset_pages(catalog_graph=catalog_graph, output_dir=output_dir)
# create_concept_pages(catalog_graph=catalog_graph, output_dir=output_dir)
# get_lineage(catalog_graph=catalog_graph, dataset=dataset)
# create_metric_pages(catalog_graph=catalog_graph, output_dir=output_dir)





# input_file= './tests/datacatalog.ttl'
# uri="https://datacatalog.github.io/test_this#73956"
# catalog_graph= parse_catalog(input_file=input_file)
# print(was_derived_from_graphic(catalog_graph=catalog_graph, uri=uri))



