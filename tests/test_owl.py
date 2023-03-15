"""test_owl.py: Tests for the lmss.owl module."""

# imports
from pathlib import Path

# packages
import lxml.etree
import rdflib

# projects
import lmss.owl


# test download default version
def test_get_lmss_owl():
    """Test that we can download the latest version of the LMSS OWL data."""
    # load it
    owl = lmss.owl.get_lmss_owl()

    # check that we have xml
    assert owl.startswith("<?xml")

    # check for <Ontology> tag
    assert "<rdf:RDF" in owl


# test download specific version
def test_get_lmss_owl_version():
    """Test that we can download a specific version of the LMSS OWL data."""
    # load it
    owl = lmss.owl.get_lmss_owl(branch="develop")

    # check that we have xml
    assert owl.startswith("<?xml")

    # check for <Ontology> tag
    assert "<rdf:RDF" in owl


# test that it parses into an etree
def test_get_lmss_owl_parse():
    """Test that we can parse the LMSS OWL data into an lxml.etree document."""
    # load it
    owl = lmss.owl.get_lmss_owl()

    # parse it
    doc = lxml.etree.fromstring(owl)

    # check that we have an etree
    assert isinstance(doc, lxml.etree._Element)


# test that we can get an etree from the convenience function
def test_get_lmss_owl_etree():
    """Test that we can get an lxml.etree document from the convenience function."""
    # load it
    doc = lmss.owl.get_lmss_owl_etree()

    # check that we have an etree
    assert isinstance(doc, lxml.etree._Element)

    # check that we have an rdf:RDF tag
    assert doc.tag == "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF"


# test that we can get an rdflib graph from the convenience function
def test_get_lmss_owl_rdflib():
    """Test that we can get an rdflib graph from the convenience function."""
    # load it
    graph = lmss.owl.get_lmss_owl_rdflib()

    # check that we have an rdflib graph
    assert isinstance(graph, rdflib.graph.Graph)

    # check
    assert len(graph) > 0


# test that we can get concepts
def test_get_concepts():
    """Test that we can get concepts from the LMSS OWL data."""
    # load it
    concepts = lmss.owl.get_concepts()

    # check that we have a list
    assert isinstance(concepts, list)

    # check that we have some concepts
    assert len(concepts) > 0

    # check that we have the expected keys
    assert set(concepts[0].keys()) == {
        "iri",
        "label",
        "alt_labels",
        "hidden_labels",
        "subclass_list",
        "definition",
        "comments",
    }

    # test that we have 100s
    assert len(concepts) > 100


# test that we can export the list to CSV
def test_export_concepts_csv():
    """Test that we can export the list of concepts to CSV."""
    # load it
    concepts = lmss.owl.get_concepts()

    # export it
    lmss.owl.export_concepts(concepts, output_file="test.csv")

    # check that the file exists
    assert Path("test.csv").exists()

    # remove the file
    Path("test.csv").unlink()
