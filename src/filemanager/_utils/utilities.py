"""Small utility functions."""
import difflib
import re
import sys

from rich import print
from rich.prompt import Prompt


def select_option(
    options: dict[str, str],
    prompt: str = "Select an option",
    show_choices: bool = False,
    same_line: bool = False,
) -> str:
    """Select an option from a list of options and optionally keep the prompt on the same line.

    Args:
        options (list[str]): The list of options.
        prompt (str, optional): The prompt to display. Defaults to "Select an option: ".
        show_choices (bool, optional): Whether to print the choices. Defaults to False.
        same_line (bool, optional): Whether to keep the prompt on the same line. Defaults to False.

    Returns:
        str: The selected option.
    """
    if show_choices:
        print("[bold underline]Options:[/bold underline]\n")
        for option, text in options.items():
            print(f"[reverse bold cyan] {option.upper()} [/] [bold]{text}[/bold]")
        print(" ")

    if same_line:
        print(" ")

    while True:
        result = Prompt.ask(prompt)
        if result.lower() in (option.lower() for option in options):
            return result

        if same_line:
            sys.stdout.write("\033[1A")
            sys.stdout.write("\033[2K")
            sys.stdout.write("\033[1A")
            sys.stdout.write("\033[2K")

        print(f"[red]Invalid option: {result}[/red]")
        False


def dedupe_list(original: list) -> list:
    """Dedupe a list.

    Args:
        original (list): The list to dedupe.

    Returns:
        list: The de-duped list.

    """
    return list(set(original))


def diff_strings(a: str, b: str) -> str:
    """Visualize the difference between two strings.

    Args:
        a (str): The first string.
        b (str): The second string.

    Returns:
        str: A diff-like string using rich text colors to show the difference.

    """
    output = []
    matcher = difflib.SequenceMatcher(None, a, b)

    green = "[green reverse]"
    red = "[red reverse]"
    endgreen = "[/]"
    endred = "[/]"

    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == "equal":
            output.append(a[a0:a1])
        elif opcode == "insert":
            output.append(f"{green}{b[b0:b1]}{endgreen}")
        elif opcode == "delete":
            output.append(f"{red}{a[a0:a1]}{endred}")
        elif opcode == "replace":
            output.append(f"{green}{b[b0:b1]}{endgreen}")
            output.append(f"{red}{a[a0:a1]}{endred}")

    return "".join(output)


def from_camel_case(string: str) -> str:
    """Converts a string from camelCase to separate words.

    Args:
        string (str): String to convert.

    Returns:
        str: Converted string.
    """
    words = [word for word in re.split(r"(?=[A-Z][a-z])", string) if word]
    return " ".join(words)
