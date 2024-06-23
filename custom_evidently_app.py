import datetime
import pandas as pd
from sklearn.datasets import load_iris
from mlrun.common.schemas.model_monitoring.constants import (
    ResultKindApp,
    ResultStatusApp,
)
from mlrun.model_monitoring.application import ModelMonitoringApplicationResult
from mlrun.model_monitoring.evidently_application import (
    _HAS_EVIDENTLY,
    EvidentlyModelMonitoringApplicationBase,
)
if _HAS_EVIDENTLY:
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



    
class CustomEvidentlyMonitoringApp(EvidentlyModelMonitoringApplicationBase):
    name = "my-custom-evidently-class"

    def _lazy_init(self, *args, **kwargs) -> None:
        super()._lazy_init(*args, **kwargs)
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
    self,
    application_name: str,
    sample_df_stats: pd.DataFrame,
    feature_stats: pd.DataFrame,
    sample_df: pd.DataFrame,
    start_infer_time: pd.Timestamp,
    end_infer_time: pd.Timestamp,
    latest_request: pd.Timestamp,
    endpoint_id: str,
    output_stream_uri: str,
) -> ModelMonitoringApplicationResult:
        self.context.logger.info("Running evidently app")

        # self._init_iris_data()
        sample_df = sample_df[self.columns]

        # Create evidently reports
        data_drift_report = self.create_report(sample_df, end_infer_time)
        self.evidently_workspace.add_report(
            self.evidently_project_id, data_drift_report
        )
        
        data_quality_report = Report(metrics=[
            DataQualityPreset(),
        ])
        data_quality_report.run(reference_data=self.train_set, current_data=sample_df)

        # Create evidently test suite
        data_drift_test_suite = self.create_test_suite(sample_df, end_infer_time)
        self.evidently_workspace.add_test_suite(
            self.evidently_project_id, data_drift_test_suite
        )
        
        # Log the objects in iguazio
        self.log_evidently_object(data_drift_report, f"report_{str(end_infer_time)}")
        self.log_evidently_object(data_drift_test_suite, f"suite_{str(end_infer_time)}")
        self.log_evidently_object(data_quality_report, f"data_quality_report_{str(end_infer_time)}")
        
        # Log the dashboard in iguazio
        self.log_project_dashboard(None, end_infer_time + datetime.timedelta(minutes=1))

        self.context.logger.info("Logged evidently objects")
        
        return ModelMonitoringApplicationResult(
            application_name=self.name,
            endpoint_id=endpoint_id,
            start_infer_time=start_infer_time,
            end_infer_time=end_infer_time,
            result_name="data_drift_test",
            result_value=0.5,
            result_kind=ResultKindApp.data_drift,
            result_status=ResultStatusApp.potential_detection,
        )
    
    # Function that creates an evidently report
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

    # Function that creates an evidently test suite
    def create_test_suite(
        self, sample_df: pd.DataFrame, schedule_time: pd.Timestamp
    ) -> "TestSuite":
        data_drift_test_suite = TestSuite(
            tests=[DataDriftTestPreset()],
            timestamp=schedule_time,
        )

        data_drift_test_suite.run(reference_data=self.train_set, current_data=sample_df)
        return data_drift_test_suite
