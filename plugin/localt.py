# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QVetStat
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

from local_dialog import Ui_Dialog


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


        self.toolButton.clicked.connect(self.LISA)


    def LISA(self):
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

        x = self.datRead()
        if len(x)!=len(nb):
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

        x = array(x)
        z = x-mean(x)
        ans = empty([n])
        Wi = []
        Wi2 = []
        Wikh2 = []
        for i in xrange(n):
            Wi.append(sum(listw[i]))
            Wi2.append(sum(power(listw[i],2)))
            if len(listw[i])==0:
                Wikh2.append(0)
            else:
                Wikh2.append(1-dot(array(listw[i]), array(listw[i])))
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

        s2 = float(sum(power(z,2)))/float(n)
        # s2 = float(sum(power(z,2)))/(float(n)-1.0)
        res1 = (z/s2) * lz
        res2 = -1.0*(array(Wi)/(float(n)-1.0))
        b2 = (float(sum(power(z,4)))/float(n))/power(s2,2)
        A = (float(n)-b2)/(float(n)-1.0)
        B = (2.0 * b2 - float(n))/((float(n) - 1.0) * (float(n) - 2.0))
        C = power(Wi,2)/(power((float(n) - 1.0),2))
        res3 = A * array(Wi2) + B * array(Wikh2) - C
        res4 = (res1-res2)/sqrt(res3)

        pv = []
        if self.comboBox_3.currentText()=='less':
            for e in res4:
                pv.append(self.pnorm(e))
        elif self.comboBox_3.currentText()=='greater':
            for e in res4:
                pv.append(1-self.pnorm(e))
        else:
            for e in res4:
                pv.append(2.0*(1-self.pnorm(e)))

        # p-value adjusment!!!
        xwxlm = polyfit(z, lz, 1, full = True)
        # xwxlm = lm(wx ~ x)

        self.plainTextEdit.insertPlainText('Ii: %s\n' % res1)
        self.plainTextEdit.insertPlainText('E.Ii: %s\n' % res2)
        self.plainTextEdit.insertPlainText('Var.Ii: %s\n' % res3)
        self.plainTextEdit.insertPlainText('Z.Ii: %s\n' % res4)
        self.plainTextEdit.insertPlainText('p-value: %s\n' % pv)
        # self.plainTextEdit.insertPlainText('lm: %s\n' % xwxlm)


        QApplication.restoreOverrideCursor()


    def pnorm(self, z):
        return (1.0 + math.erf(z / sqrt(2.0))) / 2.0


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


    def datRead(self):
        lstdat = []
        fld = self.comboBox.currentText()
        feats = self.lyr.getFeatures()
        feat = QgsFeature()
        while feats.nextFeature(feat):
            lstdat.append(float(feat[fld]))

        return lstdat
