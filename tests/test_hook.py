import tempfile
import pytest
from conventional_precommit_linter.hook import main


# Fixture for arguments
@pytest.fixture(
    params=[
        {
            'types': 'change,ci,docs,feat,fix,refactor,remove,revert, fox',
            'subject-max-length': '50',
            'subject-min-length': '20',
            'body-max-line-length': '100',
        }
    ]
)
def args(request):
    return request.param


# Fixture for messages
@pytest.fixture(
    params=[
        (
            # Expected PASS: Message with scope and body
            "fix(bt): Fix4567890123456 78901234567891111111\n\nThis is a text of body",
            True,
            None,
        ),
        (
            # Expected PASS: Message with scope, without body
            "change(wifi): Added new feature with change",
            True,
            None,
        ),
        (
            # Expected PASS: Message without scope, with body
            "change: Added new feature with change\n\nThis feature adds functionality",
            True,
            None,
        ),
        (
            # Expected PASS: Message without scope, without body
            "change: Added new feature with change",
            True,
            None,
        ),
        (
            # Expected FAIL: missing blank line between 'summary' and 'body'
            "change: Added new feature with change\nThis feature adds functionality",
            False,
            '❌ Invalid commit message: "change: Added new feature with change"\nIncorrectly formatted \'body\'',
        ),
        (
            # Expected FAIL: 'summary' too short
            "change: Added thing",
            False,
            '❌ Invalid commit message: "change: Added thing"\nIssue with \'summary\'',
        ),
        (
            # Expected FAIL: 'summary' too long
            "change(rom): 012345678900123456789001234567890012345678900123456789001234567890",
            False,
            '❌ Invalid commit message: "change(rom): 012345678900123456789001234567890012345678900123456789001234567890"\nIssue with \'summary\'',  # noqa: E501
        ),
        (
            # Expected FAIL: lowercase and ends with period
            "change(rom): Fixed the another bug.",
            False,
            "❌ Invalid commit message: \"change(rom): Fixed the another bug.\"\nIssue with 'summary'. Ensure the summary does not end with a period.",  # noqa: E501
        ),
        (
            # Expected FAIL: 'summary' starts with lowercase
            "change(rom): this starts with lowercase",
            False,
            '❌ Invalid commit message: "change(rom): this starts with lowercase"\nIssue with \'summary\'. Ensure the summary starts with an uppercase letter.',  # noqa: E501
        ),
        (
            # Expected FAIL: uppercase in 'scope'
            "change(Bt): Added new feature with change\n\nThis feature adds functionality",
            False,
            '❌ Invalid commit message: "change(Bt): Added new feature with change"\nIssue with \'scope\'',
        ),
        (
            # Expected FAIL: not allowed 'type'
            "xxx(bt): Added new feature with change\n\nThis feature adds functionality",
            False,
            '❌ Invalid commit message: "xxx(bt): Added new feature with change"\nIssue with \'type\'',
        ),
        (
            # Expected FAIL: not allowed 'type' (type starts with uppercase)
            "Fix(bt): Added new feature with change\n\nThis feature adds functionality",
            False,
            '❌ Invalid commit message: "Fix(bt): Added new feature with change"\nIssue with \'type\'',
        ),
    ]
)
def message(request):
    return request.param


def test_commit_message(args, message, capsys):
    # Unpack the message, the expectation, and the expected error message
    message_text, should_pass, expected_error = message

    # Convert the args dictionary into a list of command-line arguments
    argv = []
    for k, v in args.items():
        argv.append(f"--{k}")
        argv.append(v)

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
