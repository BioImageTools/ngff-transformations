##
import xarray
from spatialdata.transformations import (
    Affine,
    get_transformation,
    set_transformation,
    Sequence,
    Scale,
    Translation,
)
from spatialdata.datasets import blobs
from xarray import DataArray
import numpy as np

sdata = blobs()

image = sdata["blobs_image"]
x = sdata["blobs_image"].x
msi = sdata["blobs_multiscale_image"]
msi["/scale0"]

get_transformation(image, get_all=True)
x

# affine = Affine(
#     [[1, 2, 3], [4, 5, 6], [0, 0, 1]], input_axes=("x", "y"), output_axes=("x", "y")
# )
affine = Sequence(
    [Scale([2, 3], axes=("x", "y")), Translation([2, 3], axes=("x", "y"))]
)
set_transformation(image, affine, "aligned")


def ngff_to_xarray_single_scale(
    image: np.ndarray, transformation: Affine
) -> xarray.DataArray:
    """
    the input is in pixel coordinates

    """
    pass


def xarray_single_scale_to_ngff(image: xarray.DataArray) -> tuple[np.ndarray, Affine]:
    """
    the input is in pixel coordinates

    """
    pass


def ngff_to_xarray_multiscale(
    image: list[np.ndarray], transformation: Affine
) -> xarray.DataTree:
    """
    the input is in pixel coordinates, each image is a different downscale levle of the same image pyramid and the
    center of each image is aligned

    """
    pass


def xarray_multiscale_to_ngff(
    image: xarray.DataTree,
) -> tuple[list[np.ndarray], Affine]:
    pass
