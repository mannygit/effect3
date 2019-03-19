from effect import Constant, Effect
from effect.do import do


@do
def py3_generator_with_return():
    yield Effect(Constant(1))
    return 2
