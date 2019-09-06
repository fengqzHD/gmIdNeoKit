# Part 0 Introduction
# gmIdSizingBasic
# Created by Fengqi Zhang
# 2019-July-18
# GUI for sizing MOS Transistor with Gm/Id Methodology

# Part 1 Libraries
# import PyQt5 for GUI
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import Qt, QRunnable, QThreadPool, QDir

# import the UI Interface
from gmIdSizingGuiVp1 import Ui_GmIdMainWindow

# import System
import sys
# import for ploting
import numpy as np
# import pyqtgraph for plotting
import pyqtgraph as pg
# import library for export data for plot
import scipy.io
# import time for sleep
import time
# import library for date stamp
import datetime
# import library for .mat file reading
import h5py
# import library for interpn data
from scipy.interpolate import interpn
from scipy.interpolate import CubicSpline
# import library for mos lookup
import LupMos as lp
import const
import decimal

# Part 2 GUI Class
class gmIdGUIWindow(QtWidgets.QMainWindow):
    # intialize, define all the signals and constants
    def __init__( self):
        # change pyqtgraph setting
        pg.setConfigOption('background', 'w')
        # Create UI Interface
        super( gmIdGUIWindow, self).__init__()
        self.ui = Ui_GmIdMainWindow()
        self.ui.setupUi( self)
        # Initialize the Data
        self.configDataLib()
        # Threading
        self.threadpool = QThreadPool()
        # Connect buttons and checkBoxes
        self.configBondKeys()
        # Set the plot
        self.configPlot()
        # Initialize the checkbox
        self.configDefault()

    def configBondKeys(self):
        ''' connect GUI elements to corresponding functions'''
        #checkBox.stateChanged.connect()
        ## checkBox for Corner Selection
        self.ui.checkBoxCornerTT.stateChanged.connect(self.PlotCornerTT)
        self.ui.checkBoxCornerFF.stateChanged.connect(self.PlotCornerFF)
        self.ui.checkBoxCornerSS.stateChanged.connect(self.PlotCornerSS)
        self.ui.checkBoxCornerFS.stateChanged.connect(self.PlotCornerFS)
        self.ui.checkBoxCornerSF.stateChanged.connect(self.PlotCornerSF)
        self.ui.checkBoxRef.stateChanged.connect(self.PlotRef)
        ## checkBox for Syn Mos Setting
        self.ui.checkBoxSynGmId.stateChanged.connect(self.SynGmId)
        self.ui.checkBoxSynVstar.stateChanged.connect(self.SynVstar)
        self.ui.checkBoxSynGm.stateChanged.connect(self.SynGm)
        self.ui.checkBoxSynId.stateChanged.connect(self.SynId)
        ## checkBox for Opt Mos Setting
        self.ui.checkBoxOptVstar.stateChanged.connect(self.OptVstar)
        self.ui.checkBoxOptFt.stateChanged.connect(self.OptFt)
        self.ui.checkBoxOptAvo.stateChanged.connect(self.OptAvo)
        self.ui.checkBoxOptGm.stateChanged.connect(self.OptGm)
        #self.ui.checkBoxOptId.stateChanged.connect(self.optId)# No such function in GuiVp1
        self.ui.checkBoxOptArea.stateChanged.connect(self.OptArea)
        #pushButton.clicked.connect()
        self.ui.pushButtonMosDirSel.clicked.connect(self.DirSel)
        self.ui.pushButtonMosMatSet.clicked.connect(self.MosMatSet)
        self.ui.pushButtonGateLSet.clicked.connect(self.GateLSet)
        self.ui.pushButtonGateLRef.clicked.connect(self.GateLRef)
        self.ui.pushButtonGateLChk.clicked.connect(self.GateLChk)
        self.ui.pushButtonPlot.clicked.connect(self.PlotUpdate)
        self.ui.pushButtonSynMos.clicked.connect(self.SynMos)
        self.ui.pushButtonFuEst.clicked.connect(self.FuEst)
        #self.ui.pushButtonLChk.clicked.connect(self.LChkVstar)
        #self.ui.pushButtonExtCheck.clicked.connect(self.ExtCheck)#No such function in GuiVp1
        self.ui.pushButtonCal.clicked.connect(self.CalMos)
        self.ui.pushButtonOptOp.clicked.connect(self.OptOpMos)
        self.ui.pushButtonOptSize.clicked.connect(self.OptSizeMos)
        #comboBox.currentIndexChanged.connect()
        self.ui.comboBoxDesignCorner.currentIndexChanged.connect(self.changeCorner)

    def configPlot(self):
        # vstar as x axis
        self.ui.topLPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotVstar.plotItem.setTitle('Fig.1 Id vs Vstar')
        self.ui.topLPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.topLPlotVstar.plotItem.setLabel('left','Id', units = 'A')
        self.ui.topLPlotVstar.plotItem.setLogMode(False, True)
        self.ui.topRPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotVstar.plotItem.setTitle('Fig.2 Ft*Gm/Id vs Vstar')
        self.ui.topRPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.topRPlotVstar.plotItem.setLabel('left','Ft*Gm/Id', units = 'Hz/V')
        self.ui.botLPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.botLPlotVstar.plotItem.setTitle('Fig.3 Avo vs Vstar')
        self.ui.botLPlotVstar.plotItem.setLabel('left','Avo', units = 'V/V')
        self.ui.botRPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.botRPlotVstar.plotItem.setTitle('Fig.4 Ft vs Vstar')
        self.ui.botRPlotVstar.plotItem.setLabel('left','Ft', units = 'Hz')
        # id as x axis
        self.ui.topLPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotId.plotItem.setTitle('Fig.1 Gm/Id vs log(Id)')
        self.ui.topLPlotId.plotItem.setLabel('bottom', 'log(Id)')
        self.ui.topLPlotId.plotItem.setLabel('left','Gm/Id', units = 'S/A')
        self.ui.topRPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotId.plotItem.setTitle('Fig.2 Ft*Gm/Id vs log(Id)')
        self.ui.topRPlotId.plotItem.setLabel('bottom', 'log(Id)')
        self.ui.topRPlotId.plotItem.setLabel('left','Ft*Gm/Id', units = 'Hz/V')
        self.ui.botLPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotId.plotItem.setTitle('Fig.2 Avo vs log(Id)')
        self.ui.botLPlotId.plotItem.setLabel('bottom', 'log(Id)')
        self.ui.botLPlotId.plotItem.setLabel('left','Avo', units = 'V/V')
        self.ui.botRPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotId.plotItem.setTitle('Fig.3 Ft*Gm/Id vs log(Id)')
        self.ui.botRPlotId.plotItem.setLabel('bottom', 'log(Id)')
        self.ui.botRPlotId.plotItem.setLabel('left','FtGm/Id', units = 'Hz/V')
        # vgs as x axis
        self.ui.topLPlotVgs.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotVgs.plotItem.setTitle('Fig.1 Id vs Vgs')
        self.ui.topLPlotVgs.plotItem.setLabel('bottom', 'Vgs', units = 'V')
        self.ui.topLPlotVgs.plotItem.setLabel('left','Id', units = 'A')
        #self.ui.topLPlotVgs.plotItem.setLogMode(False, True)
        self.ui.topRPlotVgs.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotVgs.plotItem.setTitle('Fig.2 Ft*Gm/Id vs Vgs')
        self.ui.topRPlotVgs.plotItem.setLabel('bottom', 'Vgs', units = 'V')
        self.ui.topRPlotVgs.plotItem.setLabel('left','Ft*Gm/Id', units = 'Hz/V')
        self.ui.botLPlotVgs.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotVgs.plotItem.setLabel('bottom', 'Vgs', units = 'V')
        self.ui.botLPlotVgs.plotItem.setTitle('Fig.3 Avo vs Vgs')
        self.ui.botLPlotVgs.plotItem.setLabel('left','Avo', units = 'V/V')
        self.ui.botRPlotVgs.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotVgs.plotItem.setLabel('bottom', 'Vgs', units = 'V')
        self.ui.botRPlotVgs.plotItem.setTitle('Fig.4 Ft vs Vgs')
        self.ui.botRPlotVgs.plotItem.setLabel('left','Ft', units = 'Hz')
        # gmId as x axis
        self.ui.topLPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotGmId.plotItem.setTitle('Fig.1 Id vs Gm/Id')
        self.ui.topLPlotGmId.plotItem.setLabel('bottom', 'Gm/Id', units = 'S/A')
        self.ui.topLPlotGmId.plotItem.setLabel('left','Id', units = 'A')
        self.ui.topLPlotGmId.plotItem.setLogMode(False, True)
        self.ui.topRPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotGmId.plotItem.setTitle('Fig.2 Ft*Gm/Id vs Gm/Id')
        self.ui.topRPlotGmId.plotItem.setLabel('bottom', 'Gm/Id', units = 'V')
        self.ui.topRPlotGmId.plotItem.setLabel('left','Ft*Gm/Id', units = 'Hz/V')
        self.ui.botLPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotGmId.plotItem.setLabel('bottom', 'Gm/Id', units = 'S/A')
        self.ui.botLPlotGmId.plotItem.setTitle('Fig.2 Avo vs Gm/Id')
        self.ui.botLPlotGmId.plotItem.setLabel('left','Avo', units = 'V/V')
        self.ui.botRPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotGmId.plotItem.setLabel('bottom', 'Gm/Id', units = 'S/A')
        self.ui.botRPlotGmId.plotItem.setTitle('Fig.3 Ft vs Gm/Id')
        self.ui.botRPlotGmId.plotItem.setLabel('left','Ft', units = 'Hz')
        # L as x axis
        self.ui.topLPlotL.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotL.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.topLPlotL.plotItem.setTitle('Fig.1 Vgs vs L')
        self.ui.topLPlotL.plotItem.setLabel('left','Vgs', units = 'V')
        #self.ui.topLPlotL.plotItem.addLegend()
        self.ui.topRPlotL.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotL.plotItem.setTitle('Fig.2 Vstar vs L')
        self.ui.topRPlotL.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.topRPlotL.plotItem.setLabel('left', 'Vstar', units = 'V')
        #self.ui.topRPlotL.plotItem.addLegend()
        self.ui.botLPlotL.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotL.plotItem.setTitle('Fig.3 Avo vs L')
        self.ui.botLPlotL.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.botLPlotL.plotItem.setLabel('left', 'Avo', units = 'V/V')
        self.ui.botRPlotL.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotL.plotItem.setTitle('Fig.4 Ft vs L')
        self.ui.botRPlotL.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.botRPlotL.plotItem.setLabel('left', 'Ft', units = 'Hz')
        # L as x axis for Opt
        self.ui.topLPlotOpt.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotOpt.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.topLPlotOpt.plotItem.setTitle('Fig.1 W vs L')
        self.ui.topLPlotOpt.plotItem.setLabel('left','W', units = 'um')
        self.ui.topRPlotOpt.plotItem.showGrid(True, True, 0.7)
        self.ui.topRPlotOpt.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.topRPlotOpt.plotItem.setTitle('Fig.2 Id vs L')
        self.ui.topRPlotOpt.plotItem.setLabel('left','Id', units = 'A')
        self.ui.botLPlotOpt.plotItem.showGrid(True, True, 0.7)
        self.ui.botLPlotOpt.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.botLPlotOpt.plotItem.setTitle('Fig.3 Cgg vs L')
        self.ui.botLPlotOpt.plotItem.setLabel('left','Cgg', units = 'F')
        self.ui.botRPlotOpt.plotItem.showGrid(True, True, 0.7)
        self.ui.botRPlotOpt.plotItem.setLabel('bottom', 'L', units = 'nm')
        self.ui.botRPlotOpt.plotItem.setTitle('Fig.4 Cdd vs L')
        self.ui.botRPlotOpt.plotItem.setLabel('left','Cdd', units = 'F')
        # Pen & Line & Legend
        self.legTLPlotL = pg.LegendItem()
        self.legTLPlotL.setParentItem(self.ui.topLPlotL.plotItem.graphicsItem())
        self.legTRPlotL = pg.LegendItem()
        self.legTRPlotL.setParentItem(self.ui.topRPlotL.plotItem.graphicsItem())
        self.redLinePen = pg.mkPen('r', width=1.5, style=QtCore.Qt.DashLine)
        self.greenLinePen = pg.mkPen('g', width=1.5, style=QtCore.Qt.DashLine)
        self.blueLinePen = pg.mkPen('b', width=1.5, style=QtCore.Qt.DashLine)
        self.magLinePen = pg.mkPen('m', width=1.5, style=QtCore.Qt.DashLine)
        self.dashPen = pg.mkPen('r', width=1.5, style=QtCore.Qt.DashLine)
        self.topLVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.topRVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.botLVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.botRVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.topLVLineId = pg.InfiniteLine(angle=90, pen = self.greenLinePen, movable=False)
        self.topRVLineId = pg.InfiniteLine(angle=90, pen = self.greenLinePen, movable=False)
        self.botLVLineId = pg.InfiniteLine(angle=90, pen = self.greenLinePen, movable=False)
        self.botRVLineId = pg.InfiniteLine(angle=90, pen = self.greenLinePen, movable=False)
        self.topLVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.topRVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.botLVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.botRVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.topLVLineVgs = pg.InfiniteLine(angle=90, pen = self.magLinePen, movable=False)
        self.topRVLineVgs = pg.InfiniteLine(angle=90, pen = self.magLinePen, movable=False)
        self.botLVLineVgs = pg.InfiniteLine(angle=90, pen = self.magLinePen, movable=False)
        self.botRVLineVgs = pg.InfiniteLine(angle=90, pen = self.magLinePen, movable=False)
        self.ui.topLPlotVstar.addItem(self.topLVLineVstar, ignoreBounds=True)
        self.ui.topRPlotVstar.addItem(self.topRVLineVstar, ignoreBounds=True)
        self.ui.botLPlotVstar.addItem(self.botLVLineVstar, ignoreBounds=True)
        self.ui.botRPlotVstar.addItem(self.botRVLineVstar, ignoreBounds=True)
        self.ui.topLPlotId.addItem(self.topLVLineId, ignoreBounds=True)
        self.ui.topRPlotId.addItem(self.topRVLineId, ignoreBounds=True)
        self.ui.botLPlotId.addItem(self.botLVLineId, ignoreBounds=True)
        self.ui.botRPlotId.addItem(self.botRVLineId, ignoreBounds=True)
        self.ui.topLPlotGmId.addItem(self.topLVLineGmId, ignoreBounds=True)
        self.ui.topRPlotGmId.addItem(self.topRVLineGmId, ignoreBounds=True)
        self.ui.botLPlotGmId.addItem(self.botLVLineGmId, ignoreBounds=True)
        self.ui.botRPlotGmId.addItem(self.botRVLineGmId, ignoreBounds=True)
        self.ui.topLPlotVgs.addItem(self.topLVLineVgs, ignoreBounds=True)
        self.ui.topRPlotVgs.addItem(self.topRVLineVgs, ignoreBounds=True)
        self.ui.botLPlotVgs.addItem(self.botLVLineVgs, ignoreBounds=True)
        self.ui.botRPlotVgs.addItem(self.botRVLineVgs, ignoreBounds=True)
        self.ui.topLPlotVstar.scene().sigMouseMoved.connect(self.topMouseMovedVstar)
        self.ui.topLPlotGmId.scene().sigMouseMoved.connect(self.topMouseMovedGmId)
        self.ui.topLPlotId.scene().sigMouseMoved.connect(self.topMouseMovedId)
        self.ui.topLPlotVgs.scene().sigMouseMoved.connect(self.topMouseMovedVgs)

    def configDataLib(self):
        # MOS Transistor
        self.L = 0.18
        self.Lref = 0.18
        self.Lchk = 0.18
        self.mosModel = 'nch'
        # MOS Transistor
        self.W = 10.0
        self.GmId = 10.0
        self.Gm = 10.0
        self.Id = 1.0
        self.VDS = 0.9
        self.VSB = 0.1
        # Syn MOS Transistor
        self.synW = 10.0
        self.synVGS = 0.9
        self.synGmId = 5.0
        self.synGm = 5.0
        self.synId = 1.0
        self.synState = 1
        ## synOppt : 0 for GmOverId, 1 for Vstar
        self.synOppt = 1
        ## synSize : 0 for Gm, 1 for Id
        self.synSize = 0
        # Calculation MOS Transistor
        self.calW = 10.0
        self.calGmId = 5.0
        self.calId = 1.0
        self.calVGS = 0.9
        # Optimize MOS Transistor
        self.optVGS = 0.9
        self.optW = 10.0
        self.optOpGmId = 0.2
        self.optOpFt = 50.0
        self.optOpAvo = 50.0
        self.optGm = 0.001
        self.optId = 0.0002
        self.optArea = 20.0
        self.optState = 1
        self.optPltL = []
        self.optPltFt = []
        self.optPltAvo = []
        self.optPltGmId = []
        self.optPltVstar = []
        self.optPltVgs = []
        self.optPltId = []
        self.optPltW = []
        self.optPltCgg = []
        self.optPltCdd = []
        self.optPltVth = []
        self.optPltVdsat = []
        # Process
        self.tgtCorner = 0
        #avaiable corner: TT, FF, SS, FS, SF
        self.listCorner =["tt","ff","ss","fs","sf"]
        self.avaCorner = [ 0,  0,  0,  0,  0]
        self.visCorner = [ False, False, False, False, False]
        self.mosCorner = [None, None, None, None, None]
        self.mosDat = None
        # Data
        self.listVGS = []
        self.listL = []
        self.listLChk = []
        self.listId = []
        self.listVdsat = []
        self.listGmId = []
        self.listVstar = []
        self.listFt = []
        self.listFOM = []
        self.listAv = []
        self.listVthL = []
        self.listAvL = []
        self.listFtL = []
        self.pltIdV = None
        self.pltGmId = None
        self.pltVstar = None
        self.pltFtV = None
        self.pltFOM = None
        self.pltAvV = None
        self.pltIdG = None
        self.pltFtG = None
        self.pltAvG = None
        self.EnFom = 0
        self.rangeIdV = []
        # Range of vstar, gmid
        self.minVstar = 0.085
        self.maxVstar = 1.0
        self.minGmId = 2.0
        self.maxGmId = 23.5
        self.minLogId = -9.0
        # Range of Data Sweep
        self.maxVGS = 1.8
        self.halfVGS = 0.9
        self.stepVGS = 0.01
        self.maxVSB = 0.6
        # Curve for des-L
        ## Curve for Vgs Figure
        self.pltCurveIdDDes = None
        self.pltCurveFtDDes = None
        self.pltCurveAvDDes = None
        self.pltCurveFomDDes= None
        self.pltCurveVdsatDDes= None
        self.corCurveIdDDes = [None, None, None, None, None]
        self.corCurveFtDDes = [None, None, None, None, None]
        self.corCurveAvDDes = [None, None, None, None, None]
        self.corCurveFomDDes= [None, None, None, None, None]
        ## Curve for Vstar Figure
        self.pltCurveIdVDes = None
        self.pltCurveFtVDes = None
        self.pltCurveAvVDes = None
        self.pltCurveFomVDes= None
        self.pltCurveVgsVDes= None
        self.pltCurveVdsatVDes= None
        self.corCurveIdVDes = [None, None, None, None, None]
        self.corCurveFtVDes = [None, None, None, None, None]
        self.corCurveAvVDes = [None, None, None, None, None]
        self.corCurveFomVDes= [None, None, None, None, None]
        ## Curve for GmId Figure
        self.pltCurveIdGDes = None
        self.pltCurveFtGDes = None
        self.pltCurveAvGDes = None
        self.pltCurveFomGDes= None
        self.pltCurveVgsGDes= None
        self.pltCurveVdsatGDes= None
        self.corCurveIdGDes = [None, None, None, None, None]
        self.corCurveFtGDes = [None, None, None, None, None]
        self.corCurveAvGDes = [None, None, None, None, None]
        self.corCurveFomGDes= [None, None, None, None, None]
        ## Curve for I Figure
        self.pltCurveGmIDes = None
        self.pltCurveFtIDes = None
        self.pltCurveAvIDes = None
        self.pltCurveFomIDes= None
        self.pltCurveVgsIDes= None
        self.pltCurveVdsatIDes= None
        self.corCurveGmIDes = [None, None, None, None, None]
        self.corCurveFtIDes = [None, None, None, None, None]
        self.corCurveAvIDes = [None, None, None, None, None]
        self.corCurveFomIDes= [None, None, None, None, None]
        # Curve for Lref
        ## Curve for Vgs Figure
        self.corCurveIdDRef = [None, None, None, None, None]
        self.corCurveFtDRef = [None, None, None, None, None]
        self.corCurveAvDRef = [None, None, None, None, None]
        self.corCurveFomDRef= [None, None, None, None, None]
        ## Curve for Vstar Figure Ref L
        self.corCurveIdVRef = [None, None, None, None, None]
        self.corCurveFtVRef = [None, None, None, None, None]
        self.corCurveAvVRef = [None, None, None, None, None]
        self.corCurveFomVRef= [None, None, None, None, None]
        ## Curve for GmId Figure Ref L
        self.corCurveIdGRef = [None, None, None, None, None]
        self.corCurveFtGRef = [None, None, None, None, None]
        self.corCurveAvGRef = [None, None, None, None, None]
        self.corCurveFomGRef= [None, None, None, None, None]
        ## Curve for I Figure Ref L
        self.corCurveGmIRef = [None, None, None, None, None]
        self.corCurveFtIRef = [None, None, None, None, None]
        self.corCurveAvIRef = [None, None, None, None, None]
        self.corCurveFomIRef= [None, None, None, None, None]
        # Curve as function of L
        self.curveVth = None
        self.curveVthCorner = [None, None, None, None, None]
        self.lTgtVstar = 0.15
        self.lTgtGmId = 15.0
        self.curveAvDes = None
        self.curveAvDesCorner = [None, None, None, None, None]
        self.curveAvW1 = None
        self.curveAvW1Corner = [None, None, None, None, None]
        self.curveAvS0 = None
        self.curveAvS0Corner = [None, None, None, None, None]
        self.curveFtDes = None
        self.curveFtDesCorner = [None, None, None, None, None]
        self.curveFtW1 = None
        self.curveFtW1Corner = [None, None, None, None, None]
        self.curveFtS0 = None
        self.curveFtS0Corner = [None, None, None, None, None]
        # Curve for Opt Result of L
        self.curveOptW = None
        self.curveOptCgg = None
        self.curveOptCdd = None
        self.curveOptVgs = None
        self.curveOptId = None
        self.curveOptFt = None
        self.curveOptAvo = None
        self.curveOptGmId = None
        # Pen Style for Pyqtgraph
        self.cornerPen = [None, None, None, None, None]
        self.cornerPen[0] = pg.mkPen(color=(119, 172, 48), width = 2, style=QtCore.Qt.DashLine)
        self.cornerPen[1] = pg.mkPen( color=(0, 114, 189), width = 2, style=QtCore.Qt.DashLine)
        self.cornerPen[2] = pg.mkPen(color=(126, 47, 142), width = 2, style=QtCore.Qt.DashLine)
        self.cornerPen[3] = pg.mkPen( color=(217, 83, 25), width = 2, style=QtCore.Qt.DashLine)
        self.cornerPen[4] = pg.mkPen(color=(237, 177, 32), width = 2, style=QtCore.Qt.DashLine)
        self.linePen = [None, None, None, None, None]
        self.linePen[0] = pg.mkPen(color=(119, 172, 48), width = 2)
        self.linePen[1] = pg.mkPen( color=(0, 114, 189), width = 2)
        self.linePen[2] = pg.mkPen(color=(126, 47, 142), width = 2)
        self.linePen[3] = pg.mkPen( color=(217, 83, 25), width = 2)
        self.linePen[4] = pg.mkPen(color=(237, 177, 32), width = 2)
        self.refPen = pg.mkPen(color=(77,190,238), width = 2.5, style=QtCore.Qt.DotLine)
        self.symbolStyle = 'o'
        # Flag for State
        self.curveReady = 0
        self.desLSet = 0
        self.desLInd = 0
        self.refLSet = 0
        self.refLInd = 0
        self.w0LReady = [ 0, 0, 0, 0, 0]
        self.w1LReady = [ 0, 0, 0, 0, 0]
        self.m0LReady = [ 0, 0, 0, 0, 0]
        self.m1LReady = [ 0, 0, 0, 0, 0]
        self.s0LReady = [ 0, 0, 0, 0, 0]
        self.s1LReady = [ 0, 0, 0, 0, 0]
        ## Opt Operation Point : 0-Vstar, 1-Ft, 2-Av
        self.optOpptMode = 0
        self.optOpptReady = 0
        ## Opt Size : 0-Gm, 1-Id, 2-Area
        self.optSizeMode = 0


    def configDefault(self):
        '''Initialize the GUI by setting the checkbox and so on'''
        self.ui.checkBoxOptVstar.setCheckState(2)
        self.ui.checkBoxOptGm.setCheckState(2)
        self.ui.checkBoxSynVstar.setCheckState(2)
        self.ui.checkBoxSynId.setCheckState(2)

    # checkBox Functions
    def SynGmId(self, state):
        ## synOppt : 0 for GmOverId, 1 for Vstar
        if state == Qt.Checked:
            self.synOppt = 0
            self.ui.checkBoxSynVstar.setCheckState(0)

    def SynVstar(self, state):
        if state == Qt.Checked:
            self.synOppt = 1
            self.ui.checkBoxSynGmId.setCheckState(0)

    def SynGm(self, state):
        if state == Qt.Checked:
            self.synSize = 0
            self.ui.checkBoxSynId.setCheckState(0)

    def SynId(self, state):
        if state == Qt.Checked:
            self.synSize = 1
            self.ui.checkBoxSynGm.setCheckState(0)

    def PlotCornerTT(self, state):
        if self.avaCorner[0] == 1:
            if state == Qt.Checked:
                self.visibleCorCurve(0, True)
            else:
                self.visibleCorCurve(0, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerFF(self, state):
        if self.avaCorner[1] == 1:
            if state == Qt.Checked:
                self.visibleCorCurve(1, True)
            else:
                self.visibleCorCurve(1, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerSS(self, state):
        if self.avaCorner[2] == 1:
            if state == Qt.Checked:
                self.visibleCorCurve(2, True)
            else:
                self.visibleCorCurve(2, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerFS(self, state):
        if self.avaCorner[3] == 1:
            if state == Qt.Checked:
                self.visibleCorCurve(3, True)
            else:
                self.visibleCorCurve(3, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerSF(self, state):
        if self.avaCorner[4] == 1:
            if state == Qt.Checked:
                self.visibleCorCurve(4, True)
            else:
                self.visibleCorCurve(4, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotLWI(self, state):
        '''Turn Off WI Curve'''
        pass
        #if state == Qt.Checked:
        #    self.visibleLCurve(0, True)
        #else:
        #    self.visibleLCurve(0, False)

    def PlotLSI(self, state):
        '''Turn Off SI Curve'''
        pass
        #if state == Qt.Checked:
        #    self.visibleLCurve(2, True)
        #else:
        #    self.visibleLCurve(2, False)

    def PlotRef(self, state):
        if self.refLSet == 1:
            if state == Qt.Checked:
                self.visibleRef(True)
            else:
                self.visibleRef(False)
        else:
            self.ui.labelLog.setText('No Ref Curve')

    def OptVstar(self, state):
        if state == Qt.Checked:
            self.optOpptMode = 0
            self.ui.checkBoxOptFt.setCheckState(0)
            self.ui.checkBoxOptAvo.setCheckState(0)

    def OptAvo(self, state):
        if state == Qt.Checked:
            self.optOpptMode = 2
            self.ui.checkBoxOptVstar.setCheckState(0)
            self.ui.checkBoxOptFt.setCheckState(0)

    def OptFt(self, state):
        if state == Qt.Checked:
            self.optOpptMode = 1
            self.ui.checkBoxOptVstar.setCheckState(0)
            self.ui.checkBoxOptAvo.setCheckState(0)

    def OptGm(self, state):
        if state == Qt.Checked:
            self.optSizeMode = 0
            #self.ui.checkBoxOptId.setCheckState(0)# No optid in GUI Vp1
            self.ui.checkBoxOptArea.setCheckState(0)

    def OptId(self, state):
        if state == Qt.Checked:
            self.optSizeMode = 1
            self.ui.checkBoxOptGm.setCheckState(0)
            self.ui.checkBoxOptArea.setCheckState(0)

    def OptArea(self, state):
        if state == Qt.Checked:
            self.optSizeMode = 2
            self.ui.checkBoxOptGm.setCheckState(0)
            #self.ui.checkBoxOptId.setCheckState(0)# No optid in GUI Vp1

    # pushButton Functions
    def DirSel(self):
        '''Select the Directory for the Data'''
        self.matDirPath = QFileDialog.getExistingDirectory()
        self.matDir = QDir(self.matDirPath)
        self.matDir.setFilter(QtCore.QDir.Files)
        self.matFileList = self.matDir.entryList()
        self.ui.listWidgetMat.clear()
        for i in range(len(self.matFileList)):
            if self.matFileList[i][0] == '.':
                continue
            self.ui.listWidgetMat.addItem(self.matFileList[i])

    def MosMatSet(self):
        self.matItem = self.ui.listWidgetMat.currentItem()
        if self.matItem == None:
            self.ui.labelLog.setText('No MOS Data Set')
        else:
            self.matFilePath = self.matDirPath + '/' + self.matItem.text()
            self.matFileName = self.matItem.text().split('.')[0]
            self.matFileInfo = self.matFileName.split('-')
            self.mosModel = self.matFileInfo[1]
            self.ui.titleMosCharData.setText(self.matFileName)
            self.ui.labelDevType.setText(self.mosModel)
            if (self.mosModel[0] == 'n'):
                self.ui.labelDevType.setStyleSheet("*{\n"
                                                   "background-color:rgb(102, 255, 102);\n"
                                                    "}")
                self.ui.titleToolBox.setStyleSheet("*{\n"
                                                   "background-color:rgb(102, 255, 102);\n"
                                                    "}")
            else:
                self.ui.labelDevType.setStyleSheet("*{\n"
                                                   "background-color:rgb(255, 102, 255);\n"
                                                    "}")
                self.ui.titleToolBox.setStyleSheet("*{\n"
                                                   "background-color:rgb(255, 102, 255);\n"
                                                    "}")
            self.loadMat()

    def GateLSet(self):
        self.gateLItem = self.ui.listWidgetL.currentItem()
        if self.gateLItem == None:
            self.ui.labelLog.setText('No Gate Length Set')
        else:
            self.L = float(self.gateLItem.text())
            self.ui.labelGateL.setText(self.gateLItem.text())
            self.desLSet = 1
            self.desLInd, = np.where(self.listL == self.L)
            self.desLInd = self.desLInd[0]

    def GateLRef(self):
        self.gateLRefItem = self.ui.listWidgetLRef.currentItem()
        if self.gateLRefItem == None:
            self.ui.labelLog.setText('No Ref Gate Length')
        else:
            self.Lref = float(self.gateLRefItem.text())
            self.ui.labelGateLRef.setText(self.gateLRefItem.text())
            self.refLSet = 1
            self.refLInd, = np.where(self.listL == self.Lref)
            self.refLInd = self.refLInd[0]

    def GateLChk(self):
        self.gateLChkItem = self.ui.listWidgetLChk.currentItem()
        if self.gateLChkItem == None:
            self.ui.labelLog.setText('No Check Gate Length')
        else:
            self.Lchk = float(self.gateLChkItem.text())
            self.ui.labelGateLChk.setText(self.gateLChkItem.text())

    def PlotUpdate(self):
        if self.desLSet == 0:
            self.ui.labelLog.setText('No Des Gate Length')
        elif self.refLSet == 0:
            self.ui.labelLog.setText('No Ref Gate Length')
        else:
            if(self.desLInd < self.refLInd):
                self.listLChk = self.listL[self.desLInd:self.refLInd + 1]
                self.cornerMat()
            elif (self.desLInd > self.refLInd):
                self.listLChk = self.listL[self.refLInd:self.desLInd + 1]
                self.cornerMat()
            else:
                self.ui.labelLog.setText('Des and Ref should be different')

    def restCurveOff(self):
        if self.avaCorner[0] == 1:
            self.ui.checkBoxCornerTT.setCheckState(2)
            self.ui.checkBoxCornerTT.setCheckState(0)
        if self.avaCorner[1] == 1:
            self.ui.checkBoxCornerFF.setCheckState(2)
            self.ui.checkBoxCornerFF.setCheckState(0)
        if self.avaCorner[2] == 1:
            self.ui.checkBoxCornerSS.setCheckState(2)
            self.ui.checkBoxCornerSS.setCheckState(0)
        if self.avaCorner[3] == 1:
            self.ui.checkBoxCornerFS.setCheckState(2)
            self.ui.checkBoxCornerFS.setCheckState(0)
        if self.avaCorner[4] == 1:
            self.ui.checkBoxCornerSF.setCheckState(2)
            self.ui.checkBoxCornerSF.setCheckState(0)
        if self.refLSet == 1:
            self.visibleAllRef(True)
            self.visibleAllRef(False)

    def CalMos(self):
        self.UpdateBias()
        self.calVGS = float(self.ui.lineEditCalVgs.text())
        self.calW = float(self.ui.lineEditCalWidth.text())
        self.calGmId = lp.lookupfz(self.mosDat, self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=self.calVGS)
        self.calId = lp.lookupfz(self.mosDat, self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=self.calVGS) * self.calW / self.W
        self.ui.labelCalGmId.setText(self.sciPrint(self.calGmId, 'S/A'))
        self.ui.labelCalVstar.setText(self.sciPrint((2.0/self.calGmId), 'V'))
        self.ui.labelChkId.setText(self.sciPrint(self.calId, 'A'))
        self.ui.labelChkGm.setText(self.sciPrint(self.calId*self.calGmId, 'S'))
        self.ChkMos(self.calW, self.calVGS)

    def OptOpMos(self):
        '''Search the Operation Point for the Target'''
        self.UpdateBias()
        self.ui.topLPlotOpt.clear()
        self.ui.topRPlotOpt.clear()
        self.ui.botLPlotOpt.clear()
        self.ui.botRPlotOpt.clear()
        self.ui.topLPlotL.clear()
        self.ui.topRPlotL.clear()
        self.ui.botLPlotL.clear()
        self.ui.botRPlotL.clear()
        self.optPltL = []
        self.optPltFt = []
        self.optPltAvo = []
        self.optPltGmId = []
        self.optPltVgs = []
        self.optPltVth = []
        self.optPltVdsat = []
        self.optPltVstar = []
        if self.optOpptReady == 1:
            self.legTLPlotL.removeItem('Vgs')
            self.legTLPlotL.removeItem('Vth')
            self.legTRPlotL.removeItem('Vstar')
            self.legTRPlotL.removeItem('Vdsat')
        # GmOverId as Constriant
        if self.optOpptMode == 0:
            self.optOpGmId = 2000.0/float(self.ui.lineEditOptVstar.text())
            for optL in self.listLChk:
                self.optVGS, self.optState = self.SearchVGSG( self.tgtCorner, self.optOpGmId, optL, 4)
                if self.optState == 1:
                    self.optPltL.append(1000*optL)
                    self.optPltVgs.append(self.optVGS)
                    self.optPltVth.append(lp.lookupfz(self.mosDat, self.mosModel, 'VT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVdsat.append(lp.lookupfz(self.mosDat, self.mosModel, 'VDSAT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVstar.append(2.0/lp.lookupfz(self.mosDat, self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltFt.append(lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltAvo.append(lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
        # Ft as constriant
        elif self.optOpptMode == 1:
            self.optOpFt = 1000000.0*float(self.ui.lineEditOptFt.text())
            for optL in self.listLChk:
                self.optVGS, self.optState = self.SearchVGSF(self.optOpFt, optL)
                if self.optState == 1:
                    self.optPltL.append(1000*optL)
                    self.optPltVgs.append(self.optVGS)
                    self.optPltVth.append(lp.lookupfz(self.mosDat, self.mosModel, 'VT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVdsat.append(lp.lookupfz(self.mosDat, self.mosModel, 'VDSAT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVstar.append(2.0/lp.lookupfz(self.mosDat, self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltFt.append(lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltAvo.append(lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
        # Avo as constriant
        elif self.optOpptMode == 2:
            self.optOpAvo = float(self.ui.lineEditOptAvo.text())
            for optL in self.listLChk:
                self.optVGS, self.optState = self.SearchVGSA(self.optOpAvo, optL)
                if self.optState == 1:
                    self.optPltL.append(1000*optL)
                    self.optPltVgs.append(self.optVGS)
                    self.optPltVth.append(lp.lookupfz(self.mosDat, self.mosModel, 'VT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVdsat.append(lp.lookupfz(self.mosDat, self.mosModel, 'VDSAT', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltVstar.append(2.0/lp.lookupfz(self.mosDat, self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltFt.append(lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
                    self.optPltAvo.append(lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=optL, VGS=self.optVGS))
        # If Curve is Ready
        if len(self.optPltL) != 0:
            self.optOpptReady = 1
            self.curveOptFt = pg.PlotDataItem( self.optPltL, self.optPltFt, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.curveOptAvo = pg.PlotDataItem( self.optPltL, self.optPltAvo, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.curveOptVstar = pg.PlotDataItem( self.optPltL, self.optPltVstar, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', symbol = 'o', name = 'Vstar', clear=True)
            self.curveOptVdsat = pg.PlotDataItem( self.optPltL, self.optPltVdsat, pen = self.cornerPen[self.tgtCorner], symbolBrush=(255,0,255), symbolPen='w', symbol = 'p', name = 'Vdsat', clear=True)
            self.curveOptVgs = pg.PlotDataItem( self.optPltL, self.optPltVgs, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', symbol = 'o', name = 'Vgs', clear=True)
            self.curveOptVth = pg.PlotDataItem( self.optPltL, self.optPltVth, pen = self.cornerPen[self.tgtCorner], symbolBrush=(255,0,255), symbolPen='w', symbol = 'p', name = 'Vth', clear=True)
            self.ui.topLPlotL.addItem(self.curveOptVgs)
            self.legTLPlotL.addItem(self.curveOptVgs, 'Vgs')
            self.ui.topLPlotL.addItem(self.curveOptVth)
            self.legTLPlotL.addItem(self.curveOptVth, 'Vth')
            self.ui.topRPlotL.addItem(self.curveOptVstar)
            self.legTRPlotL.addItem(self.curveOptVstar, 'Vstar')
            self.ui.topRPlotL.addItem(self.curveOptVdsat)
            self.legTRPlotL.addItem(self.curveOptVdsat, 'Vdsat')
            self.ui.botLPlotL.addItem(self.curveOptAvo)
            self.ui.botRPlotL.addItem(self.curveOptFt)
        else:
            self.optOpptReady = 0

    def OptSizeMos(self):
        '''Size the Mos'''
        sizeW = 10.0
        sizeL = 0.18
        sizeId = 10.0
        sizeCgg = 0.0
        sizeCdd = 0.0
        if self.optOpptReady == 0:
            self.optOpMos()
        if self.optOpptReady == 1:
            self.ui.botLPlotOpt.clear()
            self.ui.botRPlotOpt.clear()
            self.ui.topLPlotOpt.clear()
            self.ui.topRPlotOpt.clear()
            self.optPltW = []
            self.optPltId = []
            self.optPltCgg = []
            self.optPltCdd = []
            if self.optSizeMode == 0:
                self.optGm = float(self.ui.lineEditOptGm.text())*0.000001
                for i in range(len(self.optPltL)):
                    sizeL = self.optPltL[i]/1000.0
                    sizeW = self.optGm / lp.lookupfz(self.mosDat, self.mosModel, 'GM', VDS=self.VDS, VSB=self.VSB, L=sizeL, VGS=self.optPltVgs[i]) * self.W
                    self.optPltW.append(sizeW)
            elif self.optSizeMode == 1:
                self.optId = float(self.ui.lineEditOptId.text())*0.000001
                for i in range(len(self.optPltL)):
                    sizeL = self.optPltL[i]/1000.0
                    sizeW = self.optId / lp.lookupfz(self.mosDat, self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=sizeL, VGS=self.optPltVgs[i]) * self.W
                    self.optPltW.append(sizeW)
            elif self.optSizeMode == 2:
                self.optArea = float(self.ui.lineEditOptArea.text())
                for i in range(len(self.optPltL)):
                    sizeL = self.optPltL[i]/1000.0
                    sizeW = self.optArea/sizeL
                    self.optPltW.append(sizeW)
            for i in range(len(self.optPltL)):
                sizeL = self.optPltL[i]/1000.0
                sizeId = self.optPltW[i] * lp.lookupfz(self.mosDat, self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=sizeL, VGS=self.optPltVgs[i]) / self.W
                sizeCgg = self.optPltW[i] * lp.lookupfz(self.mosDat, self.mosModel, 'CGG', VDS=self.VDS, VSB=self.VSB, L=sizeL, VGS=self.optPltVgs[i]) / self.W
                sizeCdd = self.optPltW[i] * lp.lookupfz(self.mosDat, self.mosModel, 'CDD', VDS=self.VDS, VSB=self.VSB, L=sizeL, VGS=self.optPltVgs[i]) / self.W
                self.optPltId.append(sizeId)
                self.optPltCgg.append(sizeCgg)
                self.optPltCdd.append(sizeCdd)
            self.curveOptW = pg.PlotDataItem(self.optPltL, self.optPltW, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.curveOptCgg = pg.PlotDataItem(self.optPltL, self.optPltCgg, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.curveOptCdd = pg.PlotDataItem(self.optPltL, self.optPltCdd, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.curveOptId = pg.PlotDataItem(self.optPltL, self.optPltId, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
            self.ui.topLPlotOpt.addItem(self.curveOptW)
            self.ui.topRPlotOpt.addItem(self.curveOptId)
            self.ui.botLPlotOpt.addItem(self.curveOptCgg)
            self.ui.botRPlotOpt.addItem(self.curveOptCdd)

    def FuEst(self):
        pass

    def LChkVstar(self):
        '''Check the Specified Vstar as a function of L'''
        if (self.curveAvDes != None):
            self.ui.botLPlotL.removeItem(self.curveAvDes)
            self.ui.botRPlotL.removeItem(self.curveFtDes)
        self.UpdateBias()
        self.lTgtVstar = float(self.ui.lineEditOptVstar.text())
        self.lTgtGmId = 2.0 / self.lTgtVstar
        vstarReady = 0
        vstarVgs = 0.0
        vstarState = 0
        vstarPltAv = []
        vstarPltFt = []
        vstarPltL = []
        for swL in self.listLChk:
            vstarVgs, vstarState = self.SearchVGSG(self.tgtCorner, self.lTgtGmId, swL, 3)
            if vstarState == 1:
                vstarReady = 1
                vstarPltL.append(1000*swL)
                vstarPltAv.append(lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=vstarVgs))
                vstarPltFt.append(lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=vstarVgs))
        if (vstarReady == 1):
            self.curveAvDes = pg.PlotDataItem( vstarPltL, vstarPltAv, pen = self.pen, symbolBrush = (255,0,0), symbolPen='w', clear = True)
            self.curveFtDes = pg.PlotDataItem( vstarPltL, vstarPltFt, pen = self.pen, symbolBrush = (255,0,0), symbolPen='w', clear = True)
            self.ui.botLPlotL.addItem(self.curveAvDes)
            self.ui.botRPlotL.addItem(self.curveFtDes)

    def ExtCheck(self):
        pass

    # Background functions
    def UpdateBias(self):
        self.VDS = float(self.ui.spinBoxBiasVds.value())*0.001
        self.VSB = -float(self.ui.spinBoxBiasVbs.value())*0.001

    def SynMos(self):
        '''Syn MOS from Gm'''
        self.UpdateBias()
        if self.synOppt == 0:
            self.synGmId = float(self.ui.lineEditSynGmId.text())
        else:
            self.synGmId = 2000.0/float(self.ui.lineEditSynVstar.text())
        if self.synSize == 0:
            self.synGm = float(self.ui.lineEditSynGm.text()) * 0.000001
            self.synId = self.synGm / self.synGmId
        else:
            self.synId = float(self.ui.lineEditSynId.text()) * 0.000001
            self.synGm = self.synId * self.synGmId
        self.synVGS, self.synState = self.SearchVGSG( self.tgtCorner, self.synGmId, self.Lchk, 4)
        self.synW =  self.synId * self.W / lp.lookupfz(self.mosDat, self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=self.synVGS)
        self.ui.labelSynW.setText(self.sciPrint(0.000001 * self.synW, 'm'))
        self.ui.labelSynVgs.setText(self.sciPrint(self.synVGS, 'V'))
        self.ui.labelChkId.setText(self.sciPrint(self.synId, 'A'))
        self.ui.labelChkGm.setText(self.sciPrint(self.synGm, 'S/A'))
        self.ChkMos(self.synW, self.synVGS)

    def ChkMos(self, chkW, chkVgs):
        '''Scale the Char of MOS and Change the label'''
        mosScale = chkW / self.W
        chkCgg = mosScale * lp.lookupfz(self.mosDat, self.mosModel, 'CGG', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs)
        self.ui.labelChkCgg.setText(self.sciPrint(chkCgg, 'F'))
        #print ("Cgg : %1.24f" % chkCgg)
        chkFt = 1.0 * lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs)
        self.ui.labelChkFt.setText(self.sciPrint(chkFt, 'Hz'))
        chkRout = 1.0 / ( mosScale * lp.lookupfz(self.mosDat, self.mosModel, 'GDS', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs))
        self.ui.labelChkRout.setText(self.sciPrint(chkRout, 'Ohm'))
        chkAv = 1.0 * lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs)
        self.ui.labelChkAv.setText(self.sciPrint(chkAv, 'V/V'))
        chkVth = 1.0 * lp.lookupfz(self.mosDat, self.mosModel, 'VT', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs)
        self.ui.labelChkVth.setText(self.sciPrint(chkVth, 'V'))
        chkVdsat = 1.0 * lp.lookupfz(self.mosDat, self.mosModel, 'VDSAT', VDS=self.VDS, VSB=self.VSB, L=self.Lchk, VGS=chkVgs)
        self.ui.labelChkVdsat.setText(self.sciPrint(chkVdsat, 'V'))

    def SearchVGSG(self, cornerIndex, tgtGmId, tgtL, absRel):
        vgsStart = 0
        vgsEnd = self.maxVGS
        gmIdSeq = None
        vgsStep= [0.1,0.01,0.001,0.0001]
        vgsLeft= 0
        searchState = 1
        for i in range(absRel):
            vgsSeq = np.arange( vgsEnd, vgsStart, -vgsStep[i])
            gmIdSeq = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=tgtL, VGS=vgsSeq)
            vgsLeft = np.searchsorted( gmIdSeq, tgtGmId, 'left')
            if vgsLeft == vgsSeq.size:
                searchState = 2
                break
            vgsStart = vgsSeq[vgsLeft]
            if vgsLeft == 0:
                searchState = 0
                break
            vgsEnd = vgsSeq[vgsLeft - 1]
        return vgsStart, searchState

    def SearchVGSA(self, tgtAvo, tgtL):
        '''Search VGS for fixed Avo'''
        vgsStart = 0
        vgsEnd = self.maxVGS
        avoSeq = None
        vgsStep= [0.1,0.01,0.001,0.0001]
        vgsLeft= 0
        searchState = 1
        for i in range(4):
            vgsSeq = np.arange( vgsEnd, vgsStart, -vgsStep[i])
            avoSeq = lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=tgtL, VGS=vgsSeq)
            vgsLeft = np.searchsorted( avoSeq, tgtAvo, 'left')
            if vgsLeft == vgsSeq.size:
                searchState = 2
                break
            vgsStart = vgsSeq[vgsLeft]
            if vgsLeft == 0:
                searchState = 0
                break
            vgsEnd = vgsSeq[vgsLeft - 1]
        return vgsStart, searchState

    def SearchVGSF(self, tgtFt, tgtL):
        '''Search VGS for fixed Ft'''
        vgsStart = 0
        vgsEnd = self.maxVGS
        ftSeq = None
        vgsStep= [0.1,0.01,0.001,0.0001]
        vgsLeft= 0
        searchState = 1
        for i in range(4):
            vgsSeq = np.arange( vgsStart, vgsEnd, vgsStep[i])
            ftSeq = lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=tgtL, VGS=vgsSeq)
            vgsLeft = np.searchsorted( ftSeq, tgtFt, 'left')
            if vgsLeft == vgsSeq.size:
                searchState = 2
                break
            vgsEnd = vgsSeq[vgsLeft]
            if vgsLeft == 0:
                searchState = 0
                break
            vgsStart = vgsSeq[vgsLeft - 1]
        return vgsStart, searchState

    def loadMat(self):
        '''Load the MAT File and Set the Voltage as Bias'''
        print ('Load Mat File')
        self.mosDat = h5py.File(self.matFilePath, 'r')
        print ("Loading complete!")
        self.ui.listWidgetL.clear()
        self.ui.listWidgetLRef.clear()
        self.ui.listWidgetLChk.clear()
        self.listL = np.array(self.mosDat['L']).flatten()
        for i in range(len(self.listL)):
            self.ui.listWidgetL.addItem(str(self.listL[i]))
            self.ui.listWidgetLRef.addItem(str(self.listL[i]))
            self.ui.listWidgetLChk.addItem(str(self.listL[i]))
        self.maxVGS, self.stepVGS, self.maxVSB = lp.info(self.mosDat)
        self.listVGS = np.arange(0, self.maxVGS, self.stepVGS)
        self.halfVGS = 0.5 * self.maxVGS
        self.VDS = self.halfVGS
        self.ui.spinBoxBiasVds.setValue(1000.0*self.VDS)
        # TODO Set the VDS
        self.W = self.mosDat['W'][0][0]*self.mosDat['NFING'][0][0]
        print ('Mos Default Width : %2.2f' % self.W)

    def cornerMat(self):
        '''Search & Load all the corner Matlib Data'''
        # Set Corner
        self.tgtCorner = self.listCorner.index(self.matFileInfo[2])
        print ('Corner Set to : %s' % self.listCorner[self.tgtCorner])
        # Search Corner
        for i in range(len(self.listCorner)):
            cornerFileName = self.matFileInfo[0]+'-'+self.matFileInfo[1]+'-'+self.listCorner[i]+'.mat'
            if cornerFileName in self.matFileList:
                print ('%s corner Found' % self.listCorner[i])
                self.avaCorner[i] = 1
                cornerFilePath = self.matDirPath + '/' + cornerFileName
                self.mosCorner[i] = h5py.File(cornerFilePath, 'r')
            else:
                print ('%s corner None' % self.listCorner[i])
                self.avaCorner[i] = 0
                self.mosCorner[i] = None
        # Update Plots
        ## Clear the plots and then add back the indicator
        self.ui.topLPlotVgs.clear()
        self.ui.topRPlotVgs.clear()
        self.ui.botLPlotVgs.clear()
        self.ui.botRPlotVgs.clear()
        self.ui.topLPlotVstar.clear()
        self.ui.topRPlotVstar.clear()
        self.ui.botLPlotVstar.clear()
        self.ui.botRPlotVstar.clear()
        self.ui.topLPlotGmId.clear()
        self.ui.topRPlotGmId.clear()
        self.ui.botLPlotGmId.clear()
        self.ui.botRPlotGmId.clear()
        self.ui.topLPlotId.clear()
        self.ui.topRPlotId.clear()
        self.ui.botLPlotId.clear()
        self.ui.botRPlotId.clear()
        self.ui.topLPlotL.clear()
        self.ui.topRPlotL.clear()
        self.ui.botLPlotL.clear()
        self.ui.botRPlotL.clear()
        self.ui.topLPlotOpt.clear()
        self.ui.topRPlotOpt.clear()
        self.ui.botLPlotOpt.clear()
        self.ui.botRPlotOpt.clear()
        ## Add the VLine
        self.ui.topLPlotVgs.addItem(self.topLVLineVgs, ignoreBounds=True)
        self.ui.topRPlotVgs.addItem(self.topRVLineVgs, ignoreBounds=True)
        self.ui.botLPlotVgs.addItem(self.botLVLineVgs, ignoreBounds=True)
        self.ui.botRPlotVgs.addItem(self.botRVLineVgs, ignoreBounds=True)
        self.ui.topLPlotVstar.addItem(self.topLVLineVstar, ignoreBounds=True)
        self.ui.topRPlotVstar.addItem(self.topRVLineVstar, ignoreBounds=True)
        self.ui.botLPlotVstar.addItem(self.botLVLineVstar, ignoreBounds=True)
        self.ui.botRPlotVstar.addItem(self.botRVLineVstar, ignoreBounds=True)
        self.ui.topLPlotGmId.addItem(self.topLVLineGmId, ignoreBounds=True)
        self.ui.topRPlotGmId.addItem(self.topRVLineGmId, ignoreBounds=True)
        self.ui.botLPlotGmId.addItem(self.botLVLineGmId, ignoreBounds=True)
        self.ui.botRPlotGmId.addItem(self.botRVLineGmId, ignoreBounds=True)
        self.ui.topLPlotId.addItem(self.topLVLineId, ignoreBounds=True)
        self.ui.topRPlotId.addItem(self.topRVLineId, ignoreBounds=True)
        self.ui.botLPlotId.addItem(self.botLVLineId, ignoreBounds=True)
        self.ui.botRPlotId.addItem(self.botRVLineId, ignoreBounds=True)
        # Generate Curve
        self.genCurve()
        self.ui.comboBoxDesignCorner.setCurrentIndex(self.tgtCorner)
        self.changeCorner()
        # Update CheckBox Text
        if self.avaCorner[0] == 0:
            self.ui.checkBoxCornerTT.setText("--")
        else:
            self.ui.checkBoxCornerTT.setText("TT")
            self.ui.checkBoxCornerTT.setCheckState(2)
            self.ui.checkBoxCornerTT.setCheckState(0)
        if self.avaCorner[1] == 0:
            self.ui.checkBoxCornerFF.setText("--")
        else:
            self.ui.checkBoxCornerFF.setText("FF")
            self.ui.checkBoxCornerFF.setCheckState(2)
            self.ui.checkBoxCornerFF.setCheckState(0)
        if self.avaCorner[2] == 0:
            self.ui.checkBoxCornerSS.setText("--")
        else:
            self.ui.checkBoxCornerSS.setText("SS")
            self.ui.checkBoxCornerSS.setCheckState(2)
            self.ui.checkBoxCornerSS.setCheckState(0)
        if self.avaCorner[3] == 0:
            self.ui.checkBoxCornerFS.setText("--")
        else:
            self.ui.checkBoxCornerFS.setText("FS")
            self.ui.checkBoxCornerFS.setCheckState(2)
            self.ui.checkBoxCornerFS.setCheckState(0)
        if self.avaCorner[4] == 0:
            self.ui.checkBoxCornerSF.setText("--")
        else:
            self.ui.checkBoxCornerSF.setText("SF")
            self.ui.checkBoxCornerSF.setCheckState(2)
            self.ui.checkBoxCornerSF.setCheckState(0)

    def changeCorner(self):
        '''Change the Temp Corner'''
        newTgtCorner = self.ui.comboBoxDesignCorner.currentIndex()
        if self.avaCorner[newTgtCorner] == 1:
            # Change Pen Setting
            self.corCurveIdVDes[self.tgtCorner].setPen(self.cornerPen[self.tgtCorner])
            self.corCurveFtVDes[self.tgtCorner].setPen(self.cornerPen[self.tgtCorner])
            self.ui.checkBoxRef.setCheckState(0)
            self.tgtCorner = newTgtCorner
            self.ui.labelLog.setText("Corner Set")
            self.pen = self.linePen[self.tgtCorner]
            self.corCurveIdVDes[self.tgtCorner].setPen(self.linePen[self.tgtCorner])
            self.corCurveFtVDes[self.tgtCorner].setPen(self.linePen[self.tgtCorner])
            self.mosDat = self.mosCorner[self.tgtCorner]
            self.pltCurveUpdate()
            self.LChkVstar()
            self.restCurveOff()
            self.ui.checkBoxRef.setCheckState(2)
        else:
            self.ui.labelLog.setText("Corner Not Found")

    def genCurve(self):
        '''Generate all the curve'''
        self.UpdateBias()
        for i in range(len(self.listCorner)):
            if self.avaCorner[i] == 1:
                # Curve for GmId at des-l and ref-l
                self.gmIdCurve(i)
                print ('GmIdCurve for Corner : ' + self.listCorner[i])
                # Vgs
                self.ui.topLPlotVgs.addItem(self.corCurveIdDDes[i])
                self.ui.topRPlotVgs.addItem(self.corCurveFomDDes[i])
                self.ui.botLPlotVgs.addItem(self.corCurveAvDDes[i])
                self.ui.botRPlotVgs.addItem(self.corCurveFtDDes[i])
                self.ui.topLPlotVgs.addItem(self.corCurveIdDRef[i])
                self.ui.topRPlotVgs.addItem(self.corCurveFomDRef[i])
                self.ui.botLPlotVgs.addItem(self.corCurveAvDRef[i])
                self.ui.botRPlotVgs.addItem(self.corCurveFtDRef[i])
                # Vstar
                self.ui.topLPlotVstar.addItem(self.corCurveIdVDes[i])
                self.ui.topRPlotVstar.addItem(self.corCurveFomVDes[i])
                self.ui.botLPlotVstar.addItem(self.corCurveAvVDes[i])
                self.ui.botRPlotVstar.addItem(self.corCurveFtVDes[i])
                self.ui.topLPlotVstar.addItem(self.corCurveIdVRef[i])
                self.ui.topRPlotVstar.addItem(self.corCurveFomVRef[i])
                self.ui.botLPlotVstar.addItem(self.corCurveAvVRef[i])
                self.ui.botRPlotVstar.addItem(self.corCurveFtVRef[i])
                # GmId
                self.ui.topLPlotGmId.addItem(self.corCurveIdGDes[i])
                self.ui.topRPlotGmId.addItem(self.corCurveFomGDes[i])
                self.ui.botRPlotGmId.addItem(self.corCurveFtGDes[i])
                self.ui.botLPlotGmId.addItem(self.corCurveAvGDes[i])
                self.ui.topLPlotGmId.addItem(self.corCurveIdGRef[i])
                self.ui.topRPlotGmId.addItem(self.corCurveFomGRef[i])
                self.ui.botRPlotGmId.addItem(self.corCurveFtGRef[i])
                self.ui.botLPlotGmId.addItem(self.corCurveAvGRef[i])
                # Id
                self.ui.topLPlotId.addItem(self.corCurveGmIDes[i])
                self.ui.topRPlotId.addItem(self.corCurveFomIDes[i])
                self.ui.botLPlotId.addItem(self.corCurveAvIDes[i])
                self.ui.botRPlotId.addItem(self.corCurveFtIDes[i])
                self.ui.topLPlotId.addItem(self.corCurveGmIRef[i])
                self.ui.topRPlotId.addItem(self.corCurveFomIRef[i])
                self.ui.botLPlotId.addItem(self.corCurveAvIRef[i])
                self.ui.botRPlotId.addItem(self.corCurveFtIRef[i])
            else:
                # Des-L
                self.corCurveIdVDes[i] = None
                self.corCurveFtVDes[i] = None
                self.corCurveAvVDes[i] = None
                self.corCurveFomVDes[i]= None
                self.corCurveIdGDes[i] = None
                self.corCurveFtGDes[i] = None
                self.corCurveAvGDes[i] = None
                self.corCurveFomGDes[i]= None
                self.corCurveGmIDes[i] = None
                self.corCurveFtIDes[i] = None
                self.corCurveAvIDes[i] = None
                self.corCurveFomIDes[i]= None
                # Ref-L
                self.corCurveIdVRef[i] = None
                self.corCurveFtVRef[i] = None
                self.corCurveAvVRef[i] = None
                self.corCurveFomVRef[i]= None
                self.corCurveIdGRef[i] = None
                self.corCurveFtGRef[i] = None
                self.corCurveAvGRef[i] = None
                self.corCurveFomGRef[i]= None
                self.corCurveGmIRef[i] = None
                self.corCurveFtIRef[i] = None
                self.corCurveAvIRef[i] = None
                self.corCurveFomIRef[i]= None

    def pltCurveUpdate(self):
        '''Update the Plot for GmId'''
        # Update the MainCurve
        self.UpdateBias()
        if self.pltCurveIdVDes != None:
            self.ui.topLPlotVgs.removeItem(self.pltCurveIdDDes)
            self.ui.topRPlotVgs.removeItem(self.pltCurveFomDDes)
            self.ui.botLPlotVgs.removeItem(self.pltCurveAvDDes)
            self.ui.botRPlotVgs.removeItem(self.pltCurveFtDDes)
            self.ui.topLPlotVstar.removeItem(self.pltCurveIdVDes)
            self.ui.topRPlotVstar.removeItem(self.pltCurveFomVDes)
            self.ui.botLPlotVstar.removeItem(self.pltCurveAvVDes)
            self.ui.botRPlotVstar.removeItem(self.pltCurveFtVDes)
            self.ui.topLPlotGmId.removeItem(self.pltCurveIdGDes)
            self.ui.topRPlotGmId.removeItem(self.pltCurveFomGDes)
            self.ui.botLPlotGmId.removeItem(self.pltCurveAvGDes)
            self.ui.botRPlotGmId.removeItem(self.pltCurveFtGDes)
            self.ui.topLPlotId.removeItem(self.pltCurveGmIDes)
            self.ui.topRPlotId.removeItem(self.pltCurveFomIDes)
            self.ui.botLPlotId.removeItem(self.pltCurveAvIDes)
            self.ui.botRPlotId.removeItem(self.pltCurveFtIDes)
        self.listId = lp.lookupfz(self.mosDat, self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        self.listAv = lp.lookupfz(self.mosDat, self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        self.listFt = lp.lookupfz(self.mosDat, self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        self.listGmId = lp.lookupfz(self.mosDat, self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        self.listVdsat = lp.lookupfz(self.mosDat, self.mosModel, 'VDSAT', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        # Fig Line Extract
        ## Vstar Line
        self.listVstar = 2*np.reciprocal(self.listGmId)
        self.csIdV = CubicSpline( self.listVstar, self.listId)
        self.csFtV = CubicSpline( self.listVstar, self.listFt)
        self.csAvV = CubicSpline( self.listVstar, self.listAv)
        self.csVgV = CubicSpline( self.listVstar, self.listVGS)
        self.csVdsatV = CubicSpline(self.listVstar, self.listVdsat)
        ## GmId Line
        self.listGmIdG = np.flip(self.listGmId, 0)
        self.listIdG = np.flip(self.listId, 0)
        self.listFtG = np.flip(self.listFt, 0)
        self.listAvG = np.flip(self.listAv, 0)
        self.listVgG = np.flip(self.listVGS, 0)
        self.listVdsatG = np.flip(self.listVdsat, 0)
        self.csIdG = CubicSpline( self.listGmIdG, self.listIdG)
        self.csFtG = CubicSpline( self.listGmIdG, self.listFtG)
        self.csAvG = CubicSpline( self.listGmIdG, self.listAvG)
        self.csVgG = CubicSpline( self.listGmIdG, self.listVgG)
        self.csVdsatG = CubicSpline( self.listGmIdG, self.listVdsatG)
        ## Id Line
        self.listIdI = np.log10(self.listId)
        self.csGmI = CubicSpline( self.listIdI, self.listGmId)
        self.csFtI = CubicSpline( self.listIdI, self.listFt)
        self.csAvI = CubicSpline( self.listIdI, self.listAv)
        self.csVgI = CubicSpline( self.listIdI, self.listVGS)
        self.csVdsatI = CubicSpline( self.listIdI, self.listVdsat)
        # Vgs Figure
        self.pltCurveIdDDes = pg.PlotDataItem( self.listVGS, self.listId, pen = self.pen, clear=True)
        self.pltCurveFtDDes = pg.PlotDataItem( self.listVGS, self.listFt, pen = self.pen, clear=True)
        self.pltCurveAvDDes = pg.PlotDataItem( self.listVGS, self.listAv, pen = self.pen, clear=True)
        self.pltCurveFomDDes= pg.PlotDataItem( self.listVGS, self.listFt * self.listGmId, pen = self.pen, clear=True)
        self.ui.topLPlotVgs.addItem(self.pltCurveIdDDes)
        self.ui.topRPlotVgs.addItem(self.pltCurveFomDDes)
        self.ui.botLPlotVgs.addItem(self.pltCurveAvDDes)
        self.ui.botRPlotVgs.addItem(self.pltCurveFtDDes)
        # Vstar Figure
        #self.pltVstar = np.arange( self.listVstar.min(), self.listVstar.max(), 0.001)
        self.pltVstar = np.arange( self.minVstar, self.maxVstar, 0.0005)
        self.pltIdV = self.csIdV(self.pltVstar)
        self.pltFtV = self.csFtV(self.pltVstar)
        self.pltAvV = self.csAvV(self.pltVstar)
        self.pltVgV = self.csVgV(self.pltVstar)
        self.pltVdsatV = self.csVdsatV(self.pltVstar)
        self.pltCurveIdVDes = pg.PlotDataItem( self.pltVstar, self.pltIdV, pen = self.pen, clear=True)
        self.pltCurveFtVDes = pg.PlotDataItem( self.pltVstar, self.pltFtV, pen = self.pen, clear=True)
        self.pltCurveAvVDes = pg.PlotDataItem( self.pltVstar, self.pltAvV, pen = self.pen, clear=True)
        self.pltCurveFomVDes= pg.PlotDataItem( self.pltVstar, 2.0*self.pltFtV/self.pltVstar, pen = self.pen, clear=True)
        self.ui.topLPlotVstar.addItem(self.pltCurveIdVDes)
        self.ui.topRPlotVstar.addItem(self.pltCurveFomVDes)
        self.ui.botLPlotVstar.addItem(self.pltCurveAvVDes)
        self.ui.botRPlotVstar.addItem(self.pltCurveFtVDes)
        # GmId Figure
        #self.pltGmId = np.arange( self.listGmId.min(), self.listGmId.max(), 0.01)
        self.pltGmId = np.arange( self.minGmId, self.maxGmId, 0.01)
        self.pltIdG = self.csIdG(self.pltGmId)
        self.pltFtG = self.csFtG(self.pltGmId)
        self.pltAvG = self.csAvG(self.pltGmId)
        self.pltVgG = self.csVgG(self.pltGmId)
        self.pltVdsatG = self.csVdsatG(self.pltGmId)
        self.pltCurveIdGDes = pg.PlotDataItem( self.pltGmId, self.pltIdG, pen = self.pen, clear=True)
        self.pltCurveFtGDes = pg.PlotDataItem( self.pltGmId, self.pltFtG, pen = self.pen, clear=True)
        self.pltCurveAvGDes = pg.PlotDataItem( self.pltGmId, self.pltAvG, pen = self.pen, clear=True)
        self.pltCurveFomGDes= pg.PlotDataItem( self.pltGmId, self.pltGmId * self.pltFtG, pen = self.pen, clear=True)
        self.ui.topLPlotGmId.addItem(self.pltCurveIdGDes)
        self.ui.topRPlotGmId.addItem(self.pltCurveFomGDes)
        self.ui.botLPlotGmId.addItem(self.pltCurveAvGDes)
        self.ui.botRPlotGmId.addItem(self.pltCurveFtGDes)
        # Id Figure
        self.pltIdI = np.arange( self.listIdI.min(), self.listIdI.max(), 0.05)
        self.pltGmI = self.csGmI( self.pltIdI)
        self.pltFtI = self.csFtI( self.pltIdI)
        self.pltAvI = self.csAvI( self.pltIdI)
        self.pltVgI = self.csVgI( self.pltIdI)
        self.pltVdsatI = self.csVdsatI( self.pltIdI)
        self.pltCurveGmIDes = pg.PlotDataItem( self.pltIdI, self.pltGmI, pen = self.pen, clear=True)
        self.pltCurveFtIDes = pg.PlotDataItem( self.pltIdI, self.pltFtI, pen = self.pen, clear=True)
        self.pltCurveFomIDes = pg.PlotDataItem( self.pltIdI, self.pltFtI*self.pltGmI, pen = self.pen, clear=True)
        self.pltCurveAvIDes = pg.PlotDataItem( self.pltIdI, self.pltAvI, pen = self.pen, clear=True)
        self.ui.topLPlotId.addItem(self.pltCurveGmIDes)
        self.ui.topRPlotId.addItem(self.pltCurveFomIDes)
        self.ui.botLPlotId.addItem(self.pltCurveAvIDes)
        self.ui.botRPlotId.addItem(self.pltCurveFtIDes)
        # Vth Figure
        #self.curveVth = pg.PlotDataItem( 1000.0*self.listLChk, self.listVthL, pen = self.pen, symbolBrush=(255,0,0), symbolPen='w', clear=True)
        #self.ui.topLPlotL.addItem(self.curveVth)
        # Set Flag
        self.curveReady = 1

    def gateLCurve(self, cornerIndex):
        '''Generate the Vth, Avo, Ft as a function of L for the mosdat'''
        # Reset the flags for the curve
        self.w0LReady[cornerIndex] = 0
        self.w1LReady[cornerIndex] = 0
        self.m0LReady[cornerIndex] = 0
        self.m1LReady[cornerIndex] = 0
        self.s0LReady[cornerIndex] = 0
        self.s1LReady[cornerIndex] = 0
        self.UpdateBias()
        listVth = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'VT', VDS=self.halfVGS, VSB=0, L=self.listLChk, VGS=self.halfVGS)
        self.curveVthCorner[cornerIndex] = pg.PlotDataItem( 1000*self.listLChk, listVth, pen = self.cornerPen[cornerIndex], symbolBrush = (255,0,0), symbolPen = 'w', symbol = 'o', clear=True)
        # Generate Curve for WI, SI, MI
        w1Vgs = 0.0
        w1State = 0
        w1PltAv = []
        w1PltFt = []
        w1PltL = []
        s0Vgs = 0.0
        s0State = 0
        s0PltAv = []
        s0PltFt = []
        s0PltL = []
        for swL in self.listLChk:
            #print ('Curve for Av + Ft @ L = %1.3f in %s corner' % (swL, self.listCorner[cornerIndex]))
            w1Vgs, w1State = self.SearchVGSG( cornerIndex, const.GMIDLW1, swL, 3)
            s0Vgs, s0State = self.SearchVGSG( cornerIndex, const.GMIDLS0, swL, 3)
            if w1State == 1:
                self.w1LReady[cornerIndex] = 1
                w1PltL.append(1000*swL)
                w1PltAv.append(lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=w1Vgs))
                w1PltFt.append(lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=w1Vgs))
            if s0State == 1:
                self.s0LReady[cornerIndex] = 1
                s0PltL.append(1000*swL)
                s0PltAv.append(lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=s0Vgs))
                s0PltFt.append(lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=swL, VGS=s0Vgs))
        # Add Curve
        if (self.w1LReady[cornerIndex] == 1):
            self.curveAvW1Corner[cornerIndex] = pg.PlotDataItem( w1PltL, w1PltAv, symbolBrush=const.COLORW1, symbolPen = 'w', symbol = const.SYMW1, name = const.NAMEW1, pen = self.cornerPen[cornerIndex], clear=True)
            self.curveFtW1Corner[cornerIndex] = pg.PlotDataItem( w1PltL, w1PltFt, symbolBrush=const.COLORW1, symbolPen = 'w', symbol = const.SYMW1, name = const.NAMEW1, pen = self.cornerPen[cornerIndex], clear=True)
        if (self.s0LReady[cornerIndex] == 1):
            self.curveAvS0Corner[cornerIndex] = pg.PlotDataItem( s0PltL, s0PltAv, symbolBrush=const.COLORS0, symbolPen = 'w', symbol = const.SYMS0, name = const.NAMES0, pen = self.cornerPen[cornerIndex], clear=True)
            self.curveFtS0Corner[cornerIndex] = pg.PlotDataItem( s0PltL, s0PltFt, symbolBrush=const.COLORS0, symbolPen = 'w', symbol = const.SYMS0, name = const.NAMES0, pen = self.cornerPen[cornerIndex], clear=True)

    def gmIdCurve(self, cornerIndex):
        # All Curve For Des-L
        listId = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        listGmOverId = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        listFt = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        listAv = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.listVGS)
        ## Vgs Curve
        self.corCurveIdDDes[cornerIndex] = pg.PlotDataItem( self.listVGS, listId, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFtDDes[cornerIndex] = pg.PlotDataItem( self.listVGS, listFt, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveAvDDes[cornerIndex] = pg.PlotDataItem( self.listVGS, listAv, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFomDDes[cornerIndex]= pg.PlotDataItem( self.listVGS, listFt * listGmOverId, pen = self.cornerPen[cornerIndex], clear=True)
        ## VstarCurve
        listVstar = 2*np.reciprocal(listGmOverId)
        csIdV = CubicSpline( listVstar, listId)
        csFtV = CubicSpline( listVstar, listFt)
        csAvV = CubicSpline( listVstar, listAv)
        #pltVstar = np.arange( listVstar.min(), listVstar.max(), 0.001)
        pltVstar = np.arange( self.minVstar, self.maxVstar, 0.0005)
        pltIdV = csIdV(pltVstar)
        pltFtV = csFtV(pltVstar)
        pltAvV = csAvV(pltVstar)
        self.corCurveIdVDes[cornerIndex] = pg.PlotDataItem( pltVstar, pltIdV, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFtVDes[cornerIndex] = pg.PlotDataItem( pltVstar, pltFtV, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveAvVDes[cornerIndex] = pg.PlotDataItem( pltVstar, pltAvV, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFomVDes[cornerIndex]= pg.PlotDataItem( pltVstar, 2.0 * pltFtV / pltVstar, pen = self.cornerPen[cornerIndex], clear=True)
        ## GmOverId Curve
        listGmId = np.flip(listGmOverId, 0)
        listIdG = np.flip(listId, 0)
        listFtG = np.flip(listFt, 0)
        listAvG = np.flip(listAv, 0)
        csIdG = CubicSpline( listGmId, listIdG)
        csFtG = CubicSpline( listGmId, listFtG)
        csAvG = CubicSpline( listGmId, listAvG)
        pltGmId = np.arange( self.minGmId, self.maxGmId, 0.01)
        pltIdG = csIdG(pltGmId)
        pltFtG = csFtG(pltGmId)
        pltAvG = csAvG(pltGmId)
        self.corCurveIdGDes[cornerIndex] = pg.PlotDataItem( pltGmId, pltIdG, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFtGDes[cornerIndex] = pg.PlotDataItem( pltGmId, pltFtG, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveAvGDes[cornerIndex] = pg.PlotDataItem( pltGmId, pltAvG, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFomGDes[cornerIndex]= pg.PlotDataItem( pltGmId, pltGmId * pltFtG, pen = self.cornerPen[cornerIndex], clear=True)
        ## Id Curve
        listIdI = np.log10(listId)
        csGmI = CubicSpline( listIdI, listGmOverId)
        csFtI = CubicSpline( listIdI, listFt)
        csAvI = CubicSpline( listIdI, listAv)
        pltIdI = np.arange( listIdI.min(), listIdI.max(), 0.05)
        pltGmI = csGmI(pltIdI)
        pltFtI = csFtI(pltIdI)
        pltAvI = csAvI(pltIdI)
        self.corCurveGmIDes[cornerIndex] = pg.PlotDataItem( pltIdI, pltGmI, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFtIDes[cornerIndex] = pg.PlotDataItem( pltIdI, pltFtI, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveAvIDes[cornerIndex] = pg.PlotDataItem( pltIdI, pltAvI, pen = self.cornerPen[cornerIndex], clear=True)
        self.corCurveFomIDes[cornerIndex] = pg.PlotDataItem( pltIdI, pltFtI*pltGmI, pen = self.cornerPen[cornerIndex], clear=True)
        # All Curve for Ref-L
        listId = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'ID', VDS=self.VDS, VSB=self.VSB, L=self.Lref, VGS=self.listVGS)
        listGmOverId = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.Lref, VGS=self.listVGS)
        listFt = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'FUG', VDS=self.VDS, VSB=self.VSB, L=self.Lref, VGS=self.listVGS)
        listAv = lp.lookupfz(self.mosCorner[cornerIndex], self.mosModel, 'SELF_GAIN', VDS=self.VDS, VSB=self.VSB, L=self.Lref, VGS=self.listVGS)
        ## Vgs Curve
        self.corCurveIdDRef[cornerIndex] = pg.PlotDataItem( self.listVGS, listId, pen = self.refPen, clear=True)
        self.corCurveFtDRef[cornerIndex] = pg.PlotDataItem( self.listVGS, listFt, pen = self.refPen, clear=True)
        self.corCurveAvDRef[cornerIndex] = pg.PlotDataItem( self.listVGS, listAv, pen = self.refPen, clear=True)
        self.corCurveFomDRef[cornerIndex]= pg.PlotDataItem( self.listVGS, listFt * listGmOverId, pen = self.refPen, clear=True)
        ## VstarCurve
        listVstar = 2*np.reciprocal(listGmOverId)
        csIdV = CubicSpline( listVstar, listId)
        csFtV = CubicSpline( listVstar, listFt)
        csAvV = CubicSpline( listVstar, listAv)
        pltIdV = csIdV(pltVstar)
        pltFtV = csFtV(pltVstar)
        pltAvV = csAvV(pltVstar)
        self.corCurveIdVRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltIdV, pen = self.refPen, clear=True)
        self.corCurveFtVRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltFtV, pen = self.refPen, clear=True)
        self.corCurveAvVRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltAvV, pen = self.refPen, clear=True)
        self.corCurveFomVRef[cornerIndex]= pg.PlotDataItem( pltVstar, 2.0 * pltFtV / pltVstar, pen = self.refPen, clear=True)
        ## GmOverID Curve
        listGmId = np.flip(listGmOverId, 0)
        listIdG = np.flip(listId, 0)
        listFtG = np.flip(listFt, 0)
        listAvG = np.flip(listAv, 0)
        csIdG = CubicSpline( listGmId, listIdG)
        csFtG = CubicSpline( listGmId, listFtG)
        csAvG = CubicSpline( listGmId, listAvG)
        pltIdG = csIdG(pltGmId)
        pltFtG = csFtG(pltGmId)
        pltAvG = csAvG(pltGmId)
        self.corCurveIdGRef[cornerIndex] = pg.PlotDataItem( pltGmId, pltIdG, pen = self.refPen, clear=True)
        self.corCurveFtGRef[cornerIndex] = pg.PlotDataItem( pltGmId, pltFtG, pen = self.refPen, clear=True)
        self.corCurveAvGRef[cornerIndex] = pg.PlotDataItem( pltGmId, pltAvG, pen = self.refPen, clear=True)
        self.corCurveFomGRef[cornerIndex]= pg.PlotDataItem( pltGmId, pltGmId * pltFtG, pen = self.refPen, clear=True)
        ## Id Curve
        listIdI = np.log10(listId)
        csGmI = CubicSpline( listIdI, listGmOverId)
        csFtI = CubicSpline( listIdI, listFt)
        csAvI = CubicSpline( listIdI, listAv)
        pltIdI = np.arange( listIdI.min(), listIdI.max(), 0.05)
        pltGmI = csGmI(pltIdI)
        pltFtI = csFtI(pltIdI)
        pltAvI = csAvI(pltIdI)
        self.corCurveGmIRef[cornerIndex] = pg.PlotDataItem( pltIdI, pltGmI, pen = self.refPen, clear=True)
        self.corCurveFtIRef[cornerIndex] = pg.PlotDataItem( pltIdI, pltFtI, pen = self.refPen, clear=True)
        self.corCurveAvIRef[cornerIndex] = pg.PlotDataItem( pltIdI, pltAvI, pen = self.refPen, clear=True)
        self.corCurveFomIRef[cornerIndex]= pg.PlotDataItem(pltIdI, pltFtI*pltGmI, pen = self.refPen, clear=True)

    def visibleRef(self, curveState):
        ''' TurnOff the Ref Curve'''
        if(self.refLSet == 1):
            self.corCurveIdVRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFtVRef[self.tgtCorner].setVisible(curveState)
            self.corCurveAvVRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFomVRef[self.tgtCorner].setVisible(curveState)
            self.corCurveIdGRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFtGRef[self.tgtCorner].setVisible(curveState)
            self.corCurveAvGRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFomGRef[self.tgtCorner].setVisible(curveState)
            self.corCurveGmIRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFtIRef[self.tgtCorner].setVisible(curveState)
            self.corCurveAvIRef[self.tgtCorner].setVisible(curveState)
            self.corCurveFomIRef[self.tgtCorner].setVisible(curveState)

    def visibleAllRef(self, curveState):
        ''' TurnOff all the Ref Curve'''
        if(self.refLSet == 1):
            # Ref Curve is Generated
            for i in range(len(self.listCorner)):
                if self.avaCorner[i] == 1:
                    self.corCurveIdVRef[i].setVisible(curveState)
                    self.corCurveFtVRef[i].setVisible(curveState)
                    self.corCurveAvVRef[i].setVisible(curveState)
                    self.corCurveFomVRef[i].setVisible(curveState)
                    self.corCurveIdGRef[i].setVisible(curveState)
                    self.corCurveFtGRef[i].setVisible(curveState)
                    self.corCurveAvGRef[i].setVisible(curveState)
                    self.corCurveFomGRef[i].setVisible(curveState)
                    self.corCurveGmIRef[i].setVisible(curveState)
                    self.corCurveFtIRef[i].setVisible(curveState)
                    self.corCurveAvIRef[i].setVisible(curveState)
                    self.corCurveFomIRef[i].setVisible(curveState)

    def visibleCorCurve(self, curveIndex, curveState):
        self.visCorner[curveIndex] = curveState
        self.corCurveIdVDes[curveIndex].setVisible(curveState)
        self.corCurveFtVDes[curveIndex].setVisible(curveState)
        self.corCurveAvVDes[curveIndex].setVisible(curveState)
        self.corCurveFomVDes[curveIndex].setVisible(curveState)
        self.corCurveIdGDes[curveIndex].setVisible(curveState)
        self.corCurveFtGDes[curveIndex].setVisible(curveState)
        self.corCurveAvGDes[curveIndex].setVisible(curveState)
        self.corCurveFomGDes[curveIndex].setVisible(curveState)
        self.corCurveGmIDes[curveIndex].setVisible(curveState)
        self.corCurveFtIDes[curveIndex].setVisible(curveState)
        self.corCurveAvIDes[curveIndex].setVisible(curveState)
        self.corCurveFomIDes[curveIndex].setVisible(curveState)

    def visibleLCurve(self, invIndex, curveState):
        if invIndex == 0:
            self.curveAvW1Corner[self.tgtCorner].setVisible(curveState)
            self.curveFtW1Corner[self.tgtCorner].setVisible(curveState)
        else:
            self.curveAvS0Corner[self.tgtCorner].setVisible(curveState)
            self.curveFtS0Corner[self.tgtCorner].setVisible(curveState)

    def topMouseMovedVgs(self, evt):
        mousePoint = self.ui.topLPlotVgs.plotItem.vb.mapSceneToView(evt)
        self.topLVLineVgs.setPos(mousePoint.x())
        self.topRVLineVgs.setPos(mousePoint.x())
        self.botLVLineVgs.setPos(mousePoint.x())
        self.botRVLineVgs.setPos(mousePoint.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.listVGS, mousePoint.x(), side="left")
            if index > 0 and index < len(self.listVGS):
                self.ui.labelId.setText(self.sciPrint(self.listId[index], 'A'))
                self.ui.labelFt.setText(self.sciPrint(self.listFt[index], 'Hz'))
                self.ui.labelVgs.setText(self.sciPrint(self.listVGS[index], 'V'))
                self.ui.labelVdsat.setText(self.sciPrint(self.listVdsat[index], 'V'))
                self.ui.labelGain.setText(self.sciPrint(self.listAv[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((self.listFt[index]*self.listGmId[index]),'Hz/V'))
                # TODO Fix the Error
                self.ui.labelVstar.setText(self.sciPrint(2.0/self.listGmId[index], 'V'))
                self.ui.labelGmId.setText(self.sciPrint(self.listGmId[index], '1/V'))
                #self.ui.labelGmId.setText('---')
                #self.ui.labelVstar.setText('---')
            else:
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelVgs.setText('---')
                self.ui.labelVdsat.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')
                self.ui.labelGain.setText('---')

    def topMouseMovedVstar(self, evt):
        '''Read out the number at the point'''
        mousePoint = self.ui.topLPlotVstar.plotItem.vb.mapSceneToView(evt)
        self.topLVLineVstar.setPos(mousePoint.x())
        self.topRVLineVstar.setPos(mousePoint.x())
        self.botLVLineVstar.setPos(mousePoint.x())
        self.botRVLineVstar.setPos(mousePoint.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.pltVstar, mousePoint.x(), side="left")
            if index > 0 and index < len(self.pltVstar):
                self.ui.labelId.setText(self.sciPrint(self.pltIdV[index], 'A'))
                self.ui.labelVstar.setText(self.sciPrint(self.pltVstar[index], 'V'))
                self.ui.labelGmId.setText(self.sciPrint((2.0/self.pltVstar[index]), '1/V'))
                self.ui.labelFt.setText(self.sciPrint(self.pltFtV[index], 'Hz'))
                self.ui.labelVgs.setText(self.sciPrint(self.pltVgV[index], 'V'))
                self.ui.labelVdsat.setText(self.sciPrint(self.pltVdsatV[index], 'V'))
                self.ui.labelGain.setText(self.sciPrint(self.pltAvV[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((2.0*self.pltFtV[index]/self.pltVstar[index]),'Hz/V'))
            else:
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelVgs.setText('---')
                self.ui.labelVdsat.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')
                self.ui.labelGain.setText('---')

    def topMouseMovedGmId(self, evt):
        '''Read out the number at the point'''
        mousePointG = self.ui.topLPlotGmId.plotItem.vb.mapSceneToView(evt)
        self.topLVLineGmId.setPos(mousePointG.x())
        self.topRVLineGmId.setPos(mousePointG.x())
        self.botRVLineGmId.setPos(mousePointG.x())
        self.botLVLineGmId.setPos(mousePointG.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.pltGmId, mousePointG.x(), side="left")
            if index > 0 and index < len(self.pltGmId):
                self.ui.labelId.setText(self.sciPrint(self.pltIdG[index], 'A'))
                self.ui.labelVstar.setText(self.sciPrint((2.0/self.pltGmId[index]), 'V'))
                self.ui.labelGmId.setText(self.sciPrint(self.pltGmId[index], '1/V'))
                self.ui.labelFt.setText(self.sciPrint(self.pltFtG[index], 'Hz'))
                self.ui.labelVgs.setText(self.sciPrint(self.pltVgG[index], 'V'))
                self.ui.labelVdsat.setText(self.sciPrint(self.pltVdsatG[index], 'V'))
                self.ui.labelGain.setText(self.sciPrint(self.pltAvG[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((self.pltFtG[index]*self.pltGmId[index]),'Hz/V'))
            else:
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelVgs.setText('---')
                self.ui.labelVdsat.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')
                self.ui.labelGain.setText('---')

    def topMouseMovedId(self, evt):
        '''Read out the number at the point'''
        mousePointI = self.ui.topLPlotId.plotItem.vb.mapSceneToView(evt)
        self.topLVLineId.setPos(mousePointI.x())
        self.topRVLineId.setPos(mousePointI.x())
        self.botRVLineId.setPos(mousePointI.x())
        self.botLVLineId.setPos(mousePointI.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.pltIdI, mousePointI.x(), side="left")
            if index > 0 and index < len(self.pltIdI):
                self.ui.labelId.setText(self.sciPrint( (10**self.pltIdI[index]), 'A'))
                self.ui.labelVstar.setText(self.sciPrint((2.0/self.pltGmI[index]), 'V'))
                self.ui.labelGmId.setText(self.sciPrint(self.pltGmI[index], '1/V'))
                self.ui.labelFt.setText(self.sciPrint(self.pltFtI[index], 'Hz'))
                self.ui.labelVgs.setText(self.sciPrint(self.pltVgI[index], 'V'))
                self.ui.labelVdsat.setText(self.sciPrint(self.pltVdsatI[index], 'V'))
                self.ui.labelGain.setText(self.sciPrint(self.pltAvI[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((self.pltFtI[index]*self.pltGmI[index]),'Hz/V'))
            else:
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelVgs.setText('---')
                self.ui.labelVdsat.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')
                self.ui.labelGain.setText('---')

    def sciPrint( self, rawNum, unit):
        '''Print the rawNum with autoscale'''
        shiftNum = (decimal.Decimal(str(rawNum)) * decimal.Decimal('1E33')).normalize()
        preNum, scaleNum= shiftNum.to_eng_string().split('E')
        quanNum = decimal.Decimal(preNum).quantize(decimal.Decimal('.001'))
        scaleChar = const.UNIT_PREFIX[int(scaleNum)//3]
        return str(quanNum) + " " + scaleChar + unit

    def closeEvent( self, event):
        event.accept()

# Part 3 GUI Excute
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    form = gmIdGUIWindow()
    form.show()
    app.exec_()
