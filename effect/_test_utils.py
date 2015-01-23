"""Another sad little module."""

from testtools.matchers import MatchesException


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
                return Mismatch('%s has different arguments to %s.' % (
                        _error_repr(other[1]), _error_repr(self.expected)))
        elif self.value_re is not None:
            return self.value_re.match(other[1])
