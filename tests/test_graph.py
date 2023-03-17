"""test_graph.py - tests for the graph module"""

# project imports
from lmss.graph import LMSSGraph


def test_load_graph():
    # load the LMSS ontology from the local cache
    lmss_graph = LMSSGraph()


def test_load_graph_cache():
    # load the LMSS ontology from the loc
    lmss_graph = LMSSGraph(use_cache=True)

    # load without
    lmss_graph = LMSSGraph(use_cache=False)


def test_graph_key_concepts():
    # load the LMSS ontology from the local cache
    lmss_graph = LMSSGraph(owl_branch="develop")

    # get the key concepts
    assert len(lmss_graph.key_concepts) == 24

    # check for area of law
    assert "Area of Law" in lmss_graph.key_concepts.keys()


def test_graph_search_labels():
    # load the LMSS ontology from the local cache
    lmss_graph = LMSSGraph()

    # search for a label in the graph
    results = lmss_graph.search_labels("Admiralty and Maritime Law")
    assert results[0]["label"] == "Admiralty and Maritime Law"
    assert results[0]["distance"] == 0.0

    # do the same with area of law limited
    results = lmss_graph.search_labels("Admiralty and Maritime Law",
                                       concept_type=lmss_graph.key_concepts["Area of Law"])
    assert results[0]["label"] == "Admiralty and Maritime Law"
    assert results[0]["distance"] == 0.0

    # do the same with area of law limited
    results = lmss_graph.search_labels("Admiralty and Maritime Law",
                                       concept_type=lmss_graph.key_concepts["Area of Law"],
                                       concept_depth=1)
    assert results[0]["label"] != "Admiralty and Maritime Law"
    print(results[0])
    assert results[0]["distance"] > 0.0


def test_graph_search_definitions():
    # load the LMSS ontology from the local cache
    lmss_graph = LMSSGraph()

    # search for a label in the graph
    results = lmss_graph.search_definitions("nautical")
    assert results[0]["label"] == "Admiralty and Maritime Law"

    # do the same with area of law limited
    results = lmss_graph.search_definitions("nautical",
                                            concept_type=lmss_graph.key_concepts["Area of Law"])
    assert results[0]["label"] == "Admiralty and Maritime Law"

    # do the same with area of law limited
    results = lmss_graph.search_definitions("nautical",
                                            concept_type=lmss_graph.key_concepts["Area of Law"],
                                            concept_depth=1)
    assert results[0]["label"] != "Admiralty and Maritime Law"


def test_graph_convenience_lists():
    # test all of the get_... convenience methods
    lmss_graph = LMSSGraph(owl_branch="develop")

    for method in dir(lmss_graph):
        if method.startswith("get_"):
            if method == "get_children":
                continue
            # all top levels must not be empty
            assert len(list(getattr(lmss_graph, method)())) > 0


def test_graph_parents():
    lmss_graph = LMSSGraph()

    iri = lmss_graph.label_to_iri["Education Law"][0]

    assert lmss_graph.concepts[iri]["parents"] == [
        "http://lmss.sali.org/RSYBzf149Mi5KE0YtmpUmr"
      ]
