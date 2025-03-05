from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window_width = 800
window_height = 800

shapes = []

def add_point_to_shape(shape_index, x, y):
    global shapes
    while len(shapes) <= shape_index:
        shapes.append([])
    shapes[shape_index].append((x, y))
    glutPostRedisplay()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glScalef(10, 10, 1)
    
    glColor3f(0, 0, 0)
    
    for shape in shapes:
        if len(shape) >= 2:
            glBegin(GL_LINE_STRIP)
            for (x, y) in shape:
                glVertex2f(x, y)
            glEnd()
    
    glutSwapBuffers()


def reshape(width, height):
    global window_width, window_height
    window_width, window_height = width, height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(4.0)

def init():
    glClearColor(1, 1, 1, 1)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Grafikom K6")
    
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)

    # Ini buat titik titik cihiuy
    add_point_to_shape(0, 45, 35)
    add_point_to_shape(0, 40, 15)
    add_point_to_shape(0, 35, 35)
    add_point_to_shape(0, 28, 31.5)
    add_point_to_shape(0, 32, 39)
    add_point_to_shape(0, 12, 43)
    add_point_to_shape(0, 32, 49)
    add_point_to_shape(0, 28, 56)
    add_point_to_shape(0, 35, 52)
    add_point_to_shape(0, 40, 72)
    add_point_to_shape(0, 45, 52)
    add_point_to_shape(0, 52, 56)
    add_point_to_shape(0, 48, 49)
    add_point_to_shape(0, 68, 43)
    add_point_to_shape(0, 48, 39)
    add_point_to_shape(0, 52, 31.5)
    add_point_to_shape(0, 45, 35)

    
    glutMainLoop()

if __name__ == '__main__':
    main()
