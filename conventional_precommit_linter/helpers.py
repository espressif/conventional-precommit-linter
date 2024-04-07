from colorama import Fore
from colorama import init
from colorama import Style

init(autoreset=True)  # Automatically reset the style after each print


def _color_bold_green(text: str) -> str:
    return f'{Style.BRIGHT}{Fore.GREEN}{text}{Style.RESET_ALL}'


def _color_purple(text: str) -> str:
    return f'{Fore.MAGENTA}{text}{Style.RESET_ALL}'


def _color_orange(text: str) -> str:
    return f'{Fore.YELLOW}{text}{Style.RESET_ALL}'


def _color_blue(text: str) -> str:
    return f'{Fore.LIGHTBLUE_EX}{text}{Style.RESET_ALL}'


def _color_grey(text: str) -> str:
    return f'{Fore.LIGHTBLACK_EX}{text}{Style.RESET_ALL}'


def _color_red(text: str) -> str:
    return f'{Fore.RED}{text}{Style.RESET_ALL}'


def _color_green(text: str) -> str:
    return f'{Fore.GREEN}{text}{Style.RESET_ALL}'
