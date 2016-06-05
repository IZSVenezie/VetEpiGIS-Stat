# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VetEpiGIS-Stat
   A QGIS plugin
   Spatial functions for vet epidemiology
                              -------------------
        begin                : 2016-01-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Norbert Solymosi
        email                : solymosi.norbert@gmail.com
 ***************************************************************************/

 /***************************************************************************
 The functions are based on the spdep R package: https://cran.r-project.org/web/packages/spdep
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL, Qt, QSettings, QCoreApplication, QFile, QFileInfo, QDate, QVariant, \
    pyqtSignal, QRegExp, QDateTime, QTranslator
from PyQt4.QtSql import *

from qgis.core import QgsField, QgsSpatialIndex, QgsMessageLog, QgsProject, \
    QgsCoordinateTransform, QGis, QgsVectorFileWriter, QgsMapLayerRegistry, QgsFeature, \
    QgsGeometry, QgsFeatureRequest, QgsPoint, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsRectangle, QgsDataSourceURI, QgsDataProvider, QgsVectorDataProvider
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMessageBar, QgsRubberBand
from numpy import *
import itertools, math

from globalt_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):         
    def __init__(self, lyr):
        """Constructor for the dialog.
        
        """
        
        QDialog.__init__(self)                               
                        
        self.setupUi(self)

        self.nb = []
        self.lyr = lyr
        flds = lyr.dataProvider().fields()
        for fld in flds:
            self.comboBox.addItem(fld.name())

        self.comboBox_2.addItem('B')
        self.comboBox_2.addItem('C')
        self.comboBox_2.addItem('S')
        self.comboBox_2.addItem('U')
        self.comboBox_2.addItem('W')

        self.comboBox_3.addItem('greater')
        self.comboBox_3.addItem('less')
        self.comboBox_3.addItem('two sided')

        self.comboBox_4.addItem('randomization')
        self.comboBox_4.addItem('normality')


        self.toolButton.clicked.connect(self.MoranI)


    def MoranI(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if len(self.nb)==0:
            nb = self.poly2nb()
            self.nb = nb
        else:
            nb = self.nb

        cardnb = self.card(nb)
        zero = 0
        if len(cardnb)==0:
            zero += 1
            return

        glist = []
        for m in cardnb:
            s = []
            if m>0:
                s = [1]*m
            glist.append(s)

        n = len(cardnb)
        effn = n-zero
        if effn<1:
            return

        vlist = [None]*n

        if self.comboBox_2.currentText()=='B':
            for i in xrange(n):
                g = glist[i]
                if cardnb[i]>0:
                    vlist[i] = g

        elif self.comboBox_2.currentText()=='C' or self.comboBox_2.currentText()=='U':
            D = sum(list(itertools.chain.from_iterable(glist)))
            if D<1:
                return

            if self.comboBox_2.currentText()=='C':
                nu = float(effn)
            else:
                nu = 1.0

            qr = nu/float(D)
            for i in xrange(n):
                if cardnb[i]>0:
                    vlist[i] = [x * qr for x in glist[i]]

        elif self.comboBox_2.currentText()=='S':
            q = []
            for i in xrange(len(glist)):
                gg = []
                for j in xrange(len(glist[i])):
                    gg.append(power(2*glist[i][j],2))
                q.append(sqrt(sum(gg)))
            for i in xrange(n):
                if cardnb[i]>0:
                    if q[i]>0:
                        mpl = (1.0/float(q[i]))
                    else:
                        mpl = 0.0

                    v = [x * mpl for x in glist[i]]
                    glist[i] = v

            Q = sum(list(itertools.chain.from_iterable(glist)))
            if Q<1:
                return

            qr = float(effn)/float(Q)
            for i in xrange(n):
                if cardnb[i]>0:
                    vlist[i] = [x * qr for x in glist[i]]

        elif self.comboBox_2.currentText()=='W':
            for i in xrange(n):
                g = glist[i]
                d = sum(g)
                if cardnb[i]>0:
                    if d>0:
                        mpl = (1.0/float(d))
                    else:
                        mpl = 0.0

                    vlist[i] = [x * mpl for x in g]

        listw = vlist

        S0 = sum(sum(listw))
        S1 = 0
        rS = [0]*len(nb)
        cS = [0]*len(nb)

        for i in xrange(len(nb)):
            ij = nb[i]
            wij = listw[i]
            rS[i] = sum(wij)
            for j in xrange(len(ij)):
                dij = wij[j]
                ijj = ij[j]
                cS[ijj] = cS[ijj] + dij
                try:
                    ijlkup = nb[ijj].index(i)
                    dji = listw[ijj][ijlkup]
                except ValueError:
                    dji = 0

                S1 = S1 + (dij * dij) + (dij * dji)

        S2 = sum(power([x + y for x, y in zip(rS, cS)],2))
        S02 = float(S0) * float(S0)
        n1 = n-1
        n2 = n-2
        n3 = n-3
        nn = n*n

        x = self.datRead()

        if len(x)!=len(nb):
            return

        x = array(x)
        z = x-mean(x)
        zz = sum(power(z,2))
        K = (len(x)*sum(power(z,4)))/power(zz,2)

        ans = empty([n])
        for i in xrange(n):
            if cardnb[i]==0:
                ans[i] = 0
            else:
                sm = 0
                for j in xrange(cardnb[i]):
                    k = int(nb[i][j])
                    wt = listw[i][j]
                    tmp = z[k]
                    sm = sm+(tmp*wt)

                ans[i] = sm

        lz = ans

        I = (float(n)/float(S0)) * ((sum(z * lz))/float(zz))
        EI = (-1.0)/float(n1)

        if self.comboBox_4.currentText()=='randomization':
            VI = float(n) * (float(S1) * (float(nn) - 3.0 * float(n) + 3.0) - float(n) * float(S2) + 3.0 * float(S02))
            tmp = float(K) * (float(S1) * (float(nn) - float(n)) - 2.0 * float(n) * float(S2) + 6.0 * float(S02))
            if tmp>VI:
                self.plainTextEdit.insertPlainText('Kurtosis overflow, distribution of variable does not meet test assumptions\n')

            VI = (VI - tmp)/(float(n1) * float(n2) * float(n3) * float(S02))
            tmp = (VI - power(EI,2))
            if tmp<0:
                self.plainTextEdit.insertPlainText('Negative variance, ndistribution of variable does not meet test assumptions\n')
            VI = tmp
        else:
            VI = (float(nn) * float(S1) - float(n) * float(S2) + 3.0 * float(S02))/(float(S02) * (float(nn) - 1.0))
            tmp = (VI - power(EI,2))
            if tmp < 0:
                self.plainTextEdit.insertPlainText('Negative variance, ndistribution of variable does not meet test assumptions\n')
            VI = tmp

        ZI = (I - EI)/sqrt(VI)

        if self.comboBox_3.currentText()=='less':
            PrI = self.pnorm(ZI)
        elif self.comboBox_3.currentText()=='greater':
            PrI = 1.0-self.pnorm(ZI)
        else:
            PrI = 2.0*(1.0-self.pnorm(abs(ZI)))

        self.plainTextEdit.insertPlainText("Moran's I: %s\n" % I)
        self.plainTextEdit.insertPlainText("Expectation: %s\n" % EI)
        self.plainTextEdit.insertPlainText("Variance: %s\n" % VI)
        self.plainTextEdit.insertPlainText("Moran's I standard deviate: %s\n" % ZI)
        self.plainTextEdit.insertPlainText("p-value: %s\n" % PrI)


        ans = empty([n])
        for i in xrange(n):
            if cardnb[i]==0:
                ans[i] = 0
            else:
                sm = 0
                for j in xrange(cardnb[i]):
                    k = int(nb[i][j])
                    wt = listw[i][j]
                    diff = x[i]-x[k]
                    res = diff*diff
                    sm = sm+(res*wt)

                ans[i] = sm

        res = ans
        C = (float(n1)/(2.0*float(S0))) * ((sum(res))/float(zz))
        EC = 1.0

        if self.comboBox_4.currentText()=='randomization':
            VC = (float(n1) * float(S1) * (float(nn) - 3.0 * float(n) + 3.0 - float(K) * float(n1)))
            VC = VC - ((1.0/4.0) * (float(n1) * float(S2) * (float(nn) + 3.0 * float(n) - 6.0 - float(K) * (float(nn) - float(n) + 2.0))))
            VC = VC + (float(S02) * (float(nn) - 3.0 - float(K) * (power(n1,2))))
            VC = VC/(float(n) * float(n2) * float(n3) * float(S02))
        else:
            VC = ((2.0 * float(S1) + float(S2)) * float(n1) - 4.0 * float(S02))/(2.0 * (float(n) + 1.0) * float(S02))

        ZC = (EC - C)/sqrt(VC)

        if self.comboBox_3.currentText()=='less':
            PrI = self.pnorm(ZC)
        elif self.comboBox_3.currentText()=='greater':
            PrI = 1.0-self.pnorm(ZC)
        else:
            PrI = 2.0*(1.0-self.pnorm(abs(ZC)))

        self.plainTextEdit.insertPlainText('\n\n')
        self.plainTextEdit.insertPlainText("Geary's c: %s\n" % C)
        self.plainTextEdit.insertPlainText("Expectation: %s\n" % EC)
        self.plainTextEdit.insertPlainText("Variance: %s\n" % VC)
        self.plainTextEdit.insertPlainText("Geary's c standard deviate: %s\n" % ZC)
        self.plainTextEdit.insertPlainText("p-value: %s\n" % PrI)


        QApplication.restoreOverrideCursor()


    def pnorm(self, z):
        return (1.0 + math.erf(z / sqrt(2.0))) / 2.0


    def normpdf(x, mean, sd):
        var = float(sd)**2
        pi = 3.1415926
        denom = (2*pi*var)**.5
        num = math.exp(-(float(x)-float(mean))**2/(2*var))
        return num/denom


# function (x, listw, n, S0, zero.policy = NULL, NAOK = FALSE)
# {
#     if (is.null(zero.policy))
#         zero.policy <- get("zeroPolicy", envir = .spdepOptions)
#     stopifnot(is.logical(zero.policy))
#     n1 <- length(listw$neighbours)
#     x <- c(x)
#     if (n1 != length(x))
#         stop("objects of different length")
#     xx <- mean(x, na.rm = NAOK)
#     z <- x - xx
#     zz <- sum(z^2, na.rm = NAOK)
#     K <- (length(x) * sum(z^4, na.rm = NAOK))/(zz^2)
#     lz <- lag.listw(listw, z, zero.policy = zero.policy, NAOK = NAOK)
#     I <- (n/S0) * ((sum(z * lz, na.rm = NAOK))/zz)
#     res <- list(I = I, K = K)
#     res




#         QApplication.setOverrideCursor(Qt.WaitCursor)
#         nblst = self.nbCalc()
#         # lst = nblst[0]
#
#         x = self.datRead()
#         x = array(x)
#
#         sd = x[nblst[0]]
#         for d in sd:
#             self.plainTextEdit.insertPlainText('%s, ' % d)
#
#         self.plainTextEdit.insertPlainText('\n\n')
#
#         sd = x[nblst[1]]
#         for d in sd:
#             self.plainTextEdit.insertPlainText('%s, ' % d)
#
#         self.plainTextEdit.insertPlainText('\n\n')
#
#         sd = x
#         for d in sd:
#             self.plainTextEdit.insertPlainText('%s, ' % d)
#
#         # xi = arange(0,9)
#         # A = array([ xi, ones(9)])
#         # # linearly generated sequence
#         # y = [19, 20, 20.5, 21.5, 22, 23, 23, 25.5, 24]
#         # w = linalg.lstsq(A.T,y)[0] # obtaining the parameters
#         #
#         # self.plainTextEdit.insertPlainText('\n\n%s' % w)
# # http://docs.scipy.org/doc/numpy-1.10.0/reference/routines.linalg.html
#
#         z = x-mean(x)
#         sz2 = sum(power(z,2))
#         s0 = len(nblst[0])
#         n = len(x)
#         zi = x[nblst[0]]
#         zj = x[nblst[1]]
#         I = (n/(2*s0*sz2))*sum(array(zi)*array(zj))
#
#         self.plainTextEdit.insertPlainText('\n\nMoran I: %s' % I)
#
#         QApplication.restoreOverrideCursor()


    def poly2nb(self):
        lst = []

        index = QgsSpatialIndex()
        featsA = self.lyr.getFeatures()
        featsB = self.lyr.getFeatures()
        for ft in featsA:
            index.insertFeature(ft)

        featB = QgsFeature()
        prv = self.lyr.dataProvider()
        while featsB.nextFeature(featB):
            geomB = featB.constGeometry()
            idb = featB.id()
            idxs = index.intersects(geomB.boundingBox())
            sor = []
            for idx in idxs:
                rqst = QgsFeatureRequest().setFilterFid(idx)
                featA = prv.getFeatures(rqst).next()
                ida = featA.id()
                geomA = QgsGeometry(featA.geometry())
                if idb!=ida:
                    if geomB.touches(geomA)==True:
                        sor.append(ida)

            lst.append(sor)

        return lst


    def card(self, nb):
        cardnb = []
        for n in nb:
            cardnb.append(len(n))

        return cardnb


    def nbCalc(self):
        lsta = []
        lstb = []

        index = QgsSpatialIndex()
        featsA = self.lyr.getFeatures()
        featsB = self.lyr.getFeatures()
        for ft in featsA:
            index.insertFeature(ft)

        featB = QgsFeature()
        prv = self.lyr.dataProvider()
        while featsB.nextFeature(featB):
            geomB = featB.constGeometry()
            idb = featB.id()
            idxs = index.intersects(geomB.boundingBox())
            for idx in idxs:
                rqst = QgsFeatureRequest().setFilterFid(idx)
                featA = prv.getFeatures(rqst).next()
                ida = featA.id()
                geomA = QgsGeometry(featA.geometry())
                if idb>ida:
                    if geomB.touches(geomA)==True:
                        lsta.append(idb)
                        lstb.append(ida)
                        # self.plainTextEdit.insertPlainText('%s - %s\n' % (idb, ida))

        lstc = [lsta, lstb]
        return lstc


    def datRead(self):
        lstdat = []
        fld = self.comboBox.currentText()
        feats = self.lyr.getFeatures()
        feat = QgsFeature()
        while feats.nextFeature(feat):
            lstdat.append(float(feat[fld]))

        return lstdat








# from numpy import *
# property_a = array([545., 656., 5.4, 33.])
# property_b = array([ 1.2,  1.3, 2.3, 0.3])
# good_objects = [True, False, False, True]
# good_indices = [0, 3]
# property_asel = property_a[good_objects]
# property_bsel = property_b[good_indices]


    # def nbTouches(self):
    #     feat = QgsFeature()
    #     provider = self.ml.dataProvider()
    #     e = provider.featureCount()
    #
    #     for ne in range(self.mod, e + self.mod):
    #         feat = QgsFeature()
    #         geom = QgsGeometry()
    #         fiter = self.ml.getFeatures(QgsFeatureRequest(ne))
    #         if fiter.nextFeature(feat):
    #             geom = QgsGeometry(feat.geometry())
    #
    #         neighbours = self.htouch(feat)
    #         row = feat.id()-self.mod
    #         self.model.setData(self.model.index(row, 0, QModelIndex()), neighbours)
    #         self.progressBar.setValue(100*ne/e)
    #
    #
    # def htouch(self, feata):
    #     geoma = QgsGeometry(feata.geometry())
    #     feat = QgsFeature()
    #     provider = self.ml.dataProvider()
    #     feats = provider.getFeatures()
    #     self.emit(SIGNAL("runStatus(PyQt_PyObject)"), 0)
    #     self.emit(SIGNAL("runRange(PyQt_PyObject)"), (0, provider.featureCount()))
    #     ne = 0
    #     neighbours = ""
    #     while feats.nextFeature(feat):
    #         ne += 1
    #         self.emit(SIGNAL("runStatus(PyQt_PyObject)"), ne)
    #         geomb = QgsGeometry(feat.geometry())
    #         if feata.id()!=feat.id():
    #             if geoma.touches(geomb)==True:
    #                 neighbours = neighbours + '%s,' % (feat.id()+self.p)
    #     return neighbours[:-1]



        
        
        


