# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BDTopoIporter
                                 A QGIS plugin
 Import facile des couches de la BDTopo dans une base de données PostGIS
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-01-13
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Augustin Roche
        email                : augustin.roche@gmail.com
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
import os.path
import re

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog

from qgis.core import Qgis, QgsProcessingUtils, QgsMessageLog
from qgis import processing


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .bdtopo_importer_dialog import BDTopoImporterDialog
from . import extractors



class BDTopoImporter:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

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
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BDTopoIporter_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&BDTopo Importer')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.file_path = None
        self.tempdir = QgsProcessingUtils.tempFolder()

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
        return QCoreApplication.translate('BDTopoImporter', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/bdtopo_importer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Import BDTopo'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True

    def process_layer(self, layername, layerpath):
        """
        Runs the GDAL algoritm to store layer in postgis
        """
        
        db = self.dlg.dbselect.currentConnection()
        params = {
            'DATABASE': db,
            'INPUT': layerpath,
            'SCHEMA': self.dlg.schemaselect.currentSchema(),
            'TABLE': layername.lower(),
            'APPEND': self.dlg.radioButton_append.isChecked(),
            'OVERWRITE': self.dlg.radioButton_overwrite.isChecked()
        }
        processing.run('gdal:importvectorintopostgisdatabaseavailableconnections', params)
        self.dlg.progressBar.setValue(100)
        
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&BDTopo Importer'),
                action)
            self.iface.removeToolBarIcon(action)

    def getWorkingDir(self):
        """ Gets directory where layers are stored """
        if self.dlg.radio_folder.isChecked():
            # selected folder
            return self.dlg.lineEdit_folder_path.text()
        else:
            return self.tempdir

    def importLayers(self):
        """ Main method to import selected layers """
        working_dir = self.getWorkingDir()
        if not os.path.isdir(working_dir):
            self.iface.messageBar().pushMessage(self.tr("Erreur"), 
                self.tr("Le dossier n'a pas été trouvé"), level=Qgis.Critical)
            return

        layers = self.dlg.getCheckedLayers()
        if len(layers) == 0:
            self.iface.messageBar().pushMessage(self.tr("Erreur"),
                self.tr("Sélectionnez au moins une couche."), level=Qgis.Warning)
            return
        
        self.dlg.progressBar.setMaximum(len(layers) * 2)
        self.dlg.progressBar.reset()
        self.dlg.progressBar.setEnabled(True)
        self.dlg.label_progress.setEnabled(True)
        self.dlg.repaint()

        s = QSettings()
        executable = s.value('bdtopo_importer/sevenzip_executable', "7z")
        
        counter = 0
        for theme, lyr in layers:
            self.dlg.label_progress.setText(f"Extracting layer {lyr}...")
            self.dlg.repaint()
            if self.dlg.import_method() == 'download':
                # first download file
                # TODO
                pass
            if self.dlg.import_method() in ('download', 'compressed'):
                # extracting from compressed file
                # check archive exists
                archive = self.dlg.lineEdit_file_path.text()
                if not os.path.isfile(archive):
                    self.iface.messageBar().pushMessage(self.tr("Erreur"),
                        self.tr("Le fichier .7z n'a pas été trouvé."), level=Qgis.Warning)
                    return
               
                try:
                    layerpath = extractors.extract_7zip(archive, theme, lyr, working_dir, executable)
                except extractors.ProgramNotFoundError:
                    self.iface.messageBar().pushMessage(self.tr("Erreur"),
                            self.tr("L'exécutable 7zip n'a pas été trouvé"), level=Qgis.Warning)
                    # Let the user chose the 7zip program
                    executable, _ = QFileDialog.getOpenFileName(
                        self.dlg,
                        self.tr("Sélectionnez le fichier d'exécutable de 7zip")
                    )
                    if executable:
                        s.setValue('bdtopo_importer/sevenzip_executable', executable)
                        self.iface.messageBar().pushMessage(self.tr("Exécutable 7zip modifié"),
                            self.tr("Relancez le traitement."), level=Qgis.Warning)
                    return
            else:
                # process already extracted files
                layerpath = extractors.get_folder(working_dir, theme, lyr)
            
            counter += 1
            self.dlg.progressBar.setValue(counter)

            self.dlg.label_progress.setText(f"Importing layer {lyr}...")
            self.dlg.repaint()
            self.process_layer(lyr, layerpath)
            counter += 1
            self.dlg.progressBar.setValue(counter)
            self.dlg.repaint()
        
        self.dlg.reset_progress()
        self.dlg.accept()
        self.iface.messageBar().pushMessage(self.tr("Import BDTopo terminé"), Qgis.Success)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start:
            self.first_start = False
            self.dlg = BDTopoImporterDialog()
            self.dlg.button_box.accepted.connect(self.importLayers)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            pass
