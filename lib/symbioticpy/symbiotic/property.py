#!/usr/bin/python

from . exceptions import SymbioticException
from os.path import abspath, join

class Property:
    def __init__(self, prpfile = None):
        self._prpfile = prpfile
        # property as LTL formulae (if available)
        self._ltl = []

    def memsafety(self):
        """ Check for memory safety violations """
        return False

    def memcleanup(self):
        """ Check for memory leaks """
        return False

    def signedoverflow(self):
        """ Check for signed integer overflows """
        return False

    def assertions(self):
        """ Check for assertion violations """
        return False

    def undefinedness(self):
        """ Check for undefined behavior """
        return False

    def termination(self):
        """ Check termination """
        return False

    def ltl(self):
        """ Is the property described by a generic LTL formula(e)? """
        return False

    def errorcall(self):
        """ Check for error calls """
        return False

    def coverage(self):
        """ Generate tests for coverage """
        return False

    def getPrpFile(self):
        return self._prpfile

    def getLTL(self):
        return self._ltl


class PropertyMemSafety(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def memsafety(self):
        return True

class PropertyMemCleanup(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def memcleanup(self):
        return True


class PropertyNoOverflow(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def signedoverflow(self):
        return True


class PropertyDefBehavior(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def undefinedness(self):
        return True


class PropertyUnreachCall(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def assertions(self):
        return True


class PropertyTermination(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def termination(self):
        return True

class PropertyErrorCall(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def errorcall(self):
        return True

class PropertyCoverage(Property):
    def __init__(self, prpfile = None):
        Property.__init__(self, prpfile)

    def coverage(self):
        return True


supported_ltl_properties = {
    'CHECK( init(main()), LTL(G ! call(__VERIFIER_error())) )'         : 'REACHCALL',
    'CHECK( init(main()), LTL(G valid-free) )'                         : 'MEMSAFETY',
    'CHECK( init(main()), LTL(G valid-deref) )'                        : 'MEMSAFETY',
    'CHECK( init(main()), LTL(G valid-memtrack) )'                     : 'MEMSAFETY',
    'CHECK( init(main()), LTL(G valid-memcleanup) )'                   : 'MEMCLEANUP',
    'CHECK( init(main()), LTL(G ! overflow) )'                         : 'SIGNED-OVERFLOW',
    'CHECK( init(main()), LTL(G def-behavior) )'                       : 'UNDEF-BEHAVIOR',
    'CHECK( init(main()), LTL(F end) )'                                : 'TERMINATION',
    'COVER( init(main()), FQL(COVER EDGES(@DECISIONEDGE)) )'           : 'COVER-BRANCHES',
    'COVER( init(main()), FQL(COVER EDGES(@CONDITIONEDGE)) )'          : 'COVER-CONDITIONS',
    'COVER( init(main()), FQL(COVER EDGES(@BASICBLOCKENTRY)) )'        : 'COVER-STMTS',
    'COVER( init(main()), FQL(COVER EDGES(@CALL(__VERIFIER_error))) )' : 'COVER-ERROR',
}

supported_properties = {
    'valid-deref'                                              : 'MEMSAFETY',
    'valid-free'                                               : 'MEMSAFETY',
    'valid-memtrack'                                           : 'MEMSAFETY',
    'null-deref'                                               : 'NULL-DEREF',
    'undefined-behavior'                                       : 'UNDEF-BEHAVIOR',
    'undef-behavior'                                           : 'UNDEF-BEHAVIOR',
    'undefined'                                                : 'UNDEF-BEHAVIOR',
    'signed-overflow'                                          : 'SIGNED-OVERFLOW',
    'no-overflow'                                              : 'SIGNED-OVERFLOW',
    'memsafety'                                                : 'MEMSAFETY',
    'memcleanup'                                               : 'MEMCLEANUP',
    'termination'                                              : 'TERMINATION',
    'coverage'                                                 : 'COVER-STMTS',
    'cover-branches'                                           : 'COVER-BRANCHES',
    'cover-conditions'                                         : 'COVER-CONDITIONS',
    'cover-statements'                                         : 'COVER-STMTS',
    'cover-error'                                              : 'COVER-ERROR',
}

def _get_prp(prp):
    from os.path import expanduser, isfile
    # if property is given in file, read the file
    epath = abspath(expanduser(prp))
    if isfile(epath):
        prp_list = []
        f = open(epath, 'r')
        for line in f.readlines():
            line = line.strip()
            # ignore empty lines
            if line:
                prp_list.append(line)
        f.close()
        return (prp_list, epath)

    # it is not a file, so it is given as a string
    # FIXME: this does not work for properties given
    # as LTL (there are spaces)
    return (prp.split(), None)


def _map_property(prps):
    mapped_prps = []
    ltl_prps = []
    for prp in prps:
        prp_key = supported_properties.get(prp)
        if not prp_key:
            prp_key = supported_ltl_properties.get(prp)
            if prp_key:
                ltl_prps.append(prp)

        if prp_key:
            mapped_prps.append(prp_key)
        else:
            msg  = 'Unknown or unsupported property: {0}\n'.format(prp)
            msg += 'Supported properties are:\n'
            for k in supported_ltl_properties.keys():
                msg += '    {0}\n'.format(k)
            msg += "or use shortcuts:\n"
            for k in supported_properties.keys():
                msg += '    {0}\n'.format(k)
            msg += '\nBy default, we are looking just for assertion violations.\n'

            raise SymbioticException(msg)

    return (mapped_prps, ltl_prps)

def get_property(symbiotic_dir, prp):
    if prp is None:
        prop = PropertyUnreachCall()
        prop._prpfile = abspath(join(symbiotic_dir, 'properties/unreach-call.prp'))
        return prop

    prps, prpfile = _get_prp(prp)
    prps, ltl_prps = _map_property(prps)
    prop = None

    if 'REACHCALL' in prps:
        prop = PropertyUnreachCall(prpfile)
        if prpfile is None:
            # _get_prp will check that the file exists
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/unreach-call.prp')))
            assert prop._prpfile
    elif 'MEMSAFETY' in prps:
        prop = PropertyMemSafety(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/valid-memsafety.prp')))
            assert prop._prpfile

    elif 'MEMCLEANUP' in prps:
        prop = PropertyMemCleanup(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/valid-memcleanup.prp')))
            assert prop._prpfile

    elif 'UNDEF-BEHAVIOR' in prps:
        prop = PropertyDefBehavior(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/def-behavior.prp')))
            assert prop._prpfile

    elif 'SIGNED-OVERFLOW' in prps:
        prop = PropertyNoOverflow(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/no-overflow.prp')))
            assert prop._prpfile

    elif 'TERMINATION' in prps:
        prop = PropertyTermination(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/termination.prp')))
            assert prop._prpfile

    # we do not differentiate different coverage properties now
    elif 'COVER-BRANCHES' in prps:
        prop = PropertyCoverage(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/coverage-branches.prp')))
            assert prop._prpfile

    elif 'COVER-CONDITIONS' in prps:
        prop = PropertyCoverage(prpfile)
        if prpfile is None:
            prop._prpfile = abspath(join(symbiotic_dir, 'properties/coverage-conditions.prp'))
            assert prop._prpfile

    elif 'COVER-STMTS' in prps:
        prop = PropertyCoverage(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/coverage-statements.prp')))
            assert prop._prpfile

    elif 'COVER-ERROR' in prps:
        prop = PropertyErrorCall(prpfile)
        if prpfile is None:
            ltl_prps, prop._prpfile = _get_prp(abspath(join(symbiotic_dir, 'properties/coverage-error-call.prp')))
            assert prop._prpfile

    if prop:
        prop._ltl = ltl_prps
    return prop
