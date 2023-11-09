from inspect import cleandoc
import click
from python_explorer import run_app

@click.command("python-explorer", short_help="Launch Python Explorer in browser.")
@click.option("--host", "-h", default="127.0.0.1", help="The interface to bind to.")
@click.option("--port", "-p", default='8080', help="The port to bind to.")
@click.option('--threads', '-t', default=8, help='Number of waitress threads.')
def run_explore(
    host,
    port,
    threads,
):
    """Launch Python Explorer in browser.
    """
    
    msg=  f"""
      Exploring: Python explorer started on 'http://{host}:{port}/
      Exploring: Number of threads: {threads}
      Exploring: Press Ctrl+C to terminate
    """

    click.echo(cleandoc(msg))
    
    run_app(
        host,
        port,
        threads,
    )