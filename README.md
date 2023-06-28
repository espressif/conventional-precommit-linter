# Conventional Precommit Linter

The Conventional Precommit Linter hook is a Python script that checks the format of the commit messages, ensuring they adhere to the Conventional Commits standard with some additional parameters.

It is intended to be used as a pre-commit hook to verify the commit messages before they are committed, improving the overall quality and consistency of your commit history.

## Getting Started

To use the Conventional Precommit Linter Hook in your project, add the following configuration to your `.pre-commit-config.yaml` file:

```yaml
- repo: https://github.com/espressif/conventional-precommit-linter
  rev: v1.0.0
  hooks:
    - id: conventional-precommit-linter
      stages: [commit-msg]
```

### Install commit-msg hooks
**IMPORTANT**: To install `commit-msg` type hooks, execute the command:
```sh
pre-commit install -t pre-commit -t commit-msg
```

Simple `pre-commit install` will not help here - The `pre-commit install` command in default is responsible ... for installing the pre-commit stage hooks only. This means that it sets up hooks which get triggered before the commit process really starts (that is, before you type a commit message). These hooks are typically used to run checks like linting or unit tests, which need to pass before the commit can be made.

However, the `commit-msg` stage hooks (as the `conventional-precommit-linter` is) are a separate set of hooks that run at a different stage in the commit process. These hooks get triggered after you've typed in your commit message but before the commit is finalized.

Since these two types of hooks run at different stages in the commit process and serve different purposes, the pre-commit framework treats them as distinct. Therefore, you need to use `pre-commit install` to set up the `pre-commit` hooks, and `pre-commit install -t commit-msg` to set up the `commit-msg` hooks.

The `pre-commit install -t pre-commit -t commit-msg` command combines these two commands above.

The developer only needs to execute this command once. Subsequent changes to the `.pre-commit-config.yaml` file do not require re-running it, but it is recommended to run it after each change to this file.


## Parameters

The script supports additional parameters to customize its behavior:

- `--types`: Optional list of commit types to support. If not specified, the default types are `["change", "ci", "docs", "feat", "fix", "refactor", "remove", "revert"]`.

- `--subject-min-length`: Minimum length of the 'Summary' field in commit message. Defaults to `20`.

- `--subject-max-length`: Maximum length of the 'Summary' field in commit message. Defaults to `50`.

- `--body-max-line-length`: Maximum length of a line in the commit message body. Defaults to `100`.

- `--summary-uppercase`: Summary must start with an uppercase letter. If not specified, the default is `false` (uppercase not required).

You can modify these parameters by adding them to the `args` array in the `.pre-commit-config.yaml` file. For example, to change the `--subject-min-length` to `10` and add a new type `fox`, your configuration would look like this:

```yaml
- repo: https://github.com/espressif/conventional-precommit-linter
  rev: v1.0.0
  hooks:
    - id: conventional-precommit-linter
      stages: [commit-msg]
      args:
        - --types=change,ci,docs,feat,fix,refactor,remove,revert,fox
        - --subject-min-length=10
```

## Commit Message Structure

The script checks commit messages for the following structure:

```text
<type><(scope/component)>: <Summary>

<Body>
```

Where:

- `<type>`: a descriptor of the performed change, e.g., `feat`, `fix`, `refactor`, etc. Use one of the specified types (either default or provided using the `--types` parameter).

- `<scope/component>` (optional): the scope or component that the commit pertains to. It should start with a lowercase letter.

- `<summary>`: a short, concise description of the change. It should not end with a period, and be between `subject_min_length` and `subject_max_length` characters long (as specified by script parameters). If the `--summary-uppercase` flag is used, then the summary must start with a uppercase letter.

- `<body>` (optional): a detailed description of the change. Each line should be no longer than `body_max_line_length` characters (as specified by script parameters). There should be one blank line between the summary and the body.

Examples:

```text
fix(freertos): Fix startup timeout issue

This is a detailed description of the commit message body ...

...

ci: added target test job for ESP32-Wifi6

...
```

With the Conventional Precommit Linter hook, your project can maintain clean and understandable commit messages that follow the Conventional Commits standard.


## Testing

Our Conventional Precommit Linter hook also includes a test suite to ensure the correct functioning of the script.

To run these tests, you will need to have `pytest` installed. Once `pytest` is installed, you can run the tests by navigating to the root directory of this project and executing:

```sh
pytest
```
... or create a content in file `test_message.txt` and run:
```sh
python -m conventional_precommit_linter.hook --subject-min-length 20 --subject-max-length 50 --body-max-line-length 100 test_message.txt
```

.... or (with default arguments):
```sh
python -m conventional_precommit_linter.hook test_message.txt
```

The test cases include a variety of commit message scenarios and check if the script correctly identifies valid and invalid messages. The test suite ensures the correct identification of message structure, format, length, and content, amongst other parameters.

This way, the integrity of the Conventional Precommit Linter hook is continuously checked. Regularly running these tests after modifications to the script is highly recommended to ensure its consistent performance.

***


## Credit
Inspired by project: https://github.com/compilerla/conventional-pre-commit
