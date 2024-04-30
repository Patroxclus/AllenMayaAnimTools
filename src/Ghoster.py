import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QAbstractButton, QAbstractItemView, QColorDialog
from PySide2.QtGui import QColor, QPainter, QBrush
def GetCurrentFrame():
    return int(mc.currentTime(q=True))

class Ghost:
    def __init__(self):
        self.srcMeshes = set() # a set is a list that has unique elements.
        self.ghostGrp = "ghost_grp"
        self.frameAttr = "frame"
        self.srcAttr = "src"

    def InitIfGhostGrpNotExist(self):
        if mc.objExists(self.ghostGrp):
            storedSrcMeshes = mc.getAttr(self.ghostGrp + "." + self.srcAttr)
            self.srcMeshes = set(storedSrcMeshes.split(","))
            return
        
        mc.createNode("transform", n = self.ghostGrp)
        mc.addAttr(self.ghostGrp, ln = self.srcAttr, dt="string")
    
    def SetSelectedAsSrcMesh(self):
        selection = mc.ls(sl=True)
        self.srcMeshes.clear() # removes all elements in the set.
        for selected in selection:
            shapes = mc.listRelatives(selected, s=True)
            for s in shapes:
                if mc.objectType(s) == "mesh" : #the object is a mesh
                    self.srcMeshes.add(selected) # add the mesh to our set
    


    def AddGhost(self):
        for srcMesh in self.srcMeshes:
            currentFrame = GetCurrentFrame()
            ghostName = srcMesh + "_" + str(currentFrame)
            if mc.objExists(ghostName):
                mc.delete(ghostName)

            dup = mc.duplicate(srcMesh, n=ghostName)
            # Create the group if it doesn't exist
            if not mc.objExists(self.ghostGrp):
                mc.createNode("transform", n=self.ghostGrp)
            # Parent the duplicate under the group
            mc.parent(ghostName, self.ghostGrp)
            mc.addAttr(ghostName, ln=self.frameAttr, dv=currentFrame)

            matName = self.GetMaterialNameForGhost(ghostName) #figure out the name for the material
            if not mc.objExists(matName):
                mc.shadingNode("lambert", asShader= True, name = matName)
            
            sgName = self.GetShadingEngineForGhost(ghostName)
            if not mc.objExists(sgName):
                mc.sets(name = sgName, renderable = True, empty = True)

            mc.connectAttr(matName + ".outColor", sgName + ".surfaceShader", force = True)
            mc.sets(ghostName, edit=True, forceElement = sgName)


    def GetMaterialNameForGhost(self, ghost):
        return ghost + "_mat"


    def GetShadingEngineForGhost(self, ghost):
        return ghost + "_sg"
    
    
                           
    def DeleteAllGhosts(self):
        if mc.objExists(self.ghostGrp):
            ghosts = mc.listRelatives(self.ghostGrp, c=True) or []
            for ghost in ghosts:
                self.DeleteGhost(ghost)

    def GoToNextGhost(self):
        frames = self.GetGhostFramesSorted()
        if not frames:
            return
        
        currentFrame = GetCurrentFrame()
        for frame in frames:
            if frame > currentFrame:
                mc.currentTime(frame, e=True)
                return
        
        mc.currentTime(frames[0], e=True)

    def DeleteGhostOnFrame(self, frame):
        ghosts = mc.listRelatives(self.ghostGrp, c=True) or []
        for ghost in ghosts:
            ghost_frame = mc.getAttr(ghost + "." + self.frameAttr)
            if ghost_frame == frame:
                self.DeleteGhost(ghost)

    def DeleteGhost(self, ghost):
        mat = self.GetMaterialNameForGhost(ghost)
        if mc.objExists(mat):
            mc.delete(mat)
        sg = self.GetShadingEngineForGhost(ghost)
        if mc.objExists(sg):
            mc.delete(sg)

        if mc.objExists(ghost):
            mc.delete(ghost)


    def GoToPrevGhost(self):
        frames = self.GetGhostFramesSorted()
        if not frames:
            return
        currentFrame = GetCurrentFrame()
        frames.reverse()
        for frame in frames:
            if frame < currentFrame:
                mc.currentTime(frame, e=True)
                return


    def GetGhostFramesSorted(self):
        frames = set()
        ghosts = mc.listRelatives(self.ghostGrp, c =True)
        if not ghosts:
            return[]
        
        for ghost in ghosts:
            frame = mc.getAttr(ghost + "." + self.frameAttr)
            frames.add(frame)

        frames = list(frames)
        frames.sort()
        return frames

class ColorPicker(QWidget):
    def __init__(self, width = 80, height = 20):
        super().__init__()
        self.setFixedSize(width, height)
        self.color = QColor()

    def mousePressEvent(self, event):
        color = QColorDialog().getcolor(self.color)
        self.color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QBrush(self.color))
        painter.drawRect(0,0,self.wdith(), self.height())


class GhostWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.ghost = Ghost()
        self.setWindowTitle("Allen's Ghost")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.srcMechList = QListWidget()
        self.srcMechList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.srcMechList.itemSelectionChanged.connect(self.SrcMeshSelectionChanged)
        self.srcMechList.addItems(self.ghost.srcMeshes)
        self.masterLayout.addWidget(self.srcMechList)

        addSrcMeshBtn = QPushButton("Add Source Mesh")
        addSrcMeshBtn.clicked.connect(self.AddSrcMeshBtnClicked)
        self.masterLayout.addWidget(addSrcMeshBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.ctrlLayout)

        addGhostBtn = QPushButton("Add")
        addGhostBtn.clicked.connect(self.ghost.AddGhost)
        self.ctrlLayout.addWidget(addGhostBtn)

        prevGhostBtn = QPushButton("Prev")
        prevGhostBtn.clicked.connect(self.ghost.GoToPrevGhost)
        self.ctrlLayout.addWidget(prevGhostBtn)

        nextGhostBtn = QPushButton("Next")
        nextGhostBtn.clicked.connect(self.ghost.GoToNextGhost)
        self.ctrlLayout.addWidget(nextGhostBtn)

        self.deleteLayout = QHBoxLayout()  # Create a layout for delete buttons
        self.masterLayout.addLayout(self.deleteLayout)  # Add delete layout to master layout

        deleteGhostOnFrameBtn = QPushButton("Delete Ghost on Frame")
        deleteGhostOnFrameBtn.clicked.connect(self.DeleteGhostOnFrameBtnClicked)
        self.deleteLayout.addWidget(deleteGhostOnFrameBtn)

        deleteAllGhostsBtn = QPushButton("Delete All Ghosts")
        deleteAllGhostsBtn.clicked.connect(self.DeleteAllGhostsBtnClicked)
        self.deleteLayout.addWidget(deleteAllGhostsBtn)

        colorPicker = ColorPicker()
        self.masterLayout.addWidget(colorPicker)

    def SrcMeshSelectionChanged(self):
        mc.select(cl=True)
        for item in self.srcMechList.selectedItems():
            mc.select(item.text(), add=True)

    def AddSrcMeshBtnClicked(self):
        self.ghost.SetSelectedAsSrcMesh()
        self.srcMechList.clear()
        self.srcMechList.addItems(self.ghost.srcMeshes)

    def DeleteGhostOnFrameBtnClicked(self):
        # Get the current frame
        currentFrame = GetCurrentFrame()
        # Call the DeleteGhostOnFrame method of the Ghost object
        self.ghost.DeleteGhostOnFrame(currentFrame)

    def DeleteAllGhostsBtnClicked(self):
        self.ghost.DeleteAllGhosts()

ghostWidget = GhostWidget()
ghostWidget.show()