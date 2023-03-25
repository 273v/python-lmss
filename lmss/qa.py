"""lmss.qa provides quality assurance/control tools for the SALI LMSS ontology"""


# imports
import argparse
import csv
import json
from pathlib import Path

# packages
import networkx

# projects
import lmss.owl
import lmss.graph


class LMSSGraphQA:
    """LMSSGraphQA provides quality assurance/control tools for the SALI LMSS ontology.  It provides the following
    QA/QC methods for the OWL/SKOS in the ontology:
    - check for missing rdfs:label
    - check for missing skos:prefLabel
    - check for missing skos:definition
    - check for labels with parentheses, hyphens, or other signs of a pref/alt label
    - check for Classes that should probably be instances, e.g., Courts or Agencies
    - check for loops in subclass relationships with networkx find_cycle()
    """

    def __init__(
        self,
        owl_path: Path | str | None = None,
        owl_branch: str = lmss.owl.DEFAULT_REPO_BRANCH,
        owl_repo_url: str = lmss.owl.DEFAULT_REPO_ARTIFACT_URL,
    ):
        """Initialize LMSSGraphQA with the LMSS OWL/SKOS graph

        :param owl_path: Path to the LMSS OWL/SKOS file
        :param owl_branch: LMSS OWL/SKOS git branch
        :param owl_repo_url: LMSS OWL/SKOS git repository URL
        """
        # initialize graph
        self.graph = lmss.graph.LMSSGraph(owl_path, owl_branch, owl_repo_url)

        # initialize finding list
        self.findings: list[dict] = []

    def check_rdfs_label(self):
        """
        Check for missing rdfs:label in the LMSS OWL/SKOS graph
        """

        # iterate through all nodes in the graph
        for iri, concept in self.graph.concepts.items():
            # skip owl thing - you make my heart sing
            if iri == "http://www.w3.org/2002/07/owl#Thing":
                continue

            # check if there is an empty/0-byte rdfs:label
            if "label" not in concept:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": None,
                        "description": "Missing rdfs:label",
                        "source": "check_rdfs_label",
                    }
                )
            # check if there is a None rdfs:label
            elif concept["label"] is None:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": None,
                        "description": "None rdfs:label",
                        "source": "check_rdfs_label",
                    }
                )
            # check if there is an empty rdfs:label
            elif len(concept["label"].strip()) == 0:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": None,
                        "description": "Empty rdfs:label",
                        "source": "check_rdfs_label",
                    }
                )

    def check_skos_pref_label(self):
        """
        Check for missing skos:prefLabel in the LMSS OWL/SKOS graph
        """

        # iterate through all nodes in the graph
        for iri, concept in self.graph.concepts.items():
            # skip owl thing - you make my heart sing
            if not iri.startswith("http://lmss.sali.org"):
                continue

            # get label
            label = concept.get("label", None)

            # check if there is an empty/0-byte skos:prefLabel
            if "prefLabel" not in concept:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Missing skos:prefLabel",
                        "source": "check_skos_pref_label",
                    }
                )
            # check if there is a None skos:prefLabel
            elif concept["prefLabel"] is None:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "None skos:prefLabel",
                        "source": "check_skos_pref_label",
                    }
                )
            # check if there is an empty skos:prefLabel
            elif len(concept["prefLabel"].strip()) == 0:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Empty skos:prefLabel",
                        "source": "check_skos_pref_label",
                    }
                )

    def check_skos_definition(self):
        """
        Check for missing skos:definition in the LMSS OWL/SKOS graph
        """
        # iterate through all nodes in the graph
        for iri, concept in self.graph.concepts.items():
            # skip owl thing - you make my heart sing
            if not iri.startswith("http://lmss.sali.org"):
                continue

            # get label
            label = concept.get("label", None)

            # check if there is an empty/0-byte skos:definition
            if "definition" not in concept:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Missing skos:definition",
                        "source": "check_skos_definition",
                    }
                )
            # check if there is a None skos:definition
            elif concept["definition"] is None:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "None skos:definition",
                        "source": "check_skos_definition",
                    }
                )
            # check if there is an empty skos:definition
            elif len(concept["definition"].strip()) == 0:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Empty skos:definition",
                        "source": "check_skos_definition",
                    }
                )

    def check_label_punctuation(self):
        """
        Check for labels with parentheses, hyphens, or other signs of a pref/alt label
        """
        # iterate through all nodes in the graph
        for iri, concept in self.graph.concepts.items():
            # skip owl thing - you make my heart sing
            if not iri.startswith("http://lmss.sali.org"):
                continue

            # get label
            label = concept.get("label", None)

            # check if there is a label
            if label is None:
                continue

            # check for parentheses
            if "(" in label or ")" in label:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Label contains parentheses",
                        "source": "check_label_punctuation",
                    }
                )

            # check for hyphens
            if " - " in label:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Label contains hyphens",
                        "source": "check_label_punctuation",
                    }
                )

            # check for slashes
            if "/" in label:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Label contains slashes",
                        "source": "check_label_punctuation",
                    }
                )

            # check for colon or semi-colon
            if ":" in label or ";" in label:
                self.findings.append(
                    {
                        "iri": iri,
                        "label": label,
                        "description": "Label contains colons or semi-colons",
                        "source": "check_label_punctuation",
                    }
                )

    def check_loops(self):
        """
        Check for loops in the LMSS OWL/SKOS graph
        """
        # iterate through all nodes in the graph and build an edge list
        edges = set()
        for iri, concept in self.graph.concepts.items():
            # skip owl thing - you make my heart sing
            if not iri.startswith("http://lmss.sali.org"):
                continue

            # get the children and parents
            children = concept.get("children", [])
            parents = concept.get("parents", [])

            # add edges both directions
            for child in children:
                edges.add((iri, child))
            for parent in parents:
                edges.add((parent, iri))

        # create networkx graph from edges
        nx_graph = networkx.DiGraph()
        nx_graph.add_edges_from(edges)

        #  check if it's a DAG
        if not networkx.is_directed_acyclic_graph(nx_graph):
            # get the cycles
            cycles = list(networkx.simple_cycles(nx_graph))

            # iterate through the cycles
            for cycle in cycles:
                # get the label for the first node in the cycle
                label = self.graph.concepts[cycle[0]].get("label", None)

                # add finding
                self.findings.append(
                    {
                        "iri": cycle[0],
                        "label": label,
                        "description": f"Cycle in graph: {cycle}",
                        "source": "check_loops",
                    }
                )

    # pylint: disable=R0912
    def check_duplicate_labels(self):
        """
        Check for duplicate labels in the LMSS OWL/SKOS graph
        """

        # setup mapping where keys are: label, label type (e.g., rdfs:label, skos:prefLabel, etc.), and value is list
        # of IRIs
        label_maps: dict[str, dict[str, list[str]]] = {}

        # iterate through all concepts and track the rdfs:label, skos:prefLabel, skos:altLabel, and skos:hiddenLabel
        for iri, concept in self.graph.concepts.items():
            label = concept.get("label", None)
            if label is not None:
                if label not in label_maps:
                    label_maps[label] = {}
                if "rdfs:label" not in label_maps[label]:
                    label_maps[label]["rdfs:label"] = []
                label_maps[label]["rdfs:label"].append(iri)

            # check pref labels
            for pref_label in concept.get("pref_labels", []):
                if pref_label not in label_maps:
                    label_maps[pref_label] = {}
                if "skos:prefLabel" not in label_maps[pref_label]:
                    label_maps[pref_label]["skos:prefLabel"] = []
                label_maps[pref_label]["skos:prefLabel"].append(iri)

            # check alt labels
            for alt_label in concept.get("alt_labels", []):
                if alt_label not in label_maps:
                    label_maps[alt_label] = {}
                if "skos:altLabel" not in label_maps[alt_label]:
                    label_maps[alt_label]["skos:altLabel"] = []
                label_maps[alt_label]["skos:altLabel"].append(iri)

            # check hidden labels
            for hidden_label in concept.get("hidden_labels", []):
                if hidden_label not in label_maps:
                    label_maps[hidden_label] = {}
                if "skos:hiddenLabel" not in label_maps[hidden_label]:
                    label_maps[hidden_label]["skos:hiddenLabel"] = []
                label_maps[hidden_label]["skos:hiddenLabel"].append(iri)

        # iterate through the label maps and check for duplicates
        for label, label_type_map in label_maps.items():
            # keep an IRI set
            label_iri_set = set()

            # we are de-duping across all label types
            for iri_list in label_type_map.values():
                label_iri_set.update(iri_list)

            # if there are more than one IRIs, we have a problem
            if len(label_iri_set) > 1:
                # iterate through the IRIs and add findings
                for iri in label_iri_set:
                    self.findings.append(
                        {
                            "iri": iri,
                            "label": label,
                            "description": f"Duplicate label: {label} "
                            f"(label types: {','.join(label_type_map.keys())})",
                            "source": "check_duplicate_labels",
                        }
                    )


if __name__ == "__main__":
    # setup arguments as optional for owl file, owl branch
    parser = argparse.ArgumentParser()
    parser.add_argument("--owl-file", help="Path to OWL file", default=None)
    parser.add_argument(
        "--owl-branch", help="OWL branch to use", default=lmss.owl.DEFAULT_REPO_BRANCH
    )
    parser.add_argument(
        "--owl-repo-url",
        help="URL to GitHub repo for OWL file",
        default=lmss.owl.DEFAULT_REPO_ARTIFACT_URL,
    )

    # setup arguments for check types
    parser.add_argument(
        "--disable-rdfs-label",
        help="Disable check for missing rdfs:label",
        action="store_true",
    )
    parser.add_argument(
        "--disable-skos-pref-label",
        help="Disable check for missing skos:prefLabel",
        action="store_true",
    )
    parser.add_argument(
        "--disable-skos-definition",
        help="Disable check for missing skos:definition",
        action="store_true",
    )
    parser.add_argument(
        "--disable-label-punctuation",
        help="Disable check for labels with parentheses, hyphens, or other signs of a pref/alt label",
        action="store_true",
    )
    parser.add_argument(
        "--disable-duplicate-labels",
        help="Disable check for duplicate labels",
        action="store_true",
    )
    parser.add_argument(
        "--disable-loops",
        help="Disable check for loops in the LMSS OWL/SKOS graph",
        action="store_true",
    )

    # allow stdout or csv output
    parser.add_argument(
        "--output",
        help="Output format (- for stdout or filename for csv/json)",
        default="-",
    )

    # parse arguments
    args = parser.parse_args()

    # setup owl file
    lmss_qa = LMSSGraphQA(args.owl_file, args.owl_branch)

    # run checks
    if not args.disable_rdfs_label:
        lmss_qa.check_rdfs_label()
    if not args.disable_skos_pref_label:
        lmss_qa.check_skos_pref_label()
    if not args.disable_skos_definition:
        lmss_qa.check_skos_definition()
    if not args.disable_label_punctuation:
        lmss_qa.check_label_punctuation()
    if not args.disable_duplicate_labels:
        lmss_qa.check_duplicate_labels()
    if not args.disable_loops:
        lmss_qa.check_loops()

    # sort by IRI by default
    lmss_qa.findings.sort(key=lambda x: x["iri"])

    # output findings
    if args.output == "-":
        # output to stdout line by line in human-readable format
        for finding in lmss_qa.findings:
            print(
                f"{finding['iri']} : ({finding['label']}) : {finding['source']} : {finding['description']}"
            )
    elif args.output.lower().endswith("csv"):
        with open(args.output, "wt", encoding="utf-8") as output_file:
            writer = csv.DictWriter(
                output_file, fieldnames=["iri", "label", "description", "source"]
            )
            writer.writeheader()
            writer.writerows(lmss_qa.findings)
    elif args.output.lower().endswith("json"):
        with open(args.output, "wt", encoding="utf-8") as output_file:
            json.dump(lmss_qa.findings, output_file, indent=2)
