# Inclusive Employment

Practical guidance from Double FW Ltd for making employment accessible, equitable and sustainable. Inclusion means people can access opportunity, contribute, influence decisions, belong and progress with dignity.

**Version 0.1.0 — review draft, 4 November 2026.** These are actual knowledge-base files, not just a development plan. Practical recommendations are proposed for local adoption. Legal content is a sourced draft awaiting qualified review; no organisational approval, staff evaluation or legal certification is claimed. The licence is reserved pending an owner decision. Five upstream repositories remain unverified.

## Start with the problem

| You need to… | Start here |
| --- | --- |
| Recruit or promote fairly | [Recruitment](docs/02-recruitment.md) and [progression](docs/09-culture.md#progression) |
| Respond to an access or support request | [Adjustment workflow](workflows/adjustments.md) |
| Run a meeting everyone can participate in | [Communication](docs/04-communication.md) and [meeting plan](templates/meeting-access-plan.md) |
| Fix an inaccessible tool or benefit | [System-barrier workflow](workflows/system-barriers.md) |
| Address performance or attendance concerns | [Fair-performance workflow](workflows/fair-performance.md) |
| Explore a team workaround or an AI trial | [Team solutions](workflows/team-solutions.md) and [AI trials](workflows/ai-trials.md) |
| Raise a concern outside your manager | [Employee route](roles/employees.md) |

## Choose your role

[Hiring managers](roles/hiring-managers.md) · [HR](roles/hr.md) · [Line managers](roles/line-managers.md) · [Teams](roles/teams.md) · [Employees and applicants](roles/employees.md)

## Knowledge map

1. [Inclusion foundations](docs/01-foundations.md)
2. [Role design and recruitment](docs/02-recruitment.md)
3. [Onboarding and support](docs/03-onboarding.md)
4. [Communication and collaboration](docs/04-communication.md)
5. [Work design and environments](docs/05-work-design.md)
6. [Adjustments and funding](docs/06-adjustments.md)
7. [Systems, benefits and procurement](docs/07-systems.md)
8. [Performance and employment procedures](docs/08-performance.md)
9. [Culture and progression](docs/09-culture.md)
10. [AI support and governance](docs/10-ai.md)
11. [Evaluation and improvement](docs/11-evaluation.md)

## Use and boundaries

The initial legal scope is Great Britain. [Northern Ireland](legal/northern-ireland.md) is a separate routing module; other jurisdictions require their own review. Disabled, Deaf and neurodivergent identities and needs vary. Ask about the individual, work and barrier rather than prescribing from a diagnosis.

Managers coordinate support; process, IT, procurement and facilities owners deliver their parts. Ask privately, arrange interim access, agree ownership and review whether the result works. Provide a challenge route. Do not require a passport, diagnostic label or grant award before ordinary support can begin.

This repository stores guidance and **synthetic examples only**. Completed passports, health data, applicant records and grievances belong in approved confidential systems, never GitHub. It is not a case-management system or an automated employment decision service.

## Tools and assurance

- [Templates](templates/README.md) and [worked scenarios](examples/README.md)
- [Source register](evidence/source-register.md), [dependency map](evidence/dependency-map.md) and [input disposition](evidence/input-disposition.csv)
- [Agent instructions](AGENTS.md), [retrieval rules](retrieval/README.md) and [structured guidance](data/guidance.yaml)
- [Acceptance criteria](validation/acceptance-criteria.md), [check instructions](validation/README.md) and [release status](validation/release-status.yaml)
- [Governance](GOVERNANCE.md), [contributing](CONTRIBUTING.md), [privacy/security](SECURITY.md), [rights](LICENSE) and [changes](CHANGELOG.md)

## Validate locally

Use Python 3.11 or newer. Install the pinned development dependencies in a virtual environment, then run:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python scripts/test_validator.py
python scripts/build_index.py
```

On Windows, activate the environment using `.venv\Scripts\activate` in Command Prompt. GitHub Actions runs the same checks on pull requests. The validator checks structure, schemas, links and traceability; it does not prove legal accuracy, accessibility or humane practice. See the validation report for the checks actually run and the reviews still pending.

## Prepare for GitHub

Extract this folder and upload its contents, including `.github`, to the intended repository. Nothing has been pushed or published by creating this package. Review the release gates and licence before public release. To preserve the workflow directory, Git upload or GitHub's upload interface must include hidden directories.
