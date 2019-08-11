# File to show the basics gm id figures
# Created by Fengqi Zhang
# 2019-07-23
# based on pyMOSChar
# Updated for Gm Id GUI Tool
# 2019-07-31

import numpy as np
from scipy.interpolate import interpn

mosDat = None

def info(mosDat):
    if( mosDat == None):
        print ("No MOSFET data available. Please set first")
    else:
        lenVgs = mosDat['VGS'].shape[1] - 1
        lenVds = mosDat['VDS'].shape[1] - 1
        lenVsb = mosDat['VSB'].shape[1] - 1
        minVgs = mosDat['VGS'][0][0]
        maxVgs = mosDat['VGS'][0][lenVgs]
        stepVgs = (maxVgs - minVgs)/lenVgs
        minVds = mosDat['VDS'][0][0]
        maxVds = mosDat['VDS'][0][lenVds]
        stepVds = (maxVds - minVds)/lenVds
        minVsb = mosDat['VSB'][0][0]
        maxVsb = mosDat['VSB'][0][lenVsb]
        stepVsb = (maxVsb - minVsb)/lenVsb
        print ('VGS : from %1.3f to %1.3f with step of %1.3f' % (minVgs, maxVgs, stepVgs))
        print ('VDS : from %1.3f to %1.3f with step of %1.3f' % (minVds, maxVds, stepVds))
        print ('VSB : from %1.3f to %1.3f with step of %1.3f' % (minVsb, maxVsb, stepVsb))
        #print ('Gate Length Set :', end = ' ')

def lookup(mosDat, mosType, *outVars, **inVars):
    '''Main lookup function'''

    defaultL =  min(mosDat['L'][0])
    defaultVGS = mosDat['VGS'][0]
    defaultVDS = max(mosDat['VDS'][0])/2
    defaultVSB = 0

    # Figure out the mode of operation and the requested output arguments.
    # Mode 1 : Just one variable requested as output.
    # Mode 2 : A ratio or product of variables requested as output.
    # Mode 3 : Two ratios or products of variables requested as output.
    mode = 1
    outVarList = []

    if (len(outVars) == 2):
        mode = 3
        for outVar in outVars:
            if (type(outVar) == str):
                if (outVar.find('/') != -1):
                    pos = outVar.find('/')
                    outVarList.append(outVar[:pos].upper())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].upper())
                elif (outVar.find('*') != -1):
                    pos = outVar.find('*')
                    outVarList.append(outVar[:pos].upper())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].upper())
                else:
                    print ("ERROR: Outputs requested must be a ratio or product of variables")
                    return None
            else:
                print ("ERROR: Output variables must be strings!")
                return None
    elif (len(outVars) == 1):
        outVar = outVars[0]
        if (type(outVar) == str):
            if (outVar.find('/') == -1 and outVar.find('*') == -1):
                mode = 1
                outVarList.append( outVar.upper())
            else:
                mode = 2
                if (outVar.find('/') != -1):
                    pos = outVar.find('/')
                    outVarList.append(outVar[:pos].upper())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].upper())
                elif (outVar.find('*') != -1):
                    pos = outVar.find('*')
                    outVarList.append(outVar[:pos].upper())
                    outVarList.append(outVar[pos])
                    outVarList.append(outVar[pos+1:].upper())
        else:
            print ("ERROR: Output variables must be strings!")
            return None
    else:
        print ("ERROR: No output variables specified")
        return None

    # Figure out the input arguments. Set to default those not specified.
    varNames = [key for key in inVars.keys()]

    for varName in varNames:
        if (not varName.isupper()):
            print ("ERROR: Keyword args must be upper case. Allowed arguments: L, VGS, VDS and VSB.")
            return None
        if (varName not in ['L', 'VGS', 'VDS', 'VSB']):
            print ("ERROR: Invalid keyword arg(s). Allowed arguments: L, VGS, VDS and VSB.")
            return None

    L = defaultL
    VGS = defaultVGS
    VDS = defaultVDS
    VSB = defaultVSB
    if ('L' in varNames):
        L = inVars['L']
    if ('VGS' in varNames):
        VGS = inVars['VGS']
    if ('VDS' in varNames):
        VDS = inVars['VDS']
    if ('VSB' in varNames):
        VSB = inVars['VSB']

    xdataRaw = None
    ydataRaw = None

    # Extract the data that was requested
    if (mode == 1):
        ydataRaw = mosDat[outVarList[0]]
    elif (mode == 2 or mode == 3):
        ydataRaw = eval("mosDat[outVarList[0]][0]" + outVarList[1] + "mosDat[outVarList[2]][0]")
        if (mode == 3):
            xdataRaw = eval("mosDat[outVarList[3]][0]" + outVarList[4] + "mosDat[outVarList[5]][0]")
    # Change Data Type
    xdata = np.array(xdataRaw)
    ydata = np.array(ydataRaw)
    vsbf = np.array(mosDat['VSB']).flatten()
    vdsf = np.array(mosDat['VDS']).flatten()
    vgsf = np.array(mosDat['VGS']).flatten()
    lf = np.array(mosDat['L']).flatten()
    # Interpolate for the input variables provided
    if (mosType == 'nch'):
        #points = ( -mosDat['VSB'][0], mosDat['VDS'][0], mosDat['VGS'][0], mosDat['L'][0])
        points = ( -vsbf, vdsf, vgsf, lf)
    else:
        #points = ( mosDat['VSB'][0], -mosDat['VDS'][0], -mosDat['VGS'][0], mosDat['L'][0])
        points = ( vsbf, -vdsf, -vgsf, lf)

    xi_mesh = np.array(np.meshgrid(VSB, VDS, VGS, L))
    xi = np.rollaxis(xi_mesh, 0, 5)
    xi = xi.reshape(xi_mesh.size//4, 4)

    result = None
    len_VSB = len(VSB) if type(VSB) == np.ndarray or type(VSB) == list else 1
    len_VDS = len(VDS) if type(VDS) == np.ndarray or type(VDS) == list else 1
    len_VGS = len(VGS) if type(VGS) == np.ndarray or type(VGS) == list else 1
    len_L = len(L) if type(L) == np.ndarray or type(L) == list else 1

    if (mode == 1 or mode == 2):
        result = np.squeeze(interpn(points, ydata, xi).reshape( len_VSB, len_VDS, len_VGS, len_L))
    elif (mode == 3):
        print ("ERROR: Mode 3 not supported yet :-(")

    # Return the result
    return result

def lookupfz(mosDat, mosTypeVar,*outVars, **inVars):
    '''Development of simplified version of lookup function'''
    mosType = mosTypeVar.lower()

    defaultL =  min(mosDat['L'][0])
    defaultVGS = mosDat['VGS'][0]
    defaultVDS = max(mosDat['VDS'][0])/2
    defaultVSB = 0

    # Figure out the mode of operation and the requested output arguments.
    # Mode 1 : Just one variable requested as output.
    # Mode 2 : Two variables requested as output.
    mode = 1
    outVarList = []
    if (len(outVars) == 2):
        mode = 2
        for outVar in outVars:
            if (type(outVar) != str):
                print ("ERROR: Output variables must be strings!")
                return None
            else:
                outVarList.append(outVar)
    elif (len(outVars) == 1):
        mode = 1
        outVarList.append(outVars[0])
        if (type(outVars[0]) != str):
            print ("ERROR: Output variables must be strings!")
            return None
    else:
        print ("ERROR: No output variables specified")
        return None

    # Figure out the input arguments. Set to default those not specified.
    varNames = []
    varNames = [key for key in inVars.keys()]
    varNamesRef = [ key.encode('ascii','ignore') for key in mosDat.keys()]

    for varName in varNames:
        if (not varName.isupper()):
            print ("ERROR: Keyword args must be upper case. Allowed arguments: L, VGS, VDS and VSB.")
            return None
        if(mode == 1):
            if (varName not in ['L', 'VGS', 'VDS', 'VSB']):
                print ("ERROR: Invalid keyword arg(s). Allowed arguments: L, VGS, VDS and VSB.")
                return None
        else:
            if (varName not in varNamesRef):
                print ("ERROR: Invalid keyword arg(s)")

    L = defaultL
    VGS = defaultVGS
    VDS = defaultVDS
    VSB = defaultVSB
    if ('L' in varNames):
        L = inVars['L']
    if ('VGS' in varNames):
        VGS = inVars['VGS']
    if ('VDS' in varNames):
        VDS = inVars['VDS']
    if ('VSB' in varNames):
        VSB = inVars['VSB']

    xdataRaw = None
    ydataRaw = None

    # Extract the data that was requested
    ydataRaw = mosDat[outVarList[0]]
    if (mode == 2):
        xdataRaw = mosDat[outVarList[1]]

    # Change Data Type
    xdata = np.array(xdataRaw)
    ydata = np.array(ydataRaw)
    vsbf = np.array(mosDat['VSB']).flatten()
    vdsf = np.array(mosDat['VDS']).flatten()
    vgsf = np.array(mosDat['VGS']).flatten()
    lf = np.array(mosDat['L']).flatten()
    # Interpolate for the input variables provided
    if (mosType == 'nch'):
        #points = ( -mosDat['VSB'][0], mosDat['VDS'][0], mosDat['VGS'][0], mosDat['L'][0])
        points = ( -vsbf, vdsf, vgsf, lf)
    else:
        #points = ( mosDat['VSB'][0], -mosDat['VDS'][0], -mosDat['VGS'][0], mosDat['L'][0])
        points = ( vsbf, -vdsf, -vgsf, lf)

    xi_mesh = np.array(np.meshgrid(VSB, VDS, VGS, L))
    xi = np.rollaxis(xi_mesh, 0, 5)
    xi = xi.reshape(xi_mesh.size//4, 4)

    len_VSB = len(VSB) if type(VSB) == np.ndarray or type(VSB) == list else 1
    len_VDS = len(VDS) if type(VDS) == np.ndarray or type(VDS) == list else 1
    len_VGS = len(VGS) if type(VGS) == np.ndarray or type(VGS) == list else 1
    len_L = len(L) if type(L) == np.ndarray or type(L) == list else 1

    yfit = None
    xfit = None
    result = None
    if (mode == 1):
        result = np.squeeze(interpn(points, ydata, xi).reshape( len_VSB, len_VDS, len_VGS, len_L))
    elif (mode == 2):
        yfit = np.squeeze(interpn(points, ydata, xi).reshape( len_VSB, len_VDS, len_VGS, len_L))
        xfit = np.squeeze(interpn(points, xdata, xi).reshape( len_VSB, len_VDS, len_VGS, len_L))
        #TODO find yfit at desired xfit
        print ("ERROR: Mode 2 not supported yet :-(")

    return result
