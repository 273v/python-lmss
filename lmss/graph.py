"""lmss.graph provides a convenient, efficient, OOP interface for interacting with the SALI LMSS ontology.

The LMSSGraph class supports the following methods:
* loading the LMSS ontology from a local file, remote URL like the official repo, or local cache
* retrieving specific concepts from the ontology
* listing certain types of concepts
* querying the ontology for concepts based on label or definition
* querying the ontology for concepts based on basic relationships
"""

# imports
import importlib.resources
from pathlib import Path

# project
import lmss.owl

# packages
from rapidfuzz.distance import DamerauLevenshtein
import rapidfuzz.fuzz
import rdflib.resource
from rdflib.namespace import OWL, RDF, SKOS, RDFS


class LMSSGraph(rdflib.Graph):
    """LMSSGraph is a wrapper around rdflib.Graph that provides a convenient, efficient, OOP interface for
    interacting with the SALI LMSS ontology."""

    def __init__(
            self,
            owl_path: Path | str | None = None,
            owl_branch: str = lmss.owl.DEFAULT_REPO_BRANCH,
            owl_repo_url: str = lmss.owl.DEFAULT_REPO_ARTIFACT_URL,
            default_max_depth: int = 16,
            use_cache: bool = True,
    ):
        """Initialize the LMSSGraph by loading the ontology from a local file, remote URL like the official
        repo, or local cache and then calling the parent class constructor with the ontology as the data.

        Args:
            owl_path (Path | str | None): The path to the local LMSS ontology file. Defaults to None.
            owl_branch (str): The branch of the LMSS ontology repo to use. Defaults to main (lmss.owl.DEFAULT_REPO_BRANCH).
            owl_repo_url (str): The URL of the LMSS ontology repo. Defaults to lmss.owl.DEFAULT_REPO_ARTIFACT_URL.
            use_cache (bool): Whether to use the local cache. Defaults to True.
        """

        # load the ontology from a local file, remote URL like the official repo, or local cache
        owl_data: str = None
        if owl_path:
            if isinstance(owl_path, str):
                owl_path = Path(owl_path)
            owl_data = owl_path.read_text()
        else:
            if use_cache:
                try:
                    with importlib.resources.path(lmss.owl, "lmss.owl") as cache_path:
                        with open(cache_path, "r") as f:
                            owl_data = f.read()
                except (FileNotFoundError, PermissionError, ModuleNotFoundError, TypeError):
                    pass

            if not owl_data:
                owl_data = lmss.owl.get_lmss_owl(owl_branch, owl_repo_url)

        # initialize the parent class with the ontology as the data
        super().__init__()
        self.parse(
            data=owl_data,
            format="xml",
        )

        # set default max depth
        self.default_max_depth = default_max_depth

        # setup basic structures
        self.concepts: dict[str, dict] = {}
        self.edges: dict[str, list[str]] = {}
        self.iri_to_label: dict[str, str] = {}
        self.label_to_iri: dict[str, list[str]] = {}

        # set default excluded top-level concepts
        self.top_level_concepts = {
            'LMSS Type': 'http://lmss.sali.org/R8uI6AZ9vSgpAdKmfGZKfTZ',
            'Legal Entity': 'http://lmss.sali.org/R7L5eLIzH0CpOUE74uJvSjL',
            'System Identifiers': 'http://lmss.sali.org/R8EoZh39tWmXCkmP2Xzjl6E',
            'Governmental Body': 'http://lmss.sali.org/RBQGborh1CfXanGZipDL0Qo',
            'Currency': 'http://lmss.sali.org/R767niCLQVC5zIcO5WDQMSl',
            'Location': 'http://lmss.sali.org/R9aSzp9cEiBCzObnP92jYFX',
            'Objectives': 'http://lmss.sali.org/RlNFgB3TQfMzV26V4V7u4E',
            'Asset Type': 'http://lmss.sali.org/RCIwc6WJi6IT7xePURxsi4T',
            'Matter Narrative Format': 'http://lmss.sali.org/R8ONVC8pLVJC5dD4eKqCiZL',
            'Communication Modality': 'http://lmss.sali.org/R8qItBwG2pRMFhUq1HQEMnb',
            'Area of Law': 'http://lmss.sali.org/RSYBzf149Mi5KE0YtmpUmr',
            'Event': 'http://lmss.sali.org/R73hoH1RXYjBTYiGfolpsAF',
            'Matter Narrative': 'http://lmss.sali.org/R7ReDY2v13rer1U8AyOj55L',
            'Standards Compatibility': 'http://lmss.sali.org/RB4cFSLB4xvycDlKv73dOg6',
            'Legal Authorities': 'http://lmss.sali.org/RC1CZydjfH8oiM4W3rCkma3',
            'Industry': 'http://lmss.sali.org/RDIwFaFcH4KY0gwEY0QlMTp'
        }

        # initialize the graph by doing a forward pass on all nodes and building basic trees
        self._init_graph()

    def _init_graph(self):
        """Initialize the graph by doing a forward pass on all nodes and building basic trees."""
        # iterate over all concepts
        for concept in self.subjects(RDF.type, OWL.Class):
            # get the rdf:about attribute
            iri = str(concept)

            # get the rdfs:label value
            label = self.value(concept, RDFS.label).toPython() if self.value(concept, RDFS.label) else None

            # update iri->label and label->iri maps
            self.iri_to_label[iri] = label
            if label not in self.label_to_iri:
                self.label_to_iri[label] = []
            self.label_to_iri[label].append(iri)

            # get the list of all skos:altLabel string literal values
            alt_labels = [alt_label.toPython() for alt_label in self.objects(concept, SKOS.altLabel)]

            # get the list of all skos:hiddenLabel string literal values
            hidden_labels = [hidden_label.toPython() for hidden_label in self.objects(concept, SKOS.hiddenLabel)]

            # get the list of all skos:definition string literal values
            definitions = [definition.toPython() for definition in self.objects(concept, SKOS.definition)]

            # get direct parents
            parents = [str(parent) for parent in self.objects(concept, RDFS.subClassOf)]

            # get direct children
            children = [str(child) for child in self.subjects(RDFS.subClassOf, concept)]

            # build the dictionary to store the concept
            self.concepts[iri] = {
                "iri": iri,
                "label": label,
                "alt_labels": alt_labels,
                "hidden_labels": hidden_labels,
                "definitions": definitions,
                "parents": parents,
                "children": children,
            }

        # build the edgelist for the graph
        for concept in self.concepts.values():
            for parent in concept["parents"]:
                if parent not in self.edges:
                    self.edges[parent] = []
                self.edges[parent].append(concept["iri"])

    def get_top_level_concepts(self) -> set[str]:
        """Get the list of top-level concepts based on the class dict.  Note that some
        "real" top-level concepts are excluded by default, such as deprecated or OWL root
        concepts.

        Returns:
            set[str]: The list of top-level concept IRIs.
        """
        return set(self.top_level_concepts.values())

    def get_children(self, iri: str, max_depth: int | None = None) -> set[str]:
        """Get the list of child IRIs, by default, recursively up to 16 levels deep.
        For first level children, use self.concepts[iri]["children"] or set max_depth=1.

        Args:
            iri (str): The IRI of the concept to get the children of.
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of child IRIs.

        TODO: Decide if we want to use a faster algorithm for loop-handling; see kelvin graph.
        """
        # set the default max depth
        if max_depth is None:
            max_depth = self.default_max_depth

        children = set()

        # iterate through the edgelist
        for child in self.edges.get(iri, []):
            # add the child to the list
            children.add(child)

            # recurse if the max depth has not been reached
            if max_depth > 1:
                children |= self.get_children(child, max_depth - 1)
            elif max_depth == -1:
                children |= self.get_children(child, max_depth)

        return children

    """
    'LMSS Type': 'http://lmss.sali.org/R8uI6AZ9vSgpAdKmfGZKfTZ',
    'Legal Entity': 'http://lmss.sali.org/R7L5eLIzH0CpOUE74uJvSjL',
    'System Identifiers': 'http://lmss.sali.org/R8EoZh39tWmXCkmP2Xzjl6E',
    'Governmental Body': 'http://lmss.sali.org/RBQGborh1CfXanGZipDL0Qo',
    'Currency': 'http://lmss.sali.org/R767niCLQVC5zIcO5WDQMSl',
    'Location': 'http://lmss.sali.org/R9aSzp9cEiBCzObnP92jYFX',
    'Objectives': 'http://lmss.sali.org/RlNFgB3TQfMzV26V4V7u4E',
    'Asset Type': 'http://lmss.sali.org/RCIwc6WJi6IT7xePURxsi4T',
    'Matter Narrative Format': 'http://lmss.sali.org/R8ONVC8pLVJC5dD4eKqCiZL',
    'Communication Modality': 'http://lmss.sali.org/R8qItBwG2pRMFhUq1HQEMnb',
    'Area of Law': 'http://lmss.sali.org/RSYBzf149Mi5KE0YtmpUmr',
    'Event': 'http://lmss.sali.org/R73hoH1RXYjBTYiGfolpsAF',
    'Matter Narrative': 'http://lmss.sali.org/R7ReDY2v13rer1U8AyOj55L',
    'Standards Compatibility': 'http://lmss.sali.org/RB4cFSLB4xvycDlKv73dOg6',
    'Legal Authorities': 'http://lmss.sali.org/RC1CZydjfH8oiM4W3rCkma3',
    'Industry': 'http://lmss.sali.org/RDIwFaFcH4KY0gwEY0QlMTp'
    """

    def get_lmss_types(self, max_depth: int | None = None) -> set[str]:
        """Get the list of LMSS Types.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of LMSS Type IRIs.
        """
        return self.get_children(self.top_level_concepts["LMSS Type"], max_depth)


    def get_legal_entities(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Legal Entities.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Legal Entity IRIs.
        """
        return self.get_children(self.top_level_concepts["Legal Entity"], max_depth)

    def get_system_identifiers(self, max_depth: int | None = None) -> set[str]:
        """Get the list of System Identifiers.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of System Identifier IRIs.
        """
        return self.get_children(self.top_level_concepts["System Identifiers"], max_depth)

    def get_governmental_bodies(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Governmental Bodies.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Governmental Body IRIs.
        """
        return self.get_children(self.top_level_concepts["Governmental Body"], max_depth)

    def get_currencies(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Currencies.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Currency IRIs.
        """
        return self.get_children(self.top_level_concepts["Currency"], max_depth)

    def get_locations(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Locations.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Location IRIs.
        """
        return self.get_children(self.top_level_concepts["Location"], max_depth)

    def get_objectives(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Objectives.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Objective IRIs.
        """
        return self.get_children(self.top_level_concepts["Objectives"], max_depth)

    def get_asset_types(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Asset Types.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Asset Type IRIs.
        """
        return self.get_children(self.top_level_concepts["Asset Type"], max_depth)

    def get_matter_narrative_formats(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Matter Narrative Formats.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Matter Narrative Format IRIs.
        """
        return self.get_children(self.top_level_concepts["Matter Narrative Format"], max_depth)

    def get_communication_modalities(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Communication Modalities.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Communication Modality IRIs.
        """
        return self.get_children(self.top_level_concepts["Communication Modality"], max_depth)

    def get_areas_of_law(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Areas of Law.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Area of Law IRIs.
        """
        return self.get_children(self.top_level_concepts["Area of Law"], max_depth)

    def get_standards_compatibility(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Standards Compatibility.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Standards Compatibility IRIs.
        """
        return self.get_children(self.top_level_concepts["Standards Compatibility"], max_depth)

    def get_legal_authorities(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Legal Authorities.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Legal Authority IRIs.
        """
        return self.get_children(self.top_level_concepts["Legal Authorities"], max_depth)

    def get_industries(self, max_depth: int | None = None) -> set[str]:
        """Get the list of Industries.

        Args:
            max_depth (int): The maximum depth to recurse. Defaults to 8.

        Returns:
            set[str]: The list of Industry IRIs.
        """
        return self.get_children(self.top_level_concepts["Industry"], max_depth)


    def search_labels(self,
                      search_term: str,
                      concept_type: str | None = None,
                      concept_depth: int | None = None,
                      num_results: int = 10,
                      include_alt_labels: bool = True,
                      include_hidden_labels: bool = True
                      ) -> list[dict]:
        """Search the labels of the ontology.

        Args:
            search_term (str): The search term.
            concept_type (str): The concept type to search. Defaults to None.
            concept_depth (int): The depth to search. Defaults to None.
            num_results (int): The number of results to return. Defaults to 10.
            include_alt_labels (bool): Whether to include alternative labels. Defaults to True.
            include_hidden_labels (bool): Whether to include hidden labels. Defaults to True.

        Returns:
            list[dict]: A list of dictionaries containing the concept data and search information including
            whether the match was an exact substring match and the distance
        """
        # get the list of concepts to search
        if concept_type is not None:
            samples = {iri: self.concepts[iri] for iri in self.get_children(concept_type, concept_depth)}
        else:
            samples = self.concepts

        # search the labels
        for iri, concept in samples.items():
            # score
            concept_labels = []
            if concept["label"]:
                concept_labels.append(concept["label"])

            if include_alt_labels and concept["alt_labels"]:
                concept_labels.extend(concept["alt_labels"])

            if include_hidden_labels and concept["hidden_labels"]:
                concept_labels.extend(concept["hidden_labels"])

            # check if the search term is an exact substring match
            concept["exact"] = any([search_term.lower() == label.lower() for label in concept_labels])
            concept["substring"] = any([search_term.lower() in label.lower() for label in concept_labels])

            # check if any labels start with the search term
            concept["starts_with"] = any(
                [label.lower().startswith(search_term.lower()) for label in concept_labels])

            # find the minimum distance between the search term and the concept labels
            if concept["exact"]:
                concept["distance"] = 0
            else:
                concept["distance"] = min(
                    [DamerauLevenshtein.normalized_distance(search_term.lower(), label.lower()) for label in concept_labels]
                ) if len(concept_labels) > 0 else 999

        # sort by distance and return the top 10
        return sorted(
            samples.values(),
            key=lambda x: (-x["exact"], -x["starts_with"], -x["substring"], x["distance"])
        )[:num_results]


    def search_definitions(
            self,
            search_term: str,
            concept_type: str | None = None,
            concept_depth: int | None = None,
            num_results: int = 10,
    ) -> list[dict]:
        """Search the definitions of the ontology using partial token set ratios instead of
        simple string distance functions."""

        # get the list of concepts to search
        if concept_type is not None:
            samples = {iri: self.concepts[iri] for iri in self.get_children(concept_type, concept_depth)}
        else:
            samples = self.concepts

        # search the labels
        for iri, concept in samples.items():
            # score
            if concept["definition"]:
                concept["exact"] = search_term.lower() == concept["definition"].lower()
                concept["substring"] = search_term.lower() in concept["definition"].lower()
                concept["distance"] = rapidfuzz.fuzz.partial_token_set_ratio(search_term.lower(), concept["definition"].lower())
            else:
                concept["exact"] = False
                concept["substring"] = False
                concept["distance"] = 0

        # sort by distance and return the top 10
        return sorted(
            samples.values(),
            key=lambda x: (-x["exact"], -x["substring"], -x["distance"])
        )[:num_results]
