import numpy as np
from xarray import DataArray
import networkx as nx
import ome_zarr_models as ozm


def validata_point_shape(point: np.ndarray, transformation_sequence: ozm._v06.coordinate_transforms.Sequence):
    for transformation in transformation_sequence.transformations:
        assert len(point) == transformation.ndim, "Point ndim doesn't match transformation ndim"

def transform_with_sequence(data: np.ndarray, transformation_sequence: ozm._v06.coordinate_transforms.Sequence, 
                            output_axes: list[str]) -> DataArray:
    # locate (inside the graph) the coordinate_system classes from the coordinate_system names
    # first validate the input data wrt to axes and input_coordinate_system
        # 1. check that the data shape is (n x len(axes))
        # 2. check that the axes are the same (and in the same order) of the axes of the input_coordinate_system
    # traverse the graph to find the transformation -> Transform class
    # apply the transformations to the data (code to get inspired from https://github.com/scverse/spatialdata/blob/6652a03b1d66c8902a8f7a159176c51d8c9f823b/src/spatialdata/transformations/operations.py#L212)
    # tranform the data
        # return the transformed data as tuple (numpy array, output axes from the output coordinate systme)
    
    H, W, C = data.shape
    yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing='ij')
    points = np.stack([xx, yy], axis=-1).reshape(-1, 2)

    validata_point_shape(points[0], transformation_sequence)

    transformed_points = np.array([transformation_sequence.transform_point(p) for p in points])
    x_prime = transformed_points[:, 0].reshape(H, W)
    y_prime = transformed_points[:, 1].reshape(H, W)

    return xarray.DataArray(data, 
                            coords={
                                "x_prime": (("y", "x"), x_prime),
                                "y_prime": (("y", "x"), y_prime),
                            },
                            dims=output_axes)
