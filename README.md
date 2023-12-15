<div align="center">
  <h1>Conventional Precommit Linter</h1>
  <img src="docs/conventional-precommit-linter.jpg" width="800">
  <br>
  <br>
  <!-- GitHub Badges -->
   <img alt="release" src="https://img.shields.io/github/v/release/espressif/conventional-precommit-linter" />
   <img alt="tests" src="https://github.com/espressif/conventional-precommit-linter/actions/workflows/pytest.yml/badge.svg" />
</div>
The Conventional Precommit Linter is a tool designed to ensure commit messages follow the Conventional Commits standard, enhancing the readability and traceability of your project's history.
<hr>


## Table of Contents

- [Table of Contents](#table-of-contents)
- [Getting Started](#getting-started)
  - [Commit Message Structure](#commit-message-structure)
  - [Installation](#installation)
  - [Install Commit-msg Hooks](#install-commit-msg-hooks)
- [Configuration](#configuration)
- [Project issues](#project-issues)
- [Contributing](#contributing)
- [Credits](#credits)

---

## Getting Started

### Commit Message Structure
Commit messages are validated against the following format:
```
<type>(<optional-scope>): <summary>
  < ... empty line ... >
<optional body lines>
<optional body lines>
<optional body lines>
```
Each component is checked for compliance with the provided or default configuration.

**Example output for failed message:**
<img src="docs/example-output-default-args.jpg" width="800">

**Example output for failed message (with custom arguments):**
<img src="docs/example-output-custom-args.jpg" width="710">

### Installation

To integrate the **Conventional Precommit Linter** into your project, add to your `.pre-commit-config.yaml`:

```yaml
# FILE: .pre-commit-config.yaml
repos:
  - repo: https://github.com/espressif/conventional-precommit-linter
    rev: v1.3.0  # The version tag you wish to use
    hooks:
      - id: conventional-precommit-linter
        stages: [commit-msg]
```

### Install Commit-msg Hooks
**IMPORTANT:** `commit-msg` hooks require a specific installation command:
```sh
pre-commit install -t pre-commit -t commit-msg
```

**Note:** The `pre-commit install` command by default sets up only the `pre-commit` stage hooks. The additional flag `-t commit-msg` is necessary to set up `commit-msg` stage hooks.

For a simplified setup (just with `pre-commit install` without flags), ensure your `.pre-commit-config.yaml` contains the following:
```yaml
# FILE: .pre-commit-config.yaml
---
minimum_pre_commit_version: 3.3.0
default_install_hook_types: [pre-commit,commit-msg]
...
```
After modifying `.pre-commit-config.yaml`, re-run the installation command (`pre-commit install`) for changes to take effect.

---

## Configuration

The linter accepts several configurable parameters to tailor commit message validation:
- `--types`: Define the types of commits allowed (default: [`change`, `ci`, `docs`, `feat`, `fix`, `refactor`, `remove`, `revert`, `test`]).
- `--scopes`: Specifies a list of allowed scopes. If not defined, all scopes are allowed (restriction is `disabled`).
- `--subject-min-length`: Set the minimum length for the summary (default: `20`).
- `--subject-max-length`: Set the maximum length for the summary (default: `72`).
- `--body-max-line-length`: Set the maximum line length for the body (default: `100`).
- `--summary-uppercase`: Enforce the summary to start with an uppercase letter (default: `disabled`).
- `--allow-breaking`: Allow exclamation mark in the commit type (default: `false`).

The **custom configuration** can be specified in `.pre-commit-config.yaml` like this:
```yaml
# FILE: .pre-commit-config.yaml
...
- repo: https://github.com/espressif/conventional-precommit-linter
  rev: v1.3.0  # The version tag you wish to use
  hooks:
    - id: conventional-precommit-linter
      stages: [commit-msg]
      args:
        - --types=change,ci,docs,feat,fix,refactor,remove,revert,fox
        - --scopes=bt,wifi,ethernet
        - --subject-min-length=10
```

---

## Project issues

If you encounter any issues, feel free to report them in the [project's issues](https://github.com/espressif/conventional-precommit-linter/issues) or create Pull Request with your suggestion.

---

## Contributing

📘 If you are interested in contributing to this project, see the [project Contributing Guide](CONTRIBUTING.md).

---

## Credits
Inspired by project: https://github.com/compilerla/conventional-pre-commit
