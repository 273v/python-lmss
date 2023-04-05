"""lmss.diff provides an interface for diffing two versions of the LMSS graphs.

Sample Usage:
python -m lmss.diff branch=main branch=ec84c97148d9ef5ccbf2512c56ca5a8bbc7963e7 --format json
python -m lmss.diff file=owl1.owl branch=develop --format csv
"""


# imports
import argparse
import csv
import json
import sys

# project imports
import lmss.owl
from lmss.graph import LMSSGraph


def diff_graphs(graph1: LMSSGraph, graph2: LMSSGraph, output_format: str = "csv") -> None:
    """Diff two graphs and print the results as either plain text, CSV, or JSON records.

    Args:
        graph1 (LMSSGraph): The first graph.
        graph1 (LMSSGraph): The second graph.
        output_format (str): The output format. One of "csv", "json", or "text".
    """

    # store diff findings
    diff_list = []

    # get the IRIs on each branch
    g1_iris = set(graph1.concepts.keys())
    g2_iris = set(graph2.concepts.keys())

    # get the IRIs that are only in one
    g1_only_iris = g1_iris.difference(g2_iris)
    g2_only_iris = g2_iris.difference(g1_iris)

    for iri in g1_only_iris:
        diff_list.append(
            {"iri": iri, "field": None, "g1": True, "g2": False, "diff_type": "iri"}
        )

    for iri in g2_only_iris:
        diff_list.append(
            {"iri": iri, "field": None, "g1": False, "g2": True, "diff_type": "iri"}
        )

    # get the IRIs that are in both
    common_iris = g1_iris.intersection(g2_iris)

    for iri in common_iris:
        # get the triples for each
        for field in graph1.concepts[iri].keys():
            if graph1.concepts[iri][field] != graph1.concepts[iri][field]:
                diff_list.append(
                    {
                        "iri": iri,
                        "field": field,
                        "g1": graph1.concepts[iri][field],
                        "g2": graph1.concepts[iri][field],
                        "diff_type": "field",
                    }
                )

    # print the results
    if output_format == "text":
        for diff in diff_list:
            if diff["diff_type"] == "iri":
                print(f"IRI={diff['iri']}: {'only' if diff['g1'] else 'not'} in g1")
            elif diff["diff_type"] == "field":
                print(
                    f"IRI={diff['iri']}, field={diff['field']}: g1={diff['g1']}, g2={diff['g2']}"
                )
    elif output_format == "csv":
        writer = csv.DictWriter(
            sys.stdout, fieldnames=["iri", "field", "g1", "g2", "diff_type"]
        )
        writer.writeheader()
        writer.writerows(diff_list)
    elif output_format == "json":
        print(json.dumps(diff_list, indent=4))


def get_graph_from_arg(arg_str: str) -> LMSSGraph:
    """Parse a branch=, file=, or url= token into a graph.

    Examples:
        branch=main
        branch=develop
        file=/path/to/file.owl
        branch=main&url=https://raw.githubusercontent.com/my-github/my-fork/"

    Args:
        arg_str (str): The argument string to parse.

    Returns:
        LMSSGraph: The graph.
    """
    # split into tokens separated by "&" and then parse each into k=v
    tokens = arg_str.split("&")
    owl_args = {}
    for token in tokens:
        key, value = token.split("=", 1)
        owl_args[key] = value

    # cannot pass both url/branch and file
    if "branch" in owl_args and "file" in owl_args:
        raise ValueError(f"Cannot pass both branch and file: {arg_str}")

    # create the graph
    if "branch" in owl_args:
        url = owl_args.get("url", lmss.owl.DEFAULT_REPO_ARTIFACT_URL)
        return LMSSGraph(owl_branch=owl_args["branch"], owl_repo_url=url)

    if "file" in owl_args:
        return LMSSGraph(owl_path=owl_args["file"])

    raise ValueError(f"Invalid argument string: {arg_str}")


if __name__ == "__main__":
    # create the parser
    parser = argparse.ArgumentParser(description="Diff two LMSS graphs.")
    parser.add_argument("g1", type=str, help="branch=[branch] or file=/path/to/file")
    parser.add_argument("g2", type=str, help="branch=[branch] or file=/path/to/file")
    parser.add_argument(
        "--format", type=str, default="text", help="Output format: csv, json, or text"
    )

    # parse the arguments
    args = parser.parse_args()

    # parse the branch or file strings
    lmss_graph1 = get_graph_from_arg(args.g1)
    lmss_graph2 = get_graph_from_arg(args.g2)

    # diff the graphs
    diff_graphs(lmss_graph1, lmss_graph2, output_format=args.format)
