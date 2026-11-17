# Contributing

## Branch and review policy

- Create a feature branch for every change.
- Do not commit directly to `main`.
- Open a pull request for reviewable changes.
- Merge only with explicit approval after required checks pass.

## Commit convention

Use a concise conventional prefix where it clarifies the change:

```text
feat: add a new case study
fix: correct an evidence label
docs: clarify operations guidance
ci: strengthen asset validation
```

A commit must be independently reviewable. When one change affects implementation, generated public assets, validation, and documentation, include those parts in the same commit.

## Documentation updates

Update relevant documentation when changing:

- route structure or homepage navigation;
- source data, snapshot period, boundary version, processing method, or display filter;
- metadata contract, validator, or CI behavior;
- case-study scope, limitation wording, or evidence vocabulary;
- local validation or release procedure.

Update `AGENTS.md` when an overall project constraint, source-of-truth location, validation command, or do-not-change boundary changes.

## Runtime and sensitive data

Do not commit credentials, API keys, raw API responses, source exports, caches, raw tool output, customer data, or runtime logs. Publish only the reviewed display assets and metadata required by a static case study.

## Release gate

Before requesting a merge:

1. Run relevant local validators and JavaScript syntax checks.
2. Run `git diff --check`.
3. Test changed pages in a browser on desktop and mobile.
4. Verify every interactive control works, every map state is present, and no horizontal overflow exists.
5. Confirm evidence wording matches the documented source and limitations.
6. Wait for CI on the pull request.

After merge, wait for GitHub Pages deployment and verify public routes before declaring a change live.

## Versioning

The site has no formal release tags yet. Use semantic versioning when a versioned application or reusable package is introduced. Until then, Git commits and pull requests are the release record.
