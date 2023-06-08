import argparse
import sys
import re
from typing import Optional, List, Union

DEFAULT_TYPES = ["change", "ci", "docs", "feat", "fix", "refactor", "remove", "revert"]


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="conventional-pre-commit", description="Check a git commit message for Conventional Commits formatting.")

    parser.add_argument("--types", type=str, nargs="*", help="Optional list of types to support")
    parser.add_argument("--subject-min-length", type=int, default=20, help="Minimum length of the 'Summary' field in commit message")
    parser.add_argument("--subject-max-length", type=int, default=50, help="Maximum length of the 'Summary' field in commit message")
    parser.add_argument("--body-max-line-length", type=int, default=100, help="Maximum length of the line in message body")
    parser.add_argument("input", type=str, help="A file containing a git commit message")

    return parser.parse_args(argv)


def regex_types(args: argparse.Namespace) -> str:
    # Provided types take precedence over default types
    if args.types:
        print('using input types ...')
        types = args.types[0].split(',')
        return "(?:" + "|".join(types) + ")"
    # Use default types if no types are provided
    else:
        print('using default types ...')
        return "(?:" + "|".join(DEFAULT_TYPES) + ")"


def regex_scope() -> str:
    return r"\(([a-z][^\)]*)\)"


def regex_summary(args: argparse.Namespace) -> str:
    subject_min_length = args.subject_min_length
    subject_max_length = args.subject_max_length
    return fr"([A-Z].{{{subject_min_length},{subject_max_length}}}$)"


def raise_error(message: str, error: str, types: str, args: argparse.Namespace) -> None:
    print(f'❌ Invalid commit message: "{message}"')
    print(error)

    guide_good_message = f"""

    commit message structure:  <type><(scope/component)>: <Summary>

    commit message rules:
        - use one of the following types: [{types}]
        - 'scope/component' is optional, but if used, it must start with a lowercase letter
        - 'summary' must start with a capital letter
        - 'summary' must be between {args.subject_min_length} and {args.subject_max_length} characters long
        - 'body' lines must be no longer than {args.body_max_line_length} characters
        - 'body' must be separated from the 'summary' by a blank line


        Example of a good commit message (with scope adn body):
            feat(bt): Fixed issue with the timer

            This is a text of body

            ...

        Example of a good commit message (without scope and body):
            ci: Added target test job for ESP32-Wifi6

            ...
        """
    print(guide_good_message)

    raise SystemExit(1)


def read_commit_message(file_path: str) -> Optional[str]:
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        print('❌ Problem with reading the commit message')
        raise SystemExit(1)


def parse_commit_message(args: argparse.Namespace, input_commit_message: str) -> None:
    # Split the 'commit message' into the 'message title' (first line) and 'message body' (the rest)
    message_title, *message_body = input_commit_message.strip().split("\n", 1)

    # First split 'message title' into potential 'type/scope' and 'summary'
    message_parts = message_title.split(': ', 1)  # using 1 as second argument to split only on first occurrence
    if len(message_parts) != 2:
        error = "Missing colon after 'type' or 'scope'. Ensure the commit message has the format '<type>(<scope>): <summary>'."  # noqa: E501
        types = regex_types(args)[3:-1].replace("|", ", ")
        raise_error(message_title, error, types, args)

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
    types = regex_types(args)[3:-1].replace("|", ", ")
    if commit_type not in types.split(", "):
        error = f"Issue with 'type'. Ensure the type is one of [{types}]."
        raise_error(message_title, error, types, args)

    # If 'scope' is provided, check for valid 'scope'
    if commit_scope and not re.match(r"^[a-z][a-zA-Z0-9]*$", commit_scope):
        error = "Issue with 'scope'. Ensure the scope starts with a lowercase letter and contains only alphanumeric characters."  # noqa: E501
        raise_error(message_title, error, types, args)

    # Check for valid length of 'summary'
    summary_length = len(commit_summary)
    if summary_length < args.subject_min_length or summary_length > args.subject_max_length:
        error = f"Issue with 'summary'. Ensure the summary is between {args.subject_min_length} and {args.subject_max_length} characters long."  # noqa: E501
        raise_error(message_title, error, types, args)

    # Check if the 'summary' starts with a lowercase letter
    if commit_summary[0].islower():
        error = "Issue with 'summary'. Ensure the summary starts with an uppercase letter."
        raise_error(message_title, error, types, args)

    # Check if the 'summary' ends with a period (full stop)
    if commit_summary[-1] == '.':
        error = "Issue with 'summary'. Ensure the summary does not end with a period."
        raise_error(message_title, error, types, args)

    # Parse commit message additional 'body' (if it exists)
    if message_body:
        if re.match(r"\n", message_body[0]):
            body = message_body[0][1:]  # Remove the first blank line

            # Check if each line of the 'body' is no longer than 100 characters
            lines = body.split("\n")
            invalid_lines = [line for line in lines if len(line) > args.body_max_line_length]
            num_invalid_lines = len(invalid_lines)
            if num_invalid_lines:
                error = f"Issue with 'body' line length. {num_invalid_lines} line(s) exceeding line length limit."

                for line in invalid_lines:
                    print(f"  Line: '{line[:30]}...' (length: {len(line)})")
                raise_error(message_title, error, types, args)
        else:
            error = "Incorrectly formatted 'body'. There should be one blank line between 'summary' and 'body'."
            raise_error(message_title, error, types, args)


def main(argv: Optional[List[str]] = None) -> None:
    argv = argv or sys.argv[1:]

    args = parse_args(argv)

    # Read commit message
    input_commit_message = read_commit_message(args.input)

    # Parse the commit message
    if input_commit_message is not None:
        parse_commit_message(args, input_commit_message)
    else:
        print("Error: commit message is None")
        return


if __name__ == "__main__":
    main()
