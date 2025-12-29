import io
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google.genai import types
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

def _payload_to_df(data_payload: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts a flexible data payload (dict-rows or list-rows) into a pandas DataFrame.
    """
    # 1. Try "data" key wrapper first
    data = data_payload.get("data", data_payload)
    
    cols = data.get("columns") or []
    
    # Case A: No explicit columns, check for list of dicts in 'rows'
    if not cols:
        rows = data.get("rows") or []
        if rows and isinstance(rows[0], dict):
            return pd.DataFrame(rows)
        # If no columns and no dict-rows, return empty DF to handle gracefully
        return pd.DataFrame()

    # Case B: Compact rows (list of lists)
    if data.get("rows_compact"):
        return pd.DataFrame(data["rows_compact"], columns=cols)

    # Case C: Standard rows
    rows = data.get("rows") or []
    if rows and isinstance(rows[0], dict):
        return pd.DataFrame(rows)
    
    return pd.DataFrame(rows, columns=cols)


def _fig_to_png_bytes(fig: plt.Figure) -> bytes:
    """Converts a Matplotlib figure to PNG bytes."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    return buf.getvalue()


async def plot_and_save_artifacts(
    plotting_handoff: Dict[str, Any],
    data_payload: Dict[str, Any],
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """
    Generates plots based on data and saves them as artifacts in the session.
    
    Args:
        plotting_handoff: Instructions for plotting (preferred metrics, x-axis, etc.).
        data_payload: The actual data to plot.
        tool_context: ADK context for saving artifacts.
        
    Returns:
        A dictionary containing the status and a list of generated artifact references.
    """
    try:
        df = _payload_to_df(data_payload)
        if df.empty:
            return {"status": "ERROR", "error": {"message": "Empty DataFrame, cannot plot."}}

        # Basic configurations
        metrics = plotting_handoff.get("preferred_metrics", [])
        x_col = plotting_handoff.get("preferred_time_column")
        
        # Fallback if x_col is missing or not in DF
        if not x_col or x_col not in df.columns:
            # Try to guess a date column
            date_candidates = [c for c in df.columns if "date" in c.lower() or "day" in c.lower()]
            x_col = date_candidates[0] if date_candidates else df.columns[0]

        # Ensure we have metrics to plot
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        y_cols = [m for m in metrics if m in numeric_cols]
        if not y_cols and numeric_cols:
            y_cols = numeric_cols[:2]  # Default to first 2 numeric columns if preference not found

        if not y_cols:
            return {"status": "ERROR", "error": {"message": "No numeric columns found to plot."}}

        artifacts = []
        warnings = []

        # --- Plot Generation Logic ---
        # 1. Time Series Plot (if x_col looks like time)
        if "date" in x_col.lower() or "day" in x_col.lower():
            try:
                df[x_col] = pd.to_datetime(df[x_col])
                df = df.sort_values(x_col)
            except Exception:
                pass  # Keep as is if not convertible

            fig, ax = plt.subplots(figsize=(10, 6))
            for y_c in y_cols:
                sns.lineplot(data=df, x=x_col, y=y_c, label=y_c, ax=ax, marker="o")
            
            ax.set_title(f"Trends over time ({', '.join(y_cols)})")
            ax.set_xlabel(x_col)
            ax.set_ylabel("Value")
            plt.xticks(rotation=45)
            plt.tight_layout()

            # Save Artifact
            filename = "trend_plot.png"
            png_bytes = _fig_to_png_bytes(fig)
            
            artifact_part = types.Part(
                inline_data=types.Blob(data=png_bytes, mime_type="image/png")
            )
            version = await tool_context.save_artifact(filename=filename, artifact=artifact_part)
            
            artifacts.append({
                "filename": filename,
                "title": "Trend Analysis",
                "mime_type": "image/png",
                "version": version
            })

        # 2. Bar Chart (Comparison)
        fig, ax = plt.subplots(figsize=(10, 6))
        # Determine a categorical column for grouping if possible
        cat_cols = df.select_dtypes(include=["object", "string", "category"]).columns.tolist()
        cat_col = cat_cols[0] if cat_cols else x_col

        # If too many categories, take top 10
        if df[cat_col].nunique() > 15:
            top_df = df.head(15)
        else:
            top_df = df

        top_df.plot(kind="bar", x=cat_col, y=y_cols, ax=ax)
        ax.set_title(f"Comparison by {cat_col}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        filename = "bar_comparison.png"
        png_bytes = _fig_to_png_bytes(fig)
        
        artifact_part = types.Part(
            inline_data=types.Blob(data=png_bytes, mime_type="image/png")
        )
        version = await tool_context.save_artifact(filename=filename, artifact=artifact_part)
        
        artifacts.append({
            "filename": filename,
            "title": "Metric Comparison",
            "mime_type": "image/png",
            "version": version
        })

        return {
            "status": "SUCCESS",
            "artifacts": artifacts,
            "warnings": warnings
        }

    except Exception as e:
        logger.error(f"Visualization error: {e}", exc_info=True)
        return {"status": "ERROR", "error": {"message": str(e)}}
