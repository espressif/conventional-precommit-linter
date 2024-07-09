import tempfile
from typing import List
from typing import Tuple

import pytest

from conventional_precommit_linter.hook import main
from conventional_precommit_linter.hook import rules_output_status

# Default values for the commit message format
TYPES = 'change,ci,docs,feat,fix,refactor,remove,revert,fox'
SCOPES = 'bootloader,bt,Bt,esp32,esp-rom,examples,examples*storage,rom,wifi'
SUBJECT_MIN_LENGTH = 21
SUBJECT_MAX_LENGTH = 53
BODY_MAX_LINE_LENGTH = 107
DEFAULT_ARGV_TUPLE: Tuple[str, ...] = (
    '--types',
    TYPES,
    '--scopes',
    SCOPES,
    '--subject-min-length',
    str(SUBJECT_MIN_LENGTH),
    '--subject-max-length',
    str(SUBJECT_MAX_LENGTH),
    '--body-max-line-length',
    str(BODY_MAX_LINE_LENGTH),
    '--summary-uppercase',
    '--allow-breaking',
)


# Construct the argument list for main with the new constants
def get_argv_list(scope_case_insensitive_arg=False) -> List:
    argv_list: List = list(DEFAULT_ARGV_TUPLE)
    if scope_case_insensitive_arg:
        argv_list.append('--scope-case-insensitive')

    print(argv_list)
    return argv_list


# Dynamic test naming based on the commit message
def commit_message_id(commit_message):  # pylint: disable=redefined-outer-name
    return commit_message[0]  # Use the first line of the commit message as the test ID


@pytest.fixture(
    params=[
        (
            # Expected PASS: Message with scope and body
            'feat(bootloader): This is commit message with scope and body\n\nThis is a text of body',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message with scope, without body
            'change(wifi): This is commit message with scope without body',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message with scope (with hyphen in scope), without body
            'change(esp-rom): This is commit message with hyphen in scope',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message with scope (with asterisk in scope), without body
            'change(examples*storage): This is commit message with asterisk in scope',
            {},
            get_argv_list(),
        ),
        (
            # Expected FAIL: Message with not allowed scope and body
            'feat(tomas): This is commit message with scope and body\n\nThis is a text of body',
            {'error_scope_allowed': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: Message with scope (with comma in scope), without body
            'change(examples,storage): This is commit message with comma in scope',
            {'error_scope_allowed': True},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message with scope (with slash in scope), without body
            'change(examples/storage): This is commit message with slash in scope',
            {'error_scope_allowed': True},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message without scope, with body
            "change: This is commit message without scope with body\n\nThis is a text of body\n# Please enter the commit message for your changes. Lines starting\n# with '#' will be ignored, and an empty message aborts the commit.\n#",
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message without scope, without body
            'change: This is commit message without scope and body',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Test of additional types
            'fox(esp32): Testing additional types\n\nThis is a text of body',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: 'body' line longer (custom arg 107 chars)
            'fix(bt): Update database schemas\n\nUpdating the database schema to include fields and user profile preferences, cleaning up unnecessary calls',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message without scope with exclamation mark
            'change!: This is commit with exclamation mark',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: Message with scope with exclamation mark
            'change(rom)!: This is commit with exclamation mark',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: FIXUP Message with scope and body
            'fixup! feat(bootloader): This is fixup commit message with scope and body\n\nThis is a text of body',
            {},
            get_argv_list(),
        ),
        (
            # Expected PASS: SQUASH Message with scope and body
            'squash! feat(bootloader): This is fixup commit message with scope and body\n\nThis is a text of body',
            {},
            get_argv_list(),
        ),
        (
            # Expected FAIL: Message with scope with 2 exclamation marks
            'change(rom)!!: This is commit message with 2 exclamations',
            {'error_type': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: missing colon between 'type' (and 'scope') and 'summary'
            'change this is commit message without body',
            {'missing_colon': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: empty commit message
            '   \n\n   \n',
            {'empty_message': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'summary' too short
            'fix: Fix bug',
            {'error_summary_length': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'summary' too long
            'change(rom): Refactor authentication flow for enhanced security measures',
            {'error_summary_length': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'summary' ends with period
            'change(rom): Fixed the another bug.',
            {'error_summary_period': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'summary' starts with lowercase
            'change(rom): this message starts with lowercase',
            {'error_summary_capitalization': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: uppercase in 'scope', no body
            'fix(dangerGH): Update token permissions - allow Danger to add comments to PR',
            {
                'error_scope_capitalization': True,
                'error_summary_length': True,
                'error_scope_allowed': True,
            },
            get_argv_list(),
        ),
        (
            # Expected FAIL: not allowed 'type' with scope and body
            'delete(bt): Added new feature with change\n\nThis feature adds functionality',
            {'error_type': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: not allowed 'type' without scope and without body
            'delete: Added new feature with change',
            {'error_type': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: not allowed 'type' without scope and without body
            'wip: Added new feature with change',
            {'error_type': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: not allowed 'type' (type starts with uppercase)
            'Fix(bt): Added new feature with change\n\nThis feature adds functionality',
            {'error_type': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: missing blank line between 'summary' and 'body'
            'change: Added new feature with change\nThis feature adds functionality',
            {'error_body_format': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'body' line too long
            'fix(bt): Update database schemas\n\nUpdating the database schema to include new fields and user profile preferences, cleaning up unnecessary calls',
            {'error_body_length': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: 'scope' missing parentheses
            'fix(bt: Update database schemas\n\nUpdating the database schema to include new fields.',
            {'error_scope_format': True},
            get_argv_list(),
        ),
        (
            # Expected FAIL: allowed special 'type', uppercase in 'scope' required, 'summary' too long, 'summary' ends with period
            'fox(BT): update database schemas. Updating the database schema to include new fields and user profile preferences, cleaning up unnecessary calls.',
            {
                'error_summary_capitalization': True,
                'error_scope_allowed': True,
                'error_scope_capitalization': True,
                'error_summary_length': True,
                'error_summary_period': True,
            },
            get_argv_list(),
        ),
        (
            # Expected FAIL: uppercase in 'scope'
            'change(Bt): Added new feature with change\n\nThis feature adds functionality',
            {
                'error_scope_capitalization': True,
            },
            get_argv_list(),
        ),
        (
            # Expected Pass: Allowed uppercase in 'scope'.
            'change(Bt): Added new feature with change\n\nThis feature adds functionality',
            {},
            get_argv_list(scope_case_insensitive_arg=True),
        ),
        (
            # Expected Fail: Summary ending with a period '.'
            'change(Bt): Added new feature with change.',
            {'error_summary_period': True},
            get_argv_list(scope_case_insensitive_arg=True),
        ),
    ],
    # Use the commit message to generate IDs for each test case
    ids=commit_message_id,
)
def commit_message(request, default_rules_output_status):
    # Combine the default dictionary with the test-specific dictionary
    combined_output = {**default_rules_output_status, **request.param[1]}
    return request.param[0], combined_output, request.param[2]


def test_commit_message_with_args(commit_message, default_rules_output_status):  # pylint: disable=redefined-outer-name
    message_text, expected_output, cli_arguments = commit_message

    # Reset rules_output_status to its default state before each test case
    rules_output_status.clear()
    rules_output_status.update(default_rules_output_status)

    # Create a temporary file to mock a commit message file input
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(message_text)
        temp_file_name = temp.name

    cli_arguments.append(temp_file_name)

    # Run the main function of your script with the temporary file and arguments
    main(cli_arguments)

    # Retrieve the actual rules_output_status after running the main function
    actual_output = rules_output_status

    # Assert that the actual rules_output_status matches the expected output
    assert actual_output == expected_output, f'Failed on commit message: {message_text}'
