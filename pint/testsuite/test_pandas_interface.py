# -*- coding: utf-8 -*-

# - pandas test resources https://github.com/pandas-dev/pandas/blob/master/pandas/tests/extension/base/__init__.py

import sys

import pint
import pytest
try:
    import pandas as pd
    from pandas.compat import PY3
    from pandas.tests.extension import base

    import numpy as np
    import pint.pandas_interface as ppi
except ImportError:
    pass

required_libs = [
    'pandas',
    'numpy',
]
required_libs_str = ", ".join(required_libs)
all_required_libs = all(
    x in sys.modules
    for x in required_libs
)

check_required = pytest.mark.skipif(not all_required_libs,
                                    reason=("requires the 'right' "
                                            + required_libs_str
                                            + " libraries"))

ureg = pint.UnitRegistry()

@pytest.fixture
def dtype():
    return ppi.PintType()


@pytest.fixture
def data():
    return ppi.PintArray(np.arange(100) * ureg.kilogram)


@pytest.fixture
def data_missing():
    return ppi.PintArray([np.nan, 1] * ureg.meter)


@pytest.fixture(params=['data', 'data_missing'])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == 'data':
        return data
    elif request.param == 'data_missing':
        return data_missing


@pytest.fixture
def data_repeated(data):
    """Return different versions of data for count times"""
    def gen(count):
        for _ in range(count):
            yield data  # no idea what I'm meant to put here, try just copying from https://github.com/pandas-dev/pandas/blob/master/pandas/tests/extension/integer/test_integer.py
    yield gen


@pytest.fixture
def data_for_sorting():
    return ppi.PintArray([0.3, 10, -50])
    # should probably get fancy and do something like
    # [1 * ureg.meter, 3*ureg.meter, 10 * ureg.centimeter]


@pytest.fixture
def data_missing_for_sorting():
    return ppi.PintArray([4, np.nan, -5])
    # should probably get fancy and do something like
    # [1 * ureg.meter, 3*ureg.meter, 10 * ureg.centimeter]


@pytest.fixture
def na_cmp():
    """Binary operator for comparing NA values.

    Should return a function of two arguments that returns
    True if both arguments are (scalar) NA for your type.

    By defult, uses ``operator.or``
    """
    return lambda x, y: bool(np.isnan(x)) & bool(np.isnan(y))


@pytest.fixture
def na_value():
    return ppi.PintType.na_value


@pytest.fixture
def data_for_grouping():
    a = 1
    b = 2 ** 32 + 1
    c = 2 ** 32 + 10
    return ppi.PintArray([
        b, b, np.nan, np.nan, a, a, b, c
    ])

# === missing from docs about what has to be included in tests ===
# copied from pandas/pandas/conftest.py
_all_arithmetic_operators = ['__add__', '__radd__',
                             '__sub__', '__rsub__',
                             '__mul__', '__rmul__',
                             '__floordiv__', '__rfloordiv__',
                             '__truediv__', '__rtruediv__',
                             '__pow__', '__rpow__',
                             '__mod__', '__rmod__']
if not PY3:
    _all_arithmetic_operators.extend(['__div__', '__rdiv__'])

@pytest.fixture(params=_all_arithmetic_operators)
def all_arithmetic_operators(request):
    """
    Fixture for dunder names for common arithmetic operations
    """
    return request.param

@pytest.fixture(params=['__eq__', '__ne__', '__le__',
                        '__lt__', '__ge__', '__gt__'])
def all_compare_operators(request):
    """
    Fixture for dunder names for common compare operations

    * >=
    * >
    * ==
    * !=
    * <
    * <=
    """
    return request.param
# =================================================================

@check_required
class TestCasting(base.BaseCastingTests):
    pass

@check_required
class TestConstructors(base.BaseConstructorsTests):
    pass

@check_required
class TestDtype(base.BaseDtypeTests):
    pass

@check_required
class TestGetitem(base.BaseGetitemTests):
    pass

@check_required
class TestGroupby(base.BaseGroupbyTests):
    pass

@check_required
class TestInterface(base.BaseInterfaceTests):
    pass

@check_required
class TestMethods(base.BaseMethodsTests):
    pass

@check_required
class TestArithmeticOps(base.BaseArithmeticOpsTests):
    pass

@check_required
class TestComparisonOps(base.BaseComparisonOpsTests):
    pass

@check_required
class TestOpsUtil(base.BaseOpsUtil):
    pass

@check_required
class TestMissing(base.BaseMissingTests):
    pass

@check_required
class TestReshaping(base.BaseReshapingTests):
    pass

@check_required
class TestSetitem(base.BaseSetitemTests):
    pass

# all of the below tests are pretty messy
# I'm bascially just fiddling around trying to write examples of
# how things should work, which can then be
# tidied up once we have a clearer idea of what we are trying to do

# plan is to re-write tests as self-contained blocks that can be copied and
# pasted (with addition of import substitutions and extracting function code)
# to be used in e.g. documentation

# simple examples:
# - accessing data
# - arithmetic with data
# - initialising data

"""
Notes from working out how to do data access:

I don't really understand what the `values` attributes is for on a pandas Series. Does it basically just use the `__repr__` method of the class when the values are printed and otherwise just uses the `__getitem__` method of the class to get items?

I ask because initially, I thought that I should be able to do something like

>>> import pint
>>> from pint.pandas_interface import PintArray
>>> import numpy as np
>>> import pandas as pd
>>> from pandas.core.arrays import IntegerArray
>>> ureg = pint.UnitRegistry()
>>> abc = np.arange(0,100) * ureg.meter
>>> abc
<Quantity([ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42
 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65
 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88
 89 90 91 92 93 94 95 96 97 98 99], 'meter')>
>>> ser2 = pd.Series(PintArray(abc))
>>> ser2.values
<pint.pandas_interface.pint_array.PintArray object at 0x1154f84a8>

and get back my original 'pint array' (for want of a better word), in
this case `abc`. However that wasn't the case. Although I could do

>>> ser2.values[23]

>>> ser2.values[23]
<Quantity(23, 'meter')>

which does make sense.

So then I worked out that this was simply an issue with  `__repr__`

To work this out, I fiddled around. For example,

>>> ser2.values.data
<Quantity([ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42
 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57 58 59 60 61 62 63 64 65
 66 67 68 69 70 71 72 73 74 75 76 77 78 79 80 81 82 83 84 85 86 87 88
 89 90 91 92 93 94 95 96 97 98 99], 'meter')>

from which I got a representation more like what I'd hoped to get
for `ser2.values` (although obviously the datatype changed a bit). To
get an example of the behaviour I wanted, I looked at
`IntergerArray`.

>>> intarr = IntegerArray(list(range(100)))
>>> intser = pd.Series(intarr)
>>> intser.values
IntegerArray([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
              16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
              30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43,
              44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
              58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
              72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85,
              86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
             dtype='Int64')
>>> intser.values._data
array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
       16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
       32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
       48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
       64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
       80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
       96, 97, 98, 99])

as well as a plain Series

>>> pdser = pd.Series(range(0,100))
>>> pdser.values
array([ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
       16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
       32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
       48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
       64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79,
       80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95,
       96, 97, 98, 99])

I also stepped through (with a debugger) what happens when you call
`pdser.values` and saw that it was actually going through the `__repr__`
method, at least implicitly.
"""

"""
Some thoughts on whether `Pint arrays' (for want of a better word) could ever
be used directly with pandas rather than having to go through our `PintArray`
which subclasses `ExtensionArray`.

When pandas is doing its type checking, it goes through a bunch of
steps and then has a function called `is_extension_array_dtype` in
pandas/pandas/core/dtypes/common.py. This function checks the array
dtype with the line
`dtype = getattr(arr_or_dtype, 'dtype', arr_or_dtype)`.
The problem with this is that, for a pint array, dtype is the same as
for the underlying numpy array e.g.

>>> import pint
>>> import numpy as np
>>> ureg = pint.UnitRegistry()
>>> abc = np.arange(0,100) * ureg.meter
>>> abc
<Quantity([ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
            20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38
            39 40 41 42 43 44 45 46 47 48 49 50 51 52 53 54 55 56 57
            58 59 60 61 62 63 64 65 66 67 68 69 70 71 72 73 74 75 76
            77 78 79 80 81 82 83 84 85 86 87 88 89 90 91 92 93 94 95
            96 97 98 99], 'meter')>
>>> abc.dtype
dtype('int64')
>>> type(abc)  # FYI
<class 'pint.quantity.build_quantity_class.<locals>.Quantity'>

Hence I don't think it's possible to simply register 'pint arrays'
in pandas, we have to use this extension array. The awkward thing with
that is that we have to store the actual data in another attribute of
the underlying class. Hence things like

>>> ser = pd.Series(abc)

can never work directly which is kind of sad... You have to always go
through a `PintArray`.
"""
@check_required
class TestUserInterface(object):
    def test_get_underlying_data(self, data):
        ser = pd.Series(data)
        assert ser.values == data
        assert ser.values[23] == data[23]

    def test_arithmetic(self, data):
        ser = pd.Series(data)
        ser2 = ser + ser
        assert ser2.values == 2*data

    def test_initialisation(self, data):
        # fails with plain array
        # works with PintArray
        strt = np.arange(100) * ureg.newton
        ser = pd.Series(strt)
        assert ser.values == strt
