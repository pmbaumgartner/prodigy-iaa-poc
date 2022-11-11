from typing import List, Optional
import prodigy
from prodigy.util import msg
from iaa_functions import iaa_functions_registry


@prodigy.recipe(
    "iaa.datasets",
    # fmt: off
    datasets=("Datasets to pass to annotations to collector function. Assuming one dataset per annotator.", "positional", None, prodigy.util.split_string),
    collector=("Name of function to collect overlapping examples. Loaded from spaCy's `misc` registry.", "positional", None, str),
    processor=("Name of function process/transform overlapping examples to input data necessary for metric. Loaded from spaCy's `misc` registry.", "positional", None, str),
    metric_output=("Name of function to calculate metric(s) from transformed examples. This should also handle how you want to output (print) the metric. Loaded from spaCy's `misc` registry.", "positional", None, str),
    overlap_key=("Name of function to get key used to identify overlapping annotations per example, for use with collector function. Defaults to `_task_hash`, but could bet set to something like meta['custom_key']. Loaded from spaCy's `misc` registry.", "option", None, str),
    # fmt: on
)
def iaa_datasets(
    datasets: List[str],
    collector: str,
    processor: str,
    metric_output: str,
    overlap_key: Optional[str],
):
    """Calculates IAA given a unique dataset per annotator."""
    if not overlap_key:
        overlap_key = "get_task_hash"

    collector_func = iaa_functions_registry.get(collector)
    with msg.loading("Identifying overlapped examples."):
        overlapped_annotations = collector_func(datasets, overlap_key)
    msg.info("Identified overlapped examples.")

    processor_func = iaa_functions_registry.get(processor)
    processed_annotations = processor_func(overlapped_annotations)
    msg.info("Processed overlapped examples.")

    output_func = iaa_functions_registry.get(metric_output)
    msg.info("Calculating metric.")

    # this needs to calculate and output
    output_func(processed_annotations)


@prodigy.recipe(
    "iaa.sessions",
    # fmt: off
    dataset=("Dataset to pass to annotations to collector function. Assuming one datset with multiple session IDs.", "positional", None, prodigy.util.split_string),
    session_ids=("Comma separated Session IDs representing unique annotators.", "positional", None, prodigy.util.split_string),
    collector=("Name of function to collect overlapping examples. Loaded from spaCy's `misc` registry.", "positional", None, str),
    processor=("Name of function process/transform overlapping examples to input data necessary for metric. Loaded from spaCy's `misc` registry.", "positional", None, str),
    metric_output=("Name of function to calculate metric(s) from transformed examples. This should also handle how you want to output (print) the metric. Loaded from spaCy's `misc` registry.", "positional", None, str),
    overlap_key=("Name of function to get key used to identify overlapping annotations per example, for use with collector function. Defaults to `_task_hash`, but could bet set to something like meta['custom_key']. Loaded from spaCy's `misc` registry.", "option", None, str),
    # fmt: on
)
def iaa_sessions(
    dataset: str,
    session_ids: List[str],
    collector: str,
    processor: str,
    metric_output: str,
    overlap_key: Optional[str],
):
    """Calcualtes IAA given a single dataset with multiple annotators per Session ID"""
    if not overlap_key:
        overlap_key = "get_task_hash"

    collector_func = iaa_functions_registry.get(collector)
    with msg.loading("Identifying overlapped examples."):
        overlapped_annotations = collector_func(dataset, session_ids, overlap_key)
    msg.info("Identified overlapped examples.")

    processor_func = iaa_functions_registry.get(processor)

    processed_annotations = processor_func(overlapped_annotations)
    msg.info("Processed overlapped examples.")
    output_func = iaa_functions_registry.get(metric_output)

    # This needs to calculate and output
    output_func(processed_annotations)
