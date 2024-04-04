import maya.cmds as mc

from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

class CreateLimbControl:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""

    def FindJntsBasedOnRootSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.end, c=True, type ="joint")[0]

class CreateLimbControllerWidget(QWidget):
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



controllerWidget = CreateLimbControllerWidget()
controllerWidget.show()