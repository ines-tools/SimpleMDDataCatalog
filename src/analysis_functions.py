# from import_catalog import parse_catalog
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import FOAF, DCTERMS, DCAT, PROV, OWL, RDFS, RDF, XMLNS, SKOS, SOSA, ORG, SSN, XSD
import pandas as pd
import os
import igraph as ig
import matplotlib.pyplot as plt


def was_derived_from_graphic(data_catalog=Graph, uri=URIRef):
    os.makedirs("./docs/figures/", exist_ok=True)



    identifier=str(data_catalog.value(URIRef(uri), DCTERMS.identifier))
    filename= "./docs/figures/"+ identifier+"_lineage"

    # find was derived from datasets and populate graph

    was_derived_from= data_catalog.objects(URIRef(uri), PROV.wasDerivedFrom)
    g = ig.Graph(directed=True)

    g.add_vertex(identifier, label=identifier, color='red')

    counter=0
    for i in was_derived_from:

        label2= str(i).split("#")[1]
        g.add_vertex(label2, label=label2, )
        g.add_edge(source= identifier, target=label2)
        counter= counter +1

    dataset_color= ["red"] 
    lineage_color=["light blue"]
    vertex_color = dataset_color + lineage_color * counter
    g.es["label"] = ["wasDerivedFrom"] * counter

    fig, ax = plt.subplots(figsize=(5,5))
    ig.plot(
        g,
        target=ax,
        layout="circle", # print nodes in a circular layout
        vertex_size=50,
        vertex_color= vertex_color,
    )

    graph_file=filename+'.svg' 
    fig.savefig(graph_file)
    # os.remove(filename+'.html')
    return graph_file


def get_data_quality(data_catalog= Graph, dataset_uri=URIRef):
    dqv_ns=Namespace("http://www.w3.org/ns/dqv#")
    quality_measurements= data_catalog.subjects(dqv_ns.computedOn, dataset_uri)
    return quality_measurements



