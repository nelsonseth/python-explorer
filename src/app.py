# Copyright (c) 2023 Seth M. Nelson

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path

from dash import (Dash, html, dcc,
                  callback, Input, Output, State,
                  ALL, ctx, no_update)

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Purify

from pypandoc import convert_text

from explore import Explore, AttributeDict


# Grab packages listing from text files----------------------------------------
_standards_path = Path(__file__).parent.parent/'static'/'standards_310.txt'
_commons_path = Path(__file__).parent.parent/'static'/'common_packs.txt'
_apppacks_path = Path(__file__).parent.parent/'static'/'app_packs.txt'

_standards = open(_standards_path).read()
_standards_list = [('standards', n) for n in _standards.splitlines()]

_commons = open(_commons_path).read()
_commons_list = [('commons', n) for n in _commons.splitlines()]

_app_packs = open(_apppacks_path).read()
_app_list = [('app_packs', n) for n in _app_packs.splitlines()]

_all_packages = []
_all_packages.extend(_standards_list)
_all_packages.extend(_commons_list)
_all_packages.extend(_app_list)


# Common component kwargs------------------------------------------------------

# common kwargs for dmc.Paper with scroll
_paper_kwargs_scroll = {
    'radius':'sm',
    'withBorder':True,
    'shadow':'lg',
    'p':'sm',
    'style':{
        'height':'100%',
        'max-height':'100%',
        'width':'100%',
        'overflow':'auto',
        'background-color':'#FFF8EA',
    }
}

# common kwargs for dmc.Paper with no scroll
_paper_kwargs_no_scroll = {
    'radius':'sm',
    'withBorder':True,
    'shadow':'lg',
    'p':'sm',
    'style':{
        'height':'100%',
        'max-height':'100%',
        'width':'100%',
        'overflow':'hidden',
        'background-color':'#FFF8EA',
    }
}

# common kwargs for dmc.Button components
_button_kwargs = {
    'n_clicks':0,
    'size':'sm',
    'compact':True,
    'variant':'subtle',
    'radius':'md',
}


# Helper Functions-------------------------------------------------------------

def _comp_id(comptype: str, group: str, index: int) -> dict:
    '''Return component id dict containing comptype, group, and index.'''
    # I found it easier to have every comp id be of the same form.
    return {
        'comptype':comptype,
        'group':group,
        'index':index,
    }


def _get_p_buttons(
    namelist: list,
    color: str
    ) -> list:
    '''Return list of buttons for packages.
    
    * namelist - flattened list of (group, package) tuples
    * color - color of buttons
    '''
    return [
        dmc.Button(
            children = n[1],
            id = _comp_id('p-button', n[0], namelist.index(n)),
            color=color,
            **_button_kwargs,
        ) for n in namelist
    ]


def _get_t_buttons(
    namelist: list,
    color: str,
    ) -> list:
    '''Return list of buttons for trace.
    
    * namelist - list of strings (from trace history)
    * color - color of button
    '''
    return [
        dmc.Button(
            children = n,
            id = _comp_id('t-button', 'trace', namelist.index(n)),
            color=color,
            **_button_kwargs,
        ) for n in namelist
    ]    


def _get_m_buttons(
    namelist: list,
    color: str
    ) -> list:
    '''Return list of buttons for members.
    
    * namelist - flattened list of (key, member) tuples
    * color - color of button
    '''
    return [
        dmc.Button(
            children = n[1],
            id = _comp_id('m-button', n[0], namelist.index(n)),
            color=color,
            **_button_kwargs,
        ) for n in namelist
    ]


def _get_button_stack(
    buttonlist: list,
    group: str,
    ) -> (dmc.Center | dmc.Stack):
    '''Return stack of buttons for respective layout content.
    
    * buttonlist - list of button components
    * group - str corresponding to button id.group
    '''
    buttonlist_group = [b for b in buttonlist if b.id['group'] == group]

    # if no members for a given tab, return placeholder text
    if len(buttonlist_group) == 0:
        return _placeholder_text(f'No resulting {group}.')
    else:
        return dmc.Stack(
            children = buttonlist_group,
            align='flex-start',
            justify='flex-start',
            spacing='xs',
        )


def _get_tabs(member_dict: dict) -> list:
    '''Return list of Tab components for current member stats.'''
    keys = list(member_dict.keys())
    tabs = []
    for key in keys:
        num = len(member_dict[key])
        tabs.append(dmc.Tab(
            children = f'{str.title(key)} ({num})',
            value = key,
            id = _comp_id(f'{key}-tab', 'tabs', keys.index(key))
        ))
    return tabs


def _placeholder_text(text: str) -> dmc.Center:
    '''Return simple centered text for blank layout areas.'''
    return dmc.Center(
        children = dmc.Text(text, color='#666666', size='xl'),
        style={
            'height':'100%',
            'width':'100%',
            'margin':'auto',
        },
    )


def _get_filtered_dict(filtered_flat: list) -> AttributeDict:
    '''Return dict of members from flattened list of filtered members.
    
    * filtered_flat - list of (key, member) tuples
    '''
    modules = []
    classes = []
    functions = []
    properties = []
    others = []

    for f in filtered_flat:
        if f[0] == 'modules':
            modules.append(f[1])
        elif f[0] == 'classes':
            classes.append(f[1])
        elif f[0] == 'functions':
            functions.append(f[1])
        elif f[0] == 'properties':
            properties.append(f[1])
        elif f[0] == 'others':
            others.append(f[1])

    return AttributeDict(
        {
            'modules': sorted(modules),
            'classes': sorted(classes),
            'functions': sorted(functions),
            'properties': sorted(properties),
            'others': sorted(others)
        }
    )


def _publish_signature(sig: (str | None)) -> (dmc.Center | Purify):
    '''Return Purify component for signature string.'''
    if sig == None:
        return _placeholder_text('No signature available.')
    else:
        sig_html = convert_text(sig,
                                format='md',
                                to='html5',
                                )
        return Purify(sig_html)


def _publish_docstring(doc: (str | None)) -> (dmc.Center | Purify):
    '''Return Purify component for docstring.'''
    if doc == None:
        return _placeholder_text('No docstring available.')
    else:
        doc_html = convert_text(doc,
                                format='rst',
                                to='html5',
                                extra_args=[
                                        '--webtex',
                                    ],
                                )
        return Purify(doc_html)


def _publish_member_info(tracepath: str,
                         mem_type: str,
                         ) -> html.Div:
    
    return html.Div(
        [
            dmc.Space(h=3),
            dmc.Text(f'Current Trace: {tracepath}', align='left', size='md'),
            dmc.Space(h=2),
            dmc.Text(f'Type: {mem_type}', align='left', size='md')
        ]
    )


# Layout definitions-----------------------------------------------------------

_EXPLORE_BUTTON = dmc.Button(
            'Explore More',
            id=_comp_id('explore-button', 'tabs', 0),
            color='green',
            disabled=True,
            **_button_kwargs
        )

_TITLE_ROW_CONTENT = dmc.Group(
    [
        dmc.Group(
            children=[
                dmc.ActionIcon(
                    children=DashIconify(
                        icon='iconamoon:menu-burger-horizontal',
                        width=40,
                        color='black',
                    ),
                    variant='light',
                    id=_comp_id('menu-button', 'menu', 0),
                    size='lg',
                    style={
                        'background-color':'#eaffed'
                    }
                ),
                dmc.Space(h=5),
                dmc.Text(
                    'Python Explorer',
                    style={
                        'font-size':'1.5em',
                        'font-weight':'700',
                        'align':'center'
                    },
                ),
            ],
            position='left',
        ),
        dmc.NavLink(
            icon=DashIconify(icon='devicon:github', width=40),
            href='https://github.com/nelsonseth/python-explorer',
            variant = 'subtle',
            style={
                'width':'50px',
                'background-color':'#eaffed'}
        )
    ],
    position='apart',
)



_MEMBER_TABS = dbc.Container(
    [
        dbc.Row([   
            dbc.Col(
                dmc.Tabs(
                    dmc.TabsList(
                        children=[],
                        id=_comp_id('m-tabs', 'tabs', 0),
                        grow=True,
                    ),
                    id=_comp_id('m-tabs-group', 'tabs', 0),
                    value='modules',
                    variant='default',
                    color='blue',
                    orientation='vertical',
                ),
                width='auto',
            ),
            dbc.Col(
                children=[
                    _placeholder_text('Explorer Members')
                ],
                id=_comp_id('m-tabs-content', 'tabs', 0),
                style={
                    'height':'100%',
                    'max-height':'100%',
                    'overflow':'auto'
                }
            ),
        ],
        style={
            'height':'100%',
            'width':'100%',
            'margin':'auto'
            },
        )
    ],
    style={
        'height':'100%'
    },
    fluid=True,
)

_MEMBER_HEADER = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                dmc.Breadcrumbs(
                children=[
                    _placeholder_text('Explorer Navigation')
                ],
                id=_comp_id('t-breadcrumbs','trace', 0),
                separator='.',
                ),
            ])
            ],
            align='center',
            style={
                'height':'50%',
                'width':'100%',
                'margin':'auto',
            }
        ),
        dbc.Row([
            dbc.Col([
                dmc.TextInput(
                    placeholder='Search Current Members',
                    type='text',
                    size='sm',
                    id=_comp_id('search-input', 'search', 0),
                )
                ],
                align='center'
            ),
            dbc.Col([
                dmc.RadioGroup([
                    dmc.Radio('Contains', value='contains'),
                    dmc.Radio('Starts with', value='startswith')
                    ],
                    value='startswith',
                    orientation='horizontal',
                    size='sm',
                    spacing='xs',
                    id=_comp_id('search-radio', 'search', 0),
                ),
                ],
                align='center',
            )
            ],
            style={
                'height':'50%',
                'width':'100%',
                'margin':'auto',
            }
        )
    ],
    fluid=True,
)

_MEMBER_HEADER2 = dbc.Container(
    [
        dbc.Stack([
            dbc.Row([
                dmc.Breadcrumbs(
                children=[
                    _placeholder_text('Explorer Navigation')
                ],
                id=_comp_id('t-breadcrumbs','trace', 0),
                separator='.',
                ),
                ]
            ),
            dbc.Row([
                dbc.Col([
                    dmc.TextInput(
                        placeholder='Search Current Members',
                        type='text',
                        size='sm',
                        id=_comp_id('search-input', 'search', 0),
                    )
                    ],
                    align='center'
                ),
                dbc.Col([
                    dmc.RadioGroup([
                        dmc.Radio('Contains', value='contains'),
                        dmc.Radio('Starts with', value='startswith')
                        ],
                        value='startswith',
                        orientation='horizontal',
                        size='sm',
                        spacing='xs',
                        id=_comp_id('search-radio', 'search', 0),
                    ),
                    ],
                    align='center',
                )
                ],
            )
            ],
            direction='vertical',
            gap=2,
        ),
    ],
    fluid=True,
)

_page_container_height = '100vh'
_page_container_width = '100vw'

_title_row_height = '8%'
_body_row_height = '90%'

_member_header_height = '12%'
_member_tabs_height = '85%'

_signature_row_height = '30%'
_docstring_row_height = '70%'

_LAYOUT_MAIN = dbc.Container(
    [
        # Menu / Title Row
        dbc.Row(
            children=_TITLE_ROW_CONTENT,
            style={
                'height':_title_row_height,
                'width':'100%',
                'margin':'auto',
            },
        ),
        # Body Row
        dbc.Row(
            [
                # Member tabs column 
                dbc.Col(
                    dmc.Paper(
                        children=[
                            dbc.Row(
                                _MEMBER_HEADER2,
                                style={
                                    'height':_member_header_height,
                                    'width':'100%',
                                    'margin':'auto'
                                },
                                align='start',
                                justify='start',
                            ),
                            dmc.Divider(
                                orientation='horizontal',
                                size='sm',
                                style={'width':'100%'}
                            ),
                            dmc.Space(h=3),
                            dbc.Row(
                                _MEMBER_TABS,
                                style={
                                    'height':_member_tabs_height,
                                    'width':'100%',
                                    'margin':'auto',
                                }
                            )
                        ],
                        **_paper_kwargs_no_scroll,
                    ),
                    width=4,
                    style={
                        'height':'100%',
                        'margin':'auto',
                    },
                ),
                # Member information column
                dbc.Col(
                    [
                        # signature / member info row
                        dbc.Row([
                            dmc.Paper([
                                dbc.Row([
                                    dbc.Col(
                                        dmc.Card(
                                            children=[
                                                dmc.CardSection(
                                                    dmc.Group(
                                                        children=[
                                                            dmc.Text('Current Member',
                                                                weight=700,
                                                                size='xl',
                                                                id=_comp_id('current-member-title', 'tabs', 0)
                                                            ),
                                                            _EXPLORE_BUTTON                                                                                                                            
                                                        ],
                                                        position='apart',                                                      
                                                    ),
                                                    withBorder=True,
                                                ),
                                                dmc.CardSection(
                                                    children=[
                                                        _placeholder_text('Current Member Info'),
                                                    ],
                                                    id=_comp_id('current-member-info', 'tabs', 0),
                                                )
                                            ],
                                            p='sm',
                                            style={
                                                'height':'100%',
                                                'max-height':'100%',
                                                'width':'100%', 
                                                'overflow':'auto',                                              
                                                'background-color':'#fff8ea',
                                            }
                                            
                                        ),           
                                        width=6,
                                        style={
                                            'height':'100%',
                                            'max-height':'100%',
                                            #'overflow':'auto',
                                            'border-right':'2px dashed gray'
                                        },
                                    ),
                                    dbc.Col(
                                        children=[
                                            _placeholder_text('Member Signature')
                                        ],
                                        id=_comp_id('sig-info', 'tabs', 0),
                                        width=6,
                                        style={
                                            'height':'100%',
                                            'max-height':'100%',
                                            'overflow':'auto'
                                        },
                                    )
                                    ],
                                    #class_name='g-0',
                                    style={
                                        'height':'100%',
                                        'width':'100%',
                                        'margin':'auto',
                                    },
                                )
                                ],
                                **_paper_kwargs_no_scroll
                            ),
                            ],                          
                            style={
                                'height':_signature_row_height,
                                'width':'100%',
                                'margin':'auto',
                            },
                        ),
                        # member docstring row
                        dbc.Row(                           
                            dmc.Paper(
                                children=[
                                    _placeholder_text('Member Docstring')
                                ],
                                id=_comp_id('doc-info', 'tabs', 0),
                                **_paper_kwargs_scroll,                           
                            ),
                            style={
                                'height':_docstring_row_height,
                                'width':'100%',
                                'margin':'auto',
                            },
                        ),
                    ],
                    width=8,
                    style={
                        'height':'100%',
                        'margin':'auto',
                    },
                ),
            ],
            class_name='g-0',
            style={
                'height':_body_row_height,
                'width':'100%',
                'margin':'auto',
            },
        )
    ],
    style={
        'height':_page_container_height,
        'width':_page_container_width,
        'margin':'auto',
        'background-color':'#eaffed'
    },
    fluid=True,
)

_LAYOUT_STORES = html.Div([
    dcc.Store(
        id=_comp_id('m-data', 'tabs', 0),
        storage_type='memory',
        data=[],
    ),
    dcc.Store(
        id=_comp_id('m-filtered-data', 'tabs', 0),
        storage_type='memory',
        data=[],
    ),
    dcc.Store(
        id=_comp_id('t-data', 'trace', 0),
        storage_type='memory',
        data=[],
    ),
    dcc.Store(
        id=_comp_id('notify-data', 'notify', 0),
        storage_type='memory',
        data=[]
    )
])

_package_buttons = _get_p_buttons(_all_packages, 'green')

_DRAWER_CONTENT = dmc.Accordion(
    children=[
        dmc.AccordionItem(
            [
                dmc.AccordionControl('Standard Modules (3.10)'),
                dmc.AccordionPanel(
                    dmc.Paper(
                        children=[
                            _get_button_stack(
                                _package_buttons,
                                group='standards',
                            )
                        ],
                        style={
                            'height':'60vh',
                            'max-height':'60vh',
                            'width':'100%',
                            'margin':'auto',
                            'overflow':'auto',
                        }
                    )
                )
            ],
            value='standards',   
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl('Common Libraries'),
                dmc.AccordionPanel(
                    dmc.Paper(
                        children=[
                            _get_button_stack(
                                _package_buttons,
                                group='commons',
                            )
                        ],
                        style={
                            'height':'60vh',
                            'max-height':'60vh',
                            'width':'100%',
                            'margin':'auto',
                            'overflow':'auto',
                        }
                    )
                )
            ],
            value='commons',
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl('This app is built with...'),
                dmc.AccordionPanel(
                    dmc.Paper(
                        children=[
                            _get_button_stack(
                                _package_buttons,
                                group='app_packs',
                            )
                        ],
                        style={
                            'height':'60vh',
                            'max-height':'60vh',
                            'width':'100%',
                            'margin':'auto',
                            'overflow':'auto',
                        }
                    )
                )
            ],
            value='app_packs',
        ),
    ],
)

_LAYOUT_DRAWER = dmc.Drawer(
    children=[
        _DRAWER_CONTENT
    ],
    id=_comp_id('drawer', 'drawer', 0),
    title='Choose an item to explore.',
    closeOnClickOutside=True,
    closeOnEscape=True,
    size='25vw',
    style={
        'height':'95vh',
        'overflow':'hidden',
        'margin':'auto',
    }
)


# App internal functionality (callback) definitions----------------------------

# Based on https://github.com/plotly/dash/issues/61 thread discussion on
# potential use of classes with dash.
class BaseAppWrap():
    def __init__(self, app=None):
        self.app = app

        if self.app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.app)

class AppWrap(BaseAppWrap):
    
    layout = dmc.NotificationsProvider(
        html.Div(
            [
                html.Div(id=_comp_id('notifier', 'notify', 0)),
                _LAYOUT_MAIN,
                _LAYOUT_DRAWER,
                _LAYOUT_STORES,
            ]
        ),
        position='top-right',
        autoClose=2000,
    )
    

    def __init__(self, app):
        super().__init__(app=app)

        self.explore = Explore
        self.m_buttons = []
        self.packages = [p[1] for p in _all_packages]
        self.current = ''
        self.clickstate = ''

    def callbacks(self, app):

        @app.callback(
                Output(_comp_id('notifier', 'notify', 0), 'children'),
                Input(_comp_id('notify-data', 'notify', 0), 'data'),
                prevent_initial_call=True,
        )
        def error_notify(data):
            try:
                data[0]
            except:
                return no_update
            
            return dmc.Notification(
                title=data[0],
                message=data[1],
                id='notifier',
                action='show'
            )
        
        
        @app.callback(
                Output(_comp_id('drawer', 'drawer', 0), 'opened'),
                Input(_comp_id('menu-button', 'menu', 0), 'n_clicks'),
                Input(_comp_id('p-button', ALL, ALL), 'n_clicks'),
                prevent_initial_call=True,
        )
        def drawer_control(open, n1):
            id = ctx.triggered_id.comptype

            if id == 'menu-button':
                return True
            elif id == 'p-button':
                return False


        @app.callback(
                Output(_comp_id('m-data', 'tabs', 0), 'data'),
                Output(_comp_id('t-data', 'trace', 0),'data'),
                Output(_comp_id('search-input', 'search', 0), 'value'),
                Output(_comp_id('notify-data', 'notify', 0), 'data'),
                Input(_comp_id('p-button', ALL, ALL), 'n_clicks'),
                Input(_comp_id('explore-button', 'tabs', 0), 'n_clicks'),
                Input(_comp_id('t-button', 'trace', ALL), 'n_clicks'),
                State(_comp_id('t-data', 'trace', 0), 'data'),
                prevent_intial_call=True
        )
        def set_current(pn, en, tn, trace):
            
            nada = (no_update, no_update, '', no_update)
            error = no_update
            
            try:
                comptype = ctx.triggered_id.comptype
                index = ctx.triggered_id.index
            except:
                return nada
           
            if comptype == 'p-button':
                
                module = self.packages[index]

                try:
                    exec(f'import {module}')
                    self.explore = Explore(eval(f'{module}'))
                    self.clickstate = 'package'
                except [ImportError, ModuleNotFoundError]:
                    return nada
                
            elif comptype == 'explore-button':
                self.clickstate = 'explore'
                flag = self.explore.stepin(self.current)
                if flag == 0:
                    pass
                elif flag == 1:
                    error = [
                        'Exploration Complete.',
                        f'No further members to explore in {self.current}'
                    ]
                    return (no_update, no_update, no_update, error)
                elif flag == 2:
                    error = [
                        'Exploration Error.',
                        f'{self.current} is not a valid member.'
                    ]
                    return (no_update, no_update, no_update, error)
            elif comptype == 't-button':

                self.clickstate = 'trace'

                if all(n==0 for n in tn):
                    return nada

                if index == (len(trace[0]) - 1):
                    return (no_update,
                        [self.explore._history],
                        '',
                        error)
                
                levels = len(trace[0]) - index - 1
                self.explore.stepout(levels)
                
            self.current = self.explore._history[-1]

            return ([self.explore.members, self.explore.flatmembers],
                    [self.explore._history],
                    '',
                    error)


        @app.callback(
                Output(_comp_id('m-filtered-data', 'tabs', 0), 'data'),
                Input(_comp_id('m-data', 'tabs', 0), 'data'),
                Input(_comp_id('search-input', 'search', 0), 'value'),
                Input(_comp_id('search-radio', 'search', 0), 'value'),
                prevent_initial_call=True
        )
        def set_filtered_data(data, value, choice):
        
            if value == '':
                return data
            else:
                filtered_flat = []
                if choice == 'contains':
                    for flat in data[1]:
                        if value.lower() in flat[1].lower():
                            filtered_flat.append(flat)
                elif choice == 'startswith':
                    for flat in data[1]:
                        if flat[1].lower().startswith(value):
                            filtered_flat.append(flat)

                filtered_dict = _get_filtered_dict(filtered_flat)

                return [filtered_dict, filtered_flat]


        @app.callback(
                Output(_comp_id('m-tabs', 'tabs', 0), 'children'),
                Output(_comp_id('m-tabs-group', 'tabs', 0), 'value'),
                Input(_comp_id('m-filtered-data', 'tabs', 0), 'data'),
                State(_comp_id('m-tabs-group', 'tabs', 0), 'value'),
                prevent_intial_call=True
        )
        def create_tabs(data, tab):
            try:
                members = data[0]
                flatmembers = data[1]
            except:
                return (no_update, no_update)

            self.m_buttons = _get_m_buttons(flatmembers, 'blue')

            return _get_tabs(members), tab
        

        @app.callback(
            Output(_comp_id('m-tabs-content', 'tabs', 0), 'children'),
            Input(_comp_id('m-tabs-group', 'tabs', 0), 'value'),
            State(_comp_id('m-filtered-data', 'tabs', 0), 'data'),
            prevent_intial_call=True
        )
        def get_tab_content(activetab, data):
            try:
                members = data[0]
            except:
                return no_update
            
            # keys = list(members.keys())
            # for key in keys:
            #     if activetab == key:
            return _get_button_stack(
                buttonlist = self.m_buttons,
                group = activetab
            )


        @app.callback(
            Output(_comp_id('t-breadcrumbs', 'trace', 0), 'children'),
            Input(_comp_id('t-data', 'trace', 0), 'data'),
        )
        def set_trace_buttons(data):
            return _get_t_buttons(data[0], 'red')


        @app.callback(
            Output(_comp_id('sig-info', 'tabs', 0), 'children'),
            Output(_comp_id('doc-info', 'tabs', 0), 'children'),
            Output(_comp_id('current-member-title', 'tabs', 0), 'children'),
            Output(_comp_id('current-member-info', 'tabs', 0), 'children'),
            Output(_comp_id('explore-button', 'tabs', 0), 'disabled'),
            Input(_comp_id('m-button', ALL, ALL), 'n_clicks'),
            State(_comp_id('t-data', 'trace', 0), 'data'),
            State(_comp_id('m-filtered-data', 'tabs', 0), 'data'),
            prevent_initial_call=True
        )
        def sig_doc_output(n1, t_data, m_data):           
            
            if len(m_data[1]) == 0:
                return (_placeholder_text('Member Signature'),
                        _placeholder_text('Member Docstring'),
                        'Member',
                        _placeholder_text('Current Member Info'),
                        True)
            
            
            if all(n==0 for n in n1):
                if self.clickstate in ['package', 'explore', 'trace']:
                    trace = t_data[0]

                    self.current = trace[-1]

                    return (_publish_signature(self.explore.getsignature()),
                            _publish_docstring(self.explore.getdoc()),
                            self.current,
                            _publish_member_info(self.explore.trace,
                                                 self.explore.gettype()),
                            True)
                else:
                    return (no_update, no_update, no_update, no_update, no_update)
            
            try:
                trig_id = ctx.triggered_id.index
            except AttributeError:
                return (_placeholder_text('Member Signature'),
                        _placeholder_text('Member Docstring'),
                        'Current Member',
                        _placeholder_text('Current Member Info'),
                        True)
            
            names = [n[1] for n in m_data[1]]
            name = names[trig_id]

            self.current = name

            current_trace = '.'.join([self.explore.trace, name])

            self.clickstate = 'member'

            return (_publish_signature(self.explore.getsignature(name)),
                    _publish_docstring(self.explore.getdoc(name)),
                    self.current,
                    _publish_member_info(current_trace,
                                        self.explore.gettype(name)),
                    False)


# APP--------------------------------------------------------------------------

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
                   ],
    title='Python Explorer')  

server = app.server     

appwrapper = AppWrap(app=app)

app.layout = appwrapper.layout

if __name__ == '__main__':
    app.run(debug=True)