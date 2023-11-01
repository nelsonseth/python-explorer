
from typing import Union

from dash import html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
from dash_extensions import Purify
from dash_iconify import DashIconify
from pypandoc import convert_text

# the nightmare that is figuring out relative imports
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent)

# utils is two levels up
from utils.explore import AttributeDict

# Common Settings--------------------------------------------------------------

PAPER_BCOLOR = '#f9f9f9'
BORDER_COLOR = '#a7a7a7'

HEADER_COLOR_LIGHT = '#bbd4e9'
HEADER_COLOR_DARK = '#3776AB'

ACCORDION_LIGHT = '#d6e5f2'
ACCORDION_DARK = '#bbd4e9'

# Helper Functions-------------------------------------------------------------

def comp_id(comptype: str, group: str, index: int) -> dict:
    '''Return component id dict containing comptype, group, and index.'''
    # I found it easier to have every comp id be of the same form.
    # That way, when using ctx.triggered_id, I know the structure of what is called
    # and can reference the keys consistantly.
    return {
        'comptype':comptype,
        'group':group,
        'index':index,
    }


def get_notification(
        title: str,
        note: str,
    )-> dmc.Notification:
    '''Return notification container'''
    
    return dmc.Notification(
        title=title,
        message=note,
        id='notifier',
        action='show',
        color='red',
        style={
            'background-color':'#FFF0F0'
        },
        icon=DashIconify(icon='oi:x')
    )
        

def get_package_buttons(
    namelist: list
    ) -> list:
    '''Return list of buttons for packages.
    
    * namelist - flattened list of (group, package) tuples
    '''
    return [
        dmc.Button(
            children = n[1],
            id = comp_id('p-button', n[0], namelist.index(n)),
            color='blue',
            n_clicks=0,
            size='sm',
            radius='md',
            compact=True,
            variant='subtle',
        ) for n in namelist
    ]


def get_package_button_stack(
    button_list: list,
    package_info: dict,
    group: str
    ) -> dmc.Stack:

    button_list_group = [b for b in button_list if b.id['group'] == group]

    stack_list=[]
    for bb in button_list_group:
        stack_list.append(
            dbc.Row([
                dbc.Col(
                    bb,
                    width=3,
                    align='center',
                    style={
                        'height':'100%',
                        'padding-left':'0.5em',
                        'border-right':f'1px solid {BORDER_COLOR}'
                    }
                ),
                dbc.Col(
                    dmc.Text(
                        f'{package_info[bb.children]["summary"]}',
                        italic=True,
                        truncate=True,
                    ),
                    width=8,
                    align='center',
                    style={
                        'height':'100%',
                        'padding-left':'1em'
                    }
                ),
                ],
                class_name='g-0',
                style={
                    'width':'100%',
                    'max-width':'100%',
                }
            )
        )

    return dmc.Stack(
        children = stack_list,
        align='flex-start',
        justify='flex-start',
        spacing='xs',
    )


def get_package_accordion(
    packages: list,
    std_package_info: dict,
    site_package_info: dict,
    )-> dmc.Accordion:

    button_list = get_package_buttons(packages)

    return dmc.Accordion([
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    'Standard Modules',
                    style={
                        'background-image':f'linear-gradient({ACCORDION_LIGHT} 20%, {ACCORDION_DARK} 80%)',
                        'border-top-left-radius':'5px',
                        'border-top-right-radius':'5px',
                    },
                
                ),
                dmc.AccordionPanel(
                    dmc.Paper(
                        children=get_package_button_stack(
                            button_list,
                            std_package_info,
                            group='standard',
                            ),
                        style={
                            'height':'100%',
                            'padding-top':'0.5em',
                            'padding-bottom':'0.5em',
                            'border':f'1px solid {BORDER_COLOR}',
                            'background-color':PAPER_BCOLOR,
                        }
                    ),
                    style={
                        'height':'70vh',
                        'max-height':'70vh',
                        'width':'60vw',
                        'min-width':'600px',
                        'margin':'auto',
                        'overflow':'auto',
                        'background-image':f'linear-gradient({ACCORDION_LIGHT} 20%, {ACCORDION_DARK} 80%)',
                        'border':f'1px solid {BORDER_COLOR}',
                        'border-bottom-right-radius':'6px',
                        'border-bottom-left-radius':'6px',
                        'border-top-right-radius':'6px',
                        #'zIndex':999,
                    },
                )
            ],
            value='standard', 
            style={
                #'height':'3em',
            }  
        ),
        dmc.AccordionItem(
            [
                dmc.AccordionControl(
                    'Site-Packages',
                    style={
                        'background-image':f'linear-gradient({ACCORDION_LIGHT} 20%, {ACCORDION_DARK} 80%)',
                        'border-bottom':f'1px solid {ACCORDION_DARK}'
                    },
                ),
                dmc.AccordionPanel(
                    dmc.Paper(
                        children=get_package_button_stack(
                            button_list,
                            site_package_info,
                            group='site',
                            ),
                        style={
                            'height':'100%',
                            'padding-top':'0.5em',
                            'padding-bottom':'0.5em',
                            'border':f'1px solid {BORDER_COLOR}',
                            'background-color':PAPER_BCOLOR,
                        }
                    ),
                    style={
                        'height':'70vh',
                        'max-height':'70vh',
                        'width':'60vw',
                        'min-width':'600px',
                        'margin':'auto',
                        'overflow':'auto',
                        'background-image':f'linear-gradient({ACCORDION_LIGHT} 20%, {ACCORDION_DARK} 80%)',
                        'border':f'1px solid {BORDER_COLOR}',
                        'border-bottom-right-radius':'6px',
                        'border-bottom-left-radius':'6px',
                        'border-top-right-radius':'6px',
                        #'zIndex':1000,
                    },
                )
            ],
            value='site',
            style={
                #'height':'3em',
                'border-bottom':f'1px solid {ACCORDION_DARK}'
            }   
        ),
        ],
        id=comp_id('p-accordion', 'packages', 0),
        #variant='filled',
        radius='md',
        style={
            #'width':'50%',
            #'border':f'1px solid {BORDER_COLOR}',
            #'background-color':PAPER_BCOLOR,
            #'background-image':f'linear-gradient(#bbd4e9 50%, #d6e5f2 50%)',
            'position':'relative',
            'zIndex':999,
        }
    )


def publish_package_info(
    mod: str,
    version: str,
    link: Union[str, None]
    )-> dmc.Stack:

    if link == None or link == 'UNKNOWN' or link == '':
        href = dmc.Text(
            'Not found.',
        )
    else:
        href = dmc.Anchor(
            link,
            href=link,
            color='blue',
            truncate=True,
            style={
                'font-size':'1em',
                'font-weight':'500',
            }
        )

    return dmc.Stack([
        dmc.Group([
            dmc.Text(
                mod,
                style={
                    'font-size':'1.5em',
                    'font-weight':'700'
                }
            ),
            dmc.Text(
                f'{version}',
                italic=True,
                style={
                    'font-size':'0.8em',
                    'font-weight':'550',
                }
            ),
            ],
            align='center',
            spacing=10,
            position='center',
        ),
        dmc.Group([
            dmc.Text(
                'Homepage: ',
                italic=True,
                truncate=True,
                style={
                    'font-size':'1em',
                    'font-weight':'550',
                },               
            ),
            href,
        ],
        align='center',
        position='left',
        noWrap=True,
        spacing=4,
    )
    ],
    spacing=6,
)


def get_trace_buttons(
    namelist: list,
    ) -> list:
    '''Return list of buttons for trace.
    
    * namelist - list of strings (from trace history)
    '''
    return [
        dmc.Button(
            children = n,
            id = comp_id('t-button', 'trace', namelist.index(n)),
            color='dark',
            n_clicks=0,
            size='sm',
            radius='md',
            compact=True,
            variant='light',
            style={
                'padding':'2px',
                'margin':'0',
            }
        ) for n in namelist
    ]    


def get_member_buttons(
    namelist: list,
    group: str,
    ) -> list:
    '''Return list of buttons for members.
    
    * namelist - flattened list of (key, member) tuples
    * group - active tab name
    '''
    return [
        dmc.Button(
            children = n[1],
            id = comp_id('m-button', n[0], namelist.index(n)),
            color='blue',
            n_clicks=0,
            size='sm',
            radius='md',
            compact=True,
            variant='subtle',
        ) for n in namelist if group == n[0]
    ]


def get_button_stack(
    buttonlist: list,
    group: Union[str, None] = None
    ) -> Union[dmc.Center, dmc.Stack]:
    '''Return stack of buttons for respective layout content.
    
    * buttonlist - list of button components
    * group - str corresponding to button id.group (optional if group already determined)
    '''
    if group == None:
        buttonlist_group = buttonlist
    else:
        buttonlist_group = [b for b in buttonlist if b.id['group'] == group]

    # if no members for a given tab, return placeholder text
    if len(buttonlist_group) == 0:
        return placeholder_text(f'No resulting {group}.')
    else:
        return dmc.Stack(
            children = buttonlist_group,
            align='flex-start',
            justify='flex-start',
            spacing='xs',
        )


def get_trace_group(tracebuttons: list)-> dmc.Group:
    tlist = [dmc.Text(
            'You are exploring:  ',
            italic=True,
            truncate=True,
            style={
                'font-size':'1em',
                'font-weight':'500',
            }
        ),
        tracebuttons[0]]
    
    if len(tracebuttons) == 1:
        pass
    else:
        for b in tracebuttons[1:]:
            tlist.extend([' . ', b])

    return dmc.Group(
        tlist,
        align='left',
        spacing='4px',
        noWrap=True,
        style={
            'max-width':'100%',
            'overflow-x':'auto',
        }
    )


def get_tabs(member_dict: dict) -> list:
    '''Return list of Tab components for current member stats.'''
    keys = list(member_dict.keys())
    tabs = []
    for key in keys:
        num = len(member_dict[key])
        tabs.append(dmc.Tab(
            children = f'{str.title(key)} ({num})',
            value = key,
            id = comp_id(f'{key}-tab', 'tabs', keys.index(key)),
            style={
                'height':'2em',
                'border-top':f'1px solid {BORDER_COLOR}',
                'border-left':f'1px solid {BORDER_COLOR}',
                'border-right':f'1px solid {BORDER_COLOR}',
                'border-top-left-radius':'6px',
                'border-top-right-radius':'6px',
                'margin':'0 2px 0 2px',
            },
        ))
    return tabs


def placeholder_text(text: str) -> dmc.Center:
    '''Return simple centered text for blank layout areas.'''
    return dmc.Center(
        children = dmc.Text(text, color='#5a5a5a', size='xl'),
        style={
            'height':'100%',
            'width':'100%',
            'margin':'auto',
        },
    )


def get_filtered_dict(filtered_flat: list) -> AttributeDict:
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


def publish_signature(sig: Union[str, None]) -> Union[dmc.Center, Purify]:
    '''Return Purify component for signature string.'''
    if sig == None:
        return placeholder_text('No signature available.')
    else:
        sig_html = convert_text(sig,
                                format='md',
                                to='html5',
                                )
        return Purify(sig_html)


def publish_docstring(doc: Union[str, None], format: Union[str, None]=None) -> Union[dmc.Center, Purify]:
    '''Return Purify component for docstring.'''
    if doc == None:
        return placeholder_text('No docstring available.')
    else:
        if format == None:
            format = 'rst'
        doc_html = convert_text(doc,
                                format=format,
                                to='html5',
                                extra_args=[
                                        '--webtex',
                                        '--wrap=preserve',
                                    ],
                                )
        return Purify(doc_html)


def publish_member_info(tracepath: str,
                         mem_type: str,
                         ) -> html.Div:
    '''Return member info Div for display.'''
    return html.Div(
        [
            dmc.Space(h=4),
            dmc.Text(f'Current Trace: {tracepath}', align='left', size='md'),
            dmc.Space(h=4),
            dmc.Text(f'Type: {mem_type}', align='left', size='md')
        ]
    )