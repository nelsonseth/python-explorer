
from dash import dcc, html

# local
from .layout_utils import comp_id

# the nightmare that is figuring out relative imports
# import sys
# from pathlib import Path
# sys.path.append(Path(__file__).parent.parent)

# utils is two levels up
from python_explorer.utils.envdata import all_packages

packs = [p[1] for p in all_packages]

stores = html.Div(
    [  
        dcc.Store(
            id=comp_id('notify-data', 'app', 0),
            storage_type='memory',
            data=[]
        ),
        dcc.Store(
            id=comp_id('packages', 'accordion', 0),
            storage_type='memory',
            data=packs,
        ),
        dcc.Store(
            id=comp_id('status', 'app', 0),
            storage_type='memory',
            data={}
        ),
        dcc.Store(
            id=comp_id('clickstate', 'app', 0),
            storage_type='memory',
            data=[]
        ),
        dcc.Store(
            id=comp_id('all-members', 'tabs', 0),
            storage_type='memory',
            data=[],
        ),
        dcc.Store(
            id=comp_id('all-heritage', 'cyto', 0),
            storage_type='memory',
            data=[]
        ),
        dcc.Store(
            id=comp_id('filtered-members', 'tabs', 0),
            storage_type='memory',
            data=[],
        ),        
    ]
)
