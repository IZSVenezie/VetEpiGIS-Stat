# -*- coding: utf-8 -*-
"""
/***************************************************************************
 VetEpiGIS-Stat
   A QGIS plugin 
   Spatial functions for vet epidemiology
                              -------------------
        begin                : 2016-01-06
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Norbert Solymosi
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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load VetEpiGISstat class from file VetEpiGISstat.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .vetepigis_stat import VetEpiGISstat
    return VetEpiGISstat(iface)

