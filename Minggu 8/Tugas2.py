from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

pos_y = 2.0
vel_y = 0.0
gravity = -0.01
bounce = 0.85
spin = 0.0
spin_speed = 0.0
spin_decay = 0.98

cam_x = 0.0
cam_y = 2.0
cam_z = 10.0
cam_angle = 0.0
cam_pitch = 0.0
cam_speed = 0.2

lifting = False
last_y = 0

win_w, win_h = 800, 600

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glClearColor(0.1, 0.1, 0.1, 1.0)

def update_camera():
    lx = math.cos(cam_pitch) * math.sin(cam_angle)
    ly = math.sin(cam_pitch)
    lz = -math.cos(cam_pitch) * math.cos(cam_angle)
    gluLookAt(cam_x, cam_y, cam_z, cam_x + lx, cam_y + ly, cam_z + lz, 0.0, 1.0, 0.0)

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))

def draw_hud():
    global win_w, win_h
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, win_w, 0, win_h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glColor3f(1.0, 1.0, 1.0)
    lines = [
        "Camera: W/A/S/D = forward/left/back/right",
        "I/K = pitch up/down, J/L = yaw left/right",
        "Left-click + drag = angkat bola"
    ]
    y = 20
    for ln in lines:
        draw_text(10, y, ln)
        y += 20

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_equator(radius=1.0, segments=100):
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        x = radius * math.cos(theta)
        y = 0
        z = radius * math.sin(theta)
        glVertex3f(x, y, z)
    glEnd()

def draw_meridian(radius=1.0, segments=100):
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_LOOP)
    for i in range(segments):
        theta = 2 * math.pi * i / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = 0
        glVertex3f(x, y, z)
    glEnd()

def draw_globe_grid(radius=1.0, lat_steps=12, long_steps=24):
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    for j in range(long_steps):
        phi = 2 * math.pi * j / long_steps
        glBegin(GL_LINE_LOOP)
        for i in range(lat_steps + 1):
            theta = math.pi * i / lat_steps - math.pi/2
            x = radius * math.cos(theta) * math.cos(phi)
            y = radius * math.sin(theta)
            z = radius * math.cos(theta) * math.sin(phi)
            glVertex3f(x, y, z)
        glEnd()

    glColor3f(1.0, 1.0, 1.0)
    for i in range(1, lat_steps):
        theta = math.pi * i / lat_steps - math.pi/2
        glBegin(GL_LINE_LOOP)
        for j in range(long_steps):
            phi = 2 * math.pi * j / long_steps
            x = radius * math.cos(theta) * math.cos(phi)
            y = radius * math.sin(theta)
            z = radius * math.cos(theta) * math.sin(phi)
            glVertex3f(x, y, z)
        glEnd()
    glEnable(GL_LIGHTING)

def draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-50, -1.0, -50)
    glVertex3f(50, -1.0, -50)
    glVertex3f(50, -1.0, 50)
    glVertex3f(-50, -1.0, 50)
    glEnd()
    glEnable(GL_LIGHTING)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_camera()
    draw_floor()

    glPushMatrix()
    glTranslatef(0.0, pos_y, 0.0)
    glRotatef(spin, 1.0, 0.0, 0.0)
    draw_globe_grid(radius=1.0, lat_steps=12, long_steps=24)
    glPopMatrix()

    draw_hud()
    glutSwapBuffers()

def reshape(w, h):
    global win_w, win_h
    win_w, win_h = w, h
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, w / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x, y):
    global cam_x, cam_y, cam_z, cam_angle, cam_pitch

    forward_x = math.cos(cam_pitch) * math.sin(cam_angle)
    forward_z = -math.cos(cam_pitch) * math.cos(cam_angle)
    right_x = math.cos(cam_angle)
    right_z = math.sin(cam_angle)

    if key == b'w':
        cam_x += forward_x * cam_speed
        cam_z += forward_z * cam_speed
    elif key == b's':
        cam_x -= forward_x * cam_speed
        cam_z -= forward_z * cam_speed
    elif key == b'a':
        cam_x -= right_x * cam_speed
        cam_z -= right_z * cam_speed
    elif key == b'd':
        cam_x += right_x * cam_speed
        cam_z += right_z * cam_speed
    elif key == b'i':
        cam_pitch += 0.05
    elif key == b'k':
        cam_pitch -= 0.05
    elif key == b'j':
        cam_angle -= 0.05
    elif key == b'l':
        cam_angle += 0.05
    elif key == b'\x1b':
        exit(0)

    pitch_limit = math.radians(89)
    cam_pitch = max(-pitch_limit, min(pitch_limit, cam_pitch))

    glutPostRedisplay()

def mouse(button, state, x, y):
    global lifting, last_y, vel_y, spin_speed
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            lifting = True
            last_y = y
            vel_y = 0.0
            spin_speed = 0.0
        elif state == GLUT_UP:
            lifting = False

def motion(x, y):
    global pos_y, last_y
    if lifting:
        dy = y - last_y
        pos_y += -dy * 0.01
        pos_y = max(pos_y, 1.0)
        last_y = y
        glutPostRedisplay()

def timer(i):
    global pos_y, vel_y, spin, spin_speed
    if lifting:
        glutPostRedisplay()
        glutTimerFunc(16, timer, 1)
        return

    vel_y += gravity
    pos_y += vel_y

    if pos_y - 1.0 < -1.0:
        pos_y = 0.0
        vel_y = -vel_y * bounce
        spin_speed = abs(vel_y) * 10
        if abs(vel_y) < 0.01:
            vel_y = 0.0
            spin_speed = 0.0

    if abs(spin_speed) > 0.01:
        spin = (spin + spin_speed) % 360
        spin_speed *= spin_decay
    else:
        spin_speed = 0.0

    glutPostRedisplay()
    glutTimerFunc(16, timer, 1)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(800, 600)
glutCreateWindow(b"Bola + Kamera FPS (WASD + IJKL)")
init()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutTimerFunc(16, timer, 1)
glutMainLoop()
