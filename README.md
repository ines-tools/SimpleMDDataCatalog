# SimpleMDDataCatalog
simple data catalog based on dcat that generates MD to be published as a static website using frameworks like github pages, hugo or jekyll. 


## Motivation

Data catalogs are powerful tools in managing data. Whether it is for a small project or a giant organization. There are many good (both open and closed source) data cataloging applications out there that this one doesn't aim to replace, however, most of them require the owners/publishers to have access to cloud computing environments or have their own server. The barrier to entry is quite high for reasons that have everything to do with server management and nothing to do with data management. This project aims to create a low-barrier to entry data catalog making use of:

- excel/spreadsheets for data entry
  - while spreadsheets are generally a poor choice for (meta) data management, it opens up participation in the data cataloging process to a wider range of individuals
  - as users become more familiar with (and power users of) data cataloging, it is recommended to migrate to more robust data cataloging applications. with this future migration in mind. This tool takes care of transforming the catalog into a standardized format (using [dcat](https://www.w3.org/TR/vocab-dcat-3/) and [dqv](https://www.w3.org/TR/vocab-dqv/) and [skos](https://www.w3.org/TR/skos-reference/)). This ensures that users who start here have room to grow without incurring technical debt for starting simple.
- mark down for static site generation
  - using github's pages functionality for the simplest version
  - using more advanced static site frameworks like hugo and jekyll for those who feel comfortable with those and want to be able to customize the layout with themes or access to other functionalities that those frameworks give access to 

A very simple example of the data catalog that is generated can be found [here](https://uuidea.github.io/SimpleMDDataCatalog/).

## Features

The data catalog aims to give the following overview:
- datasets and the formats in which they are published
  - organize data by (user defined) key words
- (user defined) data quality metrics and measurements
- data lineage
  - and data lineage/supply chain data quality metrics

## On privacy and security

This project allows users to generate a data catalog website relying on static site generation.

When using this function in its most basic form (making use of github pages) write access is managed through the github repository where the data is stored. Read access is wide open for public repositories, or, for private repositories however the organization/user has managed access in another way.

Given this rather crude approach (its a feature, not a bug) to read/write access, users are advised to think carefully about what they publish and who has access to it. Especially when data privacy laws (like the GDPR) are concerned, it is advised to not publish any person identifiable information (for instance in the dcterms:contactPoint field) as doing so typically comes with the legal requirement to introduce (potentially) complex data management processes (that cannot be classified as 'low barrier to entry' any longer). 




## datamodel

the datacatalog understands the following information.

![data model](/out/documentation/datamodel/datamodel.svg)

## using a spreadsheet as input

While directly editing the RDF/ttl file gives much more flexibility and control, the idea is that using a simple spreadsheet is sufficient for being able to create a simple data catalog


