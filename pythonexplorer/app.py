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

import os
import sys

from dash import (Dash, html, dcc,
                  callback, Input, Output, State,
                  MATCH, ALL, ctx, no_update)
from dash.exceptions import PreventUpdate

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Purify
from dash_extensions.enrich import DashProxy

from pypandoc import convert_text

from explore import Explore, AttributeDict

bi_data = open(rf'{sys.path[0]}\data\3_9.txt', 'rt').read()
bi_list = [('standards', n) for n in bi_data.splitlines()]


_PRELOADED_PACKAGES = [
    'numpy',
    'scipy',
    'matplotlib.pyplot',
    'seaborn',
    'pandas',
    'dash',
    'dash_extensions',
    'markdown',
    'pypandoc',
    'fluids',
    'importlib'
]

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
        'overflow':'auto'
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
        'overflow':'hidden'
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
        children = dmc.Text(text, color='dimmed', size='xl'),
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


def _publish_signature(sig: str) -> Purify:
    '''Return Purify component for signature string.'''
    sig_html = convert_text(sig,
                            format='md',
                            to='html5',
                            )
    return Purify(sig_html)


def _publish_docstring(doc: str) -> Purify:
    '''Return Purify component for docstring.'''
    doc_html = convert_text(doc,
                            format='rst',
                            to='html5',
                            extra_args=[
                                    '--webtex',
                                ],
                            )
    return Purify(doc_html)


_TITLE_ROW_CONTENT = dbc.Stack(
    children=[
        dmc.ActionIcon(
            children=DashIconify(
                icon='iconamoon:menu-burger-horizontal',
                width=40,
                color='blue',
            ),
            variant='light',
            id=_comp_id('menu-button', 'menu', 0),
            size='lg',
        ),
        dmc.Text(
            dmc.Text(
            'Python Explorer',
            style={
                'font-size':'1.5em',
                'font-weight':'700',
                'align':'center'
            },
        ),
        ),
        dmc.Button(
            'Explore More',
            id=_comp_id('explore-button', 'tabs', 0),
            color='green',
            **_button_kwargs
        )
    ],
    direction='horizontal',
    gap=2,
)

# _TITLE_SELECT_ROW = dbc.Row(
#     [
#         dbc.Col(
#             dmc.Button(
#                 id=_comp_id('menu-button', 'menu', 0),
#                 leftIcon=DashIconify(
#                     icon='iconamoon:menu-burger-horizontal',
#                     width=40,
#                     color='black',
#                 ),
#                 variant='white',
#             ),
#             width='auto',
#         ),
#         dbc.Col(
#             dmc.Text(
#                 'Python Explorer',
#                 style={
#                     'font-size':'1.5em',
#                     'font-weight':'700',
#                     'align':'center'
#                 },
#             ),
#             width='auto'
#         ),
#         dbc.Col(
#             dmc.Select(
#                 placeholder='Select package to explore.',
#                 id='package-select',
#                 value='initialize',
#                 dropdownPosition='bottom',
#                 data=bi_list,
#                 size='sm',
#             ),
#             width='auto',
#         ),
#         dbc.Col(
#             dmc.Button(
#                 'Explore More',
#                 id={'comptype':'e-button'},
#                 color='green',
#                 **_button_kwargs
#             ),
#             width='auto'
#         )
#     ],
#     justify='start',
#     align='start'
# )

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
                    _placeholder_text('Explorer Trace')
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
                    _placeholder_text('Explorer Trace')
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

_page_container_height = '98vh'
_page_container_width = '100vw'

_title_row_height = '8%'
_body_row_height = '92%'

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
                                        children=[
                                            _placeholder_text('Current Member'),
                                        ],
                                        id=_comp_id('current-member', 'tabs', 0),
                                        width=6,
                                        style={
                                            'height':'100%',
                                            'max-height':'100%',
                                            'overflow':'auto',
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

_LAYOUT_DRAWER = dmc.Drawer(
    children=[
        dmc.Paper(
            children=[
                _get_button_stack(
                    buttonlist=_get_p_buttons(
                        bi_list,
                        'green'
                    ),
                    group='standards',
                )
            ],
            #**_paper_kwargs_scroll,
            style={
                'height':'90vh',
                'max-height':'90vh',
                'width':'100%',
                'margin':'auto',
                'overflow':'auto',
            }
        )
    ],
    id=_comp_id('drawer', 'drawer', 0),
    closeOnClickOutside=True,
    closeOnEscape=True,
    size='30vw',
    style={
        'height':'95vh',
        'overflow':'hidden',
        'margin':'auto',
    }
)


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
        self.packagelist = bi_list
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
                
                pkgs = [p[1] for p in self.packagelist]
                module = pkgs[index]

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
            Output(_comp_id('current-member', 'tabs', 0), 'children'),
            Input(_comp_id('m-button', ALL, ALL), 'n_clicks'),
            State(_comp_id('t-data', 'trace', 0), 'data'),
            State(_comp_id('m-filtered-data', 'tabs', 0), 'data'),
            prevent_initial_call=True
        )
        def sig_doc_output(n1, t_data, m_data):           
            
            if len(m_data[1]) == 0:
                return (_placeholder_text('Member Signature'),
                        _placeholder_text('Member Docstring'),
                        _placeholder_text('Current Member'))
            
            
            if all(n==0 for n in n1):
                if self.clickstate in ['package', 'explore', 'trace']:
                    trace = t_data[0]

                    self.current = trace[-1]

                    return (_publish_signature(self.explore.getsignature()),
                            _publish_docstring(self.explore.getdoc()),
                            dmc.Text(self.explore.trace, align='center'))
                else:
                    return (no_update, no_update, no_update)
            
            try:
                trig_id = ctx.triggered_id.index
            except AttributeError:
                return (_placeholder_text('Member Signature'),
                        _placeholder_text('Member Docstring'),
                        _placeholder_text('Current Member'))
            
            names = [n[1] for n in m_data[1]]
            name = names[trig_id]

            self.current = name

            current_trace = '.'.join([self.explore.trace, name])

            self.clickstate = 'member'

            return (_publish_signature(self.explore.getsignature(name)),
                    _publish_docstring(self.explore.getdoc(name)),
                    dmc.Text(current_trace, align='center'))


# APP--------------------------------------------------------------------------

app = DashProxy(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
                   ],
    title='Python Explorer')       

appwrapper = AppWrap(app=app)

app.layout = appwrapper.layout

if __name__ == '__main__':
    app.run(debug=True)