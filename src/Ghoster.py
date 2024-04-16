import maya.cmds as mc
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QAbstractButton, QAbstractItemView

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

            dup = mc.duplicate(srcMesh, n = ghostName)
            mc.parent(ghostName, self.ghostGrp)
            mc.addAttr(ghostName, ln = self.frameAttr, dv = currentFrame)
    
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

    def GoToPrevGhost(self):
        pass

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



class GhostWidget(QWidget):
    def __init__(self):
        super().__init__() # needed to call if you are inheriting from a parent class. 
        self.ghost = Ghost() #create a ghost to pass command to. 
        self.setWindowTitle("Allen's Ghost")
        self.masterLayout = QVBoxLayout() # creates vertical layout
        self.setLayout(self.masterLayout) #tells the window to use the vertical layout created in the previous line

        self.srcMechList = QListWidget() # creates a list to show "stuff".
        self.srcMechList.setSelectionMode(QAbstractItemView.ExtendedSelection) #allow multi selection
        self.srcMechList.itemSelectionChanged.connect(self.SrcMeshSelectionChanged)
        self.srcMechList.addItems(self.ghost.srcMeshes)
        self.masterLayout.addWidget(self.srcMechList) # this adds the list created previously to the layout. 

        addSrcMeshBtn = QPushButton("Add Source Mesh")
        addSrcMeshBtn.clicked.connect(self.AddSrcMeshBtnClicked)
        self.masterLayout.addWidget(addSrcMeshBtn)

        self.ctrlLayout = QHBoxLayout()
        self.masterLayout.addLayout(self.ctrlLayout)

        addGhostBtn = QPushButton("Add")
        addGhostBtn.clicked.connect(self.ghost.AddGhost)
        self.ctrlLayout.addWidget(addGhostBtn)

        prevGhostBtn = QPushButton("Prev")


    def SrcMeshSelectionChanged (self):
        mc.select(cl=True)
        for item in self.srcMechList.selectedItems():
            mc.select(item.text(), add = True)
    
    def AddSrcMeshBtnClicked(self):
        self.ghost.SetSelectedAsSrcMesh() # asks ghost to populate its srcMeshes with the current selection
        self.srcMechList.clear() # this clears out list widget
        self.srcMechList.addItems(self.ghost.srcMeshes)



ghostWidget = GhostWidget()
ghostWidget.show()