<h1 style="text-align: center">Python Explorer</h1>

<p style="text-align: center; font-style: italic">A Python environment exploration interface.</p>

Written 100% in Python and renders in your browser using [Dash](https://dash.plotly.com).

An online demo version can be accessed here: [python-explorer demo](https://python-explorer.onrender.com/).

Install
-------
Install with pip into your current environment.

```cmd
> pip install python-explorer
```
To open and run the interface from the command line interface, type ```python-explorer```. This will launch the interface in your default browser. To terminate the session, press Ctrl+C while in the command prompt.

```cmd
> python-explorer
Exploring: Python Explorer started on 'http://127.0.0.1:8080/
Exploring: Number of threads: 8
Exploring: Press Ctrl+C to terminate
```
Access help features and other options with the --help option.

```cmd
> python-explorer --help
Usage: python-explorer [OPTIONS]

  Launch Python Explorer in browser.

Options:
  -h, --host TEXT        The interface to bind to.  [default: 127.0.0.1]
  -p, --port TEXT        The port to bind to.  [default: 8080]
  -t, --threads INTEGER  Number of waitress threads.  [default: 8]
  --help                 Show this message and exit.
```

Other Resources
---------------
Source Code: [github.com/nelsonseth/python-explorer](https://github.com/nelsonseth/python-explorer)

Documentation: [Github README](https://github.com/nelsonseth/python-explorer/blob/main/README.md)