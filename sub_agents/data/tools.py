import os
import inspect
from typing import Optional
from google.adk.tools.bigquery import BigQueryCredentialsConfig, BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default

def _as_int(name: str, default: Optional[int] = None) -> Optional[int]:
    v = _env(name)
    if v is None:
        return default
    try:
        return int(v)
    except ValueError:
        return default

# Environment Config
PROJECT_ID = _env("GOOGLE_CLOUD_PROJECT")
BQ_LOCATION = _env("BQ_LOCATION", _env("GOOGLE_CLOUD_LOCATION"))
DEFAULT_DATASET = _env("DEFAULT_DATASET")
MAX_BYTES_BILLED = _as_int("MAX_BYTES_BILLED")
GOOGLE_APPLICATION_CREDENTIALS = _env("GOOGLE_APPLICATION_CREDENTIALS")

def _safe_build_tool_config() -> BigQueryToolConfig:
    """Safely builds BigQueryToolConfig handling version differences."""
    # BigQueryToolConfig is experimental and changes between versions.
    try:
        cfg = BigQueryToolConfig(
            write_mode=WriteMode.BLOCKED,
            max_query_result_rows=200,
            application_name="tami4-data-agent",
        )
    except Exception:
        cfg = BigQueryToolConfig()
        # Fallback mechanism for different ADK versions
        if hasattr(cfg, "write_mode"):
            try:
                cfg.write_mode = WriteMode.BLOCKED
            except Exception: pass
        if hasattr(cfg, "max_query_result_rows"):
            try:
                cfg.max_query_result_rows = 200
            except Exception: pass
        if hasattr(cfg, "application_name"):
            try:
                cfg.application_name = "tami4-data-agent"
            except Exception: pass

    # Optional fields
    if BQ_LOCATION is not None:
        for attr in ("location", "bigquery_location"):
            if hasattr(cfg, attr):
                try: setattr(cfg, attr, BQ_LOCATION)
                except Exception: pass

    if DEFAULT_DATASET is not None:
        for attr in ("default_dataset", "dataset", "default_dataset_id"):
            if hasattr(cfg, attr):
                try: setattr(cfg, attr, DEFAULT_DATASET)
                except Exception: pass

    if MAX_BYTES_BILLED is not None:
        for attr in ("maximum_bytes_billed", "max_bytes_billed", "max_bytes_billed_per_query"):
            if hasattr(cfg, attr):
                try: setattr(cfg, attr, MAX_BYTES_BILLED)
                except Exception: pass

    return cfg

def _load_google_credentials():
    """Returns a google.auth credentials object."""
    import google.auth 
    from google.auth import exceptions as google_auth_exceptions

    # 1) Service account JSON
    if GOOGLE_APPLICATION_CREDENTIALS:
        path = os.path.abspath(GOOGLE_APPLICATION_CREDENTIALS)
        if not os.path.exists(path):
            raise FileNotFoundError(f"GOOGLE_APPLICATION_CREDENTIALS points to missing file: {path}")
        
        scopes = ["https://www.googleapis.com/auth/bigquery"]
        creds, _ = google.auth.load_credentials_from_file(path, scopes=scopes)
        return creds

    # 2) ADC
    try:
        scopes = ["https://www.googleapis.com/auth/bigquery"]
        creds, _ = google.auth.default(scopes=scopes)
        return creds
    except google_auth_exceptions.DefaultCredentialsError as e:
        raise RuntimeError(
            "No Google credentials found. Set GOOGLE_APPLICATION_CREDENTIALS or configure ADC."
        ) from e

def _build_credentials_config() -> BigQueryCredentialsConfig:
    creds = _load_google_credentials()
    sig = inspect.signature(BigQueryCredentialsConfig)
    if "credentials" in sig.parameters:
        return BigQueryCredentialsConfig(credentials=creds)
    return BigQueryCredentialsConfig(credentials=creds)

def get_bigquery_toolset() -> BigQueryToolset:
    """Builds and returns the configured BigQueryToolset."""
    tool_config = _safe_build_tool_config()
    credentials_config = _build_credentials_config()

    return BigQueryToolset(
        credentials_config=credentials_config,
        bigquery_tool_config=tool_config,
        tool_filter=[
            "list_dataset_ids",
            "get_dataset_info",
            "list_table_ids",
            "get_table_info",
            "execute_sql",
        ],
    )
