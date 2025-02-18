# SimpleMDDataCatalog
simple data catalog based on dcat that generates MD to be published as a static website using frameworks like github pages, hugo or jekyll. 


## Motivation

Data catalogs are powerful tools in managing data. Whether it is for a small project or a giant organization. There are many good (both open and closed source) data cataloging applications out there that this one doesn't aim to replace, however, most of them require the owners/publishers to have access to cloud computing environments or have their own server. The barrier to entry is quite high for reasons that have everything to do with server management and nothing to do with data management. This project aims to create a low-barrier to entry data catalog making use of:

- excel/spreadsheets for data entry
  - while spreadsheets are generally a poor choice for (meta) data management, it opens up participation in the data cataloging process to a wider range of individuals
  - as users become more familiar with (and power users of) data cataloging, it is recommended to migrate to more robust data cataloging applications. with this future migration in mind. This tool takes care of transforming the catalog into a standardized format (using [dcat](https://www.w3.org/TR/vocab-dcat-3/) and [dqv](https://www.w3.org/TR/vocab-dqv/) and [skos](https://www.w3.org/TR/skos-reference/)). This ensures that users who start here have room to grow without incurring technical debt for starting simple.
- markdown for static site generation
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

An auxiliary motivation is to introduce users to subjects like data cataloging, data quality management and data lineage, by providing a tool that addresses these concepts in a basic way.

## On privacy and security

This project allows users to generate a data catalog website relying on static site generation.

When using this function in its most basic form (making use of github pages) write access is managed through the github repository where the data is stored. Read access is wide open for public repositories, or, for private repositories however the organization/user has managed access in another way.

Given this rather crude approach (its a feature, not a bug) to read/write access, users are advised to think carefully about what they publish and who has access to it. Especially when data privacy laws (like the GDPR) are concerned, it is advised to not publish any person identifiable information (for instance in the dcterms:contactPoint field) as doing so typically comes with the legal requirement to introduce (potentially) complex data management processes (that cannot be classified as 'low barrier to entry' any longer). 




## Datamodel

The data catalog understands the following information.

![data model](/out/documentation/datamodel/datamodel.svg)

The datamodel is based on [DCAT](https://www.w3.org/TR/vocab-dcat-3/), [SKOS](https://www.w3.org/TR/skos-reference/), [DQV](https://www.w3.org/TR/vocab-dqv/) and a little bit of [PROV](https://www.w3.org/TR/prov-o/). For the definitions of each of the classes and attributes, the reader is referred to the respective standards. While al of these standards support a wide variety of these concepts and attributes, this project takes a rather opinionated approach to applying these definitions. While this constraints the expressivity that these standards offer, it allows for the data catalog to remain 'Simple'.


## Using a spreadsheet as input

While directly editing the RDF/ttl file gives much more flexibility and control, the idea is that using a simple spreadsheet is sufficient for being able to create a simple data catalog. In this section you will find instructions on how to fill in the excel spreadsheet. AN example of the spreadsheet can be found [here](./tests/example_spreadsheet.xlsx) it is recommended to make a copy of this template and use it. 

The spreadsheet has 6 tabs:
- DataCatalog: this tab can only have 1 entry
- DataSets: data for the dataset records
- Distributions: data for the different distributions of the dataset
- Concepts: the definitions of the keywords/themes with which the datasets are annotated
- Metrics: the definition of data quality metrics with which the quality of data can be measured
- QualityMeasurements: quality measurements of specific datasets


### DataCatalog

This first tab of the spreadsheet contains information about the data catalog itself. 

The definition of [data catalog](https://www.w3.org/TR/vocab-dcat-3/#Class:Catalog), according to DCAT is: 

```
A curated collection of metadata about resources.
```

This information will become part of the landing page of the data catalog. **NB: Please make sure this tab only contains a single record!**

| attribute           | instruction                                                                                                                                                         | optional? |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier  | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/)             | no        |
| dcterms:title       | The title of the data catalog as text                                                                                                                               | no        |
| dcterms:description | A more elaborate description of the dataset                                                                                                                         | yes       |
| dcterms:licence     | Either a url to a license document or the name of a common license (like cc-by-4.0)                                                                                 | yes       |
| dcterms:publisher   | Either a url to the website of the publishing organization or the name of the publisher                                                                             | yes       |
| dcat:theme          | A comma separated list of key-words. These key-words also need to be defined in the 'Concepts' tab (make sure they are spelled the same, case sensitive), see below | yes       |

### Dataset

This tab contains the data sets. Each row is a different dataset. The definition of [Dataset](https://www.w3.org/TR/vocab-dcat-3/#Class:Dataset) according to DCAT is:


```
A collection of data, published or 
curated by a single agent, and available 
for access or download in one or more 
representations.
```

For datasets, the follwing information can be entered:
| attribute           | instruction                                                                                                                                                         | optional? |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier  | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/)             | no        |
| dcterms:title       | The title of the data set as text                                                                                                                                   | no        |
| dcterms:description | A more elaborate description of the dataset                                                                                                                         | yes       |
| dcterms:publisher   | Either a url to the website of the publishing organization or the name of the publisher                                                                             | yes       |
| dcat:contactPoint   | Either a url to a website with contact information or an email address                                                                                              | yes       |
| dcterms:licence     | Either a url to a license document or the name of a common license (like cc-by-4.0)                                                                                 | yes       |
| dcat:version        | Version information of the dataset. semantic versioning example: 1.0.4                                                                                              | yes       |
| dcat:theme          | A comma separated list of key-words. These key-words also need to be defined in the 'Concepts' tab (make sure they are spelled the same, case sensitive), see below | yes       |
| dcterms:spatial     | A description of the region the dataset covers. For example: Ireland                                                                                                | yes       |
| dcterms:temporal/time:hasBeginning    | The  start of the time that is covered by the dataset. For example: 2024                                                                                              | yes       |
| dcterms:temporal/time:hasEnd    | The end of the time that is covered by the dataset. For example: 2024                                                                                           | yes       |
| adms:status         | Status information of the dataset. For example: "test" or "deprecated"                                                                                              | yes       |
| prov:wasDerivedFrom | Data lineage information. A comma separated list of urls and/or dcterms:identifiers of other datasets that were used to produce this one. For example: 12345, 56789 | yes       |
| dcat:distribution   | The distributions that are available of this dataset. A comma separated list of dcterms:identifiers of entries in the Distributions tab (see below)                  | yes       |
| dcterms:modified    | The date at which the dataset was last modified                                                                                                                     | yes       |




### Distributions

This tab contains information on the distributions of the datasets. The definition of [distribution](https://www.w3.org/TR/vocab-dcat-3/#Class:Distribution) according to DCAT is:

```
A specific representation of a dataset. 
A dataset might be available in multiple 
serializations that may differ in various 
ways, including natural language, 
media-type or format, schematic 
organization, temporal and spatial 
resolution, level of detail or profiles 
(which might specify any or all of the above). 
```

| attribute           | instruction                                                                                                                                             | optional? |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier  | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/) | no        |
| dcterms:description | A more elaborate description of the distribution                                                                                                        | yes       |
| dcat:acccessURL     | The url to where the distribution can be obtained.                                                                                                      | yes       |
| dcterms:format      | The file format/serialization of the distribution. For example: 'csv' or 'excel'                                                                        | yes       |
| dcat:version        | Version information of the distribution. semantic versioning example: 1.0.4                                                                             | yes       |
| dcterms:modified    | The date at which the distribution was last modified                                                                                                    | yes       |



### Concepts
This tab contains definition information about the keywords that are used to annotate the datasets and the data catalog. The data in this tab is conform [SKOS (Simmple Knowledge Organization System)](https://www.w3.org/TR/skos-reference/). SKOS defines [Concept](https://www.w3.org/TR/skos-reference/) as:

```
A SKOS concept can be viewed as an idea 
or notion; a unit of thought. However, 
what constitutes a unit of thought is 
subjective, and this definition is meant 
to be suggestive, rather than restrictive.
```

| attribute          | instruction                                                                                                                                             | optional? |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/) | no        |
| skos:prefLabel     | The preferred label (word) for the concept                                                                                                              | no        |
| skos:definition    | The definition of the term.                                                                                                                             | yes       |
| skos:example       | Any examples of the term in its use.                                                                                                                    | yes       |
| skos:altLabel      | Any alternative labels (words) for the same term, comma separated if there are more than one                                                            | yes       |



### Metrics
This tab contains information about the metrics with which data quality are evaluated. The data in this section is modelled to comply with the [DQV (Data Quality Vocabulary)](https://www.w3.org/TR/vocab-dqv/). 

DQC defines [Metric](https://www.w3.org/TR/vocab-dqv/#dqv:Metric) as

```
Represents a standard to measure a quality 
dimension. An observation (instance of dqv:QualityMeasurement) assigns a value 
in a given unit to a Metric. 
```


| attribute            | instruction                                                                                                                                                       | optional? |
|----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier   | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/)           | no        |
| skos:prefLabel       | The preferred label (word) for the metric.                                                                                                                        | no        |
| skos:definition      | The definition of the metric. It helps to describe in detail what the metric aims to measure and how it measures it.                                              | No        |
| dqv:expectedDataType | The Datatype that a measurement of this metric would have. It is advised (but nor required) to stick to XSD datatypes                                             | No        |
| dqv:inDImension      | The quality dimension that the metric aims to capture. It is preferred to use [ISO Quality Dimensions](https://www.w3.org/TR/vocab-dqv/#DimensionsOfISOIEC25012). | yes       |



### QualityMeasurements

This tab contains information on any quality measurements that have been performed on the datasets. The DQV defines a [QualityMeasure](https://www.w3.org/TR/vocab-dqv/#dqv:QualityMeasurement)

```
Represents the evaluation of a given 
dataset (or dataset distribution) against 
a specific quality metric. 
```


| attribute            | instruction                                                                                                                                             | optional? |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier   | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/) | no        |
| dqv:computedOn       | the dcterms:identifier of the dataset on which this measurement was taken                                                                               | no        |
| dqv:isMeasurementOf  | The dcterms:identifier of the Metric that this measurement measured against                                                                             | no        |
| dqv:value            | The value of the quality measurement.                                                                                                                   | no        |
| prov:generatedAtTime | The date/datetime at which the measurement was done.                                                                                                    | yes       |


## DatasetSeries

This tab contains the data set series. Each row is a different series. The definition of [DatasetSeries](https://www.w3.org/TR/vocab-dcat-3/#Class:Dataset_Series) according to DCAT is:


```
A collection of datasets that are published separately, but share some characteristics that group them. 
```

For DatasetSeries, the following information can be entered:
| attribute           | instruction                                                                                                                                                         | optional? |
|---------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------|
| dcterms:identifier  | A unique identifier without any spaces. It is recommended to use a uuid these can be generated using a tool like [this](https://www.uuidgenerator.net/)             | no        |
| dcterms:title       | The title of the data set as text                                                                                                                                   | no        |
| dcterms:description | A more elaborate description of the dataset                                                                                                                         | yes       |
| dcterms:publisher   | Either a url to the website of the publishing organization or the name of the publisher                                                                             | yes       |
| dcat:contactPoint   | Either a url to a website with contact information or an email address                                                                                              | yes       |
| dcterms:licence     | Either a url to a license document or the name of a common license (like cc-by-4.0)                                                                                 | yes       |
| dcat:version        | Version information of the dataset. semantic versioning example: 1.0.4                                                                                              | yes       |
| dcat:theme          | A comma separated list of key-words. These key-words also need to be defined in the 'Concepts' tab (make sure they are spelled the same, case sensitive), see below | yes       |
| dcterms:spatial     | A description of the region the dataset covers. For example: Ireland                                                                                                | yes       |
| dcterms:temporal/time:hasBeginning    | The  start of the time that is covered by the dataset. For example: 2024                                                                                              | yes       |
| dcterms:temporal/time:hasEnd    | The end of the time that is covered by the dataset. For example: 2024                                                                                           | yes       |
| adms:status         | Status information of the dataset. For example: "test" or "deprecated"                                                                                              | yes       |
| prov:wasDerivedFrom | Data lineage information. A comma separated list of urls and/or dcterms:identifiers of other datasets that were used to produce this one. For example: 12345, 56789 | yes       |
| dcat:distribution   | The distributions that are available of this dataset. A comma separated list of dcterms:identifiers of entries in the Distributions tab (see below)                  | yes       |
| dcterms:modified    | The date at which the dataset was last modified                                                                                                                     | yes       |


