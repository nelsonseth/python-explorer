
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

PAPER_BCOLOR = '#fbfbf0'
HEADER_COLOR = '#83fc95'
BORDER_COLOR = '#a7a7a7'

# common kwargs for dmc.Button components
# button_kwargs = {
#     'n_clicks':0,
#     'size':'sm',
#     'compact':True,
#     'variant':'subtle',
#     'radius':'md',
# }

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
    * color - color of buttons
    '''
    return [
        dmc.Button(
            children = n[1],
            id = comp_id('p-button', n[0], namelist.index(n)),
            color='green',
            n_clicks=0,
            size='sm',
            radius='md',
            compact=True,
            variant='subtle',
        ) for n in namelist
    ]


def get_trace_buttons(
    namelist: list,
    ) -> list:
    '''Return list of buttons for trace.
    
    * namelist - list of strings (from trace history)
    * color - color of button
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
    * color - color of button
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


def publish_docstring(doc: Union[str, None]) -> Union[dmc.Center, Purify]:
    '''Return Purify component for docstring.'''
    if doc == None:
        return placeholder_text('No docstring available.')
    else:
        doc_html = convert_text(doc,
                                format='rst',
                                to='html5',
                                extra_args=[
                                        '--webtex',
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