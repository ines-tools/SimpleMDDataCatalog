from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD
# from dcat_model import Dataset, Distribution, Resource
# from typing import List, Union
from mdutils.mdutils import MdUtils
from mdutils import Html
from mdutils.tools.Table import Table
import os
import pandas as pd

def extract_org_repo(repo_url=str):
    split_up_list = repo_url.split("/")
    
    org_name = split_up_list[len(split_up_list)-2]
    repo_name= split_up_list[len(split_up_list)-1]

    return org_name, repo_name
        

def create_index(catalog_graph: Graph, output_dir: str, repo_url :str = None):
    repo_name= extract_org_repo(repo_url=repo_url)
    os.makedirs(output_dir, exist_ok=True)
    index_md = MdUtils(
            file_name=output_dir+'index',
            title=repo_name[1]+' Data Catalog Overview')
    

    # datasets per theme
    themes= catalog_graph.objects(None, DCAT.theme)
    
    index_md.new_header(level=1, title= "Datasets organized by theme")

    for th in themes :
        
        index_md.new_header(level= 2, title= th)

        this_themes_datasets= catalog_graph.subjects(DCAT.theme, th)

        for th_ds in this_themes_datasets:
            ds_identifier = data_catalog.value(th_ds, DCTERMS.identifier)
            ds_title= data_catalog.value(th_ds, DCTERMS.title)
            
            index_md.new_line(text=index_md.new_inline_link(link=ds_identifier+'.md', text=ds_title))


    index_md.create_md_file()

    
    


def parse_catalog(input_file: str):
    os.makedirs(output_dir, exist_ok=True) 
    graph = Graph()
    adms_ns= Namespace("http://www.w3.org/ns/adms#")
    graph.bind("adms", Namespace(adms_ns))

    if input_file != None :
        graph.parse(input_file)

    return graph     

def create_dataset_pages(catalog_graph: Graph, output_dir: str):
    graph=catalog_graph
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
            theme_list.append(th) 

            
        wasDerivedFrom = graph.objects(s,PROV.wasDerivedFrom)
        wdf_list = ['was derived from'] # first entry has to be empty for table to look nice
        
        for wdf in wasDerivedFrom:
            wdf_list.append(wdf)
        if len(wdf_list) == 1:
            wdf_list.append('no information available')
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

        mdFile.new_header(level= 2, title='Data lineage')
        mdFile.new_table(columns=1, 
                         rows= len(wdf_list), 
                         text=wdf_list,
                         text_align='left')

        # license
        mdFile.new_header(level= 2, title='License')
        mdFile.new_paragraph(license)
        
        

        # Distributions
        mdFile.new_header(level=2, title='Distributions')
        dist_list= ['identifier', 'format', 'version', 'last modified', 'access url']

        for dist in graph.objects(s, DCAT.distribution):
            access_url= graph.value(dist, DCAT.accessURL)
            print(access_url)
            dist_list= dist_list+ [
                graph.value(dist, DCTERMS.identifier),
                graph.value(dist, DCTERMS.format),
                graph.value(dist, DCAT.version),
                graph.value(dist, DCTERMS.modified),
                access_url,
            ]
        # print(dist_list)
        # print(len(dist_list))
        mdFile.new_table(columns=5, rows= int(len(dist_list)/5), text= dist_list)

        mdFile.create_md_file()

            


   
#### testing

input_file= './tests/datacatalog.ttl'
output_dir = './docs/'
repo_url= "https://github.com/uuidea/SimpleMDDataCatalog"
# parse_catalog(input_file=input_file, output_dir= output_dir)

data_catalog= parse_catalog(input_file=input_file)
create_index(catalog_graph= data_catalog, output_dir=output_dir, repo_url=repo_url)




