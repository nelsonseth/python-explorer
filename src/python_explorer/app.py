import webbrowser

from dash import Dash, html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

# locals
from python_explorer.layouts import comp_id, page_layout, stores
from python_explorer.utils import callbacks

def serve_layout():
    return dmc.NotificationsProvider(
        html.Div(
            [
                html.Div(id=comp_id('notifier', 'app', 0)),
                page_layout,
                stores,  
            ],
            style={
                    'height':'100vh',
                    'width':'100vw',
                    'margin':'0',
                    'padding':'0',
                }
        ),
        position='top-right',
        autoClose=2500,
    )

# Static external bootstrap stylesheet located in /assets folder.
# This is why `external_stylesheets=[dbc.themes.BOOTSTRAP]` is not needed
# below.
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title='python explorer',
    suppress_callback_exceptions=True,
)  

server = app.server   

app.layout = serve_layout()

def run_app():
    webbrowser.open('http://127.0.0.1:8050/')
    app.run()

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run()