
from dash import dcc
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

# local
from .layout_utils import (
    comp_id,
    placeholder_text,
    PAPER_BCOLOR,
    BORDER_COLOR,
)

from .cyto_utils import cyto_layout_dropdown

# body right cyto is the contents of the main body right column when the 
# Class Explorer tab is selected. Contains and controls the cytoscape graph
# features.
body_right_cyto = dbc.Container([
        dbc.Row([
            dbc.Col([
                dmc.Card([
                    dmc.CardSection(
                        dmc.Group([
                            dcc.Markdown(
                                'Class Space',
                                id=comp_id('current-class-space', 'cyto', 0),
                                style={
                                    'margin':'0.6em 0 0 0'
                                }
                            ),
                            dmc.Group([
                                dmc.Text(
                                    'Choose a layout: ',
                                ),
                                cyto_layout_dropdown,
                                dmc.Space(h=8),
                                dmc.Text(
                                    'Show Legend: '
                                ),
                                dmc.Switch(
                                    id=comp_id('cyto-legend-switch', 'cyto', 0),
                                    radius='lg',
                                    size='sm',
                                    checked=False,
                                )
                                ],
                                position='right',
                                spacing=4,
                            ),
                            ],
                            position='apart',
                        ),
                        style={
                            'height':'3em',
                            'width':'100%',
                            'margin':'0',
                            'padding':'0 10px 0 10px',
                            'border-bottom':f'1px solid {BORDER_COLOR}'
                        }
                    ),
                    dmc.CardSection(
                        placeholder_text('Class Hierarchy'),
                        id=comp_id('cytoscape-container', 'cyto', 0),
                        style={
                            'height':r'calc(100% - 3em)',
                            'width':'100%',
                            'margin':'0',
                            'padding':'4px',
                        }
                    ),
                    
                    ],
                    radius=10,
                    shadow='sm',
                    style={
                        'border':f'1px solid {BORDER_COLOR}',
                        'height':'100%',
                        'width':'100%',
                        'margin':'0',
                        'padding':'0',
                        'background-color':PAPER_BCOLOR,
                    }
                ),
                ],
                width=12,
                style={
                    'height':'100%',
                    'margin':'0',
                    'padding':'0',
                }
            ),
        ],
        style={
            'height':'100%',
            'width':'100%',
            'margin':'0',
            'padding':'0',
            'background-color':PAPER_BCOLOR,
        }
    ),
    ],
    fluid=True,
    style={
        'height':'100%',
        'width':'100%',
        'margin':'0',
        'padding':'2px',
        'background-color':PAPER_BCOLOR,
    }
)