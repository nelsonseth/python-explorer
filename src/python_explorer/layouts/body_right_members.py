
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

# local
from .layout_utils import (
        comp_id,
        placeholder_text,
        PAPER_BCOLOR,
        BORDER_COLOR,
)


explore_button = dmc.Button(
    'Explore More',
    id=comp_id('explore-button', 'tabs', 0),
    color='green',
    disabled=True,
    size='sm',
    variant='filled',
    compact=True,
    radius='md',
)

# body right member info is the contents of main body right column when the
# Member Info tab is selected. Contains and controls the member info, member
# signature, member docstring, and the explore more button
body_right_member_info = dbc.Container([
        dbc.Row([
            dbc.Col([
                dmc.Card([
                    dmc.CardSection(
                        dmc.Group([
                            dmc.Text(
                                'Current Member',
                                id=comp_id('current-member-title', 'tabs', 0),
                                weight=600,
                            ),
                            explore_button,
                            ],
                            position='apart',
                        ),
                        style={
                            'height':'2em',
                            'width':'100%',
                            'margin':'0',
                            'padding':'2px 6px 1px 6px',
                            'border-bottom':f'1px solid {BORDER_COLOR}'
                        }
                    ),
                    dmc.CardSection(
                        placeholder_text('Current Member Information'),
                        id=comp_id('current-member-info', 'tabs', 0),
                        style={
                            'height':r'calc(100% - 2em)',
                            'width':'100%',
                            'margin':'0',
                            'padding':'4px',
                            'overflow':'auto',
                        }
                    )
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
                width=6,
                style={
                    'height':'100%',
                    'margin':'0',
                    'padding':'0 2px 0 0',
                }
            ),
            dbc.Col([
                dmc.Card([
                    dmc.CardSection(
                        dmc.Text(
                            'Member Signature:',
                            italic=True,
                        ),
                        style={
                            'height':'2em',
                            'width':'100%',
                            'margin':'0',
                            'padding':'2px 1px 1px 6px',
                            'border-bottom':f'1px solid {BORDER_COLOR}'
                        }
                    ),
                    dmc.CardSection(
                        placeholder_text('Member Signature'),
                        id=comp_id('sig-info', 'tabs', 0),
                        style={
                            'height':r'calc(100% - 2em)',
                            'width':'100%',
                            'margin':'0',
                            'padding':'4px 6px 4px 6px',
                            'overflow':'auto',
                        }
                    )
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
                width=6,
                style={
                    'height':'100%',
                    'margin':'0',
                    'padding':'0 0 0 2px'
                }
            )
        ],
        style={
            'height':'30%',
            'width':'100%',
            'margin':'0',
            'padding':'0 0 2px 0',
            'background-color':PAPER_BCOLOR,
        }
    ),
    dbc.Row([
            dbc.Col([
                dmc.Card([
                    dmc.CardSection(
                        dmc.Text(
                            'Member Docstring:',
                            italic=True,
                        ),
                        style={
                            'height':'2em',
                            'width':'100%',
                            'margin':'0',
                            'padding':'2px 1px 1px 6px',
                            'border-bottom':f'1px solid {BORDER_COLOR}'
                        }
                    ),
                    dmc.CardSection(
                        placeholder_text('Member Docstring'),
                        id=comp_id('doc-info', 'tabs', 0),
                        style={
                            'height':r'calc(100% - 2em)',
                            'width':'100%',
                            'margin':'0',
                            'padding':'4px 6px 4px 6px',
                            'overflow':'auto',
                        }
                    )
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
            'height':'70%',
            'width':'100%',
            'margin':'0',
            'padding':'2px 0 0 0',
            'background-color':PAPER_BCOLOR,
        }
    )
    
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