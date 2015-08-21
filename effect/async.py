"""Generic asynchronous performers."""

from functools import partial
from itertools import count

from . import perform
from ._intents import FirstError


def perform_parallel_async(dispatcher, intent, box):
    """
    A performer for :obj:`ParallelEffects` which works if all child Effects are
    already asynchronous. Use this for things like Twisted, asyncio, etc.

    WARNING: If this is used when child Effects have blocking performers, it
    will run them in serial, not parallel.
    """
    effects = list(intent.effects)
    if not effects:
        box.succeed([])
        return
    num_results = count()
    results = [None] * len(effects)

    def succeed(index, result):
        results[index] = result
        if next(num_results) + 1 == len(effects):
            print "********* PARALLEL succeeding", box, result
            box.succeed(results)

    failed = []
    def fail(index, result):
        print "********* PARALLEL failing", box, result
        # if failed:
        #     return
        # else:
        #     failed.append(True)
        box.fail((FirstError,
                  FirstError(exc_info=result, index=index),
                  result[2]))

    for index, effect in enumerate(effects):
        perform(
            dispatcher,
            effect.on(
                success=partial(succeed, index),
                error=partial(fail, index)))
