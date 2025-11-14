# adapted from https://raw.githubusercontent.com/ome-zarr-models/ome-zarr-models-py/refs/heads/rfc5/scripts/generate_transform_graphs.py
from pathlib import Path

import pytest
import zarr
from ome_zarr_models._v06.collection import Collection
from ome_zarr_models._v06.coordinate_transforms import Sequence
from ome_zarr_models._v06.image import Image

from ngff_transformations.graph import (
    create_sequence_transformation_from_path,
    get_relative_path,
    transform_graph_to_networkx,
)


EXAMPLE_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "ngff-rfc5-coordinate-transformation-examples"
)


def get_test_zarr_paths(
    data_dir: Path = EXAMPLE_PATH
) -> list[Path]:
    """
    Get all valid test Zarr paths recursively, excluding paths matching the pattern.
    """

    exclude_patterns = [
        "byDimension",
        "scaleParams",
        "translationParams",
        "affineParams",
        "rotationParams",
        ]

    zarrs: list[Path] = []
    for item in data_dir.glob("*"):
        if item.is_dir():
            if item.suffix == ".zarr":
                # Found a Zarr group - add if it doesn't match exclusion pattern
                if not any(pattern in str(item) for pattern in exclude_patterns):
                    zarrs.append(item)
            else:
                # Recurse into subdirectories
                zarrs.extend(get_test_zarr_paths(item))
    return sorted(zarrs)


@pytest.mark.parametrize("zarr_path", get_test_zarr_paths())
def test_graph(zarr_path: Path):
    """
    Test transformation graph creation and functionality
    """
    relative_path = zarr_path.relative_to(EXAMPLE_PATH)

    # Load appropriate group type based on location
    group: Collection | Image
    if relative_path.parts[0] == "user_stories":
        group = Collection.from_zarr(zarr.open_group(zarr_path, mode="r"))
    else:
        group = Image.from_zarr(zarr.open_group(zarr_path, mode="r"))

    # Create and validate graph
    graph = group.transform_graph()
    nx_graph = transform_graph_to_networkx(graph)

    assert len(nx_graph.nodes) > 0

    # Test path finding and sequence creation
    # For now perform path finding between an example edge's nodes
    
    example_edge = list(nx_graph.edges)[0]
    path = get_relative_path(nx_graph, example_edge[0], example_edge[1])
    sequence_transformation = create_sequence_transformation_from_path(nx_graph, path)

    assert isinstance(sequence_transformation, Sequence)
