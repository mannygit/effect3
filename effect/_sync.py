# -*- test-case-name: effect.test_sync -*-

"""
Tools for dealing with Effects synchronously.
"""

import six
import sys

from ._base import async_perform
from ._utils import wraps


class NotSynchronousError(Exception):
    """Performing an effect did not immediately return a value."""


def _perform(dispatcher, effect):
    successes = []
    errors = []
    effect = effect.on(success=successes.append, error=errors.append)
    async_perform(dispatcher, effect)
    if successes:
        return ("success", successes[0])
    elif errors:
        six.reraise(*errors[0])


def perform(dispatcher, effect):
    r = _perform(dispatcher, effect)
    if r is None:
        return None
    else:
        return r[1]


def sync_perform(dispatcher, effect):
    """
    Perform an effect, and return its ultimate result. If the final result is
    an error, the exception will be raised.

    This requires that the effect (and all effects returned from any of its
    callbacks) be synchronous. If the result is not available immediately,
    :class:`NotSynchronousError` will be raised.
    """
    result = _perform(dispatcher, effect)
    if result is None:
        raise NotSynchronousError("Performing %r was not synchronous!"
                                  % (effect,))
    else:
        return result[1]


def sync_performer(f):
    """
    A decorator for performers that return a value synchronously.

    This decorator should be used if performing the intent will be synchronous,
    i.e., it will block until the result is available and the result will be
    simply returned. This is the common case unless you're using an
    asynchronous framework like Twisted or asyncio.

    Note that in addition to returning (or raising) values as normal, you can
    also return another Effect, in which case that Effect will be immediately
    performed with the same dispatcher. This is useful if you're implementing
    one intent which is built on top of other effects, without having to
    explicitly perform them.

    The function being decorated is expected to take a dispatcher and an
    intent, and should return or raise normally. The wrapper function that this
    decorator returns will accept a dispatcher, an intent, and a box
    (conforming to the performer interface). The wrapper deals with putting the
    return value or exception into the box.

    Example::

        @sync_performer
        def perform_foo(dispatcher, foo):
            return do_side_effect(foo)
    """
    @wraps(f)
    def sync_wrapper(*args):
        box = args[-1]
        pass_args = args[:-1]
        try:
            box.succeed(f(*pass_args))
        except:
            box.fail(sys.exc_info())
    return sync_wrapper
