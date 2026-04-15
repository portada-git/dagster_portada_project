import json
import os
import platform
from dagster_graphql import DagsterGraphQLClient

if __name__ == "__main__":
    so = platform.system()
    if so == "Darwin":
        mapping = "/Users/josepcanellas/PycharmProjects/dagster_portada_project/config/mapping_to_clean_chars.json"
        schema = "/Users/josepcanellas/PycharmProjects/dagster_portada_project/config/schema.json"
        config_path = "/Users/josepcanellas/PycharmProjects/dagster_portada_project/dagster_portada_project_tests/delta_data_layer_config_linux.json"
    else:
        mapping = "/home/josep/PycharmProjects/dagster_portada_project/config/mapping_to_clean_chars.json"
        schema = "/home/josep/PycharmProjects/dagster_portada_project/config/schema.json"
        config_path = "/home/josep/PycharmProjects/dagster_portada_project/dagster_portada_project_tests/delta_data_layer_config_linux.json"

    if os.path.exists(mapping):
        with open(mapping) as f:
            mapping_json = json.load(f)
    if os.path.exists(schema):
        with open(schema) as f:
            schema_json = json.load(f)

    client = DagsterGraphQLClient(hostname="localhost", port_number=3000)
    client.submit_job_execution(
        job_name="boat_fact_cleaning",
        run_config={
            "ops": {"first_entry_cleaning": {"config": {"mapping_to_clean_chars": mapping_json, "schema": schema_json}}},
            "resources": {
                "datalayer": {
                    "config": {
                        "config_path": config_path,
                        "job_name": "cleaning",
                    }
                }
            }
        }
    )
