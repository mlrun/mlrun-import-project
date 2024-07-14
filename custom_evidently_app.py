import datetime
import pandas as pd
import mlrun
from sklearn.datasets import load_iris
from mlrun.common.schemas.model_monitoring.constants import (
    ResultKindApp,
    ResultStatusApp,
)
from mlrun.model_monitoring.application import ModelMonitoringApplicationResult
from mlrun.model_monitoring.evidently_application import EvidentlyModelMonitoringApplicationBase
from evidently.metrics import (
    ColumnDriftMetric,
    ColumnSummaryMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.metric_preset import DataQualityPreset
from evidently.report import Report
from evidently.test_preset import DataDriftTestPreset
from evidently.test_suite import TestSuite
from evidently.ui.type_aliases import STR_UUID


class CustomEvidentlyMonitoringApp(EvidentlyModelMonitoringApplicationBase):
    NAME = "evidently-app-test"

    def __init__(self, evidently_workspace_path: str, evidently_project_id: STR_UUID):
        super().__init__(evidently_workspace_path, evidently_project_id)
        self._init_evidently_project()
        self._init_iris_data()

    def _init_iris_data(self) -> None:
        iris = load_iris()
        self.columns = [
            "sepal_length_cm",
            "sepal_width_cm",
            "petal_length_cm",
            "petal_width_cm",
        ]
        self.train_set = pd.DataFrame(iris.data, columns=self.columns)

    def _init_evidently_project(self) -> None:
        if self.evidently_project is None:
            if isinstance(self.evidently_project_id, str):
                self.evidently_project_id = UUID(self.evidently_project_id)
            self.evidently_project = _create_evidently_project(
                self.evidently_workspace, self.evidently_project_id
            )

    def do_tracking(
        self,
        application_name: str,
        sample_df_stats: mlrun.common.model_monitoring.helpers.FeatureStats,
        feature_stats: mlrun.common.model_monitoring.helpers.FeatureStats,
        sample_df: pd.DataFrame,
        start_infer_time: pd.Timestamp,
        end_infer_time: pd.Timestamp,
        latest_request: pd.Timestamp,
        endpoint_id: str,
        output_stream_uri: str,
    ) -> ModelMonitoringApplicationResult:
        self.context.logger.info("Running evidently app")

        sample_df = sample_df[self.columns]

        data_drift_report = self.create_report(sample_df, end_infer_time)
        self.evidently_workspace.add_report(
            self.evidently_project_id, data_drift_report
        )
        data_drift_test_suite = self.create_test_suite(sample_df, end_infer_time)
        self.evidently_workspace.add_test_suite(
            self.evidently_project_id, data_drift_test_suite
        )

        self.log_evidently_object(data_drift_report, f"report_{str(end_infer_time)}")
        self.log_evidently_object(data_drift_test_suite, f"suite_{str(end_infer_time)}")
        self.log_project_dashboard(None, end_infer_time + datetime.timedelta(minutes=1))

        self.context.logger.info("Logged evidently objects")
        return ModelMonitoringApplicationResult(
            name="data_drift_test",
            value=0.5,
            kind=ResultKindApp.data_drift,
            status=ResultStatusApp.potential_detection,
        )

    def create_report(
        self, sample_df: pd.DataFrame, schedule_time: pd.Timestamp
    ) -> "Report":
        metrics = [
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
        ]
        for col_name in self.columns:
            metrics.extend(
                [
                    ColumnDriftMetric(column_name=col_name, stattest="wasserstein"),
                    ColumnSummaryMetric(column_name=col_name),
                ]
            )

        data_drift_report = Report(
            metrics=metrics,
            timestamp=schedule_time,
        )

        data_drift_report.run(reference_data=self.train_set, current_data=sample_df)
        return data_drift_report

    def create_test_suite(
        self, sample_df: pd.DataFrame, schedule_time: pd.Timestamp
    ) -> "TestSuite":
        data_drift_test_suite = TestSuite(
            tests=[DataDriftTestPreset()],
            timestamp=schedule_time,
        )

        data_drift_test_suite.run(reference_data=self.train_set, current_data=sample_df)
        return data_drift_test_suite
