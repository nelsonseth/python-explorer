# get package lists for app drawer

from pathlib import Path

groups = ['standard', 'common', 'app']

def get_packages(groups: list) -> list:

    all_packages = []
    for group in ['standard', 'common', 'app']:
        if group == 'standard':
            # potential expansion to allow for other standard listings for other
            # python versions.... but just leaving it as 3.10 for now.
            version = '310'
            path = Path(__file__).parent.parent/'assets'/f'{group}_packs_{version}.txt'
        else:
            path = Path(__file__).parent.parent/'assets'/f'{group}_packs.txt'

        packs = open(path).read()
        packs_list = [(f'{group}', n) for n in packs.splitlines()]

        all_packages.extend(packs_list)

    return all_packages

all_packages = get_packages(groups)