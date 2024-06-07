import pytest

from conventional_precommit_linter.hook import rules_output_status


@pytest.fixture()
def default_rules_output_status():
    return rules_output_status.copy()
