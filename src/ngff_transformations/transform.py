import numpy as np
from ome_zarr_models._v06.coordinate_transforms import Sequence, CoordinateSystemIdentifier
from xarray import DataArray
import networkx as nx


def validata_point_shape(point: np.ndarray, transformation_sequence: Sequence):
    for transformation in transformation_sequence.transformations:
        assert len(point) == transformation.ndim, "Point ndim doesn't match transformation ndim"


def get_node(path: str | None = None, name: str | None = None) -> str | CoordinateSystemIdentifier:
    if path is None and name is None:
        raise ValueError("Both path and name of the coordinate system cannot be None")
    if path is None:
        return name
    if name is None:
        return path
    return CoordinateSystemIdentifier(path=path, name=name)

def find_walks_in_graph(graph, src_path, src_name, tgt_path, tgt_name):
    src_node = get_node(src_path, src_name)
    tgt_node = get_node(tgt_path, tgt_name)

    graph_walk = list(nx.all_shortest_paths(graph, src_node, tgt_node))[0]

    path_edges = []
    path_edges_names = []
    for i in range(len(graph_walk) - 1):
        path_edges.append(graph.get_edge_data(graph_walk[i], graph_walk[i + 1])['transformation'])
        path_edges_names.append((graph_walk[i], graph_walk[i + 1]))

    transformation_sequence = Sequence(
        input=graph_walk[0], 
        output=graph_walk[-1], 
        transformations=path_edges
    )
    return transformation_sequence, (graph_walk[0], graph_walk[-1]), (path_edges_names, graph_walk)

def transform_with_sequence3D(data: np.ndarray, axes: list[str], transformation_sequence: Sequence, 
                            output_axes: list[str]) -> DataArray:
    # locate (inside the graph) the coordinate_system classes from the coordinate_system names
    # first validate the input data wrt to axes and input_coordinate_system
    # 1. check that the data shape is (n x len(axes))
    # 2. check that the axes are the same (and in the same order) of the axes of the input_coordinate_system
    # traverse the graph to find the transformation -> Transform class
    # apply the transformations to the data (code to get inspired from https://github.com/scverse/spatialdata/blob/6652a03b1d66c8902a8f7a159176c51d8c9f823b/src/spatialdata/transformations/operations.py#L212)
    # tranform the data
    # return the transformed data as tuple (numpy array, output axes from the output coordinate systme)

    Y, X, Z, C = data.shape
    yy, xx, zz = np.meshgrid(np.arange(Y), np.arange(X), np.arange(Z), indexing="ij")
    points = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)

    # validata_point_shape(points[0], transformation_sequence)

    transformed_points = np.array([transformation_sequence.transform_point(p) for p in points])
    x_prime = transformed_points[:, 0].reshape(Y, X, Z)
    y_prime = transformed_points[:, 1].reshape(Y, X, Z)
    z_prime = transformed_points[:, 2].reshape(Y, X, Z)

    return DataArray(
        data,
        coords={
            "x_prime": (("y", "x", "z"), x_prime),
            "y_prime": (("y", "x", "z"), y_prime),
            "z_prime": (("y", "x", "z"), z_prime),
        },
        dims=output_axes,
    )


def transform_with_sequence(
    data: np.ndarray, axes: list[str], transformation_sequence: Sequence, output_axes: list[str]
) -> DataArray:
    # locate (inside the graph) the coordinate_system classes from the coordinate_system names
    # first validate the input data wrt to axes and input_coordinate_system
    # 1. check that the data shape is (n x len(axes))
    # 2. check that the axes are the same (and in the same order) of the axes of the input_coordinate_system
    # traverse the graph to find the transformation -> Transform class
    # apply the transformations to the data (code to get inspired from https://github.com/scverse/spatialdata/blob/6652a03b1d66c8902a8f7a159176c51d8c9f823b/src/spatialdata/transformations/operations.py#L212)
    # tranform the data
    # return the transformed data as tuple (numpy array, output axes from the output coordinate systme)

    H, W, C = data.shape
    yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    points = np.stack([xx, yy], axis=-1).reshape(-1, 2)

    validata_point_shape(points[0], transformation_sequence)

    transformed_points = np.array([transformation_sequence.transform_point(p) for p in points])
    x_prime = transformed_points[:, 0].reshape(H, W)
    y_prime = transformed_points[:, 1].reshape(H, W)

    return DataArray(
        data,
        coords={
            "x_prime": (("y", "x"), x_prime),
            "y_prime": (("y", "x"), y_prime),
        },
        dims=output_axes,
    )
