import maya.cmds as mc

from PySide2.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

def CreateCircleController(jnt, size):
    name = "ac_" + jnt
    mc.circle(n = name, nr=(1,0,0), r = size/2)
    ctrlGrpName = name + "_grp"
    mc.group(name, n = ctrlGrpName)
    mc.matchTransform(ctrlGrpName, jnt)
    mc.orientConstraint(name, jnt)

    return name,ctrlGrpName



class CreateLimbControl:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""

    def FindJntsBasedOnRootSel(self):
        self.root = mc.ls(sl=True, type = "joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type ="joint")[0]
    
    def RigLimb(self):
        rootCtrl, rootCtrlGrp = CreateCircleController(self.root, 20)
        midCtrl, midCtrlGrp = CreateCircleController(self.mid, 20)
        endCtrl, endCtrlGRP = CreateCircleController(self.end, 20)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGRP, midCtrl)


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

        self.autoFindJntDisplay = QLabel("")
        self.masterlayout.addWidget(self.autoFindJntDisplay)
        self.adjustSize()

        rightLimbBtn = QPushButton("Rig Limb")
        rightLimbBtn.clicked.connect(self.RigLimbBtnClicked)
        self.masterlayout.addWidget(rightLimbBtn)

        self.createLimbCtrl = CreateLimbControl()

    def FindJntBtnClicked(self):
        self.createLimbCtrl.FindJntsBasedOnRootSel()
        self.autoFindJntDisplay.setText(f"{self.createLimbCtrl.root},{self.createLimbCtrl.mid},{self.createLimbCtrl.end}")
    
    def RigLimbBtnClicked(self):
        self.createLimbCtrl.RigLimb()


controllerWidget = CreateLimbControllerWidget()
controllerWidget.show()