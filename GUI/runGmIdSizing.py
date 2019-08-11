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
from gmIdSizingGuiBasic import Ui_GmIdMainWindow

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
        # Connect buttons and checkBoxes
        self.configBondKeys()
        # Set the plot
        self.configPlot()

    def configBondKeys(self):
        ''' connect GUI elements to corresponding functions'''
        #checkBox.stateChanged.connect()
        self.ui.checkBoxCornerTT.stateChanged.connect(self.PlotCornerTT)
        self.ui.checkBoxCornerFF.stateChanged.connect(self.PlotCornerFF)
        self.ui.checkBoxCornerSS.stateChanged.connect(self.PlotCornerSS)
        self.ui.checkBoxCornerFS.stateChanged.connect(self.PlotCornerFS)
        self.ui.checkBoxCornerSF.stateChanged.connect(self.PlotCornerSF)
        self.ui.checkBoxRef.stateChanged.connect(self.PlotRef)
        #pushButton.clicked.connect()
        self.ui.pushButtonMosDirSel.clicked.connect(self.DirSel)
        self.ui.pushButtonMosMatSet.clicked.connect(self.MosMatSet)
        self.ui.pushButtonGateLSet.clicked.connect(self.GateLSet)
        self.ui.pushButtonGateLRef.clicked.connect(self.GateLRef)
        self.ui.pushButtonPlot.clicked.connect(self.PlotUpdate)
        self.ui.pushButtonSynGmId.clicked.connect(self.SynGmId)
        self.ui.pushButtonSynVstar.clicked.connect(self.SynVstar)
        self.ui.pushButtonFuEst.clicked.connect(self.FuEst)
        self.ui.pushButtonExtCheck.clicked.connect(self.ExtCheck)
        self.ui.pushButtonCal.clicked.connect(self.CalMos)
        #comboBox.currentIndexChanged.connect()
        self.ui.comboBoxDesignCorner.currentIndexChanged.connect(self.changeCorner)

    def configPlot(self):
        # vstar as x axis
        self.ui.topPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.topPlotVstar.plotItem.setTitle('Fig.1 Id vs Vstar')
        self.ui.topPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.topPlotVstar.plotItem.setLabel('left','Id', units = 'A')
        self.ui.topPlotVstar.plotItem.setLogMode(False, True)
        self.ui.midPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.midPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.midPlotVstar.plotItem.setTitle('Fig.2 Avo vs Vstar')
        self.ui.midPlotVstar.plotItem.setLabel('left','Avo')
        self.ui.botPlotVstar.plotItem.showGrid(True, True, 0.7)
        self.ui.botPlotVstar.plotItem.setLabel('bottom', 'Vstar', units = 'V')
        self.ui.botPlotVstar.plotItem.setTitle('Fig.3 Ft vs Vstar')
        self.ui.botPlotVstar.plotItem.setLabel('left','Ft', units = 'Hz')
        # id as x axis
        self.ui.topPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.topPlotId.plotItem.setTitle('Fig.1 Gm/Id vs Id')
        self.ui.topPlotId.plotItem.setLabel('bottom', 'Id', units = 'A')
        self.ui.topPlotId.plotItem.setLabel('left','Gm/Id', units = 'S/A')
        self.ui.midPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.midPlotId.plotItem.setLabel('bottom', 'Id', units = 'A')
        self.ui.midPlotId.plotItem.setTitle('Fig.2 Avo vs Id')
        self.ui.midPlotId.plotItem.setLabel('left','Avo')
        self.ui.botPlotId.plotItem.showGrid(True, True, 0.7)
        self.ui.botPlotId.plotItem.setLabel('bottom', 'Id', units = 'A')
        self.ui.botPlotId.plotItem.setTitle('Fig.3 Ft*Gm/Id vs Id')
        self.ui.botPlotId.plotItem.setLabel('left','Ft*Gm/Id', units = 'Hz/V')
        # gmId as x axis
        self.ui.topPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.topPlotGmId.plotItem.setTitle('Fig.1 Id vs GmId')
        self.ui.topPlotGmId.plotItem.setLabel('bottom', 'GmId', units = 'V')
        self.ui.topPlotGmId.plotItem.setLabel('left','Id', units = 'A')
        self.ui.midPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.midPlotGmId.plotItem.setLabel('bottom', 'GmId', units = 'V')
        self.ui.midPlotGmId.plotItem.setTitle('Fig.2 Avo vs GmId')
        self.ui.midPlotGmId.plotItem.setLabel('left','Avo')
        self.ui.botPlotGmId.plotItem.showGrid(True, True, 0.7)
        self.ui.botPlotGmId.plotItem.setLabel('bottom', 'GmId', units = 'V')
        self.ui.botPlotGmId.plotItem.setTitle('Fig.3 Ft vs GmId')
        self.ui.botPlotGmId.plotItem.setLabel('left','Ft', units = 'Hz')
        # L as x axis
        self.ui.topLPlotL.plotItem.showGrid(True, True, 0.7)
        self.ui.topLPlotL.plotItem.setTitle('Fig.1 Vth vs L')
        self.ui.topLPlotL.plotItem.setLabel('bottom', 'L', units = 'um')
        self.ui.topLPlotL.plotItem.setLabel('left', 'Vth', units = 'V')
        # Pen & Line
        self.redLinePen = pg.mkPen('r', width=1.5, style=QtCore.Qt.DashLine)
        self.yellowLinePen = pg.mkPen('y', width=1.5, style=QtCore.Qt.DashLine)
        self.blueLinePen = pg.mkPen('b', width=1.5, style=QtCore.Qt.DashLine)
        self.dashPen = pg.mkPen('r', width=1.5, style=QtCore.Qt.DashLine)
        self.topVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.midVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.botVLineVstar = pg.InfiniteLine(angle=90, pen = self.redLinePen, movable=False)
        self.topVLineId = pg.InfiniteLine(angle=90, pen = self.yellowLinePen, movable=False)
        self.midVLineId = pg.InfiniteLine(angle=90, pen = self.yellowLinePen, movable=False)
        self.botVLineId = pg.InfiniteLine(angle=90, pen = self.yellowLinePen, movable=False)
        self.topVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.midVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.botVLineGmId = pg.InfiniteLine(angle=90, pen = self.blueLinePen, movable=False)
        self.topHLineVstar = pg.InfiniteLine(angle=0, pen = self.redLinePen, movable=False)
        self.topHLineGmId = pg.InfiniteLine(angle=0, pen = self.blueLinePen, movable=False)
        self.ui.topPlotVstar.addItem(self.topVLineVstar, ignoreBounds=True)
        self.ui.midPlotVstar.addItem(self.midVLineVstar, ignoreBounds=True)
        self.ui.botPlotVstar.addItem(self.botVLineVstar, ignoreBounds=True)
        self.ui.topPlotVstar.addItem(self.topHLineVstar, ignoreBounds=True)
        self.ui.topPlotGmId.addItem(self.topVLineGmId, ignoreBounds=True)
        self.ui.midPlotGmId.addItem(self.midVLineGmId, ignoreBounds=True)
        self.ui.botPlotGmId.addItem(self.botVLineGmId, ignoreBounds=True)
        self.ui.topPlotGmId.addItem(self.topHLineGmId, ignoreBounds=True)
        #self.arrowFt = pg.ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=20, tailLen=None, pen={'color': 'w', 'width': 3})
        #self.arrowAvo = pg.ArrowItem(angle=90, tipAngle=30, baseAngle=20, headLen=20, tailLen=None, pen={'color': 'w', 'width': 3})
        #self.arrowFt.setPos(0,0)
        #self.arrowAvo.setPos(0,0)
        #self.ui.botPlotVstar.addItem(self.arrowFt)
        #self.ui.midPlotVstar.addItem(self.arrowAvo)
        self.ui.topPlotVstar.scene().sigMouseMoved.connect(self.topMouseMovedVstar)
        self.ui.topPlotGmId.scene().sigMouseMoved.connect(self.topMouseMovedGmId)

    def configDataLib(self):
        # MOS Transistor
        self.L = 0.18
        self.Lref = 0.18
        # MOS Transistor
        self.W = 10.0
        self.GmId = 10.0
        self.Gm = 10.0
        self.Id = 1.0
        self.VDS = 0.9
        self.VSB = 0.1
        # Calculation MOS Transistor
        self.synW = 10.0
        self.synVGS = 0.9
        self.synGmId = 5.0
        self.synGm = 5.0
        self.synId = 1.0
        # Calculation MOS Transistor
        self.calW = 10.0
        self.calGmId = 5.0
        self.calId = 1.0
        self.calVGS = 0.9
        # Process
        self.tgtCorner = 0
        #avaiable corner: TT, FF, SS, FS, SF
        self.listCorner =["tt","ff","ss","fs","sf"]
        self.avaCorner = [ 0,  0,  0,  0,  0]
        self.mosCorner = [None, None, None, None, None]
        self.mosDat = None
        # Data
        self.listL = []
        self.listId = []
        self.listGmId = []
        self.listVstar = []
        self.listFt = []
        self.listFOM = []
        self.listAvo = []
        self.listVth = []
        self.pltId = None
        self.pltGmId = None
        self.pltVstar = None
        self.pltFt = None
        self.pltFOM = None
        self.pltAvo = None
        self.pltIdG = None
        self.pltFtG = None
        self.pltAvoG = None
        self.EnFom = 0
        # Range of vstar, gmid
        self.minVstar = 0.08
        self.maxVstar = 1.0
        self.minGmId = 2.0
        self.maxGmId = 25.0
        # Curve for L
        self.curveIdFit = None
        self.curveFtFit = None
        self.curveAvoFit= None
        self.curveIdCorner = [None, None, None, None, None]
        self.curveFtCorner = [None, None, None, None, None]
        self.curveAvoCorner = [None, None, None, None, None]
        self.curveIdFitG = None
        self.curveFtFitG = None
        self.curveAvoFitG = None
        self.curveIdCornerG = [None, None, None, None, None]
        self.curveFtCornerG = [None, None, None, None, None]
        self.curveAvoCornerG = [None, None, None, None, None]
        self.curveGmFitI = None
        self.curveFomFitI = None
        self.curveAvoFitI = None
        self.curveGmCornerI = [None, None, None, None, None]
        self.curveFomCornerI = [None, None, None, None, None]
        self.curveAvoCornerI = [None, None, None, None, None]
        # Curve for Lref
        self.curveIdFitRef = None
        self.curveFtFitRef = None
        self.curveAvoFitRef = None
        self.curveIdCornerRef = [None, None, None, None, None]
        self.curveFtCornerRef = [None, None, None, None, None]
        self.curveAvoCornerRef = [None, None, None, None, None]
        self.curveIdFitGRef = None
        self.curveFtFitGRef = None
        self.curveAvoFitGRef = None
        self.curveIdCornerGRef = [None, None, None, None, None]
        self.curveFtCornerGRef = [None, None, None, None, None]
        self.curveAvoCornerGRef = [None, None, None, None, None]
        self.curveGmFitIRef = None
        self.curveFomFitIRef = None
        self.curveAvoFitIRef = None
        self.curveGmCornerIRef = [None, None, None, None, None]
        self.curveFomCornerIRef = [None, None, None, None, None]
        self.curveAvoCornerIRef = [None, None, None, None, None]
        # Curve as function of L
        self.curveVth = None
        self.curveVthCorner = [None, None, None, None, None]
        # Pen Style for Pyqtgraph
        self.plotColor = pg.hsvColor(time.time()/5%1,alpha=.5)
        self.cornerPen = [None, None, None, None, None]
        self.cornerPen[0] = pg.mkPen(color=(119, 172, 48), width = 1.5, style=QtCore.Qt.DotLine)
        self.cornerPen[1] = pg.mkPen( color=(0, 114, 189), width = 1.5, style=QtCore.Qt.DotLine)
        self.cornerPen[2] = pg.mkPen(color=(126, 47, 142), width = 1.5, style=QtCore.Qt.DotLine)
        self.cornerPen[3] = pg.mkPen( color=(217, 83, 25), width = 1.5, style=QtCore.Qt.DotLine)
        self.cornerPen[4] = pg.mkPen(color=(237, 177, 32), width = 1.5, style=QtCore.Qt.DotLine)
        self.linePen = [None, None, None, None, None]
        self.linePen[0] = pg.mkPen(color=(119, 172, 48), width = 2)
        self.linePen[1] = pg.mkPen( color=(0, 114, 189), width = 2)
        self.linePen[2] = pg.mkPen(color=(126, 47, 142), width = 2)
        self.linePen[3] = pg.mkPen( color=(217, 83, 25), width = 2)
        self.linePen[4] = pg.mkPen(color=(237, 177, 32), width = 2)
        self.dotPen = pg.mkPen(self.plotColor, width = 2, style=QtCore.Qt.DotLine)
        self.symbolStyle = 'o'
        # Flag for State
        self.arrowPos = 0
        self.curveReady = 0
        self.desLSet = 0
        self.refLSet = 0

    # checkBox Functions
    def PlotCornerTT(self, state):
        if self.avaCorner[0] == 1:
            if state == Qt.Checked:
                self.visibleCurve(0, True)
            else:
                self.visibleCurve(0, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerFF(self, state):
        if self.avaCorner[1] == 1:
            if state == Qt.Checked:
                self.visibleCurve(1, True)
            else:
                self.visibleCurve(1, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerSS(self, state):
        if self.avaCorner[2] == 1:
            if state == Qt.Checked:
                self.visibleCurve(2, True)
            else:
                self.visibleCurve(2, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerFS(self, state):
        if self.avaCorner[3] == 1:
            if state == Qt.Checked:
                self.visibleCurve(3, True)
            else:
                self.visibleCurve(3, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotCornerSF(self, state):
        if self.avaCorner[4] == 1:
            if state == Qt.Checked:
                self.visibleCurve(4, True)
            else:
                self.visibleCurve(4, False)
        else:
            self.ui.labelLog.setText('No Data Available')

    def PlotRef(self, state):
        if self.refLSet == 1:
            if state == Qt.Checked:
                self.visibleRef(True)
            else:
                self.visibleRef(False)
        else:
            self.ui.labelLog.setText('No Ref Curve')


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
            self.matFileInfo = self.matFileName.split('_')
            self.ui.titleMosCharData.setText(self.matFileName)
            self.loadMat()

    def GateLSet(self):
        self.gateLItem = self.ui.listWidgetL.currentItem()
        if self.gateLItem == None:
            self.ui.labelLog.setText('No Gate Length Set')
        else:
            self.L = float(self.gateLItem.text())
            self.ui.labelGateL.setText(self.gateLItem.text())
            self.desLSet = 1

    def GateLRef(self):
        self.gateLRefItem = self.ui.listWidgetLRef.currentItem()
        if self.gateLRefItem == None:
            self.ui.labelLog.setText('No Ref Gate Length')
        else:
            self.Lref = float(self.gateLRefItem.text())
            self.ui.labelGateLRef.setText(self.gateLRefItem.text())
            self.refLSet = 1

    def PlotUpdate(self):
        if self.desLSet == 0:
            self.ui.labelLog.setText('No Des Gate Length')
        elif self.refLSet == 0:
            self.ui.labelLog.setText('No Ref Gate Length')
        else:
            self.cornerMat()

    def PlotOff(self):
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
            self.ui.checkBoxRef.setCheckState(2)
            self.ui.checkBoxRef.setCheckState(0)

    def SynGmId(self):
        self.synGmId = float(self.ui.lineEditSynGmId.text())
        self.SynMos()

    def SynVstar(self):
        self.synGmId = 2/float(self.ui.lineEditSynVstar.text())
        self.SynMos()

    def CalMos(self):
        self.UpdateBias()
        self.calVGS = float(self.ui.lineEditCalVgs.text())
        self.calGmId = lp.lookupfz(self.mosDat, 'nch', 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.calVGS)
        self.calId = lp.lookupfz(self.mosDat, 'nch', 'ID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.calVGS) * self.calW / self.W
        self.ui.labelCalGmId.setText('%2.2f' % self.calGmId)
        self.ui.labelCalId.setText('%2.2f' % self.calId)

    def FuEst(self):
        pass

    def ExtCheck(self):
        pass

    # Background functions
    def UpdateBias(self):
        self.VDS = float(self.ui.spinBoxBiasVds.value())*0.001
        self.VSB = -float(self.ui.spinBoxBiasVbs.value())*0.001

    def SynMos(self):
        '''Syn MOS from Gm'''
        self.UpdateBias()
        self.synGm = float(self.ui.lineEditSynGm.text())
        self.synId = self.synGm / self.synGmId
        self.synW =  lp.lookupfz(self.mosDat, 'nch', 'ID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=self.synVGS) * self.W / self.synId
        print ('Width : %1.2f' % self.synW)

    def SearchVGS(self):
        vgsStart = 0
        vgsEnd = 1.8
        gmIdSeq = None
        vgsStep= [0.1,0.01,0.001]
        vgsLeft= 0
        for i in range(3):
            vgsSeq = np.arange( vgsStart, vgsEnd, vgsStep[i])
            gmIdSeq = lp.lookupfz(self.mosDat, 'nch', 'GMOVERID', VDS=self.VDS, VSB=self.VSB, L=self.L, VGS=vgsSeq)
            vgsLeft = np.searchsorted( gmIdSeq, self.synGmId, 'left')
            self.synVGS = vgsSeq[vgsLeft]
            vgsStart = vgsSeq[vgsLeft - 1]
            vgsEnd = vgsSeq[vgsLeft]

    def loadMat(self):
        print ('Load Mat File')
        self.mosDat = h5py.File(self.matFilePath, 'r')
        print ("Loading complete!")
        self.ui.listWidgetL.clear()
        self.listL = np.array(self.mosDat['L']).flatten()
        for i in range(len(self.listL)):
            self.ui.listWidgetL.addItem(str(self.listL[i]))
            self.ui.listWidgetLRef.addItem(str(self.listL[i]))
        lp.info(self.mosDat)
        self.W = self.mosDat['W'][0][0]*self.mosDat['NFING'][0][0]
        print ('Mos Default Width : %2.2f' % self.W)

    def cornerMat(self):
        '''Search & Load all the corner Matlib Data'''
        # Set Corner
        self.tgtCorner = self.listCorner.index(self.matFileInfo[2])
        print ('Corner Set to : %s' % self.listCorner[self.tgtCorner])
        # Search Corner
        for i in range(len(self.listCorner)):
            cornerFileName = self.matFileInfo[0]+'_'+self.matFileInfo[1]+'_'+self.listCorner[i]+'.mat'
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
        self.ui.topPlotVstar.clear()
        self.ui.midPlotVstar.clear()
        self.ui.botPlotVstar.clear()
        self.ui.topPlotGmId.clear()
        self.ui.midPlotGmId.clear()
        self.ui.botPlotGmId.clear()
        self.ui.topPlotVstar.addItem(self.topHLineVstar, ignoreBounds=True)
        self.ui.topPlotVstar.addItem(self.topVLineVstar, ignoreBounds=True)
        self.ui.midPlotVstar.addItem(self.midVLineVstar, ignoreBounds=True)
        self.ui.botPlotVstar.addItem(self.botVLineVstar, ignoreBounds=True)
        self.ui.topPlotGmId.addItem(self.topHLineGmId, ignoreBounds=True)
        self.ui.topPlotGmId.addItem(self.topVLineGmId, ignoreBounds=True)
        self.ui.midPlotGmId.addItem(self.midVLineGmId, ignoreBounds=True)
        self.ui.botPlotGmId.addItem(self.botVLineGmId, ignoreBounds=True)
        ## Generate the Curve
        self.GenCurve()
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
            self.curveIdCorner[self.tgtCorner].setPen(self.cornerPen[self.tgtCorner])
            self.curveFtCorner[self.tgtCorner].setPen(self.cornerPen[self.tgtCorner])
            if(self.refLSet == 1):
                self.curveIdCornerRef[self.tgtCorner].setVisible(False)
            self.tgtCorner = newTgtCorner
            self.ui.labelLog.setText("Corner Set")
            self.pen = self.linePen[self.tgtCorner]
            self.curveIdCorner[self.tgtCorner].setPen(self.linePen[self.tgtCorner])
            self.curveFtCorner[self.tgtCorner].setPen(self.linePen[self.tgtCorner])
            self.mosDat = self.mosCorner[self.tgtCorner]
            self.UpdatePlot()
            self.PlotOff()
            if(self.refLSet == 1):
                self.curveIdCornerRef[self.tgtCorner].setVisible(True)
        else:
            self.ui.labelLog.setText("Corner Not Found")

    def GenCurve(self):
        '''Generate all the curve'''
        for i in range(len(self.listCorner)):
            if self.avaCorner[i] == 1:
                self.vstarCurve( self.mosCorner[i], i)
                self.ui.topPlotVstar.addItem(self.curveIdCorner[i])
                self.ui.botPlotVstar.addItem(self.curveFtCorner[i])
                self.ui.midPlotVstar.addItem(self.curveAvoCorner[i])
                self.gmIdCurve( self.mosCorner[i], i)
                self.ui.topPlotGmId.addItem(self.curveIdCornerG[i])
                self.ui.botPlotGmId.addItem(self.curveFtCornerG[i])
                self.ui.midPlotGmId.addItem(self.curveAvoCornerG[i])
                self.vthCurve( self.mosCorner[i], i)
                self.ui.topLPlotL.addItem(self.curveVthCorner[i])
                if self.refLSet == 1:
                    self.ui.topPlotVstar.addItem(self.curveIdCornerRef[i])
            else:
                self.curveIdCorner[i] = None
                self.curveFtCorner[i] = None
                self.curveAvoCorner[i] = None
                self.curveIdCornerG[i] = None
                self.curveFtCornerG[i] = None
                self.curveAvoCornerG[i] = None
                self.curveVthCorner[i] = None
                # Ref
                self.curveIdCornerRef[i] = None
                self.curveFtCornerRef[i] = None
                self.curveAvoCornerRef[i] = None
                self.curveIdCornerGRef[i] = None
                self.curveFtCornerGRef[i] = None
                self.curveAvoCornerGRef[i] = None

    def UpdatePlot(self):
        '''Update the Plot for GmId'''
        # Update the MainCurve
        if self.curveIdFit != None:
            self.ui.topPlotVstar.removeItem(self.curveIdFit)
            self.ui.midPlotVstar.removeItem(self.curveAvoFit)
            self.ui.botPlotVstar.removeItem(self.curveFtFit)
            self.ui.topPlotGmId.removeItem(self.curveIdFitG)
            self.ui.midPlotGmId.removeItem(self.curveAvoFitG)
            self.ui.botPlotGmId.removeItem(self.curveFtFitG)
            self.ui.topLPlotL.removeItem(self.curveVth)
        VGS = np.arange(0, 1.8, 0.01)
        self.listId = lp.lookupfz(self.mosDat, 'nch', 'ID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        self.listAvo= lp.lookupfz(self.mosDat, 'nch', 'SELF_GAIN', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        self.listGmId = lp.lookupfz(self.mosDat, 'nch', 'GMOVERID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        self.listFt = lp.lookupfz(self.mosDat, 'nch', 'FUG', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        self.listVth = lp.lookupfz(self.mosDat, 'nch', 'VT', VDS=0.9, VSB=0, L=self.listL, VGS=0.9)
        # Fig Line
        self.listVstar = 2*np.reciprocal(self.listGmId)
        self.csId = CubicSpline( self.listVstar, self.listId)
        self.csFt = CubicSpline( self.listVstar, self.listFt)
        self.csAvo= CubicSpline( self.listVstar, self.listAvo)
        self.listGmIdG = np.flip(self.listGmId, 0)
        self.listIdG = np.flip(self.listId, 0)
        self.listFtG = np.flip(self.listFt, 0)
        self.listAvoG = np.flip(self.listAvo, 0)
        self.csIdG = CubicSpline( self.listGmIdG, self.listIdG)
        self.csFtG = CubicSpline( self.listGmIdG, self.listFtG)
        self.csAvoG= CubicSpline( self.listGmIdG, self.listAvoG)
        # Vstar Figure
        #self.pltVstar = np.arange( self.listVstar.min(), self.listVstar.max(), 0.001)
        self.pltVstar = np.arange( self.minVstar, self.maxVstar, 0.0005)
        self.pltId = self.csId(self.pltVstar)
        self.pltFt = self.csFt(self.pltVstar)
        self.pltAvo =self.csAvo(self.pltVstar)
        self.curveIdFit = pg.PlotDataItem( self.pltVstar, self.pltId, pen = self.pen, clear=True)
        self.curveFtFit = pg.PlotDataItem( self.pltVstar, self.pltFt, pen = self.pen, clear=True)
        self.curveAvoFit = pg.PlotDataItem( self.pltVstar, self.pltAvo,pen = self.pen, clear=True)
        self.ui.topPlotVstar.addItem(self.curveIdFit)
        self.ui.midPlotVstar.addItem(self.curveAvoFit)
        self.ui.botPlotVstar.addItem(self.curveFtFit)
        # GmId Figure
        #self.pltGmId = np.arange( self.listGmId.min(), self.listGmId.max(), 0.001)
        self.pltGmId = np.arange( self.minGmId, self.maxGmId, 0.01)
        self.pltIdG = self.csIdG(self.pltGmId)
        self.pltFtG = self.csFtG(self.pltGmId)
        self.pltAvoG = self.csAvoG(self.pltGmId)
        self.curveIdFitG = pg.PlotDataItem( self.pltGmId, self.pltIdG, pen = self.pen, clear=True)
        self.curveFtFitG = pg.PlotDataItem( self.pltGmId, self.pltFtG, pen = self.pen, clear=True)
        self.curveAvoFitG = pg.PlotDataItem( self.pltGmId, self.pltAvoG,pen = self.pen, clear=True)
        self.ui.topPlotGmId.addItem(self.curveIdFitG)
        self.ui.midPlotGmId.addItem(self.curveAvoFitG)
        self.ui.botPlotGmId.addItem(self.curveFtFitG)
        # Id Figure
        self.pltIdI = np.log10(self.pltIdG)
        self.curveGmFitI = pg.PlotDataItem( self.pltIdI, self.pltGmId, pen = self.pen, clear=True)
        self.curveFomFitI = pg.PlotDataItem( self.pltIdI, self.pltFtG*self.pltGmId, pen = self.pen, clear=True)
        self.curveAvoFitI = pg.PlotDataItem( self.pltIdI, self.pltAvoG, pen = self.pen, clear=True)
        self.ui.topPlotId.addItem(self.curveGmFitI)
        self.ui.midPlotId.addItem(self.curveAvoFitI)
        self.ui.botPlotId.addItem(self.curveFomFitI)
        # Vth Figure
        self.curveVth = pg.PlotDataItem( self.listL, self.listVth, pen = self.pen,symbolBrush=(255,0,0), symbolPen='w', clear=True)
        self.ui.topLPlotL.addItem(self.curveVth)
        # Set Flag
        self.curveReady = 1

    def vthCurve(self, mosDat, cornerIndex):
        '''Generate the Vth as a function of L'''
        listVth = lp.lookupfz(mosDat, 'nch', 'VT', VDS=0.9, VSB=0, L=self.listL, VGS=0.9)
        self.curveVthCorner[cornerIndex] = pg.PlotDataItem( self.listL, listVth, pen = self.cornerPen[cornerIndex], clear=True)

    def gmIdCurve(self, mosDat, cornerIndex):
        VGS = np.arange(0, 1.8, 0.01)
        listId = lp.lookupfz(mosDat, 'nch', 'ID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listGmOverId = lp.lookupfz(mosDat, 'nch', 'GMOVERID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listFt = lp.lookupfz(mosDat, 'nch', 'FUG', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listAvo = lp.lookupfz(mosDat, 'nch', 'SELF_GAIN', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listGmId = np.flip(listGmOverId, 0)
        listIdG = np.flip(listId, 0)
        listFtG = np.flip(listFt, 0)
        listAvoG = np.flip(listAvo, 0)
        csId = CubicSpline( listGmId, listIdG)
        csFt = CubicSpline( listGmId, listFtG)
        csAvo = CubicSpline( listGmId, listAvoG)
        pltGmId = np.arange( self.minGmId, self.maxGmId, 0.01)
        pltId = csId(pltGmId)
        pltFt = csFt(pltGmId)
        pltAvo = csAvo(pltGmId)
        self.curveIdCornerG[cornerIndex] = pg.PlotDataItem( pltGmId, pltId, pen = self.cornerPen[cornerIndex], clear=True)
        self.curveFtCornerG[cornerIndex] = pg.PlotDataItem( pltGmId, pltFt, pen = self.cornerPen[cornerIndex], clear=True)
        self.curveAvoCornerG[cornerIndex] = pg.PlotDataItem( pltGmId, pltAvo, pen = self.cornerPen[cornerIndex], clear=True)

    def vstarCurve(self, mosDat, cornerIndex):
        VGS = np.arange(0, 1.8, 0.01)
        # For L
        listId = lp.lookupfz(mosDat, 'nch', 'ID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listGmOverId = lp.lookupfz(mosDat, 'nch', 'GMOVERID', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listFt = lp.lookupfz(mosDat, 'nch', 'FUG', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listAvo = lp.lookupfz(mosDat, 'nch', 'SELF_GAIN', VDS=0.9, VSB=0, L=self.L, VGS=VGS)
        listVstar = 2*np.reciprocal(listGmOverId)
        csId = CubicSpline( listVstar, listId)
        csFt = CubicSpline( listVstar, listFt)
        csAvo = CubicSpline( listVstar, listAvo)
        #pltVstar = np.arange( listVstar.min(), listVstar.max(), 0.001)
        pltVstar = np.arange( self.minVstar, self.maxVstar, 0.0005)
        pltId = csId(pltVstar)
        pltFt = csFt(pltVstar)
        pltAvo = csAvo(pltVstar)
        self.curveIdCorner[cornerIndex] = pg.PlotDataItem( pltVstar, pltId, pen = self.cornerPen[cornerIndex], clear=True)
        self.curveFtCorner[cornerIndex] = pg.PlotDataItem( pltVstar, pltFt, pen = self.cornerPen[cornerIndex], clear=True)
        self.curveAvoCorner[cornerIndex] = pg.PlotDataItem( pltVstar, pltAvo, pen = self.cornerPen[cornerIndex], clear=True)
        # For LRef
        if(self.refLSet == 1):
            listId = lp.lookupfz(mosDat, 'nch', 'ID', VDS=0.9, VSB=0, L=self.Lref, VGS=VGS)
            listGmOverId = lp.lookupfz(mosDat, 'nch', 'GMOVERID', VDS=0.9, VSB=0, L=self.Lref, VGS=VGS)
            listFt = lp.lookupfz(mosDat, 'nch', 'FUG', VDS=0.9, VSB=0, L=self.Lref, VGS=VGS)
            listAvo = lp.lookupfz(mosDat, 'nch', 'SELF_GAIN', VDS=0.9, VSB=0, L=self.Lref, VGS=VGS)
            listVstar = 2*np.reciprocal(listGmOverId)
            csId = CubicSpline( listVstar, listId)
            csFt = CubicSpline( listVstar, listFt)
            csAvo = CubicSpline( listVstar, listAvo)
            pltId = csId(pltVstar)
            pltFt = csFt(pltVstar)
            pltAvo = csAvo(pltVstar)
            self.curveIdCornerRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltId, pen = self.cornerPen[cornerIndex], clear=True)
            self.curveFtCornerRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltFt, pen = self.cornerPen[cornerIndex], clear=True)
            self.curveAvoCornerRef[cornerIndex] = pg.PlotDataItem( pltVstar, pltAvo, pen = self.cornerPen[cornerIndex], clear=True)

    def visibleRef(self, curveStae):
        print ("TODO")

    def visibleCurve(self, curveIndex, curveState):
        self.curveIdCorner[curveIndex].setVisible(curveState)
        self.curveFtCorner[curveIndex].setVisible(curveState)
        self.curveAvoCorner[curveIndex].setVisible(curveState)
        self.curveIdCornerG[curveIndex].setVisible(curveState)
        self.curveFtCornerG[curveIndex].setVisible(curveState)
        self.curveAvoCornerG[curveIndex].setVisible(curveState)
        self.curveVthCorner[curveIndex].setVisible(curveState)

    def topMouseMovedVstar(self, evt):
        '''Read out the number at the point'''
        mousePoint = self.ui.topPlotVstar.plotItem.vb.mapSceneToView(evt)
        self.topVLineVstar.setPos(mousePoint.x())
        self.midVLineVstar.setPos(mousePoint.x())
        self.botVLineVstar.setPos(mousePoint.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.pltVstar, mousePoint.x(), side="left")
            if index > 0 and index < len(self.pltVstar):
                self.topHLineVstar.setPos(self.pltId[index])
                self.ui.topPlotVstar.addItem(self.topHLineVstar, ignoreBounds = True)
                self.ui.labelId.setText(self.sciPrint(self.pltId[index], 'A'))
                self.ui.labelVstar.setText(self.sciPrint(self.pltVstar[index], 'V'))
                self.ui.labelGmId.setText(self.sciPrint((2.0/self.pltVstar[index]), '1/V'))
                self.ui.labelFt.setText(self.sciPrint(self.pltFt[index], 'Hz'))
                self.ui.labelGain.setText(self.sciPrint(self.pltAvo[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((2.0*self.pltFt[index]/self.pltVstar[index]),'Hz/V'))
                self.arrowPos = index
            else:
                if index <= 0 :
                    self.arrowPos = 0
                else:
                    self.arrowPos = len(self.pltVstar) - 1
                self.ui.topPlotVstar.removeItem(self.topHLineVstar)
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')
            #self.arrowFt.setPos(self.pltVstar[self.arrowPos], self.pltFt[self.arrowPos])
            #self.arrowAvo.setPos(self.pltVstar[self.arrowPos], self.pltAvo[self.arrowPos])
            #self.ui.botPlotVstar.addItem(self.arrowFt)
            #self.ui.midPlotVstar.addItem(self.arrowAvo)

    def topMouseMovedGmId(self, evt):
        '''Read out the number at the point'''
        mousePointG = self.ui.topPlotGmId.plotItem.vb.mapSceneToView(evt)
        self.topVLineGmId.setPos(mousePointG.x())
        self.botVLineGmId.setPos(mousePointG.x())
        self.midVLineGmId.setPos(mousePointG.x())
        if (self.curveReady == 1):
            index = np.searchsorted( self.pltGmId, mousePointG.x(), side="left")
            if index > 0 and index < len(self.pltGmId):
                self.topHLineGmId.setPos(self.pltIdG[index])
                self.ui.topPlotGmId.addItem(self.topHLineGmId, ignoreBounds = True)
                self.ui.labelId.setText(self.sciPrint(self.pltIdG[index], 'A'))
                self.ui.labelVstar.setText(self.sciPrint((2.0/self.pltGmId[index]), 'V'))
                self.ui.labelGmId.setText(self.sciPrint(self.pltGmId[index], '1/V'))
                self.ui.labelFt.setText(self.sciPrint(self.pltFtG[index], 'Hz'))
                self.ui.labelGain.setText(self.sciPrint(self.pltAvoG[index], 'V/V'))
                self.ui.labelFOM.setText(self.sciPrint((self.pltFtG[index]*self.pltGmId[index]),'Hz/V'))
            else:
                self.ui.topPlotGmId.removeItem(self.topHLineGmId)
                self.ui.labelId.setText('---')
                self.ui.labelGmId.setText('---')
                self.ui.labelFt.setText('---')
                self.ui.labelFOM.setText('---')
                self.ui.labelVstar.setText('---')

    def sciPrint( self, rawNum, unit):
        '''Print the rawNum with autoscale'''
        shiftNum = (decimal.Decimal(str(rawNum)) * decimal.Decimal('1E24')).normalize()
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
