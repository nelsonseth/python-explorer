
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

# local
from .layout_utils import (
    comp_id,
    placeholder_text,
    get_package_accordion,
    BORDER_COLOR,
    HEADER_COLOR_DARK,
    HEADER_COLOR_LIGHT,
)

# the nightmare that is figuring out relative imports
# import sys
# from pathlib import Path
# sys.path.append(Path(__file__).parent.parent)

from python_explorer.utils.envdata import (
    env_site_packages,
    env_std_modules,
    all_packages,
)


# 'border':f'1px solid {BORDER_COLOR}',

# list of dbc.Col() items to place in children of header row
header_content = [
    dbc.Col(
        get_package_accordion(all_packages, env_std_modules, env_site_packages),
        width=3,
        style={
            'height':'100%',
            'margin':'0',
            'padding':'0.5em 0.5em 0 0.5em',
        }
    ),
    dbc.Col([
        dbc.Row(
            placeholder_text('Current Package'),
            id=comp_id('package-info', 'package', 0),
            style={
                'height':'65%',
                'width':'100%',
                'margin':'0',
                'padding':'0.5em',
            }
        ),
        dbc.Row(
            placeholder_text('Explorer Navigation'),
            id=comp_id('t-breadcrumbs','trace', 0),
            style={
                'height':'35%',
                'width':'100%',
                'margin':'0',
                'padding':'0.25em 0 0 0.5em',
            }
        ),
        ],
        width=6,
        style={
            'height':'100%',
            'margin':'0',
            'padding':'0 0 0 0',
        },
    ),
    dbc.Col(
        dmc.Stack([
            dmc.Group([
                dmc.ThemeIcon(
                    DashIconify(
                        icon='logos:python',
                        style={
                            'height':'2em',
                            'width':'2em',
                        }
                    ),
                    style={
                        'background-color':'transparent',
                    }
                ),
                dmc.Text(
                    'python explorer',
                    align='center',
                    color='#ffffff',
                    style={
                        'font-family':'Arial, sans-serif',
                        'font-size':'1.8em',
                        'font-weight':'700',
                    }
                ),
                ],
                position='right',
                spacing=4,
            ),
            dmc.Group([
                dmc.Text(
                    'About:',
                    italic=True,
                    color='#ffffff',
                    style={
                        'font-family':'Arial, sans-serif',
                        'font-size':'1em',
                        'font-weight':'400',
                    }
                ),
                dmc.NavLink(
                    icon=DashIconify(
                        icon='devicon:github',
                        style={
                            'height':'2em',
                            'width':'2em',
                        }
                    ),
                    href='https://github.com/nelsonseth/python-explorer',
                    style={
                        'height':'2.3em',
                        'width':'2.3em',
                        'padding':'0.1em',
                        'margin':'0',
                        'border-top-left-radius':'8px',
                        'border-top-right-radius':'8px',
                        'border-bottom-left-radius':'8px',
                        'border-bottom-right-radius':'8px',
                        'background-color':HEADER_COLOR_LIGHT,
                    }
                ),
                ],
                position='right',
                spacing=6,
            ),
            ],
            justify='space-between',
            style={
                'height':"100%"
            },
        ),
        width=3,
        style={
            'height':'100%',
            'margin':'0',
            'padding':'0.25em 1em 0.5em 0',
            'position':'relative',  
        }
    ),
]