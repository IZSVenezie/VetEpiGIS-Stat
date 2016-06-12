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

from scan_dialog import Ui_Dialog


class Dialog(QDialog, Ui_Dialog):         
    def __init__(self):
        """Constructor for the dialog.
        
        """
        
        QDialog.__init__(self)                               
                        
        self.setupUi(self)


    # def save(self):
    #     QApplication.setOverrideCursor(Qt.WaitCursor)
    #
    #     prv = self.lyr.dataProvider()
    #     attrs = prv.fields().toList()
    #     self.lyr.startEditing()
    #
    #     fls = ['Li', 'E_Li', 'Var_Li', 'Z_Li', 'p_value']
    #     nattrs = []
    #     for fl in fls:
    #         if self.lyr.fieldNameIndex(fl) == -1:
    #             nattrs.append(QgsField(fl, 6))
    #
    #     fls = ['neighbours', 'influence']
    #     for fl in fls:
    #         if self.lyr.fieldNameIndex(fl) == -1:
    #             nattrs.append(QgsField(fl, 10))
    #
    #     if len(nattrs)>0:
    #         self.lyr.dataProvider().addAttributes(nattrs)
    #         self.lyr.updateFields()
    #
    #     feats = prv.getFeatures()
    #     feat = QgsFeature()
    #     i = 0
    #     while feats.nextFeature(feat):
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Li'),
    #             str(self.model.itemData(self.model.index(i, 0))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('E_Li'),
    #             str(self.model.itemData(self.model.index(i, 1))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Var_Li'),
    #             str(self.model.itemData(self.model.index(i, 2))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('Z_Li'),
    #             str(self.model.itemData(self.model.index(i, 3))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('p_value'),
    #             str(self.model.itemData(self.model.index(i, 4))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('neighbours'),
    #             str(self.model.itemData(self.model.index(i, 5))[0]))
    #         self.lyr.changeAttributeValue(feat.id(), feat.fieldNameIndex('influence'),
    #             str(self.model.itemData(self.model.index(i, 6))[0]))
    #         i += 1
    #
    #
    #     self.lyr.commitChanges()
    #
    #     QApplication.restoreOverrideCursor()

