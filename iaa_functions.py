from typing import List, Tuple, Dict, Any, Optional
from collections import Counter
import prodigy
import spacy
from prodigy.util import msg
from sklearn.metrics import cohen_kappa_score, accuracy_score
from wasabi import table


# YOUR PACKAGE
import catalogue

iaa_functions_registry = catalogue.create("prodigy-iaa-poc", "functions")

ExampleDict = Dict[str, Any]


@iaa_functions_registry.register("get_task_hash")
def get_task_hash(example: Dict[str, Any]):
    return example["_task_hash"]


@iaa_functions_registry.register("datasets.two-annotators")
def datasets_binary(
    datasets: List[str], overlap_key: Optional[str]
) -> List[Tuple[ExampleDict, ExampleDict]]:
    if not overlap_key:
        overlap_key_function = iaa_functions_registry.get("get_task_hash")
    else:
        overlap_key_function = iaa_functions_registry.get(overlap_key)

    d1, d2 = datasets[0], datasets[1]
    DB = prodigy.components.db.connect()
    for set_id in datasets:
        if set_id not in DB:
            msg.fail(f"Can't find dataset '{set_id}' in database", exits=1)
    dataset_examples = {}
    dataset_hashes = {}
    for set_id in (d1, d2):
        examples = DB.get_dataset_examples(set_id)
        dataset_examples[set_id] = examples
        # TODO: Fix this error check to only count those that are overlapping anyway
        # dataset_tasks = [overlap_key_function(example) for example in examples]
        # task_count = Counter(dataset_tasks).most_common()
        # if max(task_count, key=lambda x: x[1])[1] > 1:
        #     non_unique = [str(i[0]) for i in task_count if i[1] > 1]
        #     raise ValueError(f"Non-Unique examples found. Keys: {','.join(non_unique)}")
        dataset_hashes[set_id] = set(
            overlap_key_function(example) for example in examples
        )
    common_tasks = dataset_hashes[d1].intersection(dataset_hashes[d2])
    common_examples = {}
    for set_id in datasets:
        common_examples[set_id] = sorted(
            [
                example
                for example in dataset_examples[set_id]
                if overlap_key_function(example) in common_tasks
            ],
            key=lambda ex: overlap_key_function(ex),
        )
    paired_examples = list(zip(common_examples[d1], common_examples[d2]))
    return paired_examples


@iaa_functions_registry.register("sessions.two-annotators")
def sessions_binary(
    dataset: str, session_ids: List[str], overlap_key: Optional[str]
) -> List[Tuple[ExampleDict, ExampleDict]]:
    # We could more strongly type this as a tuple in the binary case
    if not overlap_key:
        overlap_key_function = iaa_functions_registry.get("get_task_hash")
    else:
        overlap_key_function = iaa_functions_registry.get(overlap_key)

    s1, s2 = session_ids[0], session_ids[1]
    DB = prodigy.components.db.connect()
    if dataset not in DB:
        msg.fail(f"Can't find dataset '{dataset}' in database", exits=1)
    dataset_examples = {}
    dataset_hashes = {}
    examples = DB.get_dataset_examples(dataset)
    for session_id in (s1, s2):
        dataset_examples[session_id] = [
            ex for ex in examples if ex.get("_session_id") == session_id
        ]
        # TODO: Fix this error check to only count those that are overlapping anyway
        # dataset_tasks = [overlap_key_function(example) for example in examples]
        # task_count = Counter(dataset_tasks).most_common()
        # if max(task_count, key=lambda x: x[1])[1] > 1:
        #     non_unique = [str(i[0]) for i in task_count if i[1] > 1]
        #     raise ValueError(f"Non-Unique examples found. Keys: {','.join(non_unique)}")
        dataset_hashes[session_id] = set(
            overlap_key_function(example) for example in examples
        )
    common_tasks = dataset_hashes[s1].intersection(dataset_hashes[s2])
    common_examples = {}
    for session_id in (s1, s2):
        common_examples[session_id] = sorted(
            [
                example
                for example in dataset_examples[session_id]
                if overlap_key_function(example) in common_tasks
            ],
            key=lambda ex: overlap_key_function(ex),
        )
    paired_examples = list(zip(common_examples[s1], common_examples[s2]))
    return paired_examples


@iaa_functions_registry.register("transform.binarize-accept")
def binarize_accept(paired_examples: List[Tuple[ExampleDict, ExampleDict]]):
    def intify_accept(example):
        return int(example["answer"] == "accept")

    binarized_examples = [
        (intify_accept(ex1), intify_accept(ex2)) for (ex1, ex2) in paired_examples
    ]
    return binarized_examples


@iaa_functions_registry.register("cohens_kappa.stdout")
def cohens_kappa(overlapping_annotaions: List[Tuple[int, int]]):
    a1, a2 = zip(*overlapping_annotaions)
    kappa = cohen_kappa_score(a1, a2)
    print(f"Cohen's Kappa: {kappa:.3f}")


@iaa_functions_registry.register("agreement.stdout")
def agreement(overlapping_annotaions: List[Tuple[int, int]]):
    a1, a2 = zip(*overlapping_annotaions)
    agreement = accuracy_score(a1, a2)
    print(f"Raw Agreement: {agreement:.3f}")


@iaa_functions_registry.register("kappa_agreement.stdout")
def kappa_agreement(overlapping_annotaions: List[Tuple[int, int]]):
    a1, a2 = zip(*overlapping_annotaions)
    agreement = accuracy_score(a1, a2)
    kappa = cohen_kappa_score(a1, a2)

    data = [("Raw Agreement", f"{agreement:.3f}"), ("Cohen's Kappa", f"{kappa:.3f}")]
    header = (
        "Metric",
        "Value",
    )
    aligns = ("l", "r")
    formatted = table(data, header=header, divider=True, aligns=aligns)
    print(formatted)
