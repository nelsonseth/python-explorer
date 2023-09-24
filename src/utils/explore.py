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

'''core functionality for Explore class'''

__all__ = [
    # classes
    'AttributeDict', 'Explore', 'ExploreFromStatus'
    
    # functions
    'isproperty', 'getmembers_categorized',
    
    # Helper functions
    '_getmember_counts', '_flat_members', '_sig_format', '_build_class_heritage'
]

__author__ = ('Seth M. Nelson <github.com/nelsonseth>')

# The bulk of the heavy lifting here is already covered by inspect.
import inspect
from warnings import warn
from typing import Union

#------------------------------------------------------------------------------

class AttributeDict(dict):
    '''Subclasses dict for some basic dot notation abilities.'''
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


# This method may not be completely fool proof... but it works for now.
def isproperty(obj) -> bool:
    '''Identify if an object is of the property type.'''
    return (hasattr(obj, 'getter') and 
            hasattr(obj, 'setter') and
            hasattr(obj, 'deleter'))


_IGNORE = [
    'False',
    'None',
    'True',
    'and',
    'as',
    'assert',
    'async',
    'await',
    'break',
    'class',
    'continue',
    'def',
    'del',
    'elif',
    'else',
    'except',
    'finally',
    'for',
    'from',
    'global',
    'if',
    'import',
    'in',
    'is',
    'lambda',
    'nonlocal',
    'not',
    'or',
    'pass',
    'raise',
    'return',
    'try',
    'while',
    'with',
    'yield',
]


def getmembers_categorized(obj) -> dict:
    '''Return categorized public members of a given object to a dictionary.
    
    Dictionary output containing five categories:
        - modules
        - classes
        - functions
        - properties
        - others (a catch-all bin)    
    '''
    # In the local function namespace, 'obj' will always eval to the 
    # desired object because we assigned it as such.
    objstr = 'obj'

    # Gather members from __all__ or inspection.
    # Ignoring and removing all dunders (__vars__ and _vars) for now. These 
    # do not serve a purpose in my current vision of this tool.
    # try:
    #     public_members_names = [m for m in obj.__all__ if not m.startswith('_')]
    # except AttributeError:
    public_members = [m for m in inspect.getmembers(obj) 
                    if not m[0].startswith('_')]
    public_members_names = [m[0] for m in public_members]

    modules = []
    classes = []
    functions = []
    properties = []
    others = []

    for name in public_members_names:
        
        # ignore any programmatical ref words (True, for, if, not,... etc.)
        # I don't know the actual name for these items, but they won't work as
        # a member object. 
        if name not in _IGNORE:
        
            # eval string built from obj.itemname
            itemstr = f'{objstr}.{name}'

            # identify imported modules if obj is module.
            if inspect.ismodule(eval(itemstr)):
                modules.append(name)

            # identify any included classes.
            elif inspect.isclass(eval(itemstr)):
                classes.append(name)

            # identify included functions.
            # The function inspect.isroutine() covers:
            #   - builtin function types
            #   - user function types
            #   - methods
            #   - method descriptors
            # NOTE: functions created by user-defined classes are not covered here.
            # (they just end up in others). Not sure how to deal with that yet.
            # Example: numpy's ufunc functions. TODO for later.
            elif inspect.isroutine(eval(itemstr)):
                functions.append(name)

            # identify any included properties
            elif isproperty(eval(itemstr)):
                properties.append(name)

            # bin anything else into 'others' for now.
            else:
                others.append(name)

    # Return dictionary of sorted name lists.  
    return AttributeDict(
            {
            'modules': sorted(modules),
            'classes': sorted(classes),
            'functions': sorted(functions),
            'properties': sorted(properties),
            'others': sorted(others)
        }
    )


def _getmember_counts(members: dict) -> dict:
    '''Internal helper method.
         
    Return counts of member categories and total count.
    '''
    counts = {}
    for k in members.keys():
        counts[f'{k}'] = len(members[f'{k}'])
        
    counts['total'] = sum(counts.values())
    
    return AttributeDict(counts)


def _flat_members(members: dict) -> list:
    '''Internal helper function.
    
    Return flattened list of member tuples... (key, member). 
    '''
    flat = []
    # for row in list(members.values()):
    #     flat.extend(row)
    # return flat
    for k in list(members.keys()):
        for v in members[k]:
            flat.append((k,v))
    return flat


def _sig_format(sig_str: str) -> str:
    '''
    Internal helper function.
    
    Formats string output from inspect.signature.__str__
    '''

    # this split by ',' also splits a parameter's listing of options, if there
    # are any, resulting in a weird output. TODO for later.
    sig_split = sig_str.split(',')
    
    if 'self' in sig_split[0]:
        if len(sig_split) > 1:
            sig_split.pop(0)
            sig_split[0] = ''.join(['(', sig_split[0][1:]])
        else:
            sig_split[0] = sig_split[0].replace('self:', '')

    # NOTE: two whitespaces required before \n for markdown to properly parse
    # new line.        
    sig_pretty = ''.join([s+',  \n' for s in sig_split])
    
    return sig_pretty[0:-2]


def _build_class_heritage(cls, nodes=None, heritage=None):
    '''Internal helper function. 
    
    Recursively builds inheritance tree for a given class.
    '''
    if nodes == None:
        nodes = set()
    if heritage == None: 
        heritage = dict()

    cn = cls.__name__
    bases = cls.__bases__

    if bases[0].__name__ == 'object':
        node_info = (cn, cls.__module__, 'base')
        if node_info not in nodes:
            nodes.add(node_info)
        return nodes, heritage
    else:

        node_info = (cn, cls.__module__, 'derived')
        nodes.add(node_info)

        keys = list(heritage.keys())

        for b in bases:
            bn = b.__name__
            if bn in keys:
                heritage[bn].add(cn)
            else:
                heritage[bn] = set([cn])
            
            # recursively step into each base heritage as well 
            nodes, heritage = _build_class_heritage(b, nodes, heritage)

    return nodes, heritage


#------------------------------------------------------------------------------


class Explore():
    
    '''Class for navigating members of a given object.
    
    Parameters
    ----------
    obj: object
        The object you want to explore. Typically a module or package.
    '''

    def __init__(self, obj) -> None:

        self._root = obj

        # internal history list of object reference strings
        self._refhistory = ['self._root']

        # internal history list of object simple names for display
        self._history = [obj.__name__]
    
        # internal join of history list 
        self._trace = self._history[0]

        # grab intial member set of inputed object.
        self._updatemembers()

            
    def _checkmember(self, member: str) -> bool:
        '''Internal helper method.
        
        Check if member string is in current member list.
        '''
        # create simple list of current member names only
        members = [m[1] for m in self._flatmembers]

        if member not in members:
            raise AttributeError(
                f"'{member}' is not a public member of '{self._trace}'"
            )
        else:
            return True


    def _updatemembers(self) -> int:
        '''Internal helper method.
        
        Update current member listing for target object exploration.
        '''
        # target object that is either current or newly added from stepin method.
        obj_str = self._refhistory[-1]
        
        # some objects fail to retrieve any members. This could be because the
        # code is faulty or the module is deprecated or other reasons.
        try:
            self._members = getmembers_categorized(eval(obj_str))
            self._membercounts = _getmember_counts(self._members)
            self._flatmembers = _flat_members(self._members)
        
            # if no new members, back out and return to previous parent.
            if len(self._flatmembers) == 0:
            
                # this is a simple warning for now. Need to figure out a better
                # way to send a message to dash interface. TODO
                warn(f'{self._trace} has no further members to explore.')
            
                # recursive return to previous
                self._updatehistory('out')
                self._updatemembers()

                return 1 # no members flag
        
            return 0 # no flag

        except AttributeError:
            # again, simple warning for now if member retrieval failed.
            # TODO figure out better message for dash interface
            warn(f"Member retrieval failed for '{self._trace}'")

            # recursive return to previous.
            self._updatehistory('out')
            self._updatemembers()

            return 2 # invalid member flag
           

    def _updatehistory(self, 
                       direction: str,
                       member: Union[str,None] = None,
                       levels_out: int = 1
                       ) -> None:
        '''Internal helper method.
        
        Update history lists for current target object exploration.
        '''

        # we are either stepping 'in' to or 'out' of an object
        if direction not in ['out', 'in']:
            raise ValueError(f"'direction' input is not 'out' or 'in'.")

        # stepping out
        if direction == 'out':
            # we are at 'root' and cannot step out
            if len(self._refhistory) == 1:
                pass
            else:
                # takes levels input (if any) and steps back that number of 
                # trace levels
                if len(self._refhistory) <= levels_out:
                    levels_out = len(self._refhistory) - 1

                # update history lists and trace
                self._refhistory = self._refhistory[0:-(levels_out)]
                self._history = self._history[0:-(levels_out)]
                self._trace = '.'.join(self._history)

        # stepping in
        elif direction == 'in':
            # requires a member to step into and that member must be valid
            if member and self._checkmember(member):
                # update history lists by appending member
                mem_str = f'{self._refhistory[-1]}.{member}'
                self._refhistory.append(mem_str)
                self._history.append(member)
                self._trace = '.'.join(self._history)
            
            
    def stepin(self, member: str) -> None:
        '''Step in to a member.
        
        Member string must be from current member listing.
        '''
        self._checkmember(member)

        self._updatehistory('in', member)

        return self._updatemembers()

    
    def stepout(self, levels: int = 1) -> None:
        '''Step out of current member into a parent object.
        
        Optional levels (int) input for stepping back multiple trace levels.
        '''
        if levels==0:
            pass
        else:
            self._updatehistory('out', levels_out=levels)
            self._updatemembers()

    
    def getdoc(self, member: Union[str,None] = None, printed: bool = False) -> None:
        '''Return docstring of current object or member of object.'''
        if member and self._checkmember(member):
            obj_str = f'{self._refhistory[-1]}.{member}'
        else:
            obj_str = self._refhistory[-1]

        if printed:
            return print(inspect.getdoc(eval(obj_str)))
        else:
            return inspect.getdoc(eval(obj_str))
    

    def getsignature(self, member: Union[str,None] = None, printed: bool = False) -> Union[str, None]:
        '''Return signature of current object or member of object.'''
        if member and self._checkmember(member):
            obj_str = f'{self._refhistory[-1]}.{member}'
        else:
            obj_str = self._refhistory[-1]

        try:
            sig = inspect.signature(eval(obj_str)).__str__()
        except:
             #return 'No signature available.'
             return None
        
        if printed:
            return print(_sig_format(sig))
        else:
            return _sig_format(sig)
        

    def gettype(self, member: Union[str,None] = None, printed: bool = False)-> Union[str, None]:
        '''Return type of current object or member of object.'''
        if member and self._checkmember(member):
            obj_str = f'{self._refhistory[-1]}.{member}'
        else:
            obj_str = self._refhistory[-1]

        try:
            member_type = type(eval(obj_str)).__name__
        except:
             return None
        
        if printed:
            return print(member_type)
        else:
            return member_type
        

    def get_class_heritage(self,
                           classes: Union[str, list[str], None] = None,
                           listify: bool = False,
                           ) -> dict:
        
        '''Return class heritage dictionary of current class members or sublist
        of current class members. Inputs limited to public classes.

        Parameters
        ----------
        classes: str or list[str] or None
            Class members string(s) within current exploration level. Default
            is None (meaning we want the heritage of all current classes).
        listify: bool, optional
            Convert heritage elements from sets to lists before returning. 
            Default is False.
        
        Returns
        ------
        class heritage: dict
            Dictionary representing class heritage. The format was geared towards
            use in the python-explorer app and inputs to the cytoscape library.

            * The dictionary has two main elements: 'nodes' and 'heritage'.
            * 'nodes' is a set of tuples. Each tuple contains 3 elements:
                - (0) class name
                - (1) class module
                - (2) 'base' or 'derived'.
                    * 'base' classes have only one base, namely 'object'.
                    * 'derived' classes inherit from at least one other class.
            * 'heritage' is a dictionary of sets:
                - key: a class parent in the heritage tree.
                - heritage[key] = set of classes that subclass 'key'
        '''

        if classes == None:
            cls_strs = self._members.classes
        else:
            if type(classes) == type(''):
                cls_strs = [classes]
            elif type(classes) == type([]):
                cls_strs = classes
            else:
                cls_strs = []

        if cls_strs == []:
            return AttributeDict(
                {
                'nodes':[],
                'heritage':{}
                }
            )
        
        for c in cls_strs:
            if c not in self._members.classes:
                raise AttributeError(
                    f"'{c}' is not a public class member of '{self._trace}'"
                )

        cls_objs = [eval(f'{self._refhistory[-1]}.{c}') for c in cls_strs]
        
        nodes = set()
        heritage = dict()

        for c in cls_objs:
            new_nodes, new_heritage = _build_class_heritage(c, nodes, heritage)
            
            nodes.update(new_nodes)

            new_keys = list(new_heritage.keys())
            old_keys = list(heritage.keys())
            for k in new_keys:
                if k in old_keys:
                    heritage[k].update(new_heritage[k])
                else:
                    heritage[k] = new_heritage[k]

        if listify:
            nodes = list(nodes)
            for k in list(heritage.keys()):
                heritage[k] = list(heritage[k])

        return AttributeDict(
            {
            'nodes': nodes,
            'heritage': heritage,
            }
        )
        
    # Public property calls for current members, membercounts, flatmembers, 
    # and trace. No setter is defined, thus these can only be written internally
    # via the class methods. 

    @property
    def members(self):
        '''Return member dictionary of current explored object.'''
        return self._members
    

    @property
    def membercounts(self):
        '''Return member counts of current explored object.'''
        return self._membercounts
    

    @property
    def flatmembers(self):
        '''Return flattened member list of current explored object.'''
        return self._flatmembers
    

    @property
    def trace(self):
        '''Return trace path of current explored object.'''
        return self._trace
    
    @property
    def status(self):
        '''Return dict of current status.
        
        Returns
        -------
        status: dict
            * Keys:
                * 'refhistory': list of internal reference call strings
                * 'history': list of the 'nice' names of the references
                * 'trace': a '.'join() of history elements
        
        '''
        return {
            'refhistory': self._refhistory,
            'history': self._history,
            'trace': self._trace
        }

    
class ExploreFromStatus(Explore):

    '''Entry point into Explore from existing Explore status info.'''

    def __init__(self, root, status: dict)-> None:
        
        '''Entry point into Explore from existing Explore status info.

        Parameters
        ----------
        root: obj
            The original parent obj of the current status. This is typically the
            module represented by status['history'][0]
        status: dict
            This is the dict created from Explore.status
        '''

        # because we are evaluating strings, it is better to evaluate root before
        # entering back into the class namespace... so that root is already a
        # valid object as an input.
        self._root = root

        self._refhistory = status['refhistory']

        self._history = status['history']

        self._trace = status['trace']

        self._updatemembers()


#------------------------------------------------------------------------------

if __name__ == '__main__':
    test = Explore(inspect)

    # test.getdoc(printed=True)
    
