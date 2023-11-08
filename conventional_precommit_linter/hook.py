import argparse
import re
import sys
from typing import List
from typing import Optional
from typing import Tuple

from .helpers import _color_blue
from .helpers import _color_bold_green
from .helpers import _color_grey
from .helpers import _color_orange
from .helpers import _color_purple


rules_output_status = {
    'empty_message': False,
    'error_body_format': False,
    'error_body_length': False,
    'error_scope_capitalization': False,
    'error_scope_format': False,
    'error_summary_capitalization': False,
    'error_summary_length': False,
    'error_summary_period': False,
    'error_type': False,
    'missing_colon': False,
}


def allowed_types(args: argparse.Namespace) -> str:
    default_types = ['change', 'ci', 'docs', 'feat', 'fix', 'refactor', 'remove', 'revert']
    # Provided types take precedence over default types
    types = args.types[0].split(',') if args.types else default_types
    return ', '.join(types)


def read_commit_message(file_path: str) -> str:
    with open(file_path, encoding='utf-8') as file:
        lines = file.readlines()
        lines = [line for line in lines if not line.startswith('#')]  # Remove comment lines (starting with '#')
        content = ''.join(lines)
        if not content.strip():
            rules_output_status['empty_message'] = True
        return content


def split_message_title(message_title: str) -> Tuple[str, Optional[str], str]:
    """Split 'message title' into 'type/scope' and 'summary'"""
    type_and_scope, _, commit_summary = message_title.partition(': ')
    commit_type, _, scope_part = type_and_scope.partition('(')

    # Check if both opening and closing parentheses are present
    if '(' in type_and_scope and ')' not in scope_part:
        rules_output_status['error_scope_format'] = True
        return commit_type, None, commit_summary  # Return None for the scope due to the error

    commit_scope: Optional[str] = scope_part.rstrip(')').strip() if scope_part else None
    commit_summary = commit_summary.strip()
    return commit_type, commit_scope, commit_summary


def check_colon_after_type(message_title: str) -> bool:
    """Check for missing column between type / type(scope) and summary."""
    message_parts = message_title.split(': ', 1)  # split only on first occurrence
    if len(message_parts) != 2:
        rules_output_status['missing_colon'] = True
        return False
    return True


def check_allowed_types(commit_type: str, args: argparse.Namespace) -> None:
    """Check for allowed types."""
    types = allowed_types(args)
    if commit_type not in types:
        rules_output_status['error_type'] = True


def check_scope(commit_scope: str) -> None:
    """Check for scope capitalization and allowed characters"""
    regex_scope = r'^[a-z0-9_/.,*-]*$'
    if commit_scope and not re.match(regex_scope, commit_scope):
        rules_output_status['error_scope_capitalization'] = True


def check_summary_length(commit_summary: str, args: argparse.Namespace) -> None:
    """Check for summary length (between min and max allowed characters)"""
    summary_length = len(commit_summary)
    if summary_length < args.subject_min_length or summary_length > args.subject_max_length:
        rules_output_status['error_summary_length'] = True


def check_summary_lowercase(commit_summary: str) -> None:
    """Check for summary starting with an uppercase letter (rule disabled in default config)"""
    if commit_summary[0].islower():
        rules_output_status['error_summary_capitalization'] = True


def check_summary_period(commit_summary: str) -> None:
    """Check for summary ending with a period"""
    if commit_summary[-1] == '.':
        rules_output_status['error_summary_period'] = True


def check_body_empty_lines(message_body: List[str]) -> None:
    """Check for empty line between summary and body"""
    if not message_body[0].strip() == '':
        rules_output_status['error_body_format'] = True


def check_body_lines_length(message_body: List[str], args: argparse.Namespace) -> None:
    """Check for body lines length (shorter than max allowed characters)"""
    if not all(len(line) <= args.body_max_line_length for line in message_body):
        rules_output_status['error_body_length'] = True


def _get_icon_for_rule(status: bool) -> str:
    """Return a icon depending on the status of the rule (True = error found, False = success))"""
    return '❌' if status else '✔️ '


def print_report(commit_type: str, commit_scope: Optional[str], commit_summary: str, args) -> None:
    # Color the input commit message with matching element colors
    commit_message = f'{_color_purple(commit_type)}: { _color_orange( commit_summary)}'
    if commit_scope:
        commit_message = (
            f'{_color_purple(commit_type)}({ _color_blue( commit_scope)}): { _color_orange( commit_summary)}'
        )

    # Rule messages that are always included
    rule_messages = [
        f"{_get_icon_for_rule(rules_output_status['error_type'])} {_color_purple('<type>')} is mandatory, use one of the following: [{_color_purple(allowed_types(args))}]",
        f"{_get_icon_for_rule(rules_output_status['error_scope_format'])} {_color_blue('(<optional-scope>)')} if used, must be enclosed in parentheses",
        f"{_get_icon_for_rule(rules_output_status['error_scope_capitalization'])} {_color_blue('(<optional-scope>)')} if used, must be written in lower case without whitespace",
        f"{_get_icon_for_rule(rules_output_status['error_summary_period'])} {_color_orange('<summary>')} must not end with a period",
        f"{_get_icon_for_rule(rules_output_status['error_summary_length'])} {_color_orange('<summary>')} must be between {args.subject_min_length} and {args.subject_max_length} characters long",
        f"{_get_icon_for_rule(rules_output_status['error_body_length'])} {_color_grey('<body>')} lines must be no longer than {args.body_max_line_length} characters",
        f"{_get_icon_for_rule(rules_output_status['error_body_format'])} {_color_grey('<body>')} must be separated from the 'summary' by a blank line",
    ]

    # Dynamically add the additional rules set by arguments
    if args.summary_uppercase:
        rule_messages.append(
            f"{_get_icon_for_rule(rules_output_status['error_summary_capitalization'])} {_color_orange('<summary>')} must start with an uppercase letter"
        )

    # Combine the rule messages into the final report block
    message_rules_block = '    ' + '\n        '.join(rule_messages)

    full_guide_message = f"""\n❌ INVALID COMMIT MESSAGE: {commit_message}
    _______________________________________________________________
    Commit message structure:  {_color_purple('<type>')}{_color_blue("(<optional-scope>)")}: {_color_orange('<summary>')}
                                <... empty line ...>
                                {_color_grey('<optional body lines>')}
                                {_color_grey('<optional body lines>')}
    _______________________________________________________________
    Commit message rules:
    {message_rules_block}
    """
    print(full_guide_message)
    print(
        f'👉 To preserve and correct a commit message, run: {_color_bold_green("git commit --edit --file=.git/COMMIT_EDITMSG")}'
    )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog='conventional-pre-commit', description='Check a git commit message for Conventional Commits formatting.'
    )
    parser.add_argument('--types', type=str, nargs='*', help='Optional list of types to support')
    parser.add_argument('--subject-min-length', type=int, default=20, help="Minimum length of the 'Summary'")
    parser.add_argument('--subject-max-length', type=int, default=72, help="Maximum length of the 'Summary'")
    parser.add_argument('--body-max-line-length', type=int, default=100, help='Maximum length of the body line')
    parser.add_argument('--summary-uppercase', action='store_true', help='Summary must start with an uppercase letter')
    parser.add_argument('input', type=str, help='A file containing a git commit message')
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    args = parse_args(argv)

    # Parse the commit message in to parts
    input_commit_message = read_commit_message(args.input)

    if not input_commit_message.strip():
        print('❌ Commit message seems to be empty.')
        return 1

    message_lines = input_commit_message.strip().split('\n')  # Split the commit message into lines
    message_title = message_lines[0]  # The summary is the first line
    message_body = message_lines[1:]  # The body is everything after the summary, if it exists
    commit_type, commit_scope, commit_summary = split_message_title(message_title)

    if not check_colon_after_type(message_title):
        print(f'❌ Missing colon after {_color_purple("<type>")} or {_color_blue("(<optional-scope>)")}.')
        print(
            f'\nEnsure the commit message has the format \"{_color_purple("<type>")}{_color_blue("(<optional-scope>)")}: {_color_orange("<summary>")}\"'
        )
        return 1

    # Commit message title (first line) checks
    check_allowed_types(commit_type, args)
    if commit_scope:
        check_scope(commit_scope)
    check_summary_length(commit_summary, args)
    check_summary_period(commit_summary)
    if args.summary_uppercase:
        check_summary_lowercase(commit_summary)

    # Commit message body checks
    if message_body:
        check_body_empty_lines(message_body)
        check_body_lines_length(message_body, args)

    # Create report if issues found
    if any(value for value in rules_output_status.values()):
        print_report(commit_type, commit_scope, commit_summary, args)
        return 1

    # No output and exit RC 0 if no issues found
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
