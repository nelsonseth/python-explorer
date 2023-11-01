from typing import Any

from dash import callback, Input, Output, State, ctx, no_update, ALL
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc

# local
from .explore import Explore, ExploreFromStatus
from .envdata import (
    env_std_modules,
    env_std_wrong_os,
    env_site_packages,
    all_packages,
)

# the nightmare that is figuring out relative imports
import sys
from pathlib import Path
sys.path.append(Path(__file__).parent.parent)

# layouts is two levels up
from layouts.layout_utils import (
    comp_id,
    placeholder_text,
    get_notification,
    get_member_buttons,
    get_button_stack,
    get_trace_buttons,
    get_trace_group,
    get_filtered_dict,
    get_tabs,
    publish_docstring,
    publish_signature,
    publish_member_info,
    publish_package_info,
)

from layouts.cyto_utils import get_cytoscape


class ImportedNamespace:
    '''This is an internally managed list of imported names and objects. 
    
    Similar function to globals() or locals() but I needed more control.
    '''

    def __init__(self):
        self.active = {}

    def import_(self, module: str):
        if module in self.active.keys():
            pass
        else:
            try:
                exec(f'import {module}')
                self.active[f'{module}'] = eval(f'{module}')
            except:
                raise ImportError(f'Failed to import {module}.')

    def get_module(self, module: str)-> Any:
        if module in self.active.keys():
            return self.active[f'{module}']
        else:
            self.import_(module)
            return self.active[f'{module}']

imports = ImportedNamespace()

def _getexplore(status):
    '''Retrieve Explore instance from status.'''
    root = imports.get_module(status['history'][0])
    loc_explore = ExploreFromStatus(root, status)
    
    return loc_explore


# display notification
@callback(
        Output(comp_id('notifier', 'app', 0), 'children'),
        Input(comp_id('notify-data', 'app', 0), 'data'),
        prevent_initial_call=True,
)
def error_notify(data):
    try:
        data[0]
    except:
        return no_update
    
    return get_notification(data[0], data[1])


@callback(
    Output(comp_id('p-accordion', 'packages', 0), 'value'),
    Input(comp_id('p-button', ALL, ALL), 'n_clicks'),
    prevent_initial_call=True,
)
def package_dropdown_close(n):
    return ''


# resets current explore space based on package click (in drawer), clicking
# on the 'explore more' button, or clicking on the trace navigation buttons
@callback(
        Output(comp_id('status', 'app', 0), 'data'),
        Output(comp_id('package-info', 'package', 0), 'children'),
        Output(comp_id('all-members', 'tabs', 0), 'data'),
        Output(comp_id('all-heritage', 'cyto', 0), 'data'),
        Output(comp_id('clickstate', 'app', 0), 'data', allow_duplicate=True),
        Output(comp_id('search-input', 'search', 0), 'value'),
        Output(comp_id('notify-data', 'app', 0), 'data', allow_duplicate=True),
        Input(comp_id('p-button', ALL, ALL), 'n_clicks'),
        Input(comp_id('explore-button', 'tabs', 0), 'n_clicks'),
        Input(comp_id('t-button', 'trace', ALL), 'n_clicks'),
        State(comp_id('packages', 'drawer', 0), 'data'),
        State(comp_id('status', 'app', 0), 'data'),
        State(comp_id('current-member-title', 'tabs', 0), 'children'),
        prevent_initial_call=True,
)
def update_explore(n1, n2, n3, packages, status, member):

    id = ctx.triggered_id.comptype

    if id == 'p-button':

        index = ctx.triggered_id.index
        mod = packages[index]
        
        try:
            try:
                mod_import = env_std_modules[mod]['import_name']
                doc_link = env_std_modules[mod]['homepage']
                version = ''
            except:
                mod_import = env_site_packages[mod]['import_name']
                doc_link = env_site_packages[mod]['homepage']
                version = env_site_packages[mod]['version']

            imports.import_(mod_import)

            lexp = Explore(imports.get_module(mod_import)) 

            lheritage = lexp.get_class_heritage(listify=True)

            package_info = publish_package_info(mod, version, doc_link)
        
        except:
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,          
                [
                    'Import Error.',
                    f'Not able to access {mod}.'
                ]
            )

        return (
            lexp.status,
            package_info,
            [lexp.flatmembers, lexp.members],
            [list(lheritage.nodes), lheritage.heritage],
            ['package'],
            '',
            no_update
        )
    
    elif id == 'explore-button':

        lexp = _getexplore(status)
        ok = lexp.stepin(member)

        if ok == True:
           lheritage = lexp.get_class_heritage(listify=True)
           return (
               lexp.status,
               no_update,
               [lexp.flatmembers, lexp.members],
               [lheritage.nodes, lheritage.heritage],
               ['explore'],
               '',
               no_update
            )

        elif ok == False:
            return(
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,
                no_update,          
                [
                    lexp._error.kind,
                    lexp._error.msg
                ]
            )

    elif id == 't-button':

        if all(n==0 for n in n3):
            return [no_update]*7

        index = ctx.triggered_id.index
        levels = len(status['history']) - index - 1

        lexp = _getexplore(status)
        lexp.stepout(levels)
        lheritage = lexp.get_class_heritage(listify=True)

        return (
            lexp.status,
            no_update,
            [lexp.flatmembers, lexp.members],
            [lheritage.nodes, lheritage.heritage],
            ['trace'],
            '',
            no_update
        )

# output filtered list of members based on search settings
@callback(
        Output(comp_id('filtered-members', 'tabs', 0), 'data'),
        Input(comp_id('all-members', 'tabs', 0), 'data'),
        Input(comp_id('search-input', 'search', 0), 'value'),
        Input(comp_id('search-radio', 'search', 0), 'value'),
        Input(comp_id('private-switch', 'tabs', 0), 'checked'),
        prevent_initial_call=True,
)
def update_members(all_mems, value, choice, privates):
    if len(all_mems) == 0:
        return all_mems
    
    if value == '':
        if privates:
            return all_mems
        else:
            filtered_flat = [m for m in all_mems[0] if not m[1].startswith('_')]
            filtered_dict = get_filtered_dict(filtered_flat)
            return [filtered_flat, filtered_dict]
    else:
        if privates:
            mems = all_mems[0]
        else:
            mems = [m for m in all_mems[0] if not m[1].startswith('_')]

        filtered_flat = []
        if choice == 'contains':
            for flat in mems:
                if value.lower() in flat[1].lower():
                    filtered_flat.append(flat)
        elif choice == 'startswith':
            for flat in mems:
                if flat[1].lower().startswith(value):
                    filtered_flat.append(flat)

        filtered_dict = get_filtered_dict(filtered_flat)

        return [filtered_flat, filtered_dict]


# create member tabs based on filtered data
@callback(
        Output(comp_id('m-tabs', 'tabs', 0), 'children'),
        Output(comp_id('m-tabs-group', 'tabs', 0), 'value'),
        Input(comp_id('filtered-members', 'tabs', 0), 'data'),
        State(comp_id('m-tabs-group', 'tabs', 0), 'value'),
        prevent_intial_call=True
)
def create_tabs(data, tab):
    try:
        return get_tabs(data[1]), tab
    except:
        return no_update, no_update


# return member tab content (list of member buttons) based on tab selection
@callback(
    Output(comp_id('m-tabs-content', 'tabs', 0), 'children'),
    Input(comp_id('m-tabs-group', 'tabs', 0), 'value'),
    State(comp_id('filtered-members', 'tabs', 0), 'data'),
    prevent_intial_call=True
)
def get_tab_content(activetab, data):
    try:
        buttons = get_member_buttons(data[0], activetab)
        return get_button_stack(
            buttonlist = buttons,
            group = activetab
        )
    except:
        return no_update
    

# create trace navigation buttons
@callback(
    Output(comp_id('t-breadcrumbs', 'trace', 0), 'children'),
    Input(comp_id('status', 'app', 0), 'data'),
    prevent_intial_call=True,
)
def show_navigation(status):
    try:
        return get_trace_group(
            get_trace_buttons(status['history'])
        )
    except:
        return no_update


# show member information (signature, docstring) when a member button is clicked
# NOTE: this is also triggered when the member buttons are recreated (every time
# a member tab is clicked or the explore space is recreated.) The 'clickstate'
# store is used to manage where the trigger cascade came from. When a member tab is clicked,
# we can look to see if all n_clicks are still 0 or not in order to proceed or not.
@callback(
    Output(comp_id('sig-info', 'tabs', 0), 'children'),
    Output(comp_id('doc-info', 'tabs', 0), 'children'),
    Output(comp_id('current-member-title', 'tabs', 0), 'children'),
    Output(comp_id('current-member-info', 'tabs', 0), 'children'),
    Output(comp_id('explore-button', 'tabs', 0), 'disabled'),
    Output(comp_id('clickstate', 'app', 0), 'data'),
    Output(comp_id('notify-data', 'app', 0), 'data'),
    Input(comp_id('m-button', ALL, ALL), 'n_clicks'),
    Input(comp_id('status', 'app', 0), 'data'),
    State(comp_id('clickstate', 'app', 0), 'data'),
    State(comp_id('filtered-members', 'tabs', 0), 'data'),
    prevent_initial_call=True
)
def show_member_info(n1, status, clicked, filt_mems):
    
    lexp = _getexplore(status)

    if clicked[0] in ['explore', 'trace', 'package']:

        member = status['history'][-1]
        ok, sig = lexp.getsignature()
        _, doc = lexp.getdoc()
        _, typ = lexp.gettype()
        trace = status['trace']
        disable = True
        clickstate = ['member']

    elif clicked[0] == 'member':

        if all(n==0 for n in n1):
            return [no_update]*7

        index = ctx.triggered_id.index
        member = filt_mems[0][index][1]
        ok, sig = lexp.getsignature(member)
        _, doc = lexp.getdoc(member)
        _, typ = lexp.gettype(member)
        trace = '.'.join([status['trace'], member])
        disable = False
        clickstate = ['member']

    format = 'rst'

    if ok:
        return (
            publish_signature(sig),
            publish_docstring(doc, format),
            member,
            publish_member_info(trace, typ),
            disable,
            clickstate,
            no_update,
        )
    else:
        return(
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            [lexp._error.kind, lexp._error.msg]
        )

# create cytoscape graph
@callback(
    Output(comp_id('cytoscape-container', 'cyto', 0), 'children'),
    Output(comp_id('current-class-space', 'cyto', 0), 'children'),
    Input(comp_id('all-heritage', 'cyto', 0), 'data'),
    State(comp_id('all-members', 'tabs', 0), 'data'),
    State(comp_id('status', 'app', 0), 'data'),
    prevent_initial_call=True,
)
def get_cytoscape_graph(heritage, members, status):
    
    current_classes = members[1]['classes']
    member = status['history'][-1]

    if len(current_classes) == 0:
        return (
            placeholder_text('No classes in current space.'),
            f'Class space for **{member}**.'
        )

    return (
        get_cytoscape(heritage, current_classes),
        f'Class space for **{member}**.'
    )


# layout selection for cytoscape
@callback(
        Output(comp_id('cytoscape', 'cyto', 0), 'layout'),
        Input(comp_id('dropdown-cyto-layout', 'cyto', 0), 'value'),
        prevent_initial_call=True,
    )
def update_cytoscape_layout(layout):
    return {'name': layout, 'animate':True}


# node hover event tracker to display cytoscape node origins
@callback(
    Output(comp_id('cyto-node-text', 'cyto', 0), 'children'),
    Input(comp_id('cytoscape', 'cyto', 0), 'mouseoverNodeData'),
    prevent_initial_call=True,
)
def getNodeInfo(nodedata):
    if not nodedata:
        return ''
    mod = nodedata['module']
    name = nodedata['label']
    return f'{mod}.**{name}**'


# show cytoscape legend
@callback(
    Output(comp_id('cyto-legend', 'cyto', 0), 'hidden'),
    Input(comp_id('cyto-legend-switch', 'cyto', 0), 'checked'),
    prevent_initial_call=True,
)
def show_legend(checked):
    return not checked