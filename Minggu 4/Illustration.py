from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

window_width = 800
window_height = 800

shapes = []

focal_length = 13
object_distance = 20
object_size = 15

def add_point_to_shape(shape_index, x, y):
    """Add a point to the specified shape index."""
    global shapes
    while len(shapes) <= shape_index:
        shapes.append([])
    shapes[shape_index].append((x, y))
    glutPostRedisplay()

def draw_star(size):
    """Draw a star with the specified size, centered at (0,0)."""
    original_points = [
        (45, 35), (40, 15), (35, 35), (28, 31.5), (32, 39),
        (12, 43), (32, 49), (28, 56), (35, 52), (40, 72),
        (45, 52), (52, 56), (48, 49), (68, 43), (48, 39),
        (52, 31.5), (45, 35)
    ]
    
    min_x = min(x for x, y in original_points)
    max_x = max(x for x, y in original_points)
    min_y = min(y for x, y in original_points)
    max_y = max(y for x, y in original_points)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    original_width = max_x - min_x
    original_height = max_y - min_y
    
    scale_factor = size / max(original_width, original_height)
    
    for x, y in original_points:
        scaled_x = (x - center_x) * scale_factor
        scaled_y = (y - center_y) * scale_factor
        add_point_to_shape(0, scaled_x, scaled_y)

def calculate_image():
    di = 1 / (1/focal_length - 1/object_distance)
    m = -di / object_distance
    return di, m

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    glScalef(10, 10, 1)

    glColor3f(0, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, -40)
    glVertex2f(0, 40)
    glEnd()

    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(-object_distance, 0, 0)
    for shape in shapes:
        if len(shape) >= 2:
            glBegin(GL_LINE_STRIP)
            for (x, y) in shape:
                glVertex2f(x, y)
            glEnd()
    glPopMatrix()

    di, m = calculate_image()
    glColor3f(1, 0, 0)
    glPushMatrix()
    glTranslatef(di, 0, 0)
    glScalef(m, m, 1)
    for shape in shapes:
        if len(shape) >= 2:
            glBegin(GL_LINE_STRIP)
            for (x, y) in shape:
                glVertex2f(x, y)
            glEnd()
    glPopMatrix()

    glutSwapBuffers()

def reshape(width, height):
    global window_width, window_height
    window_width, window_height = width, height
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-width/2, width/2, -height/2, height/2, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLineWidth(4.0)

def init():
    glClearColor(1, 1, 1, 1) 

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Grafikom K8 - Illustration")
    
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    
    draw_star(object_size)
    
    glutMainLoop()

if __name__ == '__main__':
    main()
