import numpy as np
from xarray import DataArray
import networkx as nx

def transform(data: np.ndarray, axes: list[str], transformation_graph: nx.DiGraph, input_coordinate_system_name: str, output_coordinate_system_name: str) -> DataArray:
    pass
    # locate (inside the graph) the coordinate_system classes from the coordinate_system names
    # first validate the input data wrt to axes and input_coordinate_system
        # 1. check that the data shape is (n x len(axes))
        # 2. check that the axes are the same (and in the same order) of the axes of the input_coordinate_system
    # traverse the graph to find the transformation -> Transform class
    # apply the transformations to the data (code to get inspired from https://github.com/scverse/spatialdata/blob/6652a03b1d66c8902a8f7a159176c51d8c9f823b/src/spatialdata/transformations/operations.py#L212)
    # tranform the data
        # return the transformed data as tuple (numpy array, output axes from the output coordinate systme)
