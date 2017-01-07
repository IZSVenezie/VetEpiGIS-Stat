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
 The functions are based on the SpatialEpi R package: https://CRAN.R-project.org/package=SpatialEpi
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

from scan_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):         
    def __init__(self, lyr):
        """Constructor for the dialog.
        
        """
        
        QDialog.__init__(self)                               
                        
        self.setupUi(self)

        self.lyr = lyr

        flds = lyr.dataProvider().fields()
        for fld in flds:
            if fld.type()!=10:
                self.comboBox_2.addItem(fld.name())
                self.comboBox_3.addItem(fld.name())
                self.comboBox_4.addItem(fld.name())

        self.comboBox.addItem('Poisson')
        self.comboBox.addItem('binomial')

        self.toolButton.clicked.connect(self.Kulldorf)
        self.comboBox.currentIndexChanged.connect(self.likhtyper)
        self.buttonBox.button(QDialogButtonBox.Save).clicked.connect(self.save)


    def likhtyper(self):
        if self.comboBox.currentText() == 'Poisson':
            self.label_7.setEnabled(True)
            self.comboBox_4.setEnabled(True)
        else:
            self.label_7.setEnabled(True)
            self.comboBox_4.setEnabled(False)


    def Kulldorf(self):
        """https://CRAN.R-project.org/package=SpatialEpi"""
        # cluster_detection.cpp

        QApplication.setOverrideCursor(Qt.WaitCursor)

        self.plainTextEdit.clear()

        toradians = math.atan(1.0)/45.0
        radiusearth = 0.5 * (6378.2 + 6356.7)
        sine51 = math.sin(51.5 * toradians)

        likelihood = self.comboBox.currentText()
        logLkhdType = likelihood.lower()
        pop_upper_bound = self.doubleSpinBox.value()
        n_simulations = self.spinBox.value()
        alpha_level = self.doubleSpinBox_2.value()

        population = []
        case = []
        xs = []
        ys = []

        feat = QgsFeature()
        feats = self.lyr.getFeatures()

        if logLkhdType=='poisson':
            expected_cases = []
            while feats.nextFeature(feat):
                cp = feat.geometry().centroid()
                x = (cp.geometry().x()*toradians)*radiusearth*sine51
                y = (cp.geometry().y()*toradians)*radiusearth
                case.append(float(feat[self.comboBox_2.currentText()]))
                population.append(float(feat[self.comboBox_3.currentText()]))
                expected_cases.append(float(feat[self.comboBox_4.currentText()]))
                xs.append(x)
                ys.append(y)
            total_pop = sum(array(population))
            denominator = expected_cases

        if logLkhdType=='binomial':
            expected_cases = []
            while feats.nextFeature(feat):
                cp = feat.geometry().centroid()
                x = (cp.geometry().x()*toradians)*radiusearth*sine51
                y = (cp.geometry().y()*toradians)*radiusearth
                case.append(float(feat[self.comboBox_2.currentText()]))
                population.append(float(feat[self.comboBox_3.currentText()]))
                xs.append(x)
                ys.append(y)
            total_pop = sum(array(population))
            denominator = population
            expected_cases = array(population) * (sum(array(case)) / total_pop)

        # total_pop = sum(array(population))
        # expected_cases = array(population)*(sum(array(case))/total_pop)

        geo = column_stack((xs, ys))

        """zones()"""
        n = len(case)
        dist = empty([n, n])

        for rowid in xrange(n):
            for colid in xrange(n):
                dist[rowid, colid] = linalg.norm(geo[rowid] - geo[colid])

        nearest_neighbors = []
        n_zones = 0
        vector_cutoffs = [0]
        vek = []

        for i in xrange(n):
            neighbors = dist[:,i].argsort()
            neighbors = list(neighbors[(cumsum([population[j] for j in neighbors])/total_pop)<=pop_upper_bound])
            nearest_neighbors.append(neighbors)
            n_zones += len(neighbors)
            vector_cutoffs.append(n_zones)
            vek.append([i]*len(neighbors))

        cluster_coords = column_stack((sum(vek), sum(nearest_neighbors)))
        """-"""

        # observedCases = case
        # expectedCases = denominator
        # nearestNeighborsList = nearest_neighbors
        # nZones = n_zones

        lkhd = self.computeAllLogLkhd(case, denominator, nearest_neighbors, n_zones, logLkhdType)
        cluster_index = lkhd.index(max(lkhd))
        center = cluster_coords[cluster_index,0]
        end = cluster_coords[cluster_index,1]
        cluster = nearest_neighbors[center]
        cluster = cluster[0:cluster.index(end)+1]
        perm = random.multinomial(int(round(sum(case))), denominator/sum(denominator), size=n_simulations)
        permutedCaseMatrix = transpose(perm)
        sim_lambda = self.kulldorffMC(permutedCaseMatrix, denominator, nearest_neighbors, n_zones, logLkhdType)
        combined_lambda = sum([sim_lambda, [max(lkhd)]])
        p_value = 1-mean([combined_lambda<max(lkhd)])

        location_IDs_included = cluster
        cluster_population = sum(array(population)[cluster])
        cluster_number_of_cases = sum(array(case)[cluster])
        cluster_expected_cases = sum(array(expected_cases)[cluster])
        cluster_SMR = sum(array(case)[cluster])/sum(array(expected_cases)[cluster])
        cluster_log_likelihood_ratio = lkhd[cluster_index]
        cluster_monte_carlo_rank = sum(combined_lambda >= lkhd[cluster_index])

        self.plainTextEdit.insertPlainText("Most likely cluster details:\n")
        self.plainTextEdit.insertPlainText("\tFeature IDs: %s\n" % str(location_IDs_included).replace('[', '').replace(']', ''))
        self.plainTextEdit.insertPlainText("\tCase number: %s\n" % int(cluster_number_of_cases))
        self.plainTextEdit.insertPlainText("\tPopulation: %s\n" % int(cluster_population))
        self.plainTextEdit.insertPlainText("\tExpected case number: %s\n" % round(cluster_expected_cases,2))
        self.plainTextEdit.insertPlainText("\tSMR: %s\n" % round(cluster_SMR,2))
        self.plainTextEdit.insertPlainText("\tLog-likelihood ratio: %s\n" % round(cluster_log_likelihood_ratio,2))
        self.plainTextEdit.insertPlainText("\tMonte Carlo rank: %s\n" % cluster_monte_carlo_rank)
        self.plainTextEdit.insertPlainText("\tP-value: %s\n" % p_value)

        self.clusters = []
        self.clusters.append(cluster)

        current_cluster = cluster
        indices = sorted(range(len(lkhd)), reverse=True, key=lkhd.__getitem__)

        for i in xrange(1, len(indices), 1):
            new_cluster_index = indices[i]
            new_center = cluster_coords[new_cluster_index, 0]
            new_end = cluster_coords[new_cluster_index, 1]
            new_cluster = nearest_neighbors[new_center]
            new_cluster = new_cluster[0:new_cluster.index(new_end)+1]
            if len(list(set(current_cluster) & set(new_cluster)))==0:
                new_secondary_cluster_location_IDs_included = new_cluster
                new_secondary_cluster_population = sum(array(population)[new_cluster])
                new_secondary_cluster_number_of_cases = sum(array(case)[new_cluster])
                new_secondary_cluster_expected_cases = sum(array(expected_cases)[new_cluster])
                new_secondary_cluster_SMR = sum(array(case)[new_cluster]) / sum(array(expected_cases)[new_cluster])
                new_secondary_cluster_log_likelihood_ratio = lkhd[new_cluster_index]
                new_secondary_cluster_monte_carlo_rank = sum(combined_lambda >= lkhd[new_cluster_index])
                new_secondary_cluster_p_value = 1-mean(combined_lambda < lkhd[new_cluster_index])
                if new_secondary_cluster_p_value > alpha_level:
                    break
                # secondary.clusters <- c(secondary.clusters, list(new.secondary.cluster))
                self.clusters.append(new_cluster)
                current_cluster = unique(sum([current_cluster, new_cluster]))
                self.plainTextEdit.insertPlainText("\nSecondary cluster details:\n")
                self.plainTextEdit.insertPlainText("\tFeature IDs: %s\n" % str(new_secondary_cluster_location_IDs_included).replace('[', '').replace(']', ''))
                self.plainTextEdit.insertPlainText("\tCase number: %s\n" % int(new_secondary_cluster_number_of_cases))
                self.plainTextEdit.insertPlainText("\tPopulation: %s\n" % int(new_secondary_cluster_population))
                self.plainTextEdit.insertPlainText("\tExpected case number: %s\n" % round(new_secondary_cluster_expected_cases,2))
                self.plainTextEdit.insertPlainText("\tSMR: %s\n" % round(new_secondary_cluster_SMR,2))
                self.plainTextEdit.insertPlainText("\tLog-likelihood ratio: %s\n" % round(new_secondary_cluster_log_likelihood_ratio,2))
                self.plainTextEdit.insertPlainText("\tMonte Carlo rank: %s\n" % new_secondary_cluster_monte_carlo_rank)
                self.plainTextEdit.insertPlainText("\tP-value: %s\n" % new_secondary_cluster_p_value)

        if len(self.clusters)==1:
            self.plainTextEdit.insertPlainText("\nNo secondary cluster.\n")

        QApplication.restoreOverrideCursor()


    def kulldorffMC(self, permutedCaseMatrix, expectedCases, nearestNeighbors, nZones, logLkhdType):
        # cluster_detection.cpp
        nAreas = shape(permutedCaseMatrix)[0]
        nSimulations = shape(permutedCaseMatrix)[1]
        # allLogLkhd = [0.0]*nZones
        permutedCases = [0.0]*nAreas
        maxLogLkhd = [0.0]*nSimulations
        for j in xrange(nSimulations):
            for i in xrange(nAreas):
                permutedCases[i] = permutedCaseMatrix[i,j]
            allLogLkhd = self.computeAllLogLkhd(permutedCases, expectedCases, nearestNeighbors, nZones, logLkhdType)
            maxLogLkhd[j] =  max(allLogLkhd)
        return maxLogLkhd


    def computeAllLogLkhd(self, observedCases, expectedCases, nearestNeighborsList, nZones, logLkhdType):
        # cluster_detection.cpp
        allLogLkhd = [0.0]*nZones
        nAreas = len(expectedCases)
        C = sum(observedCases)
        N = sum(expectedCases)
        index = 0
        # nNeighbors = 0
        for i in xrange(nAreas):
            cz = 0.0
            nz = 0.0
            nearestNeighbors = nearestNeighborsList[i]
            nNeighbors =  len(nearestNeighbors)
            for j in xrange(nNeighbors):
                cz += observedCases[nearestNeighbors[j]]
                nz += expectedCases[nearestNeighbors[j]]
                if logLkhdType=='poisson':
                    allLogLkhd[index] = self.poissonLogLkhd(cz, nz, N, C)
                if logLkhdType == 'binomial':
                    allLogLkhd[index] = self.binomialLogLkhd(cz, nz, N, C)
                index += 1
        return allLogLkhd


    def poissonLogLkhd(self, cz, nz, N, C):
        # cluster_detection.cpp
        if (cz / nz) <= ((C - cz) / (N - nz)):
            logLkhd = 0.0
        else:
            logLkhd = cz * log( (cz/nz) ) +\
                      cz * log( ( (N - nz)/(C-cz) ) ) +\
                      C * log( ( (C-cz)/(N-nz) ) ) +\
                      C * log( (N/C) )
        return logLkhd


    def binomialLogLkhd(self, cz, nz, N, C):
        # cluster_detection.cpp
        if (cz / nz) <= ((C - cz)/(N - nz)):
            logLkhd = 0.0
        else:
            logLkhd = N * ( log( N-nz-C+cz ) - log( N-C )  + log( N ) - log( N-nz ) ) +\
                      nz * ( log( nz-cz ) - log( N-nz-C+cz )  + log( N-nz ) - log( nz ) )+\
                      cz * ( log( cz ) - log( nz-cz ) + log( N-nz-C+cz ) - log( C-cz ) )+\
                      C * ( log( C-cz ) - log( C ) + log( N-C ) - log( N-nz-C+cz ) )
        return logLkhd


    def save(self):
        QApplication.setOverrideCursor(Qt.WaitCursor)

        prv = self.lyr.dataProvider()
        attrs = prv.fields().toList()
        self.lyr.startEditing()

        fls = []
        for i in xrange(len(self.clusters)):
            fls.append('clust_' + str(i))

        nattrs = []
        for fl in fls:
            if self.lyr.fieldNameIndex(fl) == -1:
                nattrs.append(QgsField(fl, 10))

        if len(nattrs)>0:
            self.lyr.dataProvider().addAttributes(nattrs)
            self.lyr.updateFields()

        i = 0
        for cluster in self.clusters:
            fln = fls[i]
            # for fid in cluster:
            feats = prv.getFeatures()
            feat = QgsFeature()
            while feats.nextFeature(feat):
                if feat.id() in cluster:
                    self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex(fln), 'True')
                else:
                    self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex(fln), 'False')
            i += 1

        self.lyr.commitChanges()

        QApplication.restoreOverrideCursor()

