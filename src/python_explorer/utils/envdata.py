
__all__ = [
    'env_std_modules',
    'env_std_wrong_os',
    'env_site_packages',
    'all_packages',
    'get_site_packages',
    'packages_distributions_reverse',
    'PYVERSION',
]

import sys
import re
from typing import Union, Any
from importlib.metadata import Distribution, packages_distributions

# Standard Modules-------------------------------------------------------------

_std_modules_exclude = [
    # extra
    'antigravity',
    'this',
    # deprecated
    'asynchat', 
    'asyncore',
    'imp',
    'binhex',
    'smtpd',
]

_std_unavailable = []
_std_valid = []

for m in sys.stdlib_module_names:
    if m not in _std_modules_exclude and not m.startswith('_'):
        try:
            exec(f'import {m}')
            _std_valid.append(m)
        except:
            _std_unavailable.append(m)


PYVERSION = f'{sys.version_info.major}.{sys.version_info.minor}'


def _get_std_modules(valid_list: list)-> dict:
    pkgs = {}
    for m in valid_list:
        try:
            summary = eval(f'{m}.__doc__.splitlines()[0]')
        except:
            summary = ''
        
        pkgs[m] = {
            'import_name':m,
            'summary':summary,
            'homepage':f'https://docs.python.org/{PYVERSION}/library/{m}.html#module-{m}'
        }
    
    return pkgs

env_std_modules = _get_std_modules(_std_valid)
env_std_wrong_os = _std_unavailable


# Site-Packages----------------------------------------------------------------

# List started from pip code. I added in other problematic pkgs as well.
_pkgs_exclude = {
    'python', # from pip exclusion
    'wsgiref', # from pip exclusion
    'argparse', # cli functions, from pip exclusion but this will be included in std_module list
    'pip',  # cli only
    'wheel', # cli only
    'pywin32', # complicated imports
    'conda', # conda things
    'conda-content-trust',
    'conda-package-handling',
    'conda-package-streaming',
    'argon2-cffi-bindings', # this one is weird. TODO: look into more.
    'wincertstore', # deprecated
    'docutils', # cli 
    'fonttools', # this is a package of libraries, some are cli
}


# this wasn't publically available within Distribution() methods. Not sure why.
def _normalize_name(name):
    """
    PEP 503 normalization plus dashes as underscores.
    """
    return re.sub(r"[-_.]+", "-", name).lower().replace('-', '_')


def _parse_content_type(ct):
    '''If metadata tag for Description-Content-Type is entered, use it to 
    determine best conversion for display'''
    if ct == None: # if none, rst should do okay with most things
        return 'rst'
    elif 'text/markdown' in ct: # if markdown, do markdown
        return 'md'
    else:
        return 'rst' # if plain or x-rst, do rst


def packages_distributions_reverse(removeprivate: bool=True)-> dict:
    '''Reverse the keys and values of importlib's packages_distributions() result.
    
    Ignore top levels with prefix of '_' by default. Can set removeprivate=False to add them back in.
    '''
    
    in_dict = packages_distributions()
    
    if removeprivate:
        in_keys = [ik for ik in in_dict.keys() if not ik.startswith('_')]
    else:
        in_keys = list(in_dict.keys())
    
    out_keys = set()
    [out_keys.add(val) for row in in_dict.values() for val in row]
    
    out_dict = {ok:[] for ok in list(out_keys)}
    
    for ik in in_keys:
        for ok in out_keys:
            if ok in in_dict[ik]:
                out_dict[ok].append(ik)
    
    return out_dict


def _get_import_name(dist: Distribution, pkg_tops: dict)-> Union[str, None]:
    '''Attempt to get the best import name for the package. Why there isn't a 
    standard logic between package names and import names is beyond me.'''
    
    normal_name = _normalize_name(dist.name)
    
    if dist.name in pkg_tops.keys():
        names = pkg_tops[dist.name]
        if len(names) == 1:
            return names.pop() # return top level found by package_distributions()
        elif normal_name in names: # multiple top levels...
            return normal_name # hopefully one makes sense
            # if not normal name, then the logic of what the names is seems to be random.
            # You have to go to the docs and hope there is an example snippet of code
            # with an import statement.
    
    else:   
        # attempt look at top files to find name that makes sense
        files = dist.files
        if files == None:
            # if no files exist... 
            return None
        else:
            names = set()
            possible = [f.parts for f in files]
            for p in possible:
                if len(p) == 1: # single file, possibly .py file
                    fname = p[0].removesuffix('.py')
                    if fname == normal_name: 
                        names.add(fname) # package is just a single file.. maybe?
                elif any(s in p[0] for s in ['dist-info', 'egg-info', '__pycache__']):
                    pass # ignore package info folders and __pycache__
                elif any(p[0].startswith(s) for s in [' ', '_', '.']):
                    pass # ignore relatives and other oddities
                else:
                    names.add(p[0]) # add findings
        if len(names) == 1:
            return names.pop() # one result
        elif normal_name in names: # an ounce of remaining hope if more than one result
                return normal_name
        else:
            return None # bail
            

def _find_website(metadata):
    
    try:
        url_list = [w.split(',') for w in metadata.get_all('Project-URL')]
            
        if url_list:
            for w in url_list:
                if 'doc' in w[0].lower():
                    return w[1].strip()
            for w in url_list:
                if 'home' in w[0].lower():
                    return w[1].strip()
    except:
        url_home = metadata['Home-Page']

        if url_home:
            return url_home.strip()
        else:
            return ''


def get_site_packages()-> dict:
    pkgs = {}
    pkg_tops = packages_distributions_reverse()

    for dist in Distribution.discover():
        if dist.name in _pkgs_exclude:
            pass
        else:
            meta = dist.metadata

        
            pkgs[meta['Name']] = {
                'import_name':_get_import_name(dist, pkg_tops),
                'version':meta['Version'], # required, so always returns
                'summary':meta['Summary'], # returns none if no entry
                'homepage':_find_website(meta),
                'description_content_type':_parse_content_type(meta['Description-Content-Type']),
                'description':meta['Description'],
            }
    return pkgs

env_site_packages = get_site_packages()


def get_packages(standards: dict, site: dict):
    
    all_packages = []
    
    stds = list(standards.keys())
    sites = list(site.keys())

    stds.sort(key=str.lower)
    sites.sort(key=str.lower)

    for p in stds:
        all_packages.append(('standard', p))
    for p in sites:
        all_packages.append(('site', p))

    return all_packages

all_packages = get_packages(env_std_modules, env_site_packages)