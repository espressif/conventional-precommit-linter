# Contributing and Development

We welcome contributions! To contribute to this repository, please follow these steps:

## Code and Testing

-   **Code Style and Structure:**

    -   **Pre-Commit Hooks:** Install pre-commit hooks in this repository using the `pre-commit install` command.

    -   **Readable Code Structure:** Structure your code in a readable manner. The main logic should be in the default rule function, with implementation details in helper functions. Avoid nested `if` statements and unnecessary `else` statements to maintain code clarity and simplicity.

    -   **Remove Debug Statements:** Remove any debug statements  from your rules.

-   **Automated Tests:** We aim for full test coverage, so **partial tests will not be accepted**. The tests should cover all typical usage scenarios as well as edge cases to ensure robustness.

-   **Testing Tool:** It is recommended to run `pytest` frequently during development to ensure that all aspects of your code are functioning as expected.


## Documentation and Maintenance

-   **Changelog:** `CHANGELOG.md` is generated automatically by `comittizen` from commit messages. Not need to update `CHANGELOG.md` manually. Focus on informative and clear commit messages which end in the release notes.

-   **Documentation:** Regularly check and update the documentation to keep it current.

    -   **PR Descriptions and Documentation:** When contributing, describe all changes or new features in the PR (Pull Request) description as well as in the documentation. When changing the style to the output style, attach a thumbnail after the change.

## Development and local testing


1. **Clone the Project**: Clone the repository to your local machine using:
    ```sh
    git clone https://github.com/espressif/conventional-precommit-linter.git
    ```

2. **Set Up Development Environment:**

- Create and activate a virtual environment:
  ```sh
  virtualenv venv -p python3.8 && source ./venv/bin/activate
  ```
  or
  ```sh
  python -m venv venv && source ./venv/bin/activate
  ```

- Install the project and development dependencies:
  ```sh
  pip install -e '.[dev]'
  ```

3. **Testing Your Changes:**

- Create a file named `test_message.txt` in the root of the repository (this file is git-ignored) and place an example commit message in it.

- Run the tool to lint the message:
  ```sh
    python -m conventional_precommit_linter.hook test_message.txt
  ```

  ... or with arguments:
  ```sh
  python -m conventional_precommit_linter.hook test_message.txt --subject-min-length="12" --subject-max-length="55" --body-max-line-length="88" --types="feat,change,style" --scopes="bt,wifi,ethernet"
  ```


Before submitting a pull request, ensure your changes pass all the tests. You can run the test suite with the following command:
```sh
pytest
```

---

👏**Thank you for your contributions.**
