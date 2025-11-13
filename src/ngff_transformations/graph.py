from collections import defaultdict
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx
from pydantic import ValidationError
from ome_zarr_models._utils import TransformGraph
from ome_zarr_models._v06.coordinate_transforms import CoordinateSystemIdentifier, Transform

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
        Nodes attributes include the coordinate system object.
        Edge attributes include the transformation object.

    Notes
    -----
    The graph structure:
    - Nodes: coordinate system names (strings)
    - Edges: directed edges from input coordinate system to output coordinate system
    - Node attributes: {"coordinate_system": CoordinateSystem object}
    - Edge attributes: {"transformation": Transform object}
    """
    g = nx.DiGraph()


    # Add all named coordinate systems as nodes
    for cs_name in tgraph._named_systems:
        g.add_node(
            cs_name,
            coordinate_system=tgraph._named_systems[cs_name],
        )

    # Add also the named coordinate systems from the subgraphs
    for path_name, subgraph in tgraph._subgraphs.items():
        for cs_name in subgraph._named_systems:
            identifier = CoordinateSystemIdentifier(
                name=cs_name,
                path=path_name,
            )
            g.add_node(
                identifier,
                coordinate_system=subgraph._named_systems[cs_name],
            )

    # finally add the "paths" coordinate systems as nodes
    for path_name, subgraph in tgraph._subgraphs.items():
        for src, edges in subgraph._graph.items():
            for tgt, transform in edges.items():
                input_image = transform.input
                path = f"{path_name}/{input_image}"
                g.add_node(
                    path,
                    coordinate_system=None,
                )

    for src, edges in tgraph._graph.items():
        for tgt, transform in edges.items():
            _add_transform_and_inverse_transformation_edges(
                g,
                src,
                tgt,
                transform,
            )


    for path_name, subgraph in tgraph._subgraphs.items():
        for src, edges in subgraph._graph.items():
            for tgt, transform in edges.items():
                # TODO: hack! Replace
                # TODO: we assume the the subgraph does not contain transformation from the parent graph, so we use the CoordinateSystemIdentifier

                _add_transform_and_inverse_transformation_edges(
                    g=g,
                    input_cs=_get_name_of_subgraph(src, path_name),
                    output_cs=_get_name_of_subgraph(tgt, path_name),
                    transform=transform,
                )
        pass
        # _add_graph_to_networkx(subgraph, g)
        # if subgraph._default_system:
        #     subgraph_default_node = subgraph._default_system
        #     collection_node = graph_name
        #     g.add_edge(
        #         subgraph_default_node,
        #         collection_node,
        #         edge_type="transformation",
        #     )

    return g

def _get_name_of_subgraph(cs_name: str, path_name: str) -> str | CoordinateSystemIdentifier:
    if cs_name in ['0', '1', '2', '3', '4', '5']:
        return f'{path_name}/{cs_name}'
    return CoordinateSystemIdentifier(
        name=cs_name,
        path=path_name,
    )

def _add_transform_and_inverse_transformation_edges(
    g: nx.DiGraph,
    input_cs: str | CoordinateSystemIdentifier,
    output_cs: str | CoordinateSystemIdentifier,
    transform: Transform,
):
    source_node = input_cs
    target_node = output_cs
    g.add_edge(
        source_node,
        target_node,
        transformation=transform,
        edge_type="transformation",
    )
    try:
        inverse = transform.get_inverse()
        g.add_edge(
            target_node,
            source_node,
            transformation=inverse,
            edge_type="transformation",
        )
    except (NotImplementedError, ValidationError):
        pass



def draw_graph(g: nx.DiGraph, figsize: tuple[int, int] = (12, 8), with_edge_labels: bool = True) -> None:
    """
    Draw a NetworkX graph showing all nodes and edges with their names.

    Parameters
    ----------
    g : nx.DiGraph
        The NetworkX directed graph to visualize.
    figsize : tuple[int, int], optional
        Figure size (width, height) in inches. Default is (12, 8).
    with_edge_labels : bool, optional
        Whether to show edge labels (transformation types). Default is True.
    """
    plt.figure(figsize=figsize)

    # Use spring layout for node positioning
    pos = nx.spring_layout(g)

    # Draw nodes
    nx.draw_networkx_nodes(
        g,
        pos,
        node_color='lightblue',
        node_size=3000,
        alpha=0.9
    )

    # Draw node labels (coordinate system names)
    nx.draw_networkx_labels(
        g,
        pos,
        font_size=10,
        font_weight='bold'
    )

    # Draw edges
    nx.draw_networkx_edges(
        g,
        pos,
        edge_color='gray',
        arrows=True,
        arrowsize=20,
        arrowstyle='->',
        width=2,
        connectionstyle='arc3,rad=0.1'
    )

    # Draw edge labels if requested
    if with_edge_labels:
        edge_labels = {}
        for u, v, data in g.edges(data=True):
            edge_type = data.get('edge_type', 'unknown')
            if edge_type == 'transformation' and data.get('transformation'):
                # Get transformation type
                transform = data['transformation']
                transform_type = type(transform).__name__
                edge_labels[(u, v)] = transform_type
            elif edge_type == 'collection_link':
                edge_labels[(u, v)] = 'collection'
            else:
                edge_labels[(u, v)] = edge_type

        nx.draw_networkx_edge_labels(
            g,
            pos,
            edge_labels,
            font_size=8,
            font_color='red'
        )

    plt.axis('off')
    plt.tight_layout()
    plt.show()

