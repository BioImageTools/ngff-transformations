# adapted from https://raw.githubusercontent.com/ome-zarr-models/ome-zarr-models-py/refs/heads/rfc5/scripts/generate_transform_graphs.py
from pathlib import Path

import zarr

from ome_zarr_models._v06.collection import Collection
from ome_zarr_models._v06.image import Image

EXAMPLE_PATH = (
    Path(__file__).parent.parent
    / "data"
    / "ngff-rfc5-coordinate-transformation-examples"
)


def get_all_zarrs(directory: Path) -> list[Path]:
    """
    Get all Zarr sub-directories.
    """
    zarrs: list[Path] = []
    for f in directory.glob("*"):
        if f.is_dir():
            if f.suffix == ".zarr":
                # Found a Zarr group
                zarrs.append(f)
            else:
                # Recurse
                zarrs += get_all_zarrs(f)

    return sorted(zarrs)


for zarr_path in get_all_zarrs(EXAMPLE_PATH):
    relative_path = zarr_path.relative_to(EXAMPLE_PATH)

    group: Collection | Image
    try:
        if relative_path.parts[0] == "user_stories":
            group = Collection.from_zarr(zarr.open_group(zarr_path, mode="r"))
        else:
            group = Image.from_zarr(zarr.open_group(zarr_path, mode="r"))
    except Exception:
        print(f"😢 Failed to load group at {zarr_path.relative_to(EXAMPLE_PATH)}")
        continue

    print(f"📈 Rendering transform graph for {zarr_path.relative_to(EXAMPLE_PATH)}")
    graph = group.transform_graph()
    graphviz_graph = graph.to_graphviz()
    from PIL import Image as PILImage
    import io

    png_bytes = graphviz_graph.pipe(format="png")

    PILImage.open(io.BytesIO(png_bytes)).show()  # uses default image viewer

    pass



