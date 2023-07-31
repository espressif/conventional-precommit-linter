import tempfile

import pytest

from conventional_precommit_linter.hook import ERROR_BODY_FORMAT
from conventional_precommit_linter.hook import ERROR_BODY_LENGTH
from conventional_precommit_linter.hook import ERROR_EMPTY_MESSAGE
from conventional_precommit_linter.hook import ERROR_MISSING_COLON
from conventional_precommit_linter.hook import ERROR_SCOPE_CAPITALIZATION
from conventional_precommit_linter.hook import ERROR_SUMMARY_CAPITALIZATION
from conventional_precommit_linter.hook import ERROR_SUMMARY_LENGTH
from conventional_precommit_linter.hook import ERROR_SUMMARY_PERIOD
from conventional_precommit_linter.hook import ERROR_TYPE
from conventional_precommit_linter.hook import main

# Input arguments
TYPES = 'change, ci, docs, feat, fix, refactor, remove, revert, fox'
SUBJECT_MIN_LENGTH = 21
SUBJECT_MAX_LENGTH = 53
BODY_MAX_LINE_LENGTH = 101
SUMMARY_UPPERCASE = True


# Fixture for messages
@pytest.fixture(
    params=[
        (
            # Expected PASS: Message with scope and body
            'feat(bootloader): This is commit message with scope and body\n\nThis is a text of body',
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope, without body
            'change(wifi): This is commit message with scope without body',
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope (with hyphen in scope), without body
            'change(esp-rom): This is commit message with hyphen in scope',
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope (with asterisk in scope), without body
            'change(examples*storage): This is commit message with asterisk in scope',
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope (with comma in scope), without body
            'change(examples,storage): This is commit message with comma in scope',
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope (with slash in scope), without body
            'change(examples/storage): This is commit message with slash in scope',
            True,
            None,
        ),
        (
            # Expected PASS: Message without scope, with body
            'change: This is commit message without scope with body\n\nThis is a text of body\n# Please enter the commit message for your changes. Lines starting\n# with \'#\' will be ignored, and an empty message aborts the commit.\n#',  # noqa: E501
            True,
            None,
        ),
        (
            # Expected PASS: Message without scope, without body
            'change: This is commit message without scope and body',
            True,
            None,
        ),
        (
            # Expected PASS: Test of additional types
            'fox(esp32): Testing additional types\n\nThis is a text of body',
            True,
            None,
        ),
        (
            # Expected FAIL: missing colon between 'type' (and 'scope') and 'summary'
            'change this is commit message without body',
            False,
            ERROR_MISSING_COLON,
        ),
        (
            # Expected FAIL: 'summary' too short
            'fix: Fix bug',
            False,
            ERROR_SUMMARY_LENGTH.format(SUBJECT_MIN_LENGTH, SUBJECT_MAX_LENGTH),
        ),
        (
            # Expected FAIL: 'summary' too long
            'change(rom): Refactor authentication flow for enhanced security measures',
            False,
            ERROR_SUMMARY_LENGTH.format(SUBJECT_MIN_LENGTH, SUBJECT_MAX_LENGTH),
        ),
        (
            # Expected FAIL: 'summary' ends with period
            'change(rom): Fixed the another bug.',
            False,
            ERROR_SUMMARY_PERIOD,
        ),
        (
            # Expected FAIL: 'summary' starts with lowercase
            'change(rom): this message starts with lowercase',
            False,
            ERROR_SUMMARY_CAPITALIZATION,
        ),
        (
            # Expected FAIL: uppercase in 'scope'
            'change(Bt): Added new feature with change\n\nThis feature adds functionality',
            False,
            ERROR_SCOPE_CAPITALIZATION,
        ),
        (
            # Expected FAIL: uppercase in 'scope'
            'fix(dangerGH): Update token permissions - allow Danger to add comments to PR',
            False,
            ERROR_SCOPE_CAPITALIZATION,
        ),
        (
            # Expected FAIL: not allowed 'type' with scope and body
            'delete(bt): Added new feature with change\n\nThis feature adds functionality',
            False,
            # Adjusted expected error message
            ERROR_TYPE.format(TYPES),
        ),
        (
            # Expected FAIL: not allowed 'type' without scope and without body
            'wip: Added new feature with change',
            False,
            # Adjusted expected error message
            ERROR_TYPE.format(TYPES),
        ),
        (
            # Expected FAIL: not allowed 'type' (type starts with uppercase)
            'Fix(bt): Added new feature with change\n\nThis feature adds functionality',
            False,
            ERROR_TYPE.format(TYPES),
        ),
        (
            # Expected FAIL: missing blank line between 'summary' and 'body'
            'change: Added new feature with change\nThis feature adds functionality',
            False,
            ERROR_BODY_FORMAT,
        ),
        (
            # Expected FAIL: 'body' line too long
            'fix(bt): Update database schemas\n\nUpdating the database schema to include new fields and user profile preferences, cleaning up unnecessary calls',  # noqa: E501
            False,
            ERROR_BODY_LENGTH.format(1),  # 1 here means found one line that is too long
        ),
        (
            # Expected FAIL: empty commit message
            '   \n\n   \n',
            False,
            ERROR_EMPTY_MESSAGE,
        ),
    ]
)
def message(request):
    return request.param


def test_commit_message(message, capsys):
    # Unpack the message, the expectation, and the expected error message
    message_text, should_pass, expected_error = message

    # Convert the constants into a list of command-line arguments
    argv = [
        '--types',
        TYPES.replace(', ', ','),
        '--subject-min-length',
        str(SUBJECT_MIN_LENGTH),
        '--subject-max-length',
        str(SUBJECT_MAX_LENGTH),
        '--body-max-line-length',
        str(BODY_MAX_LINE_LENGTH),
        '--summary-uppercase',
    ]

    # Create a temporary file and write the commit message to it
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(message_text.encode())
        temp_file_name = temp.name

    # Add the path of the temp file to the arguments
    argv.append(temp_file_name)

    # If the message is expected to be invalid, check that it raises SystemExit and that the error message matches
    if not should_pass:
        with pytest.raises(SystemExit):
            main(argv)
        captured = capsys.readouterr()
        assert expected_error in captured.out
    else:
        main(argv)
