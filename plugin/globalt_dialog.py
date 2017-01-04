# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'globalt_dialog_base.ui'
#
# Created: Wed Jan  4 05:32:35 2017
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(561, 471)
        self.gridLayout_3 = QtGui.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.splitter = QtGui.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.label = QtGui.QLabel(self.splitter)
        self.label.setObjectName(_fromUtf8("label"))
        self.comboBox = QtGui.QComboBox(self.splitter)
        self.comboBox.setMinimumSize(QtCore.QSize(251, 0))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.gridLayout_3.addWidget(self.splitter, 0, 0, 1, 7)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout_3.addWidget(self.label_5, 1, 0, 1, 1)
        self.comboBox_5 = QtGui.QComboBox(Dialog)
        self.comboBox_5.setObjectName(_fromUtf8("comboBox_5"))
        self.gridLayout_3.addWidget(self.comboBox_5, 1, 1, 1, 3)
        self.lineEdit = QtGui.QLineEdit(Dialog)
        self.lineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.lineEdit.setInputMask(_fromUtf8(""))
        self.lineEdit.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout_3.addWidget(self.lineEdit, 1, 4, 1, 1)
        self.comboBox_6 = QtGui.QComboBox(Dialog)
        self.comboBox_6.setObjectName(_fromUtf8("comboBox_6"))
        self.gridLayout_3.addWidget(self.comboBox_6, 1, 5, 1, 1)
        spacerItem = QtGui.QSpacerItem(25, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 1, 6, 1, 1)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.comboBox_2 = QtGui.QComboBox(Dialog)
        self.comboBox_2.setObjectName(_fromUtf8("comboBox_2"))
        self.gridLayout.addWidget(self.comboBox_2, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 2, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(64, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 2, 2, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout_3.addWidget(self.label_4, 2, 3, 1, 2)
        self.comboBox_4 = QtGui.QComboBox(Dialog)
        self.comboBox_4.setObjectName(_fromUtf8("comboBox_4"))
        self.gridLayout_3.addWidget(self.comboBox_4, 2, 5, 1, 1)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)
        self.comboBox_3 = QtGui.QComboBox(Dialog)
        self.comboBox_3.setObjectName(_fromUtf8("comboBox_3"))
        self.gridLayout_2.addWidget(self.comboBox_3, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout_2, 3, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(254, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem2, 3, 4, 1, 2)
        self.toolButton = QtGui.QToolButton(Dialog)
        self.toolButton.setIconSize(QtCore.QSize(30, 30))
        self.toolButton.setObjectName(_fromUtf8("toolButton"))
        self.gridLayout_3.addWidget(self.toolButton, 3, 6, 1, 1)
        self.plainTextEdit = QtGui.QPlainTextEdit(Dialog)
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout_3.addWidget(self.plainTextEdit, 4, 0, 1, 7)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 5, 4, 1, 3)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label.setText(_translate("Dialog", "Data field:", None))
        self.label_5.setText(_translate("Dialog", "Neighbouring method:", None))
        self.label_2.setText(_translate("Dialog", "Weighting scheme:", None))
        self.label_4.setText(_translate("Dialog", "Variance assumption:", None))
        self.label_3.setText(_translate("Dialog", "Alternative hypothesis:", None))
        self.toolButton.setText(_translate("Dialog", "...", None))

