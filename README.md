# SALI LMSS Python Library
### A Python library for working with the SALI LMSS OWL

**Overview**

### What is the Legal Matter Standard Specification (LMSS)?

The LMSS is a taxonomy/ontology of over 10,000 law-focused tags/nodes, as well as relationships/edges between those tags/nodes.  Each tag/node has a unique identifier (IRI). That identifier is being used — and standardized — by three stakeholder groups:
 * **Vendors** (e.g., Thomson Reuters, LexisNexis, Fastcase, Docket Alarm, NetDocuments, iManage, and many others)
 * **Providers/Firms** (e.g., DLA Piper, Clifford Chance, Perkins Coie, Crowell, Fredrikson & Byron, and many others)
 * **Corporate Law Departments** (e.g., Microsoft, Intel)

The end result: LMSS permits those stakeholders (vendors, firms, corporate law departments) to increase interoperability, fuel AI, and produce better outcomes.


### What is Standards Advancement for the Legal Industry (SALI)?
SALI is the nonprofit consortium of Vendors, Providers (e.g., firms), and Clients — all quickly and broadly moving towards standardizing with SALI tags (LMSS). Those 10,000+ tags serve as the industry’s common language, improving outcomes and value. And they are used in conjunction with the SALI API, where all stakeholders can transfer data using a standardized API protocol — leveraging SALI tags/nodes/identifiers. (edited) 


### Installation
This module is not yet available on PyPI. To install, use the following command:
```shell
$ pip3 install https://github.com/273v/python-lmss/archive/refs/heads/main.zip
```

PyPI and Conda packages will be available as soon as the API is confirmed to be stable
after additional testing.

### Current Functionality
This library currently supports:

 * [x] loading LMSS from a local file or remote URL, e.g., SALI GitHub
 * [x] loading a specific version or branch of LMSS
 * [x] loading as a raw lxml.etree or rdflib.Graph object
 * [x] loading as an `lmss.graph.LMSSGraph` object, which provides additional functionality
 * [x] searching for IRIs by label, including basic fuzzy matching
 * [x] searching for IRIs by definition, including basic fuzzy matching
 * [x] listing common key concepts (i.e., the ones visible listed in SALI's Protégé instance)


Additional functionality, including connections to public and private data models and ontologies, is
available in Kelvin Graph.

### Usage

Additional documentation will be provided as the API is finalized and more use 
cases are solicited.

```python
# Load the LMSS graph
lmss_graph = LMSSGraph()

# Search for a label in the graph by definition
results = lmss_graph.search_definitions("nautical")
print(results[0])

# Output:
{
    'alt_labels': ['Admiralty and Maritime Law'],
    'children': [],
    'definitions': ['Law that governs nautical issues and private maritime disputes.'],
    'distance': 100.0,
    'exact': False,
    'hidden_labels': ['ADMR'],
    'iri': 'http://lmss.sali.org/RCXiUipi6wkkqalyBH20P5A',
    'label': 'Admiralty and Maritime Law',
    'parents': ['http://lmss.sali.org/RqNYDJtQ1pAsGPKZNEUlETN1635a33287ad46c9986274ed71d37997'],
    'substring': True
}

results = lmss_graph.search_definitions("nautical")
print(results[0])

# Search for a label in the graph
for result in lmss_graph.search_labels(
        "resources", 
        concept_type=lmss_graph.key_concepts["Area of Law"], 
        num_results=3): 
    # output iri and name
    print(f'{result["iri"]} -> {result["label"]}')
```

```
# Output:
http://lmss.sali.org/R8NS2clrdzMdZxaKZRr45Tj -> Forest Resources Law
http://lmss.sali.org/RBioeVhKaUUVmf39x6B5LRh -> Mineral Resources Law
http://lmss.sali.org/R7KYATnZcNxJsZ1MQBADZ0x -> Water Resources and Wetlands Law
```

### Versions
 * `0.1.1`, 2021-03-16: Minor fixes and enhancements to support Suggester API and new LMSS develop version
 * `0.1.0`, 2023-03-15: Initial public release to support Suggester API release on Docker Hub

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
