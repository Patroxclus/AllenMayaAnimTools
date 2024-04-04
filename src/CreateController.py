import maya.cmds as mc

from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class CreateControllerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create IKFK limb")
        self.setGeometry(100,100,300,300)
        self.masterlayout = QVBoxLayout()
        self.setLayout(self.masterlayout)

        hintLabel = QLabel("Please select the root of the limb")
        self.masterlayout.addWidget(hintLabel)

        findJntsBtn = QPushButton("Find JNTs")
        findJntsBtn.clicked.connect(self.FindJntBtnClicked)

        self.masterlayout.addWidget(findJntsBtn)
        self.adjustSize()

    def FindJntBtnClicked(self):
        print("I am clicked")



controllerWidget = CreateControllerWidget()
controllerWidget.show()