"""lmss.owl provides a low-level interface for working with the SALI LMSS OWL data, including methods to:
1. Retrieve the latest version of the OWL data or another specific version
2. Parse the OWL data into an lxml.etree document.
3. Lookup objects by IRI or name.
4. Retrieve lists of concepts or properties.

For a more efficient, higher-level OOP interface, see the lmss.graph module."""

# SPDX-License-Identifier: MIT
# Copyright (c) 2023 273 Ventures, LLC

# imports
import csv
import json
import sys
from pathlib import Path

# packages
import httpx
import lxml.etree
import rdflib

# module constants
DEFAULT_REPO_ARTIFACT_URL = "https://raw.githubusercontent.com/sali-legal/LMSS/"
DEFAULT_REPO_BRANCH = "main"

# define standard namespace prefixes for use with etree
NSMAP = {
    "dc": "http://purl.org/dc/elements/1.1/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "lmss": "http://lmss.sali.org/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "oboInOwl": "http://www.geneontology.org/formats/oboInOwl#",
}


def get_lmss_owl(
    branch: str = DEFAULT_REPO_BRANCH,
    repo_artifact_url: str = DEFAULT_REPO_ARTIFACT_URL,
) -> str:
    """get_latest_version returns the latest version of the LMSS OWL data from the specified repo.  LMSS
    is currently vendored via GitHub using a branch-version strategy, so this method really just determines
    the correct branch URL for the OWL blob and retrieves it.

    Args:
        branch (str, optional): The branch (version) to retrieve the OWL data from. Defaults to main, which is
          latest stable.
        repo_artifact_url (str, optional): The URL to the repo artifact. Defaults to DEFAULT_REPO_ARTIFACT_URL.

    Returns:
        str: The latest version of the LMSS OWL data as raw XML.
    """
    with httpx.Client(http2=True) as client:
        response = client.get(
            f"{repo_artifact_url.rstrip('/')}/{branch.lstrip('/')}/LMSS.owl"
        )
        response.raise_for_status()
        return response.content.decode("utf-8")


def get_lmss_owl_etree(
    branch: str = DEFAULT_REPO_BRANCH,
    repo_artifact_url: str = DEFAULT_REPO_ARTIFACT_URL,
) -> lxml.etree._ElementTree:
    """get_lmss_owl_etree returns the latest version of the LMSS OWL data from the specified repo as an
    lxml.etree document.

    Args:
        branch (str, optional): The branch (version) to retrieve the OWL data from. Defaults to main, which is
          latest stable.
        repo_artifact_url (str, optional): The URL to the repo artifact. Defaults to DEFAULT_REPO_ARTIFACT_URL.

    Returns:
        lxml.etree._ElementTree: The latest version of the LMSS OWL data as an lxml.etree document.
    """
    # setup a parser
    return lxml.etree.fromstring(get_lmss_owl(branch, repo_artifact_url))


def get_lmss_owl_rdflib(
    branch: str = DEFAULT_REPO_BRANCH,
    repo_artifact_url: str = DEFAULT_REPO_ARTIFACT_URL,
) -> rdflib.Graph:
    """get_lmss_owl_rdflib returns the latest version of the LMSS OWL data from the specified repo as an
    rdflib graph.

    Args:
        branch (str, optional): The branch (version) to retrieve the OWL data from. Defaults to main, which is
          latest stable.
        repo_artifact_url (str, optional): The URL to the repo artifact. Defaults to DEFAULT_REPO_ARTIFACT_URL.

    Returns:
        rdflib.Graph: The latest version of the LMSS OWL data as an rdflib graph.
    """
    # setup a parser
    return rdflib.Graph().parse(
        data=get_lmss_owl(branch, repo_artifact_url), format="xml"
    )


def get_concepts(
    owl_etree: lxml.etree._ElementTree | None = None,
    branch: str = DEFAULT_REPO_BRANCH,
    repo_artifact_url: str = DEFAULT_REPO_ARTIFACT_URL,
) -> list[dict]:
    """get_concepts returns a list of concepts from the latest version of the LMSS OWL data as a list of dictionaries
    with the following keys:
    - iri: The IRI of the concept
    - label: The label of the concept
    - alt_labels: A list of alternative labels for the concept
    - hidden_label: The hidden label of the concept
    - subclass_list: A list of concepts that this concept is a subclass of
    - definition: The definition of the concept
    - comments: A list of comments for the concept

    Args:
        owl_etree (lxml.etree._ElementTree): The etree to parse concepts from.  If None, the latest version of the
            OWL data will be retrieved from the specified repo. Defaults to None.
        branch (str, optional): The branch (version) to retrieve the OWL data from. Defaults to main, which is
            latest stable.
        repo_artifact_url (str, optional): The URL to the repo artifact. Defaults to DEFAULT_REPO_ARTIFACT_URL.

    Returns:
        list: A list of concepts.
    """
    # get the etree if it wasn't passed in
    if owl_etree is None:
        # get the latest version of the OWL data
        owl_etree = get_lmss_owl_etree(branch, repo_artifact_url)

    # get the concepts
    concepts = owl_etree.xpath("//owl:Class", namespaces=NSMAP)

    # setup a list to hold the concepts
    concept_data = []

    # iterate over the concepts
    for concept in concepts:
        # get the IRI
        iri = concept.attrib.get(
            "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", None
        )

        # get the label
        label_element = concept.xpath("rdfs:label", namespaces=NSMAP)
        if label_element:
            label = label_element[0].text
        else:
            label = None

        # get the altLabels
        alt_labels = [
            alt_label.text
            for alt_label in concept.xpath("skos:altLabel", namespaces=NSMAP)
        ]

        # get the hiddenLabels
        hidden_labels = [
            hidden_label.text
            for hidden_label in concept.xpath("skos:hiddenLabel", namespaces=NSMAP)
        ]

        # get the skos:definition
        definition_element = concept.xpath("skos:definition", namespaces=NSMAP)
        if definition_element:
            definition = definition_element[0].text
        else:
            definition = None

        # get the list of subclass parents from <rdfs:subClassOf rdf:resource=
        subclass_list = [
            subclass.attrib.get(
                "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource", None
            )
            for subclass in concept.xpath("rdfs:subClassOf", namespaces=NSMAP)
        ]

        # get the comments
        comments = [
            comment.text for comment in concept.xpath("rdfs:comment", namespaces=NSMAP)
        ]

        # update the concept
        concept_data.append(
            {
                "iri": iri,
                "label": label,
                "alt_labels": alt_labels,
                "hidden_labels": hidden_labels,
                "subclass_list": subclass_list,
                "definition": definition,
                "comments": comments,
            }
        )

    # return the concepts
    return concept_data


def export_concepts(
    concepts: list[dict] | None = None,
    output_format: str = "csv",
    output_file: str | Path | None = None,
    branch: str = DEFAULT_REPO_BRANCH,
    repo_artifact_url: str = DEFAULT_REPO_ARTIFACT_URL,
) -> bool:
    """export_concepts exports a version of the concept list to CSV (flattened) or JSON for easy consumption.

    Args:
        concepts (list[dict], optional): The concepts to export.  If None, the latest version of the OWL data will
            be retrieved from the specified repo. Defaults to None.
        output_format (str, optional): The format to export the concepts in.  Valid values are "csv" and "json".
            Defaults to "csv".
        output_file (str | Path, optional): The file to export the concepts to.  If None, the concepts will be
            exported to stdout. Defaults to None.
        branch (str, optional): The branch (version) to retrieve the OWL data from. Defaults to main, which is
            latest stable.
        repo_artifact_url (str, optional): The URL to the repo artifact. Defaults to DEFAULT_REPO_ARTIFACT_URL.

    Returns:
        bool: True if the concepts were successfully exported, False otherwise.
    """
    # get the concepts if they weren't passed in
    if concepts is None:
        # get the concepts
        concepts = get_concepts(branch=branch, repo_artifact_url=repo_artifact_url)

    # export the concepts
    if output_format == "csv":
        # setup the fieldnames
        fieldnames = [
            "iri",
            "label",
            "alt_labels",
            "hidden_labels",
            "subclass_list",
            "definition",
            "comments",
        ]

        # export the concepts
        if output_file:
            # open the output file
            with open(output_file, "wt", encoding="utf-8") as csv_file:
                # setup the writer to join lists
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

                # write the header
                writer.writeheader()

                # write the concepts
                writer.writerows(concepts)

            # return success
            return True

        # setup the writer
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)

        # write the header
        writer.writeheader()

        # write the concepts
        writer.writerows(concepts)

        # return success
        return True

    if output_format == "json":
        # export the concepts
        if output_file:
            # open the output file
            with open(output_file, "wt", encoding="utf-8") as json_file:
                # write the concepts
                json.dump(concepts, json_file, indent=2)

            return True

        # write the concepts
        json.dump(concepts, sys.stdout, indent=2)

        # return success
        return True

    # invalid format
    raise ValueError(f"Invalid output format: {output_format}")
