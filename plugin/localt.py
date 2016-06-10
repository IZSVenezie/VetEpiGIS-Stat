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
    pyqtSignal, QRegExp, QDateTime, QTranslator, QModelIndex
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
            if fld.type()!=10:
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
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)


    def save(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        prv = self.lyr.dataProvider()
        attrs = prv.fields().toList()
        self.lyr.startEditing()

        fls = ['Li', 'E_Li', 'Var_Li', 'Z_Li', 'p_value']
        nattrs = []
        for fl in fls:
            if self.lyr.fieldNameIndex(fl) == -1:
                nattrs.append(QgsField(fl, 6))
        if len(nattrs)>0:
            self.lyr.dataProvider().addAttributes(nattrs)
            self.lyr.updateFields()

        feats = prv.getFeatures()
        feat = QgsFeature()
        i = 0
        while feats.nextFeature(feat):
            self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Li'),
                str(self.model.itemData(self.model.index(i, 0))[0]))
            self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('E_Li'),
                str(self.model.itemData(self.model.index(i, 1))[0]))
            self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Var_Li'),
                str(self.model.itemData(self.model.index(i, 2))[0]))
            self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Z_Li'),
                str(self.model.itemData(self.model.index(i, 3))[0]))
            self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('p_value'),
                str(self.model.itemData(self.model.index(i, 4))[0]))
            i += 1

        self.lyr.commitChanges()

        QApplication.restoreOverrideCursor()


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
        # xwxlm = polyfit(z, lz, 1, full = True)
        # xwxlm = lm(lz ~ z)

        # sum((polyval(polyfit(z, lz, 1), z) - lz)**2)
        # http: // www.real - statistics.com / multiple - regression / outliers - and -influencers /
        fitted = polyval(polyfit(z, lz, 1), z)
        resids = lz-fitted
        avgz = mean(z)
        n = len(z)
        k = 1
        SSz = sum((z-avgz)**2)
        SSr = sum((resids-mean(resids))**2)
        dfr = n-k-1.0
        MSr = SSr/dfr
        leverage = 1.0/n+((z-avgz)**2)/SSz # hat values
        modMSE = (MSr-resids**2/((1.0-leverage)*dfr))*dfr/(dfr-1.0)
        rstudent = resids/sqrt(modMSE*(1.0-leverage))
        CookD = (resids**2/MSr)*(leverage/(1.0-leverage)**2)/(k+1.0)
        dffit = rstudent*sqrt(leverage/(1.0-leverage))

        dfbeta = []
        dfbetaz = []
        sigma = [] #residual standard error

        # http://stackoverflow.com/questions/27757732/find-uncertainty-from-polyfit
        # http://www.mathworks.com/help/stats/coefficient-standard-errors-and-confidence-intervals.html?requestedDomain=www.mathworks.com
        fit, cov = polyfit(z, lz, 1, cov=True)
        # se = sqrt(diag(cov))
        for i in xrange(len(z)):
            zb = delete(z,i)
            lzb = delete(lz,i)
            fitb, covb = polyfit(zb, lzb, 1, cov=True)
            seb = sqrt(diag(covb))
            re = (fit-fitb)/seb
            dfbeta.append(re[1])
            dfbetaz.append(re[0])
            fittedb = polyval(polyfit(zb, lzb, 1), zb)
            residsb = lzb - fittedb
            sigma.append(sqrt(sum(residsb**2)/(n-k-1)))

        p = 2.0
        o = 1.0-leverage
        es = resids/(sigma*sqrt(o))
        covratio = 1.0/(o * (((n - p - 1.0) + es**2)/(n - p))**p)

        # https://people.duke.edu/~ccc14/sta-663/ResamplingAndMonteCarloSimulations.html


        self.plainTextEdit.insertPlainText('lz: %s\n' % lz)
        self.plainTextEdit.insertPlainText('z: %s\n' % z)

        # self.plainTextEdit.insertPlainText('Ii: %s\n' % res1)
        # self.plainTextEdit.insertPlainText('E.Ii: %s\n' % res2)
        # self.plainTextEdit.insertPlainText('Var.Ii: %s\n' % res3)
        # self.plainTextEdit.insertPlainText('Z.Ii: %s\n' % res4)
        # self.plainTextEdit.insertPlainText('p-value: %s\n' % pv)
        # self.plainTextEdit.insertPlainText('lm: %s\n' % xwxlm)

        dfbetabin = (abs(dfbeta) > 1) + 0
        dfbetazbin = (abs(dfbetaz) > 1) + 0
        dffitbin = (abs(dffit) > (3*sqrt(k/(n-k)))) + 0
        covratiobin = (abs(1.0 - covratio)) + 0
        CookDbin = (CookDbin) + 0
        hatbin = (hat > (3.0 * k)/n) + 0

        infl = dfbetabin + dfbetazbin + dffitbin + covratiobin + CookDbin + hatbin
        inflbin = infl > 0


#   absmat[, 1L:k] > 1,
#   absmat[, k + 1] > 3 * sqrt(k/(n - k)),        #dffit
#   abs(1 - infmat[, k + 2]) > (3 * k)/(n - k),   #cov.r
#   pf(infmat[, k + 3], k, n - k) > 0.5,          #cook.d
#   infmat[, k + 4] > (3 * k)/n                   #hat
# )

        self.model = QStandardItemModel(len(res1), 7)
        self.model.setHeaderData(0, Qt.Horizontal, 'Li')
        self.model.setHeaderData(1, Qt.Horizontal, 'E.Li')
        self.model.setHeaderData(2, Qt.Horizontal, 'Var.Li')
        self.model.setHeaderData(3, Qt.Horizontal, 'Z.Li')
        self.model.setHeaderData(4, Qt.Horizontal, 'p-value')
        self.model.setHeaderData(5, Qt.Horizontal, 'neighbours')
        self.model.setHeaderData(6, Qt.Horizontal, 'influence')

        for i in xrange(len(res1)):
            self.model.setData(self.model.index(i, 0, QModelIndex()), '%s' % res1[i])
            self.model.setData(self.model.index(i, 1, QModelIndex()), '%s' % res2[i])
            self.model.setData(self.model.index(i, 2, QModelIndex()), '%s' % res3[i])
            self.model.setData(self.model.index(i, 3, QModelIndex()), '%s' % res4[i])
            self.model.setData(self.model.index(i, 4, QModelIndex()), '%s' % pv[i])
            self.model.setData(self.model.index(i, 6, QModelIndex()), '%s' % inflbin[i])

        self.tableView.setModel(self.model)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selectionModel = QItemSelectionModel(self.model)
        self.tableView.setSelectionModel(self.selectionModel)
        self.tableView.horizontalHeader().setStretchLastSection(True)


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

