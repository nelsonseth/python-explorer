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

from explore import Explore


_PRELOADED_PACKAGES = ['numpy', 'scipy', 'matplotlib', 'seaborn', 'pandas', 'dash']

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

def _get_button_list(
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

def _get_button_stack(
    buttonlist: list,
    group: str,
    stack_int: int,
    ) -> list:
    
    buttonlist_group = [b for b in buttonlist if b.id['group'] == group]

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

_TITLE_SELECT_ROW = dbc.Row(
    [
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
            children=[],
            id='m-tabs-content',
            style={
                'height':'100%',
                'max-height':'100%',
                'overflow':'auto'
            }
        ),
    ],
    style={'height':'89%',
            'width':'100%',
            'margin':'auto'},
)

_TRACE_BREADCRUMBS = dmc.Breadcrumbs(
    children=[
        dmc.Button('pandas', **_button_kwargs),
        dmc.Button('DataFrame', **_button_kwargs),
        dmc.Button('align', **_button_kwargs),
    ],
    separator='.',
    p='0.5em'
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
                                _TRACE_BREADCRUMBS,
                                style={
                                    'height':'10%',
                                    'width':'100%',
                                    'margin':'auto'
                                }
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
                        dbc.Row(
                            dmc.Paper(
                                children=[],
                                id='sig-area',
                                **_paper_kwargs_scroll,
                            ),                          
                            style={
                                'height':'30%',
                                'width':'100%',
                                'margin':'auto',
                            },
                        ),
                        dbc.Row(                           
                            dmc.Paper(
                                children=[],
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
        'height':'99vh',
        'width':'100vw',
        'margin':'auto',
    },
    fluid=True,
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
            dcc.Store(
                id='m-dict',
                storage_type='memory',
                data=[],
            )
        ]
    )

    def __init__(self, app):
        super().__init__(app=app)

        self.explore = Explore
        self.buttons = []


    def callbacks(self, app):

        @app.callback(
                Output('m-dict', 'data'),
                Input('package-select', 'value'),
                prevent_intial_call=True
        )
        def initial(module):
            if module == None or module == 'initialize':
                return no_update
            else:
                try:
                    exec(f'import {module}')
                    self.explore = Explore(eval(f'{module}'))
                    return [self.explore.members, self.explore.flatmembers]
                except [ImportError, ModuleNotFoundError]:
                    return no_update


        @app.callback(
                [Output('m-tabs', 'children'),
                 Output('m-tabs-group', 'value')],
                [Input('m-dict', 'data'),
                 State('m-tabs-group', 'value')],
                 prevent_intial_call=True
        )
        def create_tabs(data, tab):
            members = data[0]
            flatmembers = data[1]

            self.buttons = _get_button_list(flatmembers, 'blue')

            return _get_tabs(members), tab
        

        @app.callback(
            Output('m-tabs-content', 'children'),
            Input('m-tabs-group', 'value'),
            State('m-dict', 'data'),
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
                        self.buttons,
                        key,
                        keys.index(key)
                    )


        @app.callback(
            Output('sig-area', 'children'),
            Output('doc-area', 'children'),
            Input({'comptype':'m-button', 'group':ALL, 'index':ALL}, 'n_clicks'),
            State('m-dict', 'data'),
            prevent_initial_call=True
        )
        def member_button_click(n, data):
            try:
                trig_id = ctx.triggered_id.index
            except AttributeError:
                return no_update
            
            names = [n[1] for n in data[1]]
            name = names[trig_id]

            return rf'{self.explore.getsignature(name)}', fr'{self.explore.getdoc(name)}'


appwrapper = AppWrap(app=app)

app.layout = appwrapper.layout

if __name__ == '__main__':
    app.run(debug=True)

