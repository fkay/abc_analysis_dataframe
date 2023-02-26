# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 08:25:46 2019

@author: ghlt@viessmann.com
"""

from typing import Any
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy.interpolate import UnivariateSpline


def abc_plot(dctResult, fltSize=6):
    """
    Visualizes the results of an ABC analysis

    Args:
        dctResult (dict): Resulting dictionary of function abc_analysis
        fltSize (float): Size of matplotlib figure
    """

    # create figure
    plt.style.use('seaborn-whitegrid')
    plt.figure(figsize=(fltSize, fltSize))
    ax = plt.axes()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # plot data
    ax.plot(dctResult["p"], dctResult["ABC"], linewidth=3)

    # plot uniform distribution
    pUnif = pd.Series(np.linspace(0, 1, 101))
    A = dctResult["CleanedData"].min()
    MaxX = dctResult["CleanedData"].max()
    if A == MaxX:
        A = 0
        MaxX = 1
    B = MaxX - A
    ABCuniform = (-0.5 * B * pUnif**2 + MaxX * pUnif) / (A + 0.5 * B)
    ax.plot(pUnif, ABCuniform, color='green')

    # add vertical and horizontal line for limit A|B
    plt.plot([dctResult["A"]["Effort"], dctResult["A"]["Effort"]],
             [0, dctResult["A"]["Yield"]],
             'red')
    plt.plot([0, dctResult["A"]["Effort"]],
             [dctResult["A"]["Yield"], dctResult["A"]["Yield"]],
             'red')

    # add vertical and horizontal line for limit B|C
    plt.plot([dctResult["C"]["Effort"], dctResult["C"]["Effort"]],
             [0, dctResult["C"]["Yield"]],
             'red')
    plt.plot([0, dctResult["C"]["Effort"]],
             [dctResult["C"]["Yield"], dctResult["C"]["Yield"]],
             'red')

    # plot anti-diagonal line
    plt.plot([0, 1], [1, 0], 'grey', linestyle='--')
    # plot identity distribution
    plt.plot([0, 1], [0, 1], 'purple', linestyle='--')

    # add title and axis labels
    plt.title('ABC analysis', fontsize=20)
    plt.xlabel('fraction of data', fontsize=12)
    plt.ylabel('fraction of sum of largest data', fontsize=12)

    # add points A, B and C
    plt.plot(dctResult["A"]["Effort"], dctResult["A"]["Yield"],
             'X', color='red')
    plt.plot(dctResult["B"]["Effort"], dctResult["B"]["Yield"],
             'X', color='green')
    plt.plot(dctResult["C"]["Effort"], dctResult["C"]["Yield"],
             'X', color='blue')

    # add group labes
    plt.annotate('A',
                 [dctResult["A"]["Effort"] / 3, 0.25],
                 fontsize=24, color='red')
    plt.annotate('B',
                 [dctResult["A"]["Effort"] + (dctResult["C"]["Effort"]
                  - dctResult["A"]["Effort"]) / 4, 0.25],
                 fontsize=24, color='red')
    plt.annotate('C',
                 [dctResult["C"]["Effort"] + (dctResult["C"]["Effort"]
                  - dctResult["A"]["Effort"]), 0.25],
                 fontsize=24, color='red')

    # add group size
    plt.annotate('n=' + str(len(dctResult["Aind"])),
                 [dctResult["A"]["Effort"] / 6, 0.16],
                 fontsize=10)
    plt.annotate('n=' + str(len(dctResult["Bind"])),
                 [dctResult["A"]["Effort"] + (dctResult["C"]["Effort"]
                  - dctResult["A"]["Effort"]) / 6, 0.16],
                 fontsize=10)
    plt.annotate('n=' + str(len(dctResult["Cind"])),
                 [dctResult["C"]["Effort"] + (dctResult["C"]["Effort"]
                  - dctResult["A"]["Effort"]), 0.16],
                 fontsize=10)

    # add limit labels
    plt.annotate('A|B',
                 [dctResult["A"]["Effort"] / 2, dctResult["A"]["Yield"]
                  + (dctResult["C"]["Yield"] - dctResult["A"]["Yield"]) / 4],
                 fontsize=16, color='red')
    plt.annotate('B|C',
                 [dctResult["C"]["Effort"] / 2, dctResult["C"]["Yield"]
                  + (1 - dctResult["C"]["Yield"]) / 4],
                 fontsize=16, color='red')

    # add legend
    plt.annotate('set limits', [0.81, 0.16], fontsize=12, color='red')
    plt.annotate('data', [0.81, 0.12], fontsize=12, color='blue')
    plt.annotate('uniform', [0.81, 0.08], fontsize=12, color='green')
    plt.annotate('identity', [0.81, 0.04], fontsize=12, color='purple')

    # show complete plot
    plt.show()


def abc_clean_data(psData):
    # Converts strings and negative numbers to 0

    psUncleanData = pd.to_numeric(psData, errors='coerce')
    psWithoutNaN = psUncleanData.dropna()
    if len(psWithoutNaN) < len(psUncleanData):
        raise ValueError('NaN or not convertable strings contained in input '
                         'vector! Please clean your data.')

    psNegative = psUncleanData[psUncleanData < 0]
    if len(psNegative) > 0:
        warnings.warn('negative values found. Will continue by replacing them'
                      ' by 0. This can lead to unexpected results!')
    psCleanData = psUncleanData.apply(lambda x: 0 if x < 0 else x)

    return psCleanData


def abc_curve(psData):
    # Interpolates yield and calculates derivative of first order

    # clean input vector
    psCleanData = abc_clean_data(psData)
    intRows = len(psCleanData)

    # create interpolated x axis
    if intRows < 101:
        p = np.linspace(0, 1, 101)
    else:
        p = np.linspace(0, 1, 1001)

    # get source x and y axis for interpolation
    psSorted = psCleanData.sort_values(ascending=False)
    y = psSorted.cumsum()
    y = y / y.max()
    x = pd.Series(range(1, intRows + 1)) / intRows

    if y.head(1).iloc[0] > 0:
        y = pd.concat([pd.Series([0]), y])
        x = pd.concat([pd.Series([0]), x])
    if y.tail(1).iloc[0] < 1:
        y = pd.concat([y, pd.Series([1])])
        x = pd.concat([x, pd.Series([1])])

    # interpolate with cubic splines and correct interpolation errors
    f = UnivariateSpline(x, y, k=3, s=0)
    dfCurve = pd.DataFrame(p, columns=["Effort"])
    dfCurve["Yield"] = f(p)
    dfCurve["Yield"] = dfCurve["Yield"].apply(lambda x: 1 if x > 1 else x)
    dfCurve["Yield"] = dfCurve["Yield"].apply(lambda x: 0 if x < 0 else x)
    dfCurve["Yield"] = dfCurve["Yield"].fillna(0)

    if dfCurve["Yield"].sum() == 0:
        raise ValueError('Could not calculate valid yield. '
                         'Is the input vector invalid?')

    # calculate derivative of first order
    intRows2 = len(p)
    f_derivative = (UnivariateSpline(p, f(p), k=3, s=0)).derivative()
    derivative = f_derivative(pd.Series(range(1, intRows2 + 1)) / intRows2)
    dfSlope = pd.DataFrame(p, columns=["p"])
    dfSlope["dABC"] = derivative

    # combine results
    dictReturn = {"Curve": dfCurve,
                  "CleanedData": psCleanData,
                  "Slope": dfSlope}
    return dictReturn


def abc_analysis(psData: Any,
                 boolPlotResult=False, fltSize=6,
                 column: str = None):
    """
    Performs an ABC analysis on given data-vector

    Args:
        psData (Any): Numeric data vector that can be converted
            to a pandas series(list, dictionary, series) or if is a pandas
            DataFrame, must provide a column name or the first column will
            be used to classify
        boolPlotResult (boolean): Creates a matplotlib visualization of the
                                  ABC analysis results
        fltSize (float): Size of matplotlib figure
        column (str): Column from the DataFrame to analyze

    Returns:
        Dictionary with results of the ABC analysis:
            ABLimit: Limit between A and B in raw yield (e.g. euro)
            BCLimit: Limit between B and C in raw yield (e.g. euro)
            ABexchanged: If true A and B are exchanged because the conditions
                         for finding A and B in this case applied to each other
            Aind: Indices of group A in input vector (numeric indices)
            Bind: Indices of group B in input vector (numeric indices)
            Cind: Indices of group C in input vector (numeric indices)
            smallestAData: Normalized yield of smallest data in A
            smallestBData: Normalized yield of smallest data in B
            AlimitIndInInterpolation: Index of limit of A in interpolated yield
            BlimitIndInInterpolation: Index of limit of B in interpolated yield
            p: Interpolated effort
            ABC: Interpolated normalized yield
            A: Point (effort, yield) with shortest distance to (0, 1)
            B: Point (Bx, By) with derivative of first order is 1
            C: Point with shortest distance to (Bx, 1)
            CleanedData: Input vector with strings and negative numbers
                         replaced by 0
        In case of pandas DataFrame, a column will be added with the
        classification of the item (a, b or c)
    """

    if psData is None:
        raise ValueError('No input!')

    df = None
    if isinstance(psData, pd.DataFrame):
        df = psData
        if column is None:
            psData = df.iloc[0, :].copy()
        else:
            psData = df[column].copy()

    elif not (isinstance(psData, dict) or isinstance(psData, list) or
              isinstance(psData, set)):
        raise TypeError('The input has to be convertible '
                        'into a pandas series!')
    # convert input vector to pandas series
    else:  # not isinstance(psData, pd.Series):
        try:
            psData = pd.Series(psData)
        except Exception:
            raise TypeError('The input has to be convertible '
                            'into a pandas series!')

    if len(psData) < 3:
        raise ValueError('Not enough input')

    # reset indices to numeric values
    # save index for future use, try not removing the index
    index_name = psData.index.name
    if index_name is None:
        index_name = 'index'
    # psData = psData.reset_index()
    # index = psData[index_name].copy()
    # psData.drop(columns=index_name, inplace=True)

    # interpolate input vector
    dictCurve = abc_curve(psData)

    # get shortest distance to (0, 1)
    dfCurve = dictCurve["Curve"]
    psEffort = dfCurve["Effort"]
    psYield = dfCurve["Yield"]
    dfCurve["Distance"] = np.linalg.norm(dfCurve[['Effort', 'Yield']]
                                         .sub(np.array([0, 1])), axis=1)
    tupPareto = (dfCurve["Distance"].idxmin(),
                 psYield[dfCurve["Distance"].idxmin()])

    # get point with derivative of 1
    dfSlope = dictCurve["Slope"]
    dfSlope["BreakEven"] = abs(dfSlope["dABC"] - 1)
    dfSlopeMin = dfSlope[dfSlope["BreakEven"] == dfSlope["BreakEven"].min()]
    tupBreakEven = (max(dfSlopeMin.index), psYield[max(dfSlopeMin.index)])

    # check if effort of A is smaller than effort of B and change points if
    # necessary
    if psEffort[tupBreakEven[0]] < psEffort[tupPareto[0]]:
        boolExchanged = True
        intJurenInd = tupBreakEven[0]
        intBind = tupPareto[0]
        A = psEffort[tupBreakEven[0]]
        B = psEffort[tupPareto[0]]
    else:
        boolExchanged = False
        intJurenInd = tupPareto[0]
        intBind = tupBreakEven[0]
        A = psEffort[tupPareto[0]]
        B = psEffort[tupBreakEven[0]]

    # calculate C
    dfCurve["Distance"] = np.linalg.norm(dfCurve[['Effort', 'Yield']]
                                         .sub(np.array([B, 1])), axis=1)
    bgrenze = dfCurve["Distance"].idxmin()
    C = psEffort[bgrenze]

    # calculate AB-limit and BC-limit in raw units of input vector (e.g. euro)
    psCleaned = abc_clean_data(psData)
    psSorted = psCleaned.sort_values(ascending=False).reset_index(drop=True)
    # psSorted = psCleaned.sort_values(ascending=False).reset_index()
    ABLimit = psSorted[round(A * len(psData)) - 1]
    BCLimit = psSorted[round(C * len(psData)) - 1]

    # get indices of input vector for each group
    Aind = psData.index[psData > ABLimit].tolist()
    Bind = psData.index[(psData <= ABLimit) & (psData >= BCLimit)].tolist()
    Cind = psData.index[psData < BCLimit].tolist()

    if df is not None:
        df['abc_class'] = 'C'
        df.loc[Aind, 'abc_class'] = 'A'
        df.loc[Bind, 'abc_class'] = 'B'

    # get points A, B and C
    dictA = {"Effort": A, "Yield": psYield[intJurenInd]}
    dictB = {"Effort": B, "Yield": psYield[intBind]}
    dictC = {"Effort": C, "Yield": psYield[bgrenze]}

    # combine results to dictionary
    dictReturn = {"ABLimit": ABLimit,
                  "BCLimit": BCLimit,
                  "ABexchanged": boolExchanged,
                  "Aind": Aind,
                  "Bind": Bind,
                  "Cind": Cind,
                  "smallestAData": psYield[intJurenInd],
                  "smallestBData": psYield[bgrenze],
                  "AlimitIndInInterpolation": intJurenInd,
                  "BlimitIndInInterpolation": bgrenze,
                  "p": psEffort,
                  "ABC": psYield,
                  "A": dictA,
                  "B": dictB,
                  "C": dictC,
                  "CleanedData": dictCurve["CleanedData"]}

    # plot results
    if boolPlotResult:
        abc_plot(dictReturn, fltSize)

    return dictReturn
