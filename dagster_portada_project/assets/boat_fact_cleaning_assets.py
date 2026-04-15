from dagster import asset
from portada_data_layer import BoatFactCleaning

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig


@asset
def first_entry_cleaning(context, datalayer: DeltaDataLayerResource, redis_config: RedisConfig):
    """Read local JSON file"""
    mapping_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["mapping_to_clean_chars"]
    schema_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["schema"]
    if "force_all" in context.run_config["ops"]["first_entry_cleaning"]["config"]:
        force_all = context.run_config["ops"]["first_entry_cleaning"]["config"]["force_all"].lower() in ['true', '1', 't', 'y', 'yes', 'si', 's', 'cierto', 'c']
    else:
        force_all = False

    layer = datalayer.get_cleaning_boat_fact_layer(schema_json, mapping_json)
    layer.set_redis_params(redis_config.host, redis_config.port)
    layer.start_session()
    df = layer.read_raw_entries(force_all=force_all)
    # 1.- Completar la estructura aceptada sin eliminar campos no aceptados
    df = layer.complete_accepted_structure(df)
    # 2.- Normalize structure
    df = layer.normalize_field_structure(df)
    # 3.- save original values
    layer.save_original_values_of_ship_entries(df)
    context.log.info(f"First claning copmpleted for {df.count()} registers of entry ships")

@asset(deps=[first_entry_cleaning])
def last_entry_cleaning(context, datalayer: DeltaDataLayerResource, redis_config: RedisConfig):
    """Read local JSON file"""
    mapping_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["mapping_to_clean_chars"]
    schema_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["schema"]

    layer = datalayer.get_cleaning_boat_fact_layer(schema_json, mapping_json)
    layer.set_redis_params(redis_config.host, redis_config.port)
    layer.start_session()
    df = layer.read_original_values_of_ship_entries()
    if df.count() > 0:
        # 4.- For null fields, fill fields from schema instructions
        df = layer.fill_with_schema(df)
        context.log.info(f"Filled entries with schema")
        # 5.- prune unaccepted fields
        df = layer.prune_unaccepted_fields(df)
        context.log.info(f"pruned unaccepted fields")
        # 6.- simplify field structure with single values for original fields
        df = layer.simplify_field_structure(df)
        context.log.info(f"field structure simplified")
        # 7.- Resolve idem/id/id. with the value of the predecessor record
        df = layer.resolve_idems(df)
        context.log.info(f"idems resolved")
        # 8.- Normalize values
        df = layer.clean_field_values_from_schema(df)
        context.log.info(f"fields cleaned")
        # 9.- If null or error, calculate values from schema instructions
        df = layer.calculate_from_schema(df)
        context.log.info(f"fields calculated")
        # 10.- Convert values form string to corrected type
        df = layer.string_to_type_from_schema(df)
        context.log.info(f"string types to schema types changed")
        # 11.- Normalize string types
        df = layer.normalize_strings_for_ship_entries(df)
        context.log.info(f"normalized strings for ship entries")
        # 12.- Save cleaned values
        layer.save_ship_entries(df, is_cleaned=True)

@asset
def know_entities_cleaning(context, datalayer: DeltaDataLayerResource, redis_config: RedisConfig):
    mapping_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["mapping_to_clean_chars"]
    schema_json = context.run_config["ops"]["first_entry_cleaning"]["config"]["schema"]
    if "force_all" in context.run_config["ops"]["first_entry_cleaning"]["config"]:
        force_all = context.run_config["ops"]["first_entry_cleaning"]["config"]["force_all"].lower() in ['true', '1', 't', 'y', 'yes', 'si', 's', 'cierto', 'c']
    else:
        force_all = False
    layer = datalayer.get_cleaning_boat_fact_layer(schema_json, mapping_json)
    layer.set_redis_params(redis_config.host, redis_config.port)
    layer.start_session()
    for entities in BoatFactCleaning.ENTITY_LIST:
        df = layer.read_raw_entities(entities, force_all=force_all)
        if df.count() > 0:
            df = layer.normalize_strings_for_entities(df)
            layer.save_entities(entity=entities, df=df, is_cleaned=True)
        context.log.info(f"normalized strings for entity {entities}")


