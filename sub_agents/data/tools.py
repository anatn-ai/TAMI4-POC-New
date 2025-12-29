import os
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

def get_bigquery_toolset():
    config = BigQueryToolConfig(
        write_mode=WriteMode.BLOCKED,
        application_name="tami4-data-agent",
        project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("BQ_LOCATION", "US")
    )
    return BigQueryToolset(bigquery_tool_config=config)
