# SALI LMSS Python Library
### A Python library for working with the SALI LMSS OWL

**Overview**

### What is the Legal Matter Standard Specification (LMSS)?

### What is Standards Advancement for the Legal Industry (SALI)?


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
 * `0.1.0`, 2023-03-15: Initial public release to support Suggester API release on Docker Hub

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.