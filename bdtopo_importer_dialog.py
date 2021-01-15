# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BDTopoIporterDialog
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

import os
import json

from qgis.PyQt import uic
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtGui import QStandardItemModel, QStandardItem
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QFileDialog

from qgis.gui import QgsProviderConnectionComboBox, QgsDatabaseSchemaComboBox


# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'bdtopo_importer_dialog_base.ui'))


class BDTopoImporterDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BDTopoImporterDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        # load db connections
        self.dbselect = QgsProviderConnectionComboBox('postgres', self)
        self.horizontalLayout_4.addWidget(self.dbselect)
        self.schemaselect = QgsDatabaseSchemaComboBox('postgres', self.dbselect.currentConnection(), self)
        self.dbselect.connectionChanged.connect(self.schemaselect.setConnectionName)
        self.horizontalLayout_5.addWidget(self.schemaselect)

        # load layer list
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r') as f:
            json_data = json.load(f)
            layer_data = json_data['themes']
        model = QStandardItemModel()
        root = model.invisibleRootItem()
        for theme in layer_data:
            item = QStandardItem(theme['title'])
            item.setData(theme['pathname'])
            root.appendRow(item)
            for layer in theme['layers']:
                layeritem = QStandardItem(layer['name'])
                layeritem.setCheckable(True)
                # layeritem.setCheckState(Qt.Checked)
                layeritem.setData(layer['filename'])
                item.appendRow(layeritem)
        
        self.treeView_layers.setModel(model)
        self.treeView_layers.expandAll()

        # file access buttons
        self.pushButton_folder_select.clicked.connect(self.onFolderSelectClicked)
        self.pushButton_file_select.clicked.connect(self.onFileSelectClicked)

        # check/uncheck all buttons
        self.pushButton_checkall.clicked.connect(self.onCheckAllClicked)
        self.pushButton_uncheckall.clicked.connect(self.onUncheckAllClicked)

    def import_method(self):
        """ Returns the chosen import method """
        if self.radio_download.isChecked():
            return 'download'
        if self.radio_file.isChecked():
            return 'compressed'
        return 'folder'

    def _layerTreeModelItems(self):
        """ generates the layer items from the tree model
        in the form (theme, layer_item)"""
        model = self.treeView_layers.model()
        root = model.invisibleRootItem()
        for row in range(root.rowCount()):
            theme_item = root.child(row)
            theme = theme_item.data()
            for subrow in range(theme_item.rowCount()):
                layer_item = theme_item.child(subrow)
                yield (theme, layer_item)

    def getCheckedLayers(self):
        """ Gets the list of cheched layers in the form [THEME, LAYER] """
        layers = []
        for theme, layer_item in self._layerTreeModelItems():
            if layer_item.checkState() == Qt.Checked:
                layers.append((theme, layer_item.data()))
        return layers

    def onFolderSelectClicked(self):
        mydir = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier")
        if mydir:
            self.lineEdit_folder_path.setText(mydir)

    def onFileSelectClicked(self):
        myfile, _ = QFileDialog.getOpenFileName(self, "Sélectionner un fichier",
            filter="Fichiers 7zip (*.7z)")
        if myfile:
            self.lineEdit_file_path.setText(myfile)

    def onCheckAllClicked(self):
        """ button to check all layers clicked """
        for _, item in self._layerTreeModelItems():
            item.setCheckState(Qt.Checked)
    
    def onUncheckAllClicked(self):
        """ button to uncheck all layers clicked """
        for _, item in self._layerTreeModelItems():
            item.setCheckState(Qt.Unchecked)