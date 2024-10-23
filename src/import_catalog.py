from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD
# from dcat_model import Dataset, Distribution, Resource
# from typing import List, Union
from mdutils.mdutils import MdUtils
from mdutils import Html
from mdutils.tools.Table import Table
from mdutils.tools.Html import Html
import os
import pandas as pd
from analysis_functions import was_derived_from_graphic, get_data_quality

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
    repo_name= extract_org_repo(repo_url=repo_url)
    os.makedirs(output_dir, exist_ok=True)
    index_md = MdUtils(
            file_name=output_dir+'index',
            title=repo_name[1]+' Data Catalog Overview')
    

    # datasets per theme
    themes= catalog_graph.subjects(RDF.type, SKOS.Concept)
    
    index_md.new_header(level=1, title= "Datasets organized by theme")

    index_md.new_line('Here you will find datasets organized by theme. The headers of each theme are links you can click to learn more about the definition')

    for th in themes :
       
        title = catalog_graph.value(th, SKOS.prefLabel)
        title=get_local_link(th, property=DCTERMS.identifier, label=SKOS.prefLabel)
        index_md.new_header(level= 2, title= title)

        this_themes_datasets= catalog_graph.subjects(DCAT.theme, th)

        for th_ds in this_themes_datasets:
           
            index_md.new_line(text=get_local_link(uri=th_ds, property=DCTERMS.identifier, label=DCTERMS.title))

    index_md.new_header(level=2, title= "About this catalog")

    index_md.new_line("This catalog was generated using the SimpleMDDataCatalog package that is is maintained [here](https://github.com/uuidea/SimpleMDDataCatalog).")

    index_md.create_md_file()

def get_local_link(uri: URIRef, property: URIRef, label: URIRef):
    # uri = the uri of the object
    # property = the value upon which the local file's name is based
    #               e.g. for datasets, the local file is named after the dcterms:identifier
    # label  = the value upon which the name of the link is to be based
    #          e.g. for datasets, the local file is named after the dcterms:title 
    #           while for skos:concepts the title is based on skos:prefLabel        
    ds_identifier = data_catalog.value(uri, property)
    ds_title= data_catalog.value(uri, label)
    link= "["+ds_title+"]"+"("+ds_identifier+".md)"
    return link

    


def parse_catalog(input_file: str):
    data_catalog = Graph()
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    data_catalog.bind("adms", Namespace(adms_ns))
    data_catalog.bind("dqv", dqv_ns)

    if input_file != None :
        data_catalog.parse(input_file)

    return data_catalog    

def create_dataset_pages(catalog_graph: Graph, output_dir: str):
    graph=catalog_graph
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    graph.bind("adms", Namespace(adms_ns))
    for s, p, o in graph.triples((None, RDF.type, DCAT.Dataset)):
        
        identifier = graph.value(s, DCTERMS.identifier)
        title = graph.value(s, DCTERMS.title)
        description = graph.value(s,DCTERMS.description)
        license = graph.value(s, DCTERMS.license)
        publisher = graph.value(s,DCTERMS.publisher)
        contactPoint = graph.value(s,DCAT.contactPoint)
        version = graph.value(s,DCAT.version)
        status = graph.value(s,adms_ns.status)
        modified = graph.value(s,DCTERMS.modified)
        spatial = graph.value(s,DCTERMS.spatial)
        temporal = graph.value(s,DCTERMS.temporal)

        theme = graph.objects(s, DCAT.theme)
        theme_list= [''] # first entry has to be empty for table to look nice
        for th in theme:
            theme_list.append(get_local_link(th,property=DCTERMS.identifier, label= SKOS.prefLabel)) 
        if len(theme_list) == 1:
            theme_list.append('no information available')
         

            
        
        # initiate md object
        mdFile = MdUtils(
            file_name=output_dir+identifier,
            title=title)
        # title and description
        mdFile.new_header(level=1  ,title= 'description')
        mdFile.new_line(description)

        # theme
        mdFile.new_header(level= 2, title='keywords')
        mdFile.new_table(columns=1, 
                         rows= len(theme_list),
                         text=theme_list,
                         text_align='left')

        # status
        mdFile.new_header(level=2, title='Status')
        mdFile.new_paragraph(status)

        # publisher info

        mdFile.new_header(level=2, title='Publisher')
        publisher_list = [
            "", "",
            'Publisher', publisher,
            'Contact', contactPoint,
        ]
        mdFile.new_table(columns=2, 
                         rows= 3, 
                         text=publisher_list,
                         text_align='left')
        
        # about dataset

        mdFile.new_header(level=2, title='About the data')
        about_list= ["", "",
                     "last modified", modified, 
                     "spatial cover", spatial,
                     "temporal cover", temporal,
                     "version", version
                     ]
        mdFile.new_table(columns=2, 
                         rows=int(len(about_list)/2), 
                         text=about_list,
                         text_align='left')

    

        # lineage

        wasDerivedFrom = graph.objects(s,PROV.wasDerivedFrom)
        wdf_list = ['was derived from'] # first entry has to be empty for table to look nice
        
        for wdf in wasDerivedFrom:
            
            if anything_known(catalog_graph=catalog_graph, uri=wdf):
                wdf_list.append(get_local_link(uri=wdf, property=DCTERMS.identifier, label=DCTERMS.title))
            else :
                wdf_list.append(str(wdf)+': No additional information this dataset was provided.')    
        if len(wdf_list) == 1:
            wdf_list.append('no lineage information available')

        mdFile.new_header(level= 2, title='Data lineage')
        mdFile.new_table(columns=1, 
                         rows= len(wdf_list), 
                         text=wdf_list,
                         text_align='left')
        if len(wdf_list)>1:
            image_path=was_derived_from_graphic(data_catalog=data_catalog, uri=s)[2:]
            mdFile.new_line(mdFile.new_inline_image(text="Lineage overview", path=image_path))

        # license
        mdFile.new_header(level= 2, title='License')
        mdFile.new_paragraph(license)
        
        

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


        # data quality
        mdFile.new_header(level=2, title="Data Quality")
        qm_list= [ "metric", "value", "time of evaluation", "dimension"]

        quality_measurements= get_data_quality(data_catalog=data_catalog, dataset_uri=s)
        for qm in quality_measurements:
            metric_link= get_local_link(
                uri= data_catalog.value(qm, dqv_ns.isMeasurementOf), 
                property=DCTERMS.identifier, 
                label= SKOS.prefLabel)
            value= str(data_catalog.value(qm, dqv_ns.value))
            time= str(data_catalog.value(qm, PROV.generatedAtTime))
            dimensions= data_catalog.objects(qm, dqv_ns.isMeasurementOf/dqv_ns.inDimension)
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
        mdFile.new_table(columns=4, rows= int(len(qm_list)/4), text= qm_list)


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
            concept_file.new_line(get_local_link(uri=ds, property=DCTERMS.identifier, label= DCTERMS.title))
        
        concept_file.create_md_file()

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
        

    
def get_lineage(data_catalog: Graph, dataset=URIRef):
    ds_uri_str=str("<"+dataset+">")

    indirect_lineage_query=("""
    SELECT DISTINCT ?lineage
    WHERE{
        %s prov:wasDerivedFrom* ?lineageds
    }
    """ % (ds_uri_str))

    indirect_lineage=data_catalog.query(indirect_lineage_query)
    
    
    return indirect_lineage
            


   
#### testing

input_file= './tests/datacatalog.ttl'
output_dir = './docs/'
repo_url= "https://github.com/uuidea/SimpleMDDataCatalog"
dataset= URIRef("https://datacatalog.github.io/test_this#73956")


data_catalog= parse_catalog(input_file=input_file)
create_index(catalog_graph= data_catalog, output_dir=output_dir, repo_url=repo_url)
create_dataset_pages(catalog_graph=data_catalog, output_dir=output_dir)
create_concept_pages(catalog_graph=data_catalog, output_dir=output_dir)
get_lineage(data_catalog=data_catalog, dataset=dataset)
create_metric_pages(catalog_graph=data_catalog, output_dir=output_dir)




# input_file= './tests/datacatalog.ttl'
# uri="https://datacatalog.github.io/test_this#73956"
# data_catalog= parse_catalog(input_file=input_file)
# print(was_derived_from_graphic(data_catalog=data_catalog, uri=uri))



