"""CLI entry point."""

import click

from ascii_render.cli.render_cmd import render_cmd
from ascii_render.cli.interactive_cmd import interactive


@click.group()
def main():
    """Render images/videos to colored ASCII art with glow effects."""
    pass


main.add_command(render_cmd)
main.add_command(interactive)


if __name__ == "__main__":
    main()
