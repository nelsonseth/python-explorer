# get package lists for app drawer

from pathlib import Path

from .envdata import (
    env_std_modules,
    env_std_wrong_os,
    env_site_packages,   
)

# groups = ['standard', 'common', 'app']
groups = ['standard', 'site']


# need to make an extended list for sklearn. Their init configuration does not 
# directly load the individual modules
sk_learn_modules = [
    "calibration",
    "cluster",
    "covariance",
    "cross_decomposition",
    "datasets",
    "decomposition",
    "dummy",
    "ensemble",
    "exceptions",
    "experimental",
    "externals",
    "feature_extraction",
    "feature_selection",
    "gaussian_process",
    "inspection",
    "isotonic",
    "kernel_approximation",
    "kernel_ridge",
    "linear_model",
    "manifold",
    "metrics",
    "mixture",
    "model_selection",
    "multiclass",
    "multioutput",
    "naive_bayes",
    "neighbors",
    "neural_network",
    "pipeline",
    "preprocessing",
    "random_projection",
    "semi_supervised",
    "svm",
    "tree",
    "discriminant_analysis",
    "impute",
    "compose"
]


# def get_packages(groups: list) -> list:

#     all_packages = []
#     for group in groups:
#         if group == 'standard':
#             # potential expansion to allow for other standard listings for other
#             # python versions.... but just leaving it as 3.10 for now.
#             version = '310'
#             path = Path(__file__).parent.parent/'assets'/f'{group}_packs_{version}.txt'
#         else:
#             path = Path(__file__).parent.parent/'assets'/f'{group}_packs.txt'

#         packs = open(path).read()
    
#         for n in packs.splitlines():
#             if n == 'sklearn':
#                 sk_learn_list = [(f'{group}', f'sklearn.{m}') for m in sk_learn_modules]
#                 all_packages.extend(sk_learn_list)
#             else:
#                 all_packages.append((f'{group}', n))
        
#     return all_packages

# all_packages = get_packages(groups)

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