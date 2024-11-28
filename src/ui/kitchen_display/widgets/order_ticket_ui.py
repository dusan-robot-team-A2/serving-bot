# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\widgets\OrderTicket.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(230, 80)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(230, 0))
        Form.setMaximumSize(QtCore.QSize(300, 16777215))
        Form.setStyleSheet("")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setStyleSheet("background-color:white;")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QtWidgets.QWidget(self.frame)
        self.widget.setStyleSheet("background-color: green;\n"
"color: white;")
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.table_num_container = QtWidgets.QHBoxLayout()
        self.table_num_container.setObjectName("table_num_container")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.table_num_container.addWidget(self.label)
        self.table_num = QtWidgets.QLabel(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.table_num.sizePolicy().hasHeightForWidth())
        self.table_num.setSizePolicy(sizePolicy)
        self.table_num.setObjectName("table_num")
        self.table_num_container.addWidget(self.table_num)
        self.verticalLayout_2.addLayout(self.table_num_container)
        self.time_since_order = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.time_since_order.setFont(font)
        self.time_since_order.setObjectName("time_since_order")
        self.verticalLayout_2.addWidget(self.time_since_order)
        self.verticalLayout.addWidget(self.widget)
        self.orders_layout = QtWidgets.QHBoxLayout()
        self.orders_layout.setObjectName("orders_layout")
        self.orders = QtWidgets.QVBoxLayout()
        self.orders.setObjectName("orders")
        self.orders_layout.addLayout(self.orders)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.orders_layout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.orders_layout)
        self.verticalLayout_3.addWidget(self.frame)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "테이블"))
        self.table_num.setText(_translate("Form", "9"))
        self.time_since_order.setText(_translate("Form", "13:05"))