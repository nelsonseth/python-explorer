
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify

from .layout_utils import (
    comp_id,
    HEADER_COLOR,
    PAPER_BCOLOR,
    BORDER_COLOR,
)

from .header import header_content
from .body_left import body_left
from .body_right_members import body_right_member_info
from .body_right_cyto import body_right_cyto


page_layout = dbc.Container([
    dbc.Row(
        children=header_content,
        align='center',
        justify='around',
        style={
            'height':'3em',
            'width':'100%',
            'margin':'0',
            'padding':'0',
            'border-left':f'1px solid {BORDER_COLOR}',
            'border-top':f'1px solid {BORDER_COLOR}',
            'border-right':f'1px solid {BORDER_COLOR}',
            'border-top-left-radius':'10px',
            'border-top-right-radius':'10px',
            'background-color':HEADER_COLOR,
        }
    ),
    dbc.Row([
        dbc.Col(
            body_left,
            width=3,
            style={
                'height':'100%',
                'margin':'0',
                'padding':'0',
            }
        ),
        dbc.Col(
            dmc.Paper(
                dmc.Tabs([
                        dmc.TabsList(
                            [
                                dmc.Tab(
                                    dmc.Text(
                                        'Member Information',
                                        size='lg',
                                        weight=600,
                                        italic=True,
                                    ),
                                    value = 'member-information',
                                    icon = DashIconify(
                                        icon='devicon:readthedocs',
                                        style={
                                            'height':'1em'
                                        }
                                    ),
                                    style={
                                        'height':'2.5em',
                                        'border-top':f'1px solid {BORDER_COLOR}',
                                        'border-left':f'1px solid {BORDER_COLOR}',
                                        'border-right':f'1px solid {BORDER_COLOR}',
                                        'border-top-left-radius':'10px',
                                        'border-top-right-radius':'10px',
                                        'margin':'0 2px 0 2px',
                                        'background-color':PAPER_BCOLOR,
                                    }
                                ),
                                dmc.Tab(
                                    dmc.Text(
                                        'Class Explorer',
                                        size='lg',
                                        weight=600,
                                        italic=True,
                                    ),
                                    value = 'class-explorer',
                                    icon = DashIconify(
                                        icon='mdi:graph',
                                        style={
                                            'height':'1em'
                                        }
                                    ),
                                    style={
                                        'height':'2.5em',
                                        'border-top':f'1px solid {BORDER_COLOR}',
                                        'border-left':f'1px solid {BORDER_COLOR}',
                                        'border-right':f'1px solid {BORDER_COLOR}',
                                        'border-top-left-radius':'10px',
                                        'border-top-right-radius':'10px',
                                        'margin':'0 2px 0 2px',
                                        'background-color':PAPER_BCOLOR,
                                    }
                                ),
                            ],
                            #grow=True,
                        ),
                        dmc.TabsPanel(
                            body_right_member_info,
                            value='member-information',
                            style={
                                'height':r'calc(100% - 2.5em)',
                                'width':'100%',
                                'margin':'0',
                                'padding':'4px 0 0 0',
                                'background-color':PAPER_BCOLOR,
                            }
                        ),
                        dmc.TabsPanel(
                            body_right_cyto,
                            value='class-explorer',
                            style={
                                'height':r'calc(100% - 2.5em)',
                                'width':'100%',
                                'margin':'0',
                                'padding':'4px 0 0 0',
                                'background-color':PAPER_BCOLOR,
                            }
                        )
                    ],
                    id=comp_id('body-right-tabs', 'app', 0),
                    value='member-information',
                    variant='default',
                    color='green',
                    orientation='horizontal',
                    style={
                        'background-color':PAPER_BCOLOR,
                        'height':'100%',
                        'width':'100%',
                        'padding':'0',
                        'margin':'0',
                    }
                ),
                radius=0,
                shadow='lg',
                style={
                    'height':'100%',
                    'width':'100%',
                    'margin':'0',
                    'padding':'2px',
                    'border-right':f'1px solid {BORDER_COLOR}',
                    'border-bottom':f'1px solid {BORDER_COLOR}',
                    'border-bottom-right-radius':'10px',
                    'background-color':PAPER_BCOLOR,
                }
            ),
            width=9,
            style={
                'height':'100%',
                'margin':'0',
                'padding':'0',
            }
        )
        ],
        align='center',
        style={
            'height':'calc(100vh - 20px - 3em)',
            'min-height':'600px',
            'width':'100%',
            'margin':'0',
            'padding':'0',
        }
    )
    ],
    fluid=True,
    style={
        'height':'100vh',
        'width':'100vw',
        'min-width':'1000px',
        'margin':'0',
        'padding':'5px 15px 15px 15px',
    }

)