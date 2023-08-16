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


from dash import (Dash, html, dcc,
                  callback, Input, Output, State,
                  MATCH, ALL, ctx, no_update)

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash_extensions import Purify

from markdown import markdown
from pypandoc import convert_text

from explore import Explore, AttributeDict

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

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP,
                   ],
    title='Python Explorer')

_paper_kwargs_scroll = {
    'radius':'xs',
    'withBorder':True,
    'shadow':'lg',
    'p':'sm',
    'style':{
        'height':'100%',
        'max-height':'100%',
        'width':'100%',
        'overflow-y':'auto'
    }
}

_paper_kwargs_no_scroll = {
    'radius':'xs',
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

_button_kwargs = {
    'n_clicks':0,
    'size':'sm',
    'compact':True,
    'variant':'subtle',
    'radius':'md',
}

def _get_m_buttons(
    namelist: list,
    color: str
    ) -> list:
    
    buttons = [
        dmc.Button(
            children = f'{n[1]}',
            id = {'comptype': 'm-button',
                  'group':n[0],
                  'index':namelist.index(n)},
            color=color,
            **_button_kwargs,
        ) for n in namelist]
    
    return buttons

def _get_t_buttons(
    namelist: list,
    color: str,
    ) -> list:
    
    buttons = [
        dmc.Button(
            children = n,
            id = {'comptype': 't-button',
                  #'group':'trace',
                  'index':namelist.index(n)},
            color=color,
            **_button_kwargs,
        ) for n in namelist]
    
    return buttons

def _get_button_stack(
    buttonlist: list,
    group: str,
    stack_int: int,
    ) -> list:
    
    buttonlist_group = [b for b in buttonlist if b.id['group'] == group]

    if len(buttonlist_group) == 0:
        bs = _placeholder_text(f'No resulting {group}.')
    else:
        bs = dmc.Stack(
            buttonlist_group,
            id={
                'comptype':'m-button-stack',
                'group':group,
                'index':stack_int,
            },
            align='flex-start',
            justify='flex-start',
            spacing='xs',
        )

    return bs

def _get_tabs(member_dict: dict) -> list:
    
    keys = list(member_dict.keys())
    tabs = []
    for key in keys:
        num = len(member_dict[key])
        tabs.append(dmc.Tab(
            f'{str.title(key)} ({num})',
            value = key,
            id = {
                'comptype':'tab',
                'group':key,
                'index':keys.index(key),
            },
        ))

    return tabs

def _placeholder_text(text):
    child = dmc.Center([
        dmc.Text(
            text,
            color='dimmed',
            size='xl'
        )
        ],
        style={'height':'100%', 'width':'100%'}
    )

    return child

def _get_filtered_dict(flat):
    modules = []
    classes = []
    functions = []
    properties = []
    others = []

    for f in flat:
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

def _publish_sig(sig: str) -> Purify:
    sig_html = convert_text(sig,
                            format='md',
                            to='html5',
                            )
    return Purify(sig_html)

def _publish_doc(doc: str) -> Purify:
    doc_html = convert_text(doc,
                            format='rst',
                            to='html5',
                            extra_args=[
                                    '--webtex',
                                ],
                            )
    return Purify(doc_html)

_TITLE_SELECT_ROW = dbc.Row(
    [
        dbc.Col(
            dmc.Button(
                id='menu-burger',
                leftIcon=DashIconify(
                    icon='iconamoon:menu-burger-horizontal',
                    width=40,
                    color='black',
                ),
                variant='white',
            ),
            width='auto',
        ),
        dbc.Col(
            dmc.Text(
                'Python Explorer',
                style={
                    'font-size':'1.5em',
                    'font-weight':'700',
                    'align':'center'
                },
            ),
            width='auto'
        ),
        dbc.Col(
            dmc.Select(
                placeholder='Select package to explore.',
                id='package-select',
                value='initialize',
                dropdownPosition='bottom',
                data=_PRELOADED_PACKAGES,
                size='sm',
            ),
            width='auto',
        ),
        dbc.Col(
            dmc.Button(
                'Explore More',
                id='explore-more',
                color='green',
                **_button_kwargs
            ),
            width='auto'
        )
    ],
    justify='start',
    align='start'
)

_MEMBER_TABS_STRUCTURE = dbc.Row(
    [   
        dbc.Col(
            dmc.Tabs(
                [
                    dmc.TabsList(
                        children=[],
                        id='m-tabs',
                        grow=True,
                    ),
                ],
                id='m-tabs-group',
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
            id='m-tabs-content',
            style={
                'height':'100%',
                'max-height':'100%',
                'overflow':'auto'
            }
        ),
    ],
    style={'height':'84%',
            'width':'100%',
            'margin':'auto'},
)

_TRACE_BREADCRUMBS = dmc.Breadcrumbs(
    children=[
        _placeholder_text('Explorer Trace')
    ],
    id='trace-breadcrumbs',
    separator='.',
    #p='0.5em'
)

_SEARCH_ROW = dbc.Row([
    dbc.Col([
        dmc.TextInput(
            placeholder='Search Current Members',
            type='text',
            size='sm',
            id='search-input',
        )
        ],
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
            id='search-radio',
        ),
    ])
    ],
    style={
        'height':'50%'
    }
)

_MEMBER_HEADER = dbc.Container([
    dbc.Row(_TRACE_BREADCRUMBS, style={'height':'50%'}),
    _SEARCH_ROW,
    ],
    style={
        'height':'100%',
        'width':'100%',
        'margin':'auto',
    }
)

_LAYOUT_BASE = dbc.Container(
    [
        dbc.Row(
            #dbc.Col(
                dmc.Paper(
                    children=[_TITLE_SELECT_ROW],
                    **_paper_kwargs_scroll,
                ),
            #),
            style={
                'height':'8%',
                'width':'100%',
                'margin':'auto',
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    dmc.Paper(
                        children=[
                            dbc.Row(
                                _MEMBER_HEADER,
                                style={
                                    'height':'15%',
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
                            _MEMBER_TABS_STRUCTURE
                        ],
                        **_paper_kwargs_no_scroll,
                    ),
                    width=4,
                    style={
                        'height':'100%',
                        #'width':'30%',
                        'margin':'auto',
                    },
                ),
                dbc.Col(
                    [
                        dbc.Row([
                            dmc.Paper([
                                dbc.Row([
                                    dbc.Col(
                                        children=[
                                            _placeholder_text('Current Member'),
                                        ],
                                        id='current-member',
                                        width=6,
                                        style={
                                            'height':'100%',
                                            'max-height':'100%',
                                            'overflow':'auto'
                                        },
                                    ),
                                    dbc.Col(
                                        children=[
                                            _placeholder_text('Member Signature')
                                        ],
                                        id='sig-area',
                                        width=6,
                                        style={
                                            'height':'100%',
                                            'max-height':'100%',
                                            'overflow':'auto'
                                        },
                                    )
                                    ],
                                    class_name='g-0',
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
                                'height':'30%',
                                'width':'100%',
                                'margin':'auto',
                            },
                        ),
                        dbc.Row(                           
                            dmc.Paper(
                                children=[
                                    _placeholder_text('Member Docstring')
                                ],
                                id='doc-area',
                                **_paper_kwargs_scroll,                           
                            ),
                            style={
                                'height':'70%',
                                'width':'100%',
                                'margin':'auto',
                            },
                        ),
                    ],
                    width=8,
                    style={
                        'height':'100%',
                        #'width':'70%',
                        'margin':'auto',
                    },
                ),
            ],
            class_name='g-0',
            style={
                'height':'92%',
                'width':'100%',
                'margin':'auto',
            },
        )
    ],
    style={
        'height':'98vh',
        'width':'100vw',
        'margin':'auto',
    },
    fluid=True,
)

_LAYOUT_STORES = html.Div([
    dcc.Store(
        id='m-data',
        storage_type='memory',
        data=[],
    ),
    dcc.Store(
        id='m-filtered-data',
        storage_type='memory',
        data=[],
    ),
    dcc.Store(
        id='t-data',
        storage_type='memory',
        data=[],
    )
])

_LAYOUT_DRAWER = dmc.Drawer(
    children=[],
    id='menu-drawer',
    closeOnClickOutside=True,
    closeOnEscape=True,
    size='30vw'
)


# Based on https://github.com/plotly/dash/issues/61 thread discussion on
# potential use of classes with dash.
class BaseAppWrap():
    def __init__(self, app=None):
        self.app = app

        if self.app is not None and hasattr(self, 'callbacks'):
            self.callbacks(self.app)

class AppWrap(BaseAppWrap):
    
    layout = html.Div(
        [
            _LAYOUT_BASE,
            _LAYOUT_DRAWER,
            _LAYOUT_STORES,
        ]
    )

    def __init__(self, app):
        super().__init__(app=app)

        self.explore = Explore
        self.m_buttons = []
        self.current = ''

    def callbacks(self, app):

        @app.callback(
                Output('menu-drawer', 'opened'),
                Input('menu-burger', 'n_clicks'),
                prevent_initial_call=True,
        )
        def drawer_control(open):
            return True


        @app.callback(
                Output('m-data', 'data'),
                Output('t-data','data'),
                Output('search-input', 'value'),
                Input('package-select', 'value'),
                Input('explore-more', 'n_clicks'),
                Input({'comptype':'t-button', 'index':ALL}, 'n_clicks'),
                State('t-data', 'data'),
                prevent_intial_call=True
        )
        def set_current(module, n1, n2, trace):
            if module == None or module == 'initialize':
                return no_update
            
            id = ctx.triggered_id
           
            if id == 'package-select':
                try:
                    exec(f'import {module}')
                    self.explore = Explore(eval(f'{module}'))
                except [ImportError, ModuleNotFoundError]:
                    return no_update
                
            elif id == 'explore-more':
                self.explore.stepin(self.current)

            else:
                if id.index == (len(trace[0]) - 1):
                    return no_update
                
                levels = len(trace[0]) - id.index - 1
                self.explore.stepout(levels)
            
            self.current = self.explore._history[-1]

            return ([self.explore.members, self.explore.flatmembers],
                    [self.explore._history],
                    '')


        @app.callback(
                Output('m-filtered-data', 'data'),
                Input('m-data', 'data'),
                Input('search-input', 'value'),
                Input('search-radio', 'value'),
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
                Output('m-tabs', 'children'),
                Output('m-tabs-group', 'value'),
                Input('m-filtered-data', 'data'),
                State('m-tabs-group', 'value'),
                prevent_intial_call=True
        )
        def create_tabs(data, tab):
            try:
                members = data[0]
                flatmembers = data[1]
            except:
                return no_update

            self.m_buttons = _get_m_buttons(flatmembers, 'blue')

            return _get_tabs(members), tab
        

        @app.callback(
            Output('m-tabs-content', 'children'),
            Input('m-tabs-group', 'value'),
            State('m-filtered-data', 'data'),
            prevent_intial_call=True
        )
        def get_tab_content(activetab, data):
            try:
                members = data[0]
            except:
                return no_update
            
            keys = list(members.keys())
            for key in keys:
                if activetab == key:
                    return _get_button_stack(
                        self.m_buttons,
                        key,
                        keys.index(key)
                    )


        @app.callback(
            Output('trace-breadcrumbs', 'children'),
            Input('t-data', 'data'),
        )
        def set_trace_buttons(data):
            return _get_t_buttons(data[0], 'red')


        @app.callback(
            Output('sig-area', 'children'),
            Output('doc-area', 'children'),
            Output('current-member', 'children'),
            Input({'comptype':'m-button', 'group':ALL, 'index':ALL}, 'n_clicks'),
            Input({'comptype':'t-button', 'index':ALL}, 'n_clicks'),
            State('t-data', 'data'),
            State('m-filtered-data', 'data'),
            prevent_initial_call=True
        )
        def sig_doc_output(n1, n2, t_data, m_data):           
            
            try:
                button = ctx.triggered_id.comptype
            except:
                return no_update

            if button == 't-button':

                trace = t_data[0]

                self.current = trace[-1]

                return (_publish_sig(self.explore.getsignature()),
                        _publish_doc(self.explore.getdoc()),
                        [dmc.Text(self.explore.trace, align='center'),
                         dmc.Text(f'mb:{n1}   tb:{n2}'),
                         dmc.Text(str(ctx.triggered_id))]
                         )

            elif button == 'm-button': 

                if len(m_data[1]) == 0:
                    return (_placeholder_text('Member Signature'),
                            _placeholder_text('Member Docstring'),
                            _placeholder_text('Current Member'))
                
                if all(n==0 for n in n1):
                    return no_update

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

                return (_publish_sig(self.explore.getsignature(name)),
                        _publish_doc(self.explore.getdoc(name)),
                        [dmc.Text(current_trace, align='center'),
                         dmc.Text(f'mb:{n1}   tb:{n2}'),
                         dmc.Text(str(ctx.triggered_id))]
                         )
            

appwrapper = AppWrap(app=app)

app.layout = appwrapper.layout

if __name__ == '__main__':
    app.run(debug=True)