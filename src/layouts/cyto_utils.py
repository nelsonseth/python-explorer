
from typing import Union

from dash import dcc, html
import dash_cytoscape as cyto
cyto.load_extra_layouts()

# local
from .layout_utils import (
    comp_id,
    placeholder_text,
    PAPER_BCOLOR,
    BORDER_COLOR,
)

member_node_color = '#5dade2'
base_border_color = '#cb4335'
gen_node_color = '#58d68d'
edge_color = '#566573'

# legend items
legend_nodes = [
    ('base_0', 'Base class\nin namespace', 'base'),
    ('base_1', 'Base class\nin namespace', 'base'),
    ('base_2', 'Base class\noutside namespace', 'base'),
    ('child_0', 'Subclass\nin namespace', 'derived'),
    ('child_1', 'Subclass\noutside namespace', 'derived'),
    ('child_2', 'Subclass\nin namespace', 'derived'),
]

legend_members = [
    'base_0',
    'base_1',
    'child_0',
    'child_2',
]

legend_hierarchy = {
    'base_1': ['child_0'],
    'base_2':['child_1'],
    'child_1':['child_2'],
}

# stylesheet for the formatting of the cytoscape graph
my_stylesheet = [
    {
        'selector': 'edge',
        'style': {
            'curve-style': 'straight',
            'target-arrow-shape': 'triangle-backcurve',
            'target-arrow-color': edge_color,
            'line-color': edge_color,
            'width': '2px',
        }
    },
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)',
            'text-valign': 'center',
            'text-halign': 'center',
            'shape': 'round-rectangle',
            'padding': '5px',
            'background-color': gen_node_color,
            'background-opacity': '0.8',
            'border-color': edge_color,
            'border-width': '2px'
        }
    },
    {
        'selector': '.base',
        'style': {
            'border-width': '6px',
            'border-color': base_border_color,
            'border-opacity': '0.8',
        },
    },
    {
        'selector': '.member',
        'style': {
            'background-color': member_node_color,
        }
    }
]

# generate node definitions from class hierarchy
def _create_cy_nodes(
    node_tuples: Union[list, set],
    members: list,
    for_legend: bool = False,
    ) -> list:
    
    nodes = list(node_tuples)
    
    if nodes == []:
        return {}
    
    cy_nodes = []
    for n in nodes:
        if n[0] in members:
            cy_cls = f'{n[2]} member'
        else:
            cy_cls = f'{n[2]} found'

        if for_legend:
            cy_nodes.append(
                {
                    'data': {
                        'id':n[0],
                        'label':n[1],
                        'module':'legend',
                    },
                    'selectable': True,
                    'style':{
                        'width': '8.5em',
                        'height': '3em',
                        'text-wrap':'wrap',
                    },
                    'classes': cy_cls,
                }
            )
        else:
            cy_nodes.append(
                {
                    'data': {
                        'id':n[0],
                        'label':n[0],
                        'module':n[1],
                    },
                    'selectable': True,
                    'style':{
                        'width': f'{0.6*len(n[0].upper())}em',
                        'height': '2em',
                    },
                    'classes': cy_cls,
                }
            ) 
    
    return cy_nodes

# generate edge definitions from class hierarchy information
def _create_cy_edges(heritage_dict: dict)-> list:
    cy_edges = []
    for k in list(heritage_dict.keys()):
        for c in heritage_dict[k]:
            cy_edges.append(
                {
                    'data': {
                        'id': f'{k}-{c}',
                        'source': k,
                        'target': c,
                    }
                }
            )
    return cy_edges

# dropdown options
layout_options = {
    'dagre':'Dagre (top-down)',
    'euler':'Euler (clusters)',
    'cola':'Cola (cleaner clusters)',
    'spread':'Spread (fill the region)',
    'breadthfirst':'Breadthfirst (large tree structure)',
    'klay':'Klay (left-right)',
    'circle':"Circle (it's a circle, chaotic)",
    'grid':'Grid (grid layout, chaotic)',
}


def dropdown_options(options: list):
    return [{'label': opt[0], 'value': opt[1]} for opt in options]


cyto_layout_dropdown = dcc.Dropdown(
    id=comp_id('dropdown-cyto-layout', 'cyto', 0),
    options=layout_options,
    value='dagre',
    clearable=False,
    style={
        'width':'280px',
        'margin':'0 0 0 0'
    }
)

legend_cy_nodes = _create_cy_nodes(legend_nodes, legend_members, for_legend=True)
legend_cy_edges = _create_cy_edges(legend_hierarchy)


# called from callback to generate current cytoscape layout output
def get_cytoscape(heritage: list, classes: list)-> list:

    nodes = heritage[0]
    heritage_info = heritage[1]

    cy_nodes = _create_cy_nodes(nodes, classes)
    cy_edges = _create_cy_edges(heritage_info)

    return [
        cyto.Cytoscape(
            id=comp_id('cytoscape', 'cyto', 0),
            elements=cy_nodes + cy_edges,
            style={
                'width':'100%',
                'height':'100%',
                'background-color': PAPER_BCOLOR,
                'position':'relative',
            },
            stylesheet=my_stylesheet,
            layout={
                'name':'dagre',
                'animate':True,
            }
        ),
        dcc.Markdown(
            id=comp_id('cyto-node-text', 'cyto', 0),
            style={
                'height':'2em',
                'width':'80%',
                'overflow':'hidden',
                'position':'absolute',
                'left': '2em',
                'bottom': '1em',
            }
        ),
        html.Div([
            cyto.Cytoscape(
                elements=legend_cy_nodes + legend_cy_edges,
                style={
                    'width':'100%',
                    'height':'100%',
                    'background-color': PAPER_BCOLOR,
                    'position':'relative',
                },
                stylesheet=my_stylesheet,
                layout={
                    'name':'dagre',
                }
            ),
            html.Div(
                'LEGEND',
                style={
                    'position':'absolute',
                    'bottom':'1em',
                    'left':'1em',
                }
            )
            ],
            id=comp_id('cyto-legend', 'cyto', 0),
            hidden=True,
            style={
                'height':'50%',
                'width':'60%',
                'border':f'3px solid {BORDER_COLOR}',
                'position':'absolute',
                'left':'5%',
                'top':'10%',
            }
        )
    ]




