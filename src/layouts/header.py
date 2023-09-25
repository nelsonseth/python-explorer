
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
from dash import html

# local
from .layout_utils import (
    comp_id,
    placeholder_text,
    HEADER_COLOR,
    BORDER_COLOR
)

# 'border':f'1px solid {BORDER_COLOR}',

# list of dbc.Col() items to place in children of header row
header_content = [
    dbc.Col(
        dmc.Group([
            dmc.ActionIcon(
                DashIconify(
                    icon='iconamoon:menu-burger-horizontal',
                    color='black',
                    style={
                        'height':'2.5em',
                        'width':'2.5em',
                    }
                ),
                variant='light',
                id=comp_id('burger', 'drawer', 0),
                style={
                    'height':'2.5em',
                    'width':'2.5em',
                    'background-color':HEADER_COLOR,
                    'margin-top':'0.2em',
                    'padding':'0',
                }
            ),
            html.Div(
                style={
                    'width':'0.5em',
                    'margin':'0',
                    'padding':'0',
                }
            ),
            dmc.ThemeIcon(
                DashIconify(
                    icon='devicon:python',
                    style={
                        'height':'1.5em',
                        'width':'1.5em',
                    }
                ),
                style={
                    'background-color':HEADER_COLOR,
                }
            ),
            dmc.Text(
                'Python Explorer',
                align='center',
                style={
                    'font-size':'1.2em',
                    'font-weight':'700',
                }
            ),
            ],
            position='left',
            spacing=2,
        ),
        width=3,
        style={
            'height':'100%',
            'margin':'0',
            'padding':'0 0 0 1em',
        }
    ),
    dbc.Col(
        placeholder_text('Explorer Navigation'),
        id=comp_id('t-breadcrumbs','trace', 0),
        width=7,
        style={
                'height':'100%',
                'margin':'0',
                'padding':'0.5em 0 0 10px',
            }
    ),
    dbc.Col(
        dmc.Group([
            dmc.Text(
                'About:',
                weight=600,
            ),
            dmc.NavLink(
                icon=DashIconify(
                    icon='devicon:github',
                    style={
                        'height':'2.2em',
                        'width':'2.2em',
                    }
                ),
                href='https://github.com/nelsonseth/python-explorer',
                variant = 'subtle',
                style={
                    'height':'2.2em',
                    'width':'2.2em',
                    'padding':'0',
                    'background-color':HEADER_COLOR,
                }
            ),
            ],
            position='right',
            spacing=6,
        ),
        width=2,
        style={
            'height':'100%',
            'margin':'0',
            'padding':'0.35em 1em 0 0',  
        }
    ),
]