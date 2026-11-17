# Portfolio

Personal portfolio for Ibanun Mangun Kusumo, an AI and Automation Solution Architect working across geospatial intelligence, Python, GIS workflow automation, cartography, and practical operational systems.

## Live site

https://ibanunmangun.github.io/portofolio/

## Published case studies

- [Karhutla Signal Review](https://ibanunmangun.github.io/portofolio/karhutla-review/): a bounded public-data review of satellite thermal signals in Central Kalimantan.
- [Aceh Tamiang Flood Context Review](https://ibanunmangun.github.io/portofolio/aceh-tamiang-flood-review/): a dated reported administrative footprint, not a flood-extent map.

## Repository guide

- [AGENTS.md](AGENTS.md): concise project constraints, data boundaries, and validation commands for agents.
- [Documentation index](docs/README.md): architecture, operations, case-study plans, and documentation status.
- [Contributing guide](CONTRIBUTING.md): branch, documentation, validation, and release conventions.

## Local preview

Serve the repository root:

```text
python3 -m http.server 8765 --bind 127.0.0.1
```

Then open:

```text
http://127.0.0.1:8765/
http://127.0.0.1:8765/karhutla-review/
http://127.0.0.1:8765/aceh-tamiang-flood-review/
```

## Publishing

GitHub Pages deploys the default branch after an approved pull request is merged. The repository CI validates the landing page and case-study assets, but a release is complete only after the Pages deployment and public routes are verified.
