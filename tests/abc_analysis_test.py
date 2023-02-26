# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 10:52:59 2019

@author: ghlt@viessmann.com
"""

from abc_analysis.abc_analysis import abc_analysis, abc_clean_data, abc_curve

import pandas as pd
import pytest


class TestABC(object):
    def test_abc_analysis(self):
        lstInput = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        dictOutput = abc_analysis(lstInput)
        assert dictOutput["Aind"] == [6, 7, 8]

    def test_wrong_input_type(self):
        with pytest.raises(TypeError):
            # dfInput = pd.DataFrame([[1, 2, 3], [4, 5, 6]],
            #                       columns={"a", "b", "c"})
            # now accepts DataFrame, test other type
            dfInput = object
            abc_analysis(dfInput)

    def test_empty_input(self):
        with pytest.raises(ValueError):
            abc_analysis([])

    def test_too_short_input(self):
        with pytest.raises(ValueError):
            abc_analysis([1, 2])

    def test_abc_clean_data(self):
        psInput = pd.Series([1, 2, -1, 4, -2, 0])
        psOutput = abc_clean_data(psInput)
        psTest = pd.Series([1, 2, 0, 4, 0, 0])
        assert psOutput.equals(psTest)

    def test_strings_contained(self):
        with pytest.raises(ValueError):
            psInput = pd.Series([1, 2, -1, 4, 'foo', 'bar'])
            abc_clean_data(psInput)

    def test_abc_curve(self):
        psInput = pd.Series([1, 2, 3, 4, 5, 6])
        dictOutput = abc_curve(psInput)
        fltOutput = round(dictOutput["Curve"]["Yield"].sum(), 6)
        assert fltOutput == 64.784286

    def test_invalid_input(self):
        with pytest.raises(ValueError):
            abc_analysis([0, 0, 0, 0])


class TestABC_pandas(object):
    def test_abc_analysis(self):
        lstInput = [5, 6, 7, 1, 2, 3, 4, 8, 9]
        lstInput2 = [chr(a - 1 + ord('a')) for a in range(1, 10)]
        df = pd.DataFrame({'test_column': lstInput,
                           'other_column': lstInput2})
        dictOutput = abc_analysis(df, column='test_column')
        assert ((dictOutput["Aind"] == [2, 7, 8]) and
                (dictOutput["Bind"] == [0, 1, 6]) and
                (df['abc_class'] == ['B', 'B', 'A', 'C', 'C',
                                     'C', 'B', 'A', 'A']).all())

    def test_abc_analysis_with_index(self):
        lstInput = [5, 6, 7, 1, 2, 3, 4, 8, 9]
        lstInput2 = [chr(a - 1 + ord('a')) for a in range(1, 10)]
        df = pd.DataFrame({'test_column': lstInput,
                           'other_column': lstInput2})
        df.set_index('other_column', inplace=True)
        dictOutput = abc_analysis(df, column='test_column')
        assert ((dictOutput["Aind"] == ['c', 'h', 'i']) and
                (dictOutput["Bind"] == ['a', 'b', 'g']) and
                (df['abc_class'] == ['B', 'B', 'A', 'C', 'C',
                                     'C', 'B', 'A', 'A']).all())
