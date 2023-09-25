
from dash import Dash, html
                 
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# locals
from layouts import comp_id, page_layout, drawer, stores
from utils import callbacks

def serve_layout():
    return dmc.NotificationsProvider(
        html.Div(
            [
                html.Div(id=comp_id('notifier', 'app', 0)),
                page_layout,
                drawer,
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
        autoClose=2000,
    )


app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title='Python Explorer',
    suppress_callback_exceptions=True,
)  

server = app.server   

app.layout = serve_layout()

if __name__ == '__main__':
    app.run(debug=True)