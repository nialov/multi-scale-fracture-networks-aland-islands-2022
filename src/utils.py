"""
General utilities.
"""

from rich.console import Console

CONSOLE = Console()


print = CONSOLE.print


def wide_table(latex_table: str) -> str:
    """
    Widen table spec.
    """
    return latex_table.replace(r"\begin{table}", r"\begin{table*}").replace(
        r"\end{table}", r"\end{table*}"
    )
