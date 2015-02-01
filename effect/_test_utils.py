"""Another sad little utility module."""

import traceback

from characteristic import attributes

from testtools.matchers import Equals, MatchesException, Mismatch


class MatchesException(MatchesException):
    """
    Just like testtools.matchers.MatchesException, except using an isinstance
    check to see if the tuple is a tuple, instead of a ``type(x) is`` check.
    This is necessary for supporting :obj:`effect.ExcInfo`.
    """

    def match(self, other):
        if not isinstance(other, tuple):
            return Mismatch('%r is not an exc_info tuple' % other)
        expected_class = self.expected
        if self._is_instance:
            expected_class = expected_class.__class__
        if not issubclass(other[0], expected_class):
            return Mismatch('%r is not a %r' % (other[0], expected_class))
        if self._is_instance:
            if other[1].args != self.expected.args:
                return Mismatch('%r has different arguments to %r.' % (
                    other[1], self.expected))
        elif self.value_re is not None:
            return self.value_re.match(other[1])


@attributes(['expected_tb', 'got_tb'])
class ReraisedTracebackMismatch(object):
    def describe(self):
        return ("The reference traceback:\n"
                + ''.join(self.expected_tb)
                + "\nshould match the tail end of the received traceback:\n"
                + ''.join(self.got_tb)
                + "\nbut it doesn't.")


@attributes(['expected'], apply_with_init=False)
class MatchesReraisedExcInfo(object):

    def __init__(self, expected):
        self.expected = expected

    def match(self, actual):
        valcheck = Equals(self.expected[1]).match(actual[1])
        if valcheck is not None:
            return valcheck
        typecheck = Equals(self.expected[0]).match(actual[0])
        if typecheck is not None:
            return typecheck
        expected = traceback.format_exception(*self.expected)
        new = traceback.format_exception(*actual)
        tail_equals = lambda a, b: a == b[-len(a):]
        if not tail_equals(expected[1:], new[1:]):
            return ReraisedTracebackMismatch(expected_tb=expected,
                                             got_tb=new)
