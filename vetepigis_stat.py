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
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL, Qt, QSettings, QCoreApplication, QFile, QFileInfo, QDate, QVariant, \
    pyqtSignal, QRegExp, QDateTime, QTranslator
from PyQt4.QtSql import *

from qgis.core import QgsField, QgsSpatialIndex, QgsMessageLog, QgsProject, \
    QgsCoordinateTransform, QGis, QgsVectorFileWriter, QgsMapLayerRegistry, QgsFeature, \
    QgsGeometry, QgsFeatureRequest, QgsPoint, QgsVectorLayer, QgsCoordinateReferenceSystem, \
    QgsRectangle, QgsDataSourceURI, QgsDataProvider
from qgis.gui import QgsMapTool, QgsMapToolEmitPoint, QgsMessageBar, QgsRubberBand


from plugin import xabout, globalt, localt, scan
import resources_rc



class VetEpiGISstat:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        self.lang = 'en'
#        self.loadSettings()

        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'VetEpiGISstat_{}.qm'.format(locale))

        self.vers = '0.12'
        self.prevcur = self.iface.mapCanvas().cursor()

        # self.thePoint = QgsPoint(0,0)
        # self.state = 0
        self.origtool = QgsMapTool(self.iface.mapCanvas())

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('VetEpiGIS-Stat', message)


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.frmGT = QAction(
            QIcon(':/plugins/VetEpiGISstat/images/worldgrid28.png'),
            QCoreApplication.translate('VetEpiGIS-Stat', "Global Moran's I, Geary's c"),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Stat', self.frmGT)
        self.frmGT.triggered.connect(self.gTests)

        self.frmLT = QAction(
            QIcon(':/plugins/VetEpiGISstat/images/route17.png'),
            QCoreApplication.translate('VetEpiGIS-Stat', "Local Moran's I (LISA)"),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Stat', self.frmLT)
        self.frmLT.triggered.connect(self.lTests)

        # self.frmSC = QAction(
        #     QIcon(':/plugins/VetEpiGISstat/images/fingerprint-scan.png'),
        #     QCoreApplication.translate('VetEpiGIS-Stat', "Scan statistic"),
        #     self.iface.mainWindow())
        # self.iface.addPluginToMenu('&VetEpiGIS-Stat', self.frmSC)
        # self.frmSC.triggered.connect(self.scan)

        self.actAbout = QAction(
            QIcon(':/plugins/VetEpiGISstat/images/icon02.png'),
            QCoreApplication.translate('VetEpiGIS-Stat', 'About'),
            self.iface.mainWindow())
        self.iface.addPluginToMenu('&VetEpiGIS-Stat', self.actAbout)
        self.actAbout.triggered.connect(self.about)


        self.toolbar = self.iface.addToolBar(
            QCoreApplication.translate('VetEpiGIS-Stat', 'VetEpiGIS-Stat'))
        self.toolbar.setObjectName(
            QCoreApplication.translate('VetEpiGIS-Stat', 'VetEpiGIS-Stat'))


        self.toolbar.addAction(self.frmGT)
        self.toolbar.addAction(self.frmLT)
        # self.toolbar.addAction(self.frmSC)



    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        self.iface.removePluginMenu('&VetEpiGIS-Stat', self.actAbout)
        del self.toolbar


    def scan(self):
        # lyr = self.iface.activeLayer()
        dlg = scan.Dialog()
        dlg.setWindowTitle("Scan statistic")
        # dlg.toolButton.setIcon(QIcon(':/plugins/VetEpiGISstat/images/verify8.png'))
        # dlg.toolButton.setToolTip('Run the analysis')

        dlg.exec_()


    def lTests(self):
        lyr = self.iface.activeLayer()
        dlg = localt.Dialog(lyr)
        dlg.setWindowTitle("Local Moran's I (LISA)")
        dlg.toolButton.setIcon(QIcon(':/plugins/VetEpiGISstat/images/verify8.png'))
        dlg.toolButton.setToolTip('Run the analysis')

        dlg.exec_()


    def gTests(self):
        lyr = self.iface.activeLayer()
        dlg = globalt.Dialog(lyr)
        dlg.setWindowTitle("Global Moran's I, Geary's c")
        dlg.toolButton.setIcon(QIcon(':/plugins/VetEpiGISstat/images/verify8.png'))
        dlg.toolButton.setToolTip('Run the analysis')

        dlg.exec_()


    def about(self):
        dlg = xabout.Dialog()
        dlg.setWindowTitle('About')
        dlg.label.setPixmap(QPixmap(':/plugins/VetEpiGISstat/images/QVetGroup-about-banner.png'))
        ow = dlg.textEdit.fontWeight()

        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('VetEpiGIS-Stat ' + self.vers + '\n')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append(
            "VetEpiGIS-Stat is a member of VetEpiGIS QGIS plugin family. The goal of the development is to collect spatial statistical methods are used in veterinary epidemiology into a plugin and create an easy to use interface for their application. Implemented methods: global Moran's I, global Geary's c, Local Moran's I.\nThe functions are based on the spdep R package: https://cran.r-project.org/web/packages/spdep\n")
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Developers:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append('Norbert Solymosi *;\n* from University of Veterinary Medicine, Budapest.\n')
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Contributors:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append(
            u'Nicola Ferrè *;\nMatteo Mazzucato *;\n* from Istituto Zooprofilattico Sperimentale delle Venezie.\n')
        dlg.textEdit.setFontWeight(QFont.Bold)
        dlg.textEdit.append('Contacts:')
        dlg.textEdit.setFontWeight(ow)
        dlg.textEdit.append('Send an email to gis@izsvenezie.it\n\n')
        dlg.textEdit.append('Original icons designed by Feepik. They were modified for this project by IZSVe.')
        dlg.textEdit.moveCursor(QTextCursor.Start, QTextCursor.MoveAnchor)
        dlg.textEdit.setReadOnly(True)

        x = (self.iface.mainWindow().x() + self.iface.mainWindow().width() / 2) - dlg.width() / 2
        y = (self.iface.mainWindow().y() + self.iface.mainWindow().height() / 2) - dlg.height() / 2
        dlg.move(x, y)
        dlg.exec_()

