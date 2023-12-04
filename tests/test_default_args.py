import tempfile

import pytest

from conventional_precommit_linter.hook import main
from conventional_precommit_linter.hook import rules_output_status

# Default values for the commit message format
TYPES = 'change, ci, docs, feat, fix, refactor, remove, revert'
SUBJECT_MIN_LENGTH = 20
SUBJECT_MAX_LENGTH = 72
BODY_MAX_LINE_LENGTH = 100


# Dynamic test naming based on the commit message
def commit_message_id(commit_message):  # pylint: disable=redefined-outer-name
    return commit_message[0]  # Use the first line of the commit message as the test ID


@pytest.fixture(
    params=[
        (
            # Expected PASS: Message with scope and body
            'feat(bootloader): This is commit message with scope and body\n\nThis is a text of body',
            {},
        ),
        (
            # Expected PASS: Message with scope, without body
            'change(wifi): This is commit message with scope without body',
            {},
        ),
        (
            # Expected PASS: Message with scope (with hyphen in scope), without body
            'change(esp-rom): This is commit message with hyphen in scope',
            {},
        ),
        (
            # Expected PASS: Message with scope (with asterisk in scope), without body
            'change(examples*storage): This is commit message with asterisk in scope',
            {},
        ),
        (
            # Expected PASS: Message with scope (with comma in scope), without body
            'change(examples,storage): This is commit message with comma in scope',
            {},
        ),
        (
            # Expected PASS: Message with scope (with slash in scope), without body
            'change(examples/storage): This is commit message with slash in scope',
            {},
        ),
        (
            # Expected PASS: Message without scope, with body
            'change: This is commit message without scope with body\n\nThis is a text of body\n# Please enter the commit message for your changes. Lines starting\n# with \'#\' will be ignored, and an empty message aborts the commit.\n#',
            {},
        ),
        (
            # Expected PASS: Message without scope, without body
            'change: This is commit message without scope and body',
            {},
        ),
        (
            # Expected PASS: 'summary' starts with lowercase
            'change(rom): this message starts with lowercase',
            {},
        ),
        (
            # Expected FAIL: Message without scope with exclamation mark
            'change!: This is commit message without scope but with exclamation mark',
            {'error_breaking': True},
        ),
        (
            # Expected FAIL: Message with scope with exclamation mark
            'change(rom)!: This is commit message with scope and with exclamation mark',
            {'error_breaking': True},
        ),
        (
            # Expected FAIL: Message with scope with 2 exclamation marks
            'change(rom)!!: This is commit message with !!',
            {'error_type': True},
        ),
        (
            # Expected FAIL: missing colon between 'type' (and 'scope') and 'summary'
            'change this is commit message without body',
            {'missing_colon': True},
        ),
        (
            # Expected FAIL: empty commit message
            '   \n\n   \n',
            {'empty_message': True},
        ),
        (
            # Expected FAIL: 'summary' too short
            'fix: Fix bug',
            {'error_summary_length': True},
        ),
        (
            # Expected FAIL: 'summary' too long
            'change(rom): Refactor authentication flow for enhanced security measures and improved user experience',
            {'error_summary_length': True},
        ),
        (
            # Expected FAIL: 'summary' ends with period
            'change(rom): Fixed the another bug.',
            {'error_summary_period': True},
        ),
        (
            # Expected FAIL: uppercase in 'scope', with body
            'change(Bt): Added new feature with change\n\nThis feature adds functionality',
            {'error_scope_capitalization': True},
        ),
        (
            # Expected FAIL: uppercase in 'scope', no body
            'fix(dangerGH): Update token permissions - allow Danger to add comments to PR',
            {'error_scope_capitalization': True},
        ),
        (
            # Expected FAIL: not allowed 'type' with scope and body
            'delete(bt): Added new feature with change\n\nThis feature adds functionality',
            {'error_type': True},
        ),
        (
            # Expected FAIL: not allowed 'type' without scope and without body
            'fox: Added new feature with change',
            {'error_type': True},
        ),
        (
            # Expected FAIL: not allowed 'type' (type starts with uppercase)
            'Fix(bt): Added new feature with change\n\nThis feature adds functionality',
            {'error_type': True},
        ),
        (
            # Expected Fail: partial type
            'chan: This is commit message with partial type',
            {'error_type': True},
        ),
        (
            # Expected FAIL: missing blank line between 'summary' and 'body'
            'change: Added new feature with change\nThis feature adds functionality',
            {'error_body_format': True},
        ),
        (
            # Expected FAIL: 'body' line too long
            'fix(bt): Update database schemas\n\nUpdating the database schema to include new fields and user profile preferences, cleaning up unnecessary calls',
            {'error_body_length': True},
        ),
        (
            # Expected FAIL: 'scope' missing parenthese
            'fix(bt: Update database schemas\n\nUpdating the database schema to include new fields.',
            {'error_scope_format': True},
        ),
        (
            # Expected FAIL: wrong 'type', uppercase in 'scope', 'summary' too long, 'summary' ends with period
            'fox(BT): Update database schemas. Updating the database schema to include new fields and user profile preferences, cleaning up unnecessary calls.',
            {
                'error_scope_capitalization': True,
                'error_summary_length': True,
                'error_summary_period': True,
                'error_type': True,
            },
        ),
    ],
    # Use the commit message to generate IDs for each test case
    ids=commit_message_id,
)
def commit_message(request, default_rules_output_status):
    # Combine the default dictionary with the test-specific dictionary
    combined_output = {**default_rules_output_status, **request.param[1]}
    return request.param[0], combined_output


def test_commit_message(commit_message, default_rules_output_status):  # pylint: disable=redefined-outer-name
    message_text, expected_output = commit_message

    # Reset rules_output_status to its default state before each test case
    rules_output_status.clear()
    rules_output_status.update(default_rules_output_status)

    # Create a temporary file to mock a commit message file input
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        temp.write(message_text)
        temp_file_name = temp.name

    # Run the main function of your script with the temporary file
    try:
        main([temp_file_name])  # Pass the file name as a positional argument
    finally:
        temp.close()  # Clean up the temporary file after the test

    # Retrieve the actual rules_output_status after running the main function
    actual_output = rules_output_status

    # Assert that the actual rules_output_status matches the expected output
    assert actual_output == expected_output, f'Failed on commit message: {message_text}'
