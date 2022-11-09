# Prodigy IAA/IRR Proof of Concept

This is a proof of concept for how IAA/IRR metrics might be implemented as a Prodigy recipe. The recipes were written to be general enough that a user could customize where the examples come from, how they're transformed into data for metric calculation, and the output of the metrics.

There are two recipes: `iaa.sessions` (for one dataset with multiple annotators indicated by Session IDs) and `iaa.datasets` (for one dataset per annotator).

Each recipe has four arguments in common:
1. **A `collector` function.** This function collects examples per annotator from prodigy and outputs overlapping examples so that they're paired by task (or some given `overlap_key`)
2. **A `processor` function.** This function takes the collected overlapping examples and transforms them into the data structure required for calculating your metric.  This can be anything from binarizing your accept/reject decisions to extracting labels from NER/Spans.
3. **A `metric_output` function.** This function takes the processed examples and calculates the metric(s) of interest and outputs them where necessary.
4. **An `overlap_key` function.** This function can be used to customize how a unique example is defined for determining overlapping examples. It will use `_task_hash` by default, but could bet set to something like meta['custom_key'].

**A note on API choices**

There are obviously alternative ways to slice and dice this problem - I think of this API as a first pass at drawing boundaries around the different stages of this functionality. You could obviously do everything in a single `collector` step if you so desired, and just write some dummy functions for `processor` and `metric_output`. But, drawing the boundaries in this way will make sharing and using different functions of these types easier. For example, if you want a new metric that takes pairs of binary examples, you can use an existing `collector` and `processor` and just write a new `metric_output` if your data is the same. If you want to try something out with NER, spans, or some other task, but you still only want to compare two annotators, you can keep the example `collector` functions shown here and write your own `processor` and `metric_output`. If you want multiple metrics displayed using third party libraries--like displaying [plots in the terminal](https://github.com/piccolomo/plotext)--you can rewrite a `metric_output` function to do that.

### API

Check arguments for both recipes with `prodigy iaa.sessions --help -F iaa_recipe.py` or `prodigy iaa.datasets --help -F iaa_recipe.py`.

### Examples

_You can use the included `data.jsonl` to run the `iaa.sessions` example_

```bash
prodigy db-in irr-session-example data.jsonl
```

```bash
prodigy iaa.sessions \
  irr-session-example \
  issue-6044-vincent,issue-6044-lechuck \
  sessions.two-annotators \
  transform.binarize-accept \
  kappa_agreement.stdout \
  -F iaa_recipe.py,iaa_functions.py
```

```
Metric          Value
-------------   -----
Raw Agreement   0.333
Cohen's Kappa   0.000
```

`iaa.datasets` I don't have example data for, but ran on two datasets I had in local storage.

```bash
prodigy iaa.datasets \
  dataset-annotator-1,dataset-annotator-2 \
  datasets.two-annotators \
  transform.binarize-accept \
  kappa_agreement.stdout \
  -F iaa_recipe.py,iaa_functions.py
```

```
Metric          Value
-------------   -----
Raw Agreement   0.945
Cohen's Kappa   0.067
```


