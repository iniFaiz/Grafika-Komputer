from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math

pos_x = 0.0
pos_y = 2.0
pos_z = 0.0
vel_x = 0.0
vel_y = 0.0
vel_z = 0.0

gravity = -0.01
bounce = 0.85
bounce_friction = 0.7
sphere_radius_val = 1.0

spin = 0.0
spin_speed = 0.0
spin_decay = 0.98
rot_x_ball = 0.0
rot_z_ball = 0.0

cam_x = 0.0
cam_y = 2.0
cam_z = 10.0
cam_angle = 0.0
cam_pitch = 0.0
cam_speed = 0.2

is_aiming_throw = False
throw_start_mouse_x = 0
throw_start_mouse_y = 0
throw_start_ball_pos_x = 0.0
throw_start_ball_pos_y = 0.0
throw_start_ball_pos_z = 0.0
throw_sensitivity_xy = 0.02
throw_sensitivity_z = 0.03
min_forward_throw_speed = 1.0

right_dragging = False
last_mouse_x_drag = 0
last_mouse_y_drag = 0
mouse_drag_sensitivity = 0.02

win_w, win_h = 800, 600

box_limit = 50.0
box_ceiling = 20.0

def normalize_vector(v):
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag == 0:
        return [0,0,0]
    return [v[0]/mag, v[1]/mag, v[2]/mag]

def cross_product(u, v):
    return [u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0]]

def init():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glClearColor(0.1, 0.1, 0.1, 1.0)

def update_camera():
    global lx_cam, ly_cam, lz_cam
    lx_cam = math.cos(cam_pitch) * math.sin(cam_angle)
    ly_cam = math.sin(cam_pitch)
    lz_cam = -math.cos(cam_pitch) * math.cos(cam_angle)
    gluLookAt(cam_x, cam_y, cam_z, cam_x + lx_cam, cam_y + ly_cam, cam_z + lz_cam, 0.0, 1.0, 0.0)

lx_cam, ly_cam, lz_cam = 0,0,0


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
        "Kamera: W/A/S/D = maju/kiri/mundur/kanan",
        "I/K = pitch atas/bawah, J/L = yaw kiri/kanan",
        "Klik kiri + drag & lepas = lempar bola",
        "Klik kanan + drag = geser bola (horizontal) & putar"
    ]
    y_offset = 20
    for i, ln in enumerate(lines):
        draw_text(10, y_offset + i * 20, ln)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_globe_grid(radius=1.0, lat_steps=12, long_steps=24):
    glDisable(GL_LIGHTING)
    glColor3f(0.7, 0.7, 1.0)
    
    for j in range(long_steps):
        phi = 2 * math.pi * j / long_steps
        glBegin(GL_LINE_LOOP)
        for i in range(lat_steps + 1):
            theta = math.pi * i / lat_steps - math.pi/2
            x_coord = radius * math.cos(theta) * math.cos(phi)
            y_coord_val = radius * math.sin(theta)
            z_coord = radius * math.cos(theta) * math.sin(phi)
            glVertex3f(x_coord, y_coord_val, z_coord)
        glEnd()

    for i in range(1, lat_steps):
        theta = math.pi * i / lat_steps - math.pi/2
        glBegin(GL_LINE_LOOP)
        for j in range(long_steps):
            phi = 2 * math.pi * j / long_steps
            x_coord = radius * math.cos(theta) * math.cos(phi)
            y_coord_val = radius * math.sin(theta)
            z_coord = radius * math.cos(theta) * math.sin(phi)
            glVertex3f(x_coord, y_coord_val, z_coord)
        glEnd()
    glEnable(GL_LIGHTING)


def draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-50, -sphere_radius_val, -50)
    glVertex3f(50, -sphere_radius_val, -50)
    glVertex3f(50, -sphere_radius_val, 50)
    glVertex3f(-50, -sphere_radius_val, 50)
    glEnd()
    glEnable(GL_LIGHTING)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_camera()
    draw_floor()

    glPushMatrix()
    glTranslatef(pos_x, pos_y, pos_z)
    
    glRotatef(spin, 1.0, 0.0, 0.0)
    glRotatef(rot_x_ball, 1.0, 0.0, 0.0)
    glRotatef(rot_z_ball, 0.0, 0.0, 1.0)
    
    glColor3f(0.2, 0.6, 1.0)
    draw_globe_grid(radius=sphere_radius_val, lat_steps=12, long_steps=24)
    glPopMatrix()

    draw_hud()
    glutSwapBuffers()

def reshape(w, h):
    global win_w, win_h
    win_w, win_h = w, h
    if h == 0: h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(w) / h, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

def keyboard(key, x_mouse, y_mouse):
    global cam_x, cam_y, cam_z, cam_angle, cam_pitch

    cam_forward_x_move = math.cos(cam_pitch) * math.sin(cam_angle)
    cam_forward_z_move = -math.cos(cam_pitch) * math.cos(cam_angle)
    cam_right_x_move = math.cos(cam_angle)
    cam_right_z_move = math.sin(cam_angle)

    if key == b'w':
        cam_x += cam_forward_x_move * cam_speed
        cam_z += cam_forward_z_move * cam_speed
    elif key == b's':
        cam_x -= cam_forward_x_move * cam_speed
        cam_z -= cam_forward_z_move * cam_speed
    elif key == b'a':
        cam_x -= cam_right_x_move * cam_speed
        cam_z -= cam_right_z_move * cam_speed
    elif key == b'd':
        cam_x += cam_right_x_move * cam_speed
        cam_z += cam_right_z_move * cam_speed
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

    pitch_limit = math.radians(89.0)
    cam_pitch = max(-pitch_limit, min(pitch_limit, cam_pitch))
    cam_angle %= (2 * math.pi)
    glutPostRedisplay()

def mouse(button, state, x, y_coord):
    global is_aiming_throw, throw_start_mouse_x, throw_start_mouse_y
    global throw_start_ball_pos_x, throw_start_ball_pos_y, throw_start_ball_pos_z
    global vel_x, vel_y, vel_z, spin_speed, pos_x, pos_y, pos_z
    global right_dragging, last_mouse_x_drag, last_mouse_y_drag

    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            is_aiming_throw = True
            throw_start_mouse_x = x
            throw_start_mouse_y = y_coord
            throw_start_ball_pos_x = pos_x
            throw_start_ball_pos_y = pos_y
            throw_start_ball_pos_z = pos_z
            vel_x, vel_y, vel_z = 0.0, 0.0, 0.0
            spin_speed = 0.0
        elif state == GLUT_UP:
            if is_aiming_throw:
                is_aiming_throw = False
                pos_x = throw_start_ball_pos_x
                pos_y = throw_start_ball_pos_y
                pos_z = throw_start_ball_pos_z

                drag_dx_screen = x - throw_start_mouse_x
                drag_dy_screen = y_coord - throw_start_mouse_y

                v_cam_x = drag_dx_screen * throw_sensitivity_xy
                v_cam_y = -drag_dy_screen * throw_sensitivity_xy
                v_cam_z = max(min_forward_throw_speed, -drag_dy_screen * throw_sensitivity_z)

                fwd_vec = [lx_cam, ly_cam, lz_cam]

                global_up = [0.0, 1.0, 0.0]
                
                z_cam_w = [-lx_cam, -ly_cam, -lz_cam]
                x_cam_w = normalize_vector(cross_product(global_up, z_cam_w))
                
                if abs(fwd_vec[0]) < 1e-4 and abs(fwd_vec[2]) < 1e-4 :
                    x_cam_w = normalize_vector([math.cos(cam_angle), 0, math.sin(cam_angle)])

                y_cam_w = normalize_vector(cross_product(z_cam_w, x_cam_w))

                vel_x = x_cam_w[0] * v_cam_x + y_cam_w[0] * v_cam_y + fwd_vec[0] * v_cam_z
                vel_y = x_cam_w[1] * v_cam_x + y_cam_w[1] * v_cam_y + fwd_vec[1] * v_cam_z
                vel_z = x_cam_w[2] * v_cam_x + y_cam_w[2] * v_cam_y + fwd_vec[2] * v_cam_z
                
    elif button == GLUT_RIGHT_BUTTON:
        if state == GLUT_DOWN:
            right_dragging = True
            last_mouse_x_drag = x
            last_mouse_y_drag = y_coord
        elif state == GLUT_UP:
            right_dragging = False

def motion(x, y_coord):
    global pos_x, pos_z, last_mouse_x_drag, last_mouse_y_drag, rot_x_ball, rot_z_ball

    if right_dragging:
        delta_mouse_x = x - last_mouse_x_drag
        delta_mouse_y = y_coord - last_mouse_y_drag

        screen_dx = delta_mouse_x * mouse_drag_sensitivity
        screen_dy = delta_mouse_y * mouse_drag_sensitivity

        cam_forward_x_world = math.sin(cam_angle)
        cam_forward_z_world = -math.cos(cam_angle)
        cam_right_x_world = math.cos(cam_angle)
        cam_right_z_world = math.sin(cam_angle)
        
        delta_world_x = (cam_right_x_world * screen_dx) - (cam_forward_x_world * screen_dy)
        delta_world_z = (cam_right_z_world * screen_dx) - (cam_forward_z_world * screen_dy)
        
        pos_x += delta_world_x
        pos_z += delta_world_z

        if sphere_radius_val != 0:
            rot_z_ball = (rot_z_ball - (delta_world_x / sphere_radius_val) * (180.0 / math.pi)) % 360
            rot_x_ball = (rot_x_ball + (delta_world_z / sphere_radius_val) * (180.0 / math.pi)) % 360
        
        last_mouse_x_drag = x
        last_mouse_y_drag = y_coord
        glutPostRedisplay()


def timer(value):
    global pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, spin, spin_speed

    if not is_aiming_throw:
        vel_y += gravity
        pos_x += vel_x
        pos_y += vel_y
        pos_z += vel_z

        if not right_dragging:
            vel_x *= 0.99
            vel_z *= 0.99

        if pos_y < 0.0: 
            pos_y = 0.0
            vel_y = -vel_y * bounce
            vel_x *= bounce_friction 
            vel_z *= bounce_friction
            
            if abs(vel_y / bounce) > 0.05 : 
                 spin_speed = abs(vel_x) + abs(vel_z) + abs(vel_y)
                 spin_speed *= 2
            else: 
                if abs(vel_y) < 0.01: vel_y = 0.0
                if math.sqrt(vel_x**2 + vel_z**2) < 0.01:
                    vel_x = 0.0
                    vel_z = 0.0
                spin_speed = 0.0
        
        if abs(spin_speed) > 0.01:
            spin = (spin + spin_speed) % 360
            spin_speed *= spin_decay
        else:
            spin_speed = 0.0

        if pos_x < -box_limit:
            pos_x = -box_limit
            vel_x = -vel_x * bounce_friction
        elif pos_x > box_limit:
            pos_x = box_limit
            vel_x = -vel_x * bounce_friction

        if pos_z < -box_limit:
            pos_z = -box_limit
            vel_z = -vel_z * bounce_friction
        elif pos_z > box_limit:
            pos_z = box_limit
            vel_z = -vel_z * bounce_friction

        if pos_y > box_ceiling:
            pos_y = box_ceiling
            vel_y = -vel_y * bounce_friction
            
    elif is_aiming_throw:
        vel_x, vel_y, vel_z = 0.0, 0.0, 0.0
        spin_speed = 0.0
        pos_x = throw_start_ball_pos_x
        pos_y = throw_start_ball_pos_y
        pos_z = throw_start_ball_pos_z


    if right_dragging and pos_y < 0.001:
         vel_y = 0.0


    glutPostRedisplay()
    glutTimerFunc(16, timer, 0)

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutInitWindowSize(win_w, win_h)
glutCreateWindow(b"Bola FPS: WASD+IJKL | Mouse: Lempar (Kiri), Geser (Kanan)")
init()
lx_cam = math.cos(cam_pitch) * math.sin(cam_angle)
ly_cam = math.sin(cam_pitch)
lz_cam = -math.cos(cam_pitch) * math.cos(cam_angle)

glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutMouseFunc(mouse)
glutMotionFunc(motion)
glutTimerFunc(16, timer, 0)
glutMainLoop()
