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
    'AttributeDict', 'Explore',
    
    # functions
    'isproperty', 'getdocstring', 'getmembers_categorized',
    
    # Helper functions
    '_getmember_counts', '_flat_members', '_sig_format'
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


# Again, inspect is doing the heavy lifting here. Just wanted to still return 
# a string if no doc found.
def getdocstring(obj) -> str:
    '''Return object docstring, if possible.'''
    doc = inspect.getdoc(obj)
    nodoc = 'No docstring available.'
    if not doc:
        return nodoc
    else:
        return doc


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
        

#------------------------------------------------------------------------------


class Explore():
    
    '''Class space controlling options for navigating a given object.'''

    def __init__(self, obj) -> None:

        # Within the local class namespace, 'self._root' will always point 
        # to the inputed object reference in the global namespace. 
        self._root = obj
        
        # internal history list of object reference strings
        self._refhistory = ['self._root']

        # internal history list of object simple names for display
        self._history = [self._getname('self._root')]
    
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
                f"'{member}' is not a member of '{self._trace}'"
            )
        else:
            return True


    def _getname(self, obj_str: str) -> str:
        '''Internal helper method. 
        
        Return simple name of root object. If none, return 'root'.
        '''
        try:
            return eval(f'{obj_str}.__name__')
        except AttributeError:
            return 'root'
        

    def _updatemembers(self) -> None:
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
        
        except AttributeError:
            # again, simple warning for now if member retrieval failed.
            # TODO figure out better message for dash interface
            warn(f"Member retrieval failed for '{self._trace}'")

            # recursive return to previous.
            self._updatehistory('out')
            self._updatemembers()
           

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

        self._updatemembers()

    
    def stepout(self, levels: int = 1) -> None:
        '''Step out of current member into a parent object.
        
        Optional levels (int) input for stepping back multiple trace levels.
        '''

        self._updatehistory('out', levels_out=levels)

        self._updatemembers()

    
    def getdoc(self, member: Union[str,None] = None, printed: bool = False) -> None:
        '''Return docstring of current object or member of object.'''
        if member and self._checkmember(member):
            obj_str = f'{self._refhistory[-1]}.{member}'
        else:
            obj_str = self._refhistory[-1]

        if printed:
            return print(getdocstring(eval(obj_str)))
        else:
            return getdocstring(eval(obj_str))
    

    def getsignature(self, member: Union[str,None] = None, printed: bool = False) -> None:
        '''Return signature of current object or member of object.'''
        if member and self._checkmember(member):
            obj_str = f'{self._refhistory[-1]}.{member}'
        else:
            obj_str = self._refhistory[-1]

        try:
            sig = inspect.signature(eval(obj_str)).__str__()
        except:
             return 'Signature not available.'
        
        if printed:
            return print(_sig_format(sig))
        else:
            return _sig_format(sig)
        
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
    

#------------------------------------------------------------------------------


if __name__ == '__main__':
    test = Explore(inspect)

    test.getdoc(printed=True)
    print(test.membercounts)
