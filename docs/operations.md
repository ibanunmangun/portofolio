# Operations

## Local preview

Serve the repository root with a local static server:

```text
python3 -m http.server 8765 --bind 127.0.0.1
```

Inspect these routes in a browser:

```text
http://127.0.0.1:8765/
http://127.0.0.1:8765/karhutla-review/
http://127.0.0.1:8765/aceh-tamiang-flood-review/
```

## Validation

Run the case-study validators from the repository root:

```text
python3 scripts/validate_kalteng_case_study.py
python3 scripts/validate_aceh_tamiang_flood_context.py
node --check karhutla-review/app.js
node --check aceh-tamiang-flood-review/app.js
git diff --check
```

When changing a builder, regenerate its assets and prove reproducibility with two consecutive builds and matching checksums before staging generated output.

## Browser verification

For any page change, verify:

1. The page loads with no browser console error.
2. Every interactive control has a real destination or behavior.
3. Map loading, empty, and error states are present where data is fetched.
4. Keyboard focus is visible and controls are keyboard-operable.
5. The desktop view has no horizontal overflow.
6. The mobile view has no horizontal overflow and controls have at least a 44px target where applicable.
7. The legend matches the map symbols and the primary evidence layer remains visually primary.

Record the results in the PR description or implementation report.

## Pull request and release flow

1. Create a feature branch from current `main`.
2. Keep implementation, generated publishable assets, validators, and related documentation together.
3. Run local validation and browser checks.
4. Open a PR and wait for GitHub Actions checks.
5. Merge only after explicit user approval and a clean, mergeable PR with passing checks.
6. Wait for the GitHub Pages deployment associated with the new `main` commit to complete successfully.
7. Load the public homepage and every new or changed route. CI does not prove the CDN is serving the current artifact.

## Failure handling

- If a data source is unavailable, do not substitute invented data. Record the blocker and use a different verified source or request a decision.
- If a validator fails, do not stage or publish until the mismatch is diagnosed and fixed.
- If GitHub Pages deployment fails, inspect the deployment log first. Retry only through the GitHub-provided rerun control when the log indicates a transient platform failure. Diagnose persistent permissions, configuration, or build failure before changing source or repository settings.
- If a browser test cannot reach the local site, confirm the static server is running before treating it as a UI failure.

## Scheduling and automation

This repository has no approved recurring jobs. Do not add cron, live refresh, periodic source pulls, or autonomous publishing without explicit contemporaneous approval.

## Handoff

When continuing portfolio work, read `AGENTS.md`, `docs/README.md`, the relevant case-study PRD, `docs/architecture.md`, and this document before changing data, UI, validation, or release workflow.
