"""
MLflow observability for chatbot query logging and dashboard metrics.
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ChatbotObserver:
    """Logs chatbot queries and metrics to MLflow."""

    def __init__(self, experiment_name: str = "chatbot_observability"):
        self.experiment_name = experiment_name
        self.enabled = False

        try:
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlflow_runs")
            os.environ.setdefault("MLFLOW_ALLOW_FILE_STORE", "true")
            import mlflow

            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(experiment_name)
            self.enabled = True
        except Exception as e:
            logger.warning(f"MLflow observability disabled: {e}")
            self.enabled = False

    def log_query(
        self,
        query: str,
        response: str,
        retrieved_chunks: List[Any],
        latency_ms: float,
        llm_type: str,
        tokens_estimated: int,
    ) -> None:
        """Log a single chat turn to MLflow."""
        if not self.enabled:
            return

        try:
            import mlflow

            chunks_count = len(retrieved_chunks)
            relevance_score = 1.0 if chunks_count > 0 else 0.0

            with mlflow.start_run(run_name="chat_turn"):
                mlflow.log_param("llm_type", llm_type)
                mlflow.log_param("chunks_retrieved", chunks_count)
                mlflow.log_metric("latency_ms", latency_ms)
                mlflow.log_metric("tokens_estimated", tokens_estimated)
                mlflow.log_metric("response_length", len(response))
                mlflow.log_metric("query_length", len(query))
                mlflow.log_metric("chunks_retrieved", chunks_count)
                mlflow.log_metric("relevance_score", relevance_score)
        except Exception as e:
            logger.warning(f"Failed to log query to MLflow: {e}")

    def get_summary_stats(self) -> Dict[str, float]:
        """Return aggregate stats for all logged chat turns."""
        empty_stats = {
            "total_queries": 0,
            "avg_latency_ms": 0.0,
            "avg_chunks_retrieved": 0.0,
            "avg_response_length": 0.0,
            "avg_relevance_score": 0.0,
        }

        if not self.enabled:
            return empty_stats

        try:
            import mlflow

            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                return empty_stats

            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time ASC"],
            )

            if runs.empty:
                return empty_stats

            return {
                "total_queries": float(len(runs)),
                "avg_latency_ms": float(runs["metrics.latency_ms"].mean()),
                "avg_chunks_retrieved": float(runs["metrics.chunks_retrieved"].mean()),
                "avg_response_length": float(runs["metrics.response_length"].mean()),
                "avg_relevance_score": float(runs["metrics.relevance_score"].mean()),
            }
        except Exception as e:
            logger.warning(f"Failed to fetch MLflow summary stats: {e}")
            return empty_stats

    def get_runs_dataframe(self):
        """Return a pandas DataFrame of logged runs for dashboard charts."""
        try:
            import mlflow
            import pandas as pd

            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                return pd.DataFrame()

            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                order_by=["start_time ASC"],
            )

            if runs.empty:
                return pd.DataFrame()

            df = pd.DataFrame({
                "run_number": range(1, len(runs) + 1),
                "latency_ms": runs["metrics.latency_ms"].tolist(),
                "chunks_retrieved": runs["metrics.chunks_retrieved"].tolist(),
                "response_length": runs["metrics.response_length"].tolist(),
                "relevance_score": runs["metrics.relevance_score"].tolist(),
            })
            return df
        except Exception as e:
            logger.warning(f"Failed to fetch MLflow runs dataframe: {e}")
            try:
                import pandas as pd
                return pd.DataFrame()
            except ImportError:
                return None
