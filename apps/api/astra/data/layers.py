"""The map layer catalogue.

Layers are declared here with an honest ``available`` flag. A layer whose
producing slice has not landed is listed but disabled, so the interface shows
what ASTRA will offer without ever rendering an empty layer as if it held data.

Availability is not a promise: a layer flips to ``available`` only once the
datasets it names exist in the provenance registry, which
:func:`astra.data.validate.validate_dataset` enforces.
"""

from __future__ import annotations

from astra.domain.enums import ProvenanceClass
from astra.domain.models import LayerDescriptor

LAYER_CATALOGUE: list[LayerDescriptor] = [
    LayerDescriptor(
        id="terrain.hillshade",
        title="Terrain and hillshade",
        description="Elevation-derived relief for the study corridor.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m"],
        geometry_type="raster",
        available=False,
        unit="m",
        default_visible=True,
    ),
    LayerDescriptor(
        id="terrain.slope",
        title="Slope",
        description="Slope angle computed from the digital elevation model.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m"],
        geometry_type="raster",
        available=False,
        unit="degrees",
    ),
    LayerDescriptor(
        id="hydrology.drainage",
        title="Drainage network",
        description="Stream network extracted from the DEM and OSM waterways.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "osm-extract"],
        geometry_type="line",
        available=False,
    ),
    LayerDescriptor(
        id="hydrology.hand",
        title="Height above nearest drainage",
        description="HAND surface driving the flood susceptibility sub-model.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m"],
        geometry_type="raster",
        available=False,
        unit="m",
    ),
    LayerDescriptor(
        id="landcover.worldcover",
        title="Land cover",
        description="ESA WorldCover classes, reclassified to buildable and protected.",
        provenance=ProvenanceClass.REAL_OPEN,
        dataset_ids=["esa-worldcover-10m"],
        geometry_type="raster",
        available=False,
    ),
    LayerDescriptor(
        id="hazard.landslide",
        title="Landslide susceptibility",
        description="Weighted overlay of slope, ruggedness, incident density, rainfall.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "landslide-inventory", "rainfall-gridded"],
        geometry_type="raster",
        available=False,
        unit="index 0-100",
    ),
    LayerDescriptor(
        id="hazard.flood",
        title="Flood susceptibility",
        description="HAND, drainage proximity, historical inundation and rainfall.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "rainfall-gridded"],
        geometry_type="raster",
        available=False,
        unit="index 0-100",
    ),
    LayerDescriptor(
        id="hazard.cloudburst",
        title="Cloudburst and flash-flood susceptibility",
        description="Extreme rainfall frequency, catchment steepness and confluences.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "rainfall-gridded"],
        geometry_type="raster",
        available=False,
        unit="index 0-100",
    ),
    LayerDescriptor(
        id="hazard.composite",
        title="Multi-hazard composite",
        description="Dominance-preserving composite of the per-hazard surfaces.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "landslide-inventory", "rainfall-gridded"],
        geometry_type="raster",
        available=False,
        unit="index 0-100",
        default_visible=True,
    ),
    LayerDescriptor(
        id="hazard.red_zones",
        title="Red zones (ASTRA analytical classification)",
        description=(
            "Thresholded, cleaned and buffered composite polygons. An ASTRA "
            "analytical classification, not a statutory designation."
        ),
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "landslide-inventory", "rainfall-gridded"],
        geometry_type="polygon",
        available=False,
        default_visible=True,
    ),
    LayerDescriptor(
        id="hazard.confidence",
        title="Evidence confidence",
        description="Where the evidence is thin. Rendered distinctly, never as certainty.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["srtm-dem-30m", "landslide-inventory"],
        geometry_type="raster",
        available=False,
    ),
    LayerDescriptor(
        id="history.incidents",
        title="Historical incidents",
        description="Recorded landslide and flood incident points with severity and date.",
        provenance=ProvenanceClass.REAL_OPEN,
        dataset_ids=["landslide-inventory"],
        geometry_type="point",
        available=False,
    ),
    LayerDescriptor(
        id="exposure.habitations",
        title="Habitations",
        description=(
            "Synthetic, terrain-calibrated settlements with fictional names. Not real "
            "villages."
        ),
        provenance=ProvenanceClass.SYNTHETIC_CALIBRATED,
        dataset_ids=["astra-habitations"],
        geometry_type="point",
        available=False,
        default_visible=True,
    ),
    LayerDescriptor(
        id="sites.candidates",
        title="Candidate relocation sites",
        description="Synthetic candidate sites with modelled service supply.",
        provenance=ProvenanceClass.SYNTHETIC_CALIBRATED,
        dataset_ids=["astra-sites"],
        geometry_type="polygon",
        available=False,
        default_visible=True,
    ),
    LayerDescriptor(
        id="network.roads",
        title="Road network",
        description="OpenStreetMap road graph with bridge dependency flags.",
        provenance=ProvenanceClass.REAL_OPEN,
        dataset_ids=["osm-extract"],
        geometry_type="line",
        available=False,
    ),
    LayerDescriptor(
        id="network.routes",
        title="Evaluated routes",
        description="Fastest and safest routes with per-route reliability.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["osm-extract"],
        geometry_type="line",
        available=False,
    ),
    LayerDescriptor(
        id="plan.assignments",
        title="Optimised assignments",
        description="Solver output: who moves where, in which phase.",
        provenance=ProvenanceClass.DERIVED,
        dataset_ids=["astra-habitations", "astra-sites"],
        geometry_type="line",
        available=False,
    ),
]

LAYERS_BY_ID: dict[str, LayerDescriptor] = {layer.id: layer for layer in LAYER_CATALOGUE}
