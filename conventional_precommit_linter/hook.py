import argparse
import re
import sys
from typing import List
from typing import Optional

DEFAULT_TYPES = ['change', 'ci', 'docs', 'feat', 'fix', 'refactor', 'remove', 'revert']

ERROR_EMPTY_MESSAGE = 'Commit message seems to be empty.'
ERROR_MISSING_COLON = "Missing colon after 'type' or 'scope'. Ensure the commit message has the format '<type><(scope/component)>: <summary>'."  # noqa: E501
ERROR_TYPE = "Issue with 'type'. Ensure the type is one of [{}]."
ERROR_SCOPE_CAPITALIZATION = "Issue with 'scope'. Ensure the scope starts with a lowercase letter. Allowed special characters in `scope` are _ / . , * -"  # noqa: E501
ERROR_SUMMARY_LENGTH = "Issue with 'summary'. Ensure the summary is between {} and {} characters long."
ERROR_SUMMARY_CAPITALIZATION = "Issue with 'summary'. Ensure the summary starts with an uppercase letter."
ERROR_SUMMARY_PERIOD = "Issue with 'summary'. Ensure the summary does not end with a period."
ERROR_BODY_FORMAT = "Incorrectly formatted 'body'. There should be one blank line between 'summary' and 'body'."
ERROR_BODY_LENGTH = "Issue with 'body' line length. {} line(s) exceeding line length limit."


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='conventional-pre-commit', description='Check a git commit message for Conventional Commits formatting.'
    )
    parser.add_argument('--types', type=str, nargs='*', help='Optional list of types to support')
    parser.add_argument(
        '--subject-min-length', type=int, default=20, help="Minimum length of the 'Summary' field in commit message"
    )
    parser.add_argument(
        '--subject-max-length', type=int, default=72, help="Maximum length of the 'Summary' field in commit message"
    )
    parser.add_argument(
        '--body-max-line-length', type=int, default=100, help='Maximum length of the line in message body'
    )
    parser.add_argument('--summary-uppercase', action='store_true', help='Summary must start with an uppercase letter')
    parser.add_argument('input', type=str, help='A file containing a git commit message')
    return parser.parse_args(argv)


def get_types(args: argparse.Namespace) -> str:
    # Provided types take precedence over default types
    types = args.types[0].split(',') if args.types else DEFAULT_TYPES
    return ', '.join(types)


def raise_error(message: str, error: str, types: str, args: argparse.Namespace) -> None:
    full_error_msg = f'❌ Invalid commit message: "{message}"\n{error}'

    guide_good_message = f"""
    commit message structure:  <type><(scope/component)>: <Summary>

    commit message rules:
        - use one of the following types: [{types}]
        - 'scope/component' is optional, but if used, it must start with a lowercase letter
        - 'summary' must not end with a period
        - 'summary' must be between {args.subject_min_length} and {args.subject_max_length} characters long
        - 'body' is optional, but if used, lines must be no longer than {args.body_max_line_length} characters
        - 'body' is optional, but if used, must be separated from the 'summary' by a blank line

    Example of a good commit message (with scope and body):
        fix(freertos): Fix startup timeout issue

        This is a text of commit message body ...

        ...

    Example of a good commit message (without scope and body):
        ci: added target test job for ESP32-Wifi6

        ...
    """

    print(f'{full_error_msg}{guide_good_message}')
    print(
        '\n\033[93m 👉 To preserve and correct a commit message, run\033[92m git commit --edit --file=.git/COMMIT_EDITMSG \033[0m'  # noqa: E501
    )
    raise SystemExit(1)


def read_commit_message(file_path: str) -> str:
    try:
        with open(file_path, encoding='utf-8') as f:
            lines = f.readlines()
            # Remove lines starting with '#'
            lines = [line for line in lines if not line.startswith('#')]
            content = ''.join(lines)
            if not content.strip():
                print(f'❌ {ERROR_EMPTY_MESSAGE}')
                raise SystemExit(1)
            return content
    except UnicodeDecodeError:
        print('❌ Problem with reading the commit message. Possible encoding issue.')
        raise SystemExit(1)


def parse_commit_message(args: argparse.Namespace, input_commit_message: str) -> None:
    # Split the 'commit message' into the 'message title' (first line) and 'message body' (the rest)
    message_title, *message_body = input_commit_message.strip().split('\n', 1)

    # First split 'message title' into potential 'type/scope' and 'summary'
    message_parts = message_title.split(': ', 1)  # using 1 as second argument to split only on first occurrence
    if len(message_parts) != 2:
        types = get_types(args)
        raise_error(message_title, ERROR_MISSING_COLON, types, args)

    # Check if a 'scope' is provided in the potential 'type/scope' part
    type_scope_parts = message_parts[0].split('(', 1)  # using 1 as second argument to split only on first occurrence
    if len(type_scope_parts) == 1:
        # no 'scope' provided
        commit_type = type_scope_parts[0]
        commit_scope = None
    else:
        # 'scope' provided
        commit_type = type_scope_parts[0]
        commit_scope = type_scope_parts[1].rstrip(')')

    commit_summary = message_parts[1]

    # Check for invalid commit 'type'
    types = get_types(args)
    if commit_type not in types.split(', '):
        error = ERROR_TYPE.format(types)
        raise_error(message_title, error, types, args)

    # If 'scope' is provided, check for valid 'scope'
    REGEX_SCOPE = r'^[a-z][a-zA-Z0-9_/.,*-]*$'
    if commit_scope and not re.match(REGEX_SCOPE, commit_scope):
        raise_error(message_title, ERROR_SCOPE_CAPITALIZATION, types, args)

    # Check for valid length of 'summary'
    summary_length = len(commit_summary)
    if summary_length < args.subject_min_length or summary_length > args.subject_max_length:
        error = ERROR_SUMMARY_LENGTH.format(args.subject_min_length, args.subject_max_length)
        raise_error(message_title, error, types, args)

    # Check if the 'summary' starts with a lowercase letter
    if args.summary_uppercase and commit_summary[0].islower():
        raise_error(message_title, ERROR_SUMMARY_CAPITALIZATION, types, args)

    # Check if the 'summary' ends with a period (full stop)
    if commit_summary[-1] == '.':
        raise_error(message_title, ERROR_SUMMARY_PERIOD, types, args)

    # Skip the rest if there is no message 'body' (as `body` is optional)
    if not message_body:
        return

    # Parse commit message 'body' (when it exists)
    if re.match(r'\n', message_body[0]):
        body = message_body[0][1:]  # Remove the first blank line

        # Check if each line of the 'body' is no longer than 100 characters
        lines = body.split('\n')
        invalid_lines = [line for line in lines if len(line) > args.body_max_line_length]
        num_invalid_lines = len(invalid_lines)
        if num_invalid_lines:
            error = ERROR_BODY_LENGTH.format(num_invalid_lines)

            for line in invalid_lines:
                print(f"  Line: '{line[:30]}...' (length: {len(line)})")
            raise_error(message_title, error, types, args)
    else:
        raise_error(message_title, ERROR_BODY_FORMAT, types, args)


def main(argv: Optional[List[str]] = None) -> None:
    argv = argv or sys.argv[1:]

    args = parse_args(argv)

    # Read commit message
    input_commit_message = read_commit_message(args.input)

    # Parse the commit message
    parse_commit_message(args, input_commit_message)


if __name__ == '__main__':
    main()
