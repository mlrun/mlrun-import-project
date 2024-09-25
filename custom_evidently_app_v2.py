import pandas as pd
from sklearn.datasets import load_iris
from mlrun.common.schemas.model_monitoring.constants import (
    ResultKindApp,
    ResultStatusApp,
)
from mlrun.model_monitoring.application import ModelMonitoringApplicationResult
from mlrun.model_monitoring.applications.evidently_base import (
    EvidentlyModelMonitoringApplicationBaseV2,
)
from mlrun.model_monitoring.applications.context import MonitoringApplicationContext
from evidently.metrics import (
    ColumnDriftMetric,
    ColumnSummaryMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.report import Report
from evidently.test_preset import DataDriftTestPreset
from evidently.test_suite import TestSuite
from evidently.ui.type_aliases import STR_UUID


class CustomEvidentlyMonitoringApp(EvidentlyModelMonitoringApplicationBaseV2):
    NAME = "evidently-app-test-v2"

    def __init__(self, evidently_workspace_path: str, evidently_project_id: STR_UUID):
        super().__init__(evidently_workspace_path, evidently_project_id)
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

    def do_tracking(
        self, monitoring_context: MonitoringApplicationContext
    ) -> ModelMonitoringApplicationResult:
        monitoring_context.logger.info("Running evidently app")

        sample_df = monitoring_context.sample_df[self.columns]

        data_drift_report = self.create_report(
            sample_df, monitoring_context.end_infer_time
        )
        data_drift_test_suite = self.create_test_suite(
            sample_df, monitoring_context.end_infer_time
        )

        self.log_evidently_object(
            monitoring_context,
            data_drift_report,
            "report_evidently",  # TODO: ML-7347
            # f"report_{str(monitoring_context.end_infer_time)}",
        )
        self.log_evidently_object(
            monitoring_context,
            data_drift_test_suite,
            "suite_evidently",  # TODO: ML-7347
            # f"suite_{str(monitoring_context.end_infer_time)}",
        )
        # TODO: commented out due to ML-7159 - evidently app pod memory consumption is constantly growing
        # self.log_project_dashboard(
        #     monitoring_context,
        #     monitoring_context.start_infer_time,
        #     monitoring_context.end_infer_time,
        # )

        monitoring_context.logger.info("Logged evidently objects")
        return ModelMonitoringApplicationResult(
            name="data_drift_test",
            value=0.5,
            kind=ResultKindApp.data_drift,
            status=ResultStatusApp.potential_detection,
        )

    def create_report(
        self, sample_df: pd.DataFrame, schedule_time: pd.Timestamp
    ) -> Report:
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
    ) -> TestSuite:
        data_drift_test_suite = TestSuite(
            tests=[DataDriftTestPreset()],
            timestamp=schedule_time,
        )

        data_drift_test_suite.run(reference_data=self.train_set, current_data=sample_df)
        return data_drift_test_suite
