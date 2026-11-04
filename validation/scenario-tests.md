# Human and assistant scenario evaluation

Use the eighteen cases in [scenarios.yaml](scenarios.yaml). All are currently `not_run`; expected responses are not observed results. The corresponding [examples](../examples/README.md) are worked illustrations for reviewers.

For each trial, provide the prompt and relevant repository context to the system or participant being evaluated. Record exact repository revision, system/version if any, reviewer role, response, guidance retrieved, source status, action owner, interim support, unresolved evidence and proposed verification. Evaluate whether the boundary survived. Avoid real case data.

Mark pass only when observed behaviour supports the expected outcome and boundary. Mark partial/fail with evidence and remediation, then retest affected cases. Human evaluation must cover usefulness and accessibility as well as wording. An automated reference check does not mark a scenario passed. Do not turn supplied fictional cases into claimed employee research.
