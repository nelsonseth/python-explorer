from inspect import cleandoc
import click
from python_explorer import run_app, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_THREADS

@click.command("python-explorer", short_help="Launch Python Explorer in browser.")
@click.option(
    "--host", "-h",
    default=DEFAULT_HOST,
    show_default=True,
    help="The interface to bind to."
)
@click.option(
    "--port", "-p",
    default=DEFAULT_PORT,
    show_default=True,
    help="The port to bind to."
)
@click.option(
    '--threads', '-t',
    default=DEFAULT_THREADS,
    show_default=True,
    help='Number of waitress threads.'
)
def run_explore(
    host,
    port,
    threads,
):
    """Launch Python Explorer in browser."""
    
    msg=  f"""
      Exploring: Python Explorer started on 'http://{host}:{port}/
      Exploring: Number of threads: {threads}
      Exploring: Press Ctrl+C to terminate
    """

    click.echo(cleandoc(msg))
    
    run_app(
        host,
        port,
        threads,
    )