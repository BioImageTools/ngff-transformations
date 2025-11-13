from collections import defaultdict
from typing import Any

import networkx as nx
from ome_zarr_models._utils import TransformGraph


def transform_graph_to_networkx(tgraph: TransformGraph) -> nx.DiGraph:
    """
    Convert a TransformGraph to a NetworkX DiGraph.

    Parameters
    ----------
    tgraph : TransformGraph
        The transformation graph from ome-zarr-models.

    Returns
    -------
    nx.DiGraph
        A NetworkX directed graph representing the coordinate system transformations.
        Nodes represent coordinate systems, and edges represent transformations between them.
        Edge attributes include the transformation object.

    Notes
    -----
    The graph structure:
    - Nodes: coordinate system names (strings)
    - Edges: directed edges from input coordinate system to output coordinate system
    - Edge attributes: {"transformation": Transform object}

    For subgraphs in collections, nodes are prefixed with the collection path.
    """
    g = nx.DiGraph()

    # Add nodes and edges from the main graph
    _add_graph_to_networkx(tgraph, g, path_prefix="")

    # Add any subgraphs (for collections)
    for graph_name, subgraph in tgraph._subgraphs.items():
        # Add subgraph nodes and edges with prefixed names
        _add_graph_to_networkx(subgraph, g, path_prefix=graph_name)

        # Add edge between default coordinate system of subgraph and the collection node
        if subgraph._default_system:
            subgraph_default_node = _node_key(graph_name, subgraph._default_system)
            collection_node = _node_key("", graph_name)
            g.add_edge(
                subgraph_default_node,
                collection_node,
                transformation=None,  # Dashed edge in graphviz, no actual transformation
                edge_type="collection_link",
            )

    return g


def _add_graph_to_networkx(
    tgraph: TransformGraph, g: nx.DiGraph, path_prefix: str = ""
) -> None:
    """
    Add nodes and edges from a TransformGraph to a NetworkX graph.

    Parameters
    ----------
    tgraph : TransformGraph
        The source transformation graph.
    g : nx.DiGraph
        The target NetworkX graph to add nodes and edges to.
    path_prefix : str
        Prefix for node names (used for subgraphs in collections).
    """
    # Add all coordinate systems as nodes
    for cs_name in tgraph._named_systems:
        node_name = _node_key(path_prefix, cs_name)
        g.add_node(
            node_name,
            coordinate_system=tgraph._named_systems[cs_name],
            path=path_prefix,
            is_default=(cs_name == tgraph._default_system),
        )

    # Add transformations as edges
    for input_cs, output_dict in tgraph._graph.items():
        for output_cs, transform in output_dict.items():
            source_node = _node_key(path_prefix, input_cs)
            target_node = _node_key(path_prefix, output_cs)
            g.add_edge(
                source_node,
                target_node,
                transformation=transform,
                edge_type="transformation",
            )


def _node_key(path: str, name: str) -> str:
    """
    Create a unique node identifier from a path and name.

    Parameters
    ----------
    path : str
        The path prefix (empty for top-level, or collection name for subgraphs).
    name : str
        The coordinate system or collection name.

    Returns
    -------
    str
        A unique node identifier.
    """
    if path:
        return f"{path}/{name}"
    return name


def to_graphviz(g: nx.DiGraph) -> Any:
    """
    Convert a NetworkX transformation graph to a Graphviz graph for visualization.

    Parameters
    ----------
    g : nx.DiGraph
        A NetworkX directed graph created by transform_graph_to_networkx().

    Returns
    -------
    graphviz.Digraph
        A Graphviz graph object that can be rendered or saved.

    Notes
    -----
    Requires the `graphviz` package to be installed.

    Examples
    --------
    >>> from ome_zarr_models._v06.image import Image
    >>> import zarr
    >>> image = Image.from_zarr(zarr.open_group("path/to/image.zarr"))
    >>> tgraph = image.transform_graph()
    >>> nx_graph = transform_graph_to_networkx(tgraph)
    >>> gv_graph = to_graphviz(nx_graph)
    >>> gv_graph.render("output", format="png")
    """
    import graphviz

    gv = graphviz.Digraph()

    # Group nodes by path to create subgraphs
    nodes_by_path: dict[str, list[str]] = defaultdict(list)
    for node, data in g.nodes(data=True):
        path = data.get("path", "")
        nodes_by_path[path].append(node)

    # Add main graph nodes
    if "" in nodes_by_path:
        with gv.subgraph(name="cluster_main") as sub:
            for node in nodes_by_path[""]:
                node_data = g.nodes[node]
                label = node
                if node_data.get("is_default", False):
                    label = f"*{label}*"  # Mark default coordinate system
                sub.node(node, label=label)
            if len([p for p in nodes_by_path if p != ""]) > 0:
                sub.attr(label="Top level collection")

    # Add subgraph clusters
    for path in sorted(nodes_by_path.keys()):
        if path == "":
            continue
        with gv.subgraph(name=f"cluster_{path}") as sub:
            for node in nodes_by_path[path]:
                node_data = g.nodes[node]
                label = node.split("/")[-1]  # Show only the local name
                if node_data.get("is_default", False):
                    label = f"*{label}*"  # Mark default coordinate system
                sub.node(node, label=label)
            sub.attr(label=path)

    # Add edges
    for source, target, data in g.edges(data=True):
        edge_type = data.get("edge_type", "transformation")
        if edge_type == "collection_link":
            gv.edge(source, target, arrowhead="none", style="dashed")
        else:
            gv.edge(source, target)

    return gv
