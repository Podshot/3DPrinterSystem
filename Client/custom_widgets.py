from PySide import QtGui, QtOpenGL, QtCore
import stl
import sys

try:
    import OpenGL.GL as GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "STL Viewer",
                            "PyOpenGL must be installed to run this application.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)


class QReadOnlyCheckBox(QtGui.QCheckBox):

    def __init__(self, *args, **kwargs):
        QtGui.QCheckBox.__init__(self, *args, **kwargs)        
        self.is_modifiable = False
        self.clicked.connect(self.value_change_slot)

    def value_change_slot(self): 
        if self.isChecked():
            self.setChecked(self.is_modifiable)
        else:
            self.setChecked(not self.is_modifiable)            

    def setModifiable(self, flag):
        self.is_modifiable = flag            

    def isModifiable(self):
        return self.is_modifiable
    
class Triangle_Vertex:
    
    def __init__(self, data):
        self._x, self._y, self._z = data.strip().split(' ')[1:]
    
    def x(self):
        return self._x
    
    def y(self):
        return self._y
    
    def z(self):
        return self._z
    
class Triangle:
    
    def __init__(self, data):
        self._normal_x, self._normal_y, self._normal_z = data[0].strip().split(' ')[2:]
        self._vertices = []
        for line in data[1:]:
            if 'outer loop' in line: continue
            self._vertices.append(Triangle_Vertex(line))
            
    def vertices(self):
        return self._vertices
    
    def normal_x(self):
        return self._normal_x
    
    def normal_y(self):
        return self._normal_y
    
    def normal_z(self):
        return self._normal_z
    
class STLViewerWidget(QtOpenGL.QGLWidget,QtGui.QWidget):
    timerId= 0
    fieldSize = 20
    step = 2
    delay = 500
    cellsCount = 0
    pos = 1.0

    def __init__(self,parent=None):
        QtOpenGL.QGLWidget.__init__(self,parent)
        self.triangles = []
        self.object = 0
        self.xRot = 2440
        self.yRot = 2160
        self.zRot = 0
        self.lastPos = QtCore.QPoint()

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def setXRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.xRot:
            self.xRot = angle
            self.updateGL()

    def setYRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.yRot:
            self.yRot = angle
            self.updateGL()

    def setZRotation(self, angle):
        angle = self.normalizeAngle(angle)
        if angle != self.zRot:
            self.zRot = angle
            self.updateGL()

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor.fromCmykF(0.2, 0.2, 0.2, 0.0))
        GL.glShadeModel(GL.GL_SMOOTH)
        
        self.object = self.makeObject()
        
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, [1.0, 1.0, 1.0, 0.0])
        
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, [0.0, 1.0, 1.0, 0.0])
        
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glScalef(self.pos, self.pos, self.pos)
        GL.glTranslated(0.0, 0.0, -20.0)
        GL.glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        GL.glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        GL.glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        GL.glCallList(self.object)
        GL.glFlush()

    def resizeGL(self, width, height):
        side = max(width, height)
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-50, +50, +50, -50, -100.0, 500.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())
        if event.buttons() & QtCore.Qt.RightButton:
            pass

    def wheelEvent(self, event):
        if event.delta() > 0:
            self.pos += 0.2
        else:
            self.pos -= 0.2
        self.updateGL()

    def mouseMoveEvent(self,event):
        dx = -(event.x() - self.lastPos.x())
        dy = -(event.y() - self.lastPos.y())
        if event.buttons() & QtCore.Qt.LeftButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setYRotation(self.yRot + 8 * dx)
        elif event.buttons() & QtCore.Qt.MiddleButton:
            self.setXRotation(self.xRot + 8 * dy)
            self.setZRotation(self.zRot + 8 * dx)
        self.lastPos = QtCore.QPoint(event.pos())

    def makeObject(self):
        genList = GL.glGenLists(1)
        GL.glNewList(genList, GL.GL_COMPILE)
        self.axis()
        GL.glEndList()
        return genList

    def timerEvent(self, event):
        self.updateGL()

    def axis(self):
        
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_FRONT)
        
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT_AND_DIFFUSE, (0.0, 0.5804, 1.0, 0.0))
        GL.glMaterialfv(GL.GL_FRONT_AND_BACK, GL.GL_EMISSION, (0.25, 0.25, 0.25, 1.0))
        
        GL.glShadeModel(GL.GL_SMOOTH)

        GL.glBegin(GL.GL_TRIANGLES)
        for triangle in self.triangles:
            GL.glNormal3d(float(triangle.normal_x()), float(triangle.normal_y()), float(triangle.normal_z()))
            for vert in triangle.vertices():
                GL.glVertex3f(float(vert.x()), float(vert.y()), float(vert.z()))
        
        GL.glEnd()
        
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_DEPTH_TEST)

    def open(self, fileName):
        print fileName
        self.triangles = []
        if fileName:
            binary = False
            try:
                print "Trying ASCII loading"
                with open(fileName, 'rb') as _in:
                    stl.read_ascii_file(_in)
                print "ASCII File"
            except:
                print "Trying Binary loading"
                fp_in = open(fileName, 'rb')
                f = stl.read_binary_file(fp_in)
                fp_in.close()
                with open(fileName + "_", 'wb') as out:
                    f.write_ascii(out)
                print "Binary File"
                binary = True
            if binary:
                file = open(fileName + '_')
            else:
                file = open(fileName)
            lines = file.readlines()
            for i in xrange(len(lines)):
                line = lines[i].lstrip()
                if line.startswith("facet normal"):
                    self.triangles.append(Triangle(lines[i:i+5]))

    def normalizeAngle(self, angle):
        while angle < 0:
            angle += 360 * 16
        while angle > 360 * 16:
            angle -= 360 * 16
        return angle