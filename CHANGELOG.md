## v1.5.0 (2023-12-15)


- feat: add support for optional `!` in scope
- Closes https://github.com/espressif/conventional-precommit-linter/issues/12
- docs: add CONTRIBUTING Guide
- ci: add PR linter Danger

## v1.4.1 (2023-12-09)


- fix: fix partial type matching
- Closes https://github.com/espressif/conventional-precommit-linter/issues/11

## v1.4.0 (2023-12-04)


- feat(scope): add optional restriction to available scopes
- ci: update commitizen auto release message
- update actions version pytest.yml workflow
- docs: update thumbnails example messages
- change(output): coloring only keywords in output

## v1.3.0 (2023-11-09)


- fix: commitizen versions settings in pyproject.toml
- change(user-output): update user output marking all issues with message - Dynamic messages in output report - Color input commit message same as message elements - Tests updated
- ci: update project settings configuration (pyproject.toml)
- add CHANGELOG.md, commitizen, test packages definitions
- GitHub action - testing on multiple OSes

## v1.2.1 (2023-07-31)


- fix(scope-capitalization): Update scope regex to be consistent with commitlint in DangerJS (#6)
- docs(README) Update default max summary length

## v1.2.0 (2023-06-29)


- Ignore comment lines from linted commit message (#5)
- fix: Ignore # lines from linted commit message
- feat: Add hint for preserving commit message to output report
- fix: Allow in scope special characters  " _ / . , * -"
- docs: Update hook install process guide (#4)

## v1.1.0 (2023-06-27)


- Update default rules (#3)
- change(rules): Set maximum summary length to 72 characters
- change(rules): Summary uppercase letter as optional rules
- docs: Update argument usage example in README.md

## v1.0.0 (2023-06-21)


- Merge pull request #1 from espressif/add_linter_hook
- feat: Add linter pre-commit hook logic (RDT-471)
- feat: Add linter pre-commit hook logic
- Init
