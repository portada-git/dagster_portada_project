from dagster import Definitions, load_assets_from_modules
from assets.boat_fact_ingestion_assets import ingestion
from resources.delta_data_layer_resource import DeltaDataLayerResource
from assets import boat_fact_ingestion_assets

# from .assets.boat_fact_ingestion_assets import ingestion
# from .resources.delta_data_layer_resource import DeltaDataLayerResource
# from .assets import boat_fact_ingestion_assets

from dagster_portada_project import assets  # noqa: TID252

all_assets = load_assets_from_modules([boat_fact_ingestion_assets])

defs = Definitions(
    assets=all_assets,
    resources={
        "datalayer": DeltaDataLayerResource()
    },
    jobs=[ingestion]
)

# from pathlib import Path
# import dagster as dg
#
# from dagster_portada_project.assets.boat_fact_ingestion_assets import ingestion
# from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource
#
# data_layer = DeltaDataLayerResource()
#
# defs = dg.load_from_defs_folder(project_root=Path(__file__).parent).merge(
#     dg.Definitions(
#         jobs=[ingestion],
#         resources={"datalayer": data_layer}
#     )
# )
