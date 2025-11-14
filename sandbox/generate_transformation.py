"""Example: Create a sequence transformation mapping x, y -> a, b"""

from ome_zarr_models._v06.coordinate_transforms import (
    Axis,
    CoordinateSystem,
    Scale,
    Sequence,
    Translation,
)

# Define input coordinate system (x, y)
input_cs = CoordinateSystem(
    name="xy_space",
    axes=(
        Axis(name="x", type="space", unit="micrometer"),
        Axis(name="y", type="space", unit="micrometer"),
    ),
)

# Define output coordinate system (a, b)
output_cs = CoordinateSystem(
    name="ab_space",
    axes=(
        Axis(name="a", type="space", unit="micrometer"),
        Axis(name="b", type="space", unit="micrometer"),
    ),
)

scale_transform = Scale(
    scale=(2.0, 3.0),
)

translation_transform = Translation(
    translation=(10.0, 20.0),
)

sequence_transform = Sequence(
    input="xy_space",
    output="ab_space",
    transformations=(scale_transform, translation_transform),
)

# Print the sequence
print("Sequence transformation:")
print(sequence_transform.model_dump_json(indent=2))


# Get inverse transformation
inverse_sequence = sequence_transform.get_inverse()
print("\nInverse sequence:")
print(f"  Input: {inverse_sequence.input}")
print(f"  Output: {inverse_sequence.output}")
print(f"  Transforms: {[t.type for t in inverse_sequence.transformations]}")
