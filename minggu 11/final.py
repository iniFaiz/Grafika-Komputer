from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math


#note to self: jangan run aplikasi jika caps lock masih nyala soalnya inputnya gak bisa
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
throw_sensitivity_xy = 0.03
throw_sensitivity_z = 0.03
min_forward_throw_speed = 1.0

right_dragging = False
last_mouse_x_drag = 0
last_mouse_y_drag = 0
mouse_drag_sensitivity = 0.02

win_w, win_h = 800, 600

box_limit = 50.0
box_ceiling = 20.0

texture_id_floor = 0 

multisampling_enabled = True
anisotropic_filtering_enabled = True

initial_ball_pos_x = 0.0
initial_ball_pos_y = 2.0
initial_ball_pos_z = 0.0

is_hud_input_mode = False
hud_input_strings = ["0.0", "0.0", "0.0"] 
hud_input_current_field = 0 
hud_prompt_message = "Enter Vx,Vy,Vz. Enter:Next/Confirm. Esc:Cancel."

def normalize_vector(v):
    mag = math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    if mag == 0:
        return [0,0,0]
    return [v[0]/mag, v[1]/mag, v[2]/mag]

def cross_product(u, v):
    return [u[1]*v[2] - u[2]*v[1],
            u[2]*v[0] - u[0]*v[2],
            u[0]*v[1] - u[1]*v[0]]

def update_anisotropic_filtering_setting():
    global anisotropic_filtering_enabled, texture_id_floor
    if texture_id_floor == 0:
        if anisotropic_filtering_enabled:
             print("No Ingfo Anisotropic Filtering.")
        return

    glBindTexture(GL_TEXTURE_2D, texture_id_floor)
    extensions = glGetString(GL_EXTENSIONS)
    if extensions and b'GL_EXT_texture_filter_anisotropic' in extensions:
        try:
            GL_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FE
            GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT = 0x84FF
            
            if anisotropic_filtering_enabled:
                max_anisotropy_val = glGetFloatv(GL_MAX_TEXTURE_MAX_ANISOTROPY_EXT)
                if isinstance(max_anisotropy_val, (list, tuple)):
                    max_anisotropy_val = max_anisotropy_val[0]
                
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, max_anisotropy_val)
                print(f"Anisotropic filtering: ON (Max: {max_anisotropy_val})")
            else:
                glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAX_ANISOTROPY_EXT, 1.0)
                print("Anisotropic filtering: OFF (Level 1.0)")
        except GLError as e:
            print(f"Error setting anisotropic filtering.")
        except NameError:
             print("Anisotropic filtering constants.")
    else:
        if anisotropic_filtering_enabled:
            print("Anisotropic filtering On.")
        else:
            print("Anisotropic filtering Off.")
    glBindTexture(GL_TEXTURE_2D, 0)

def create_checkerboard_texture():
    global texture_id_floor
    tex_width = 256
    tex_height = 256
    texture_data = []
    for y in range(tex_height):
        for x in range(tex_width):
            if (x // 128) % 2 == (y // 128) % 2:
                texture_data.extend([255, 255, 255])    #Putih
            else:
                texture_data.extend([0, 0, 0])  #Hitam
    texture_data_bytes = bytes(texture_data)

    texture_id_floor = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id_floor)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    gluBuild2DMipmaps(GL_TEXTURE_2D, GL_RGB, tex_width, tex_height, 
                      GL_RGB, GL_UNSIGNED_BYTE, texture_data_bytes)
    glBindTexture(GL_TEXTURE_2D, 0)

def draw_floor():
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id_floor)

    glColor3f(0.8, 0.8, 0.8)

    texture_repeats = 25.0

    glBegin(GL_QUADS)
    #Kiri bawah
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-box_limit, -sphere_radius_val, -box_limit)
    #Kanan bawah
    glTexCoord2f(texture_repeats, 0.0)
    glVertex3f(box_limit, -sphere_radius_val, -box_limit)
    #Kanan atas
    glTexCoord2f(texture_repeats, texture_repeats)
    glVertex3f(box_limit, -sphere_radius_val, box_limit)
    #Kiri atas
    glTexCoord2f(0.0, texture_repeats)
    glVertex3f(-box_limit, -sphere_radius_val, box_limit)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def init():
    global multisampling_enabled
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    glClearColor(0.1, 0.1, 0.1, 1.0)
    
    create_checkerboard_texture()
    update_anisotropic_filtering_setting()

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    
    if multisampling_enabled:
        glEnable(GL_MULTISAMPLE)
        print("Multisampling: ON (Initial)")
    else:
        glDisable(GL_MULTISAMPLE)
        print("Multisampling: OFF (Initial)")


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
    global win_w, win_h, is_hud_input_mode, hud_input_strings, hud_input_current_field, hud_prompt_message
    global multisampling_enabled, anisotropic_filtering_enabled
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
    
    base_y_offset = 20
    line_height = 20

    help_lines = [
        "Kamera: W/A/S/D = maju/kiri/mundur/kanan",
        "I/K = pitch atas/bawah, J/L = yaw kiri/kanan",
        "Klik kiri + drag & lepas = lempar bola",
        "Klik kanan + drag = geser bola (horizontal) & putar",
        "R = Reset bola",
        "T = Lempar bola (HUD)" 
    ]
    help_lines.append(f"Multisampling (M): {'Nyala' if multisampling_enabled else 'Mati'}")
    help_lines.append(f"Anisotropic Filt. (N): {'Nyala' if anisotropic_filtering_enabled else 'Mati'}")
    
    for i, ln in enumerate(help_lines):
        draw_text(10, base_y_offset + i * line_height, ln)

    if is_hud_input_mode:
        hud_y_start = base_y_offset + (len(help_lines) + 1) * line_height
        draw_text(10, hud_y_start, hud_prompt_message)
        
        field_labels = ["Vx:", "Vy:", "Vz:"]
        for i in range(3):
            label = field_labels[i]
            value_str = hud_input_strings[i]
            if i == hud_input_current_field:
                value_str += "_" 
            draw_text(10, hud_y_start + (i + 1) * line_height, f"{label} {value_str}")

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
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id_floor)

    glColor3f(0.8, 0.8, 0.8)

    texture_repeats = 25.0

    glBegin(GL_QUADS)
    # Bottom-left
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-box_limit, -sphere_radius_val, -box_limit)
    # Bottom-right
    glTexCoord2f(texture_repeats, 0.0)
    glVertex3f(box_limit, -sphere_radius_val, -box_limit)
    # Top-right
    glTexCoord2f(texture_repeats, texture_repeats)
    glVertex3f(box_limit, -sphere_radius_val, box_limit)
    # Top-left
    glTexCoord2f(0.0, texture_repeats)
    glVertex3f(-box_limit, -sphere_radius_val, box_limit)
    glEnd()

    glDisable(GL_TEXTURE_2D)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    update_camera()

    world_light_direction = [1.0, 1.0, 1.0, 0.0]
    glLightfv(GL_LIGHT0, GL_POSITION, world_light_direction)

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
    global pos_x, pos_y, pos_z, vel_x, vel_y, vel_z, spin, spin_speed, rot_x_ball, rot_z_ball
    global is_aiming_throw
    global is_hud_input_mode, hud_input_strings, hud_input_current_field, throw_start_ball_pos_x, throw_start_ball_pos_y, throw_start_ball_pos_z
    global multisampling_enabled, anisotropic_filtering_enabled


    if is_hud_input_mode:
        current_string_ref = hud_input_strings[hud_input_current_field]

        if key == b'\r': 
            if not hud_input_strings[hud_input_current_field].strip() or \
               hud_input_strings[hud_input_current_field] == "-" or \
               hud_input_strings[hud_input_current_field] == ".":
                hud_input_strings[hud_input_current_field] = "0.0"
            
            hud_input_current_field += 1
            if hud_input_current_field > 2:
                try:
                    vx_val = float(hud_input_strings[0])
                    vy_val = float(hud_input_strings[1])
                    vz_val = float(hud_input_strings[2])
                    
                    pos_x = throw_start_ball_pos_x
                    pos_y = throw_start_ball_pos_y
                    pos_z = throw_start_ball_pos_z
                    vel_x, vel_y, vel_z = vx_val, vy_val, vz_val
                    
                    print(f"Bola dilempar dari HUD dengan kecepatan: X={vel_x}, Y={vel_y}, Z={vel_z}")
                    is_hud_input_mode = False
                    is_aiming_throw = False 
                except ValueError:
                    print("Input HUD tidak valid. Harap masukkan angka. Resetting HUD.")
                    hud_input_strings = ["0.0", "0.0", "0.0"]
                    hud_input_current_field = 0
            else:
                if not hud_input_strings[hud_input_current_field].strip():
                     hud_input_strings[hud_input_current_field] = "0.0"

        elif key == b'\x08':
            if len(current_string_ref) > 0:
                hud_input_strings[hud_input_current_field] = current_string_ref[:-1]
        elif key == b'\x1b':
            is_hud_input_mode = False
            is_aiming_throw = False 
            print("Input HUD dibatalkan.")
        else:
            try:
                char = key.decode('ascii')
                if char.isdigit():
                    if current_string_ref == "0" or current_string_ref == "0.0":
                        hud_input_strings[hud_input_current_field] = char
                    else:
                        hud_input_strings[hud_input_current_field] += char
                elif char == '.' and '.' not in current_string_ref:
                    if not current_string_ref or current_string_ref == "-":
                         hud_input_strings[hud_input_current_field] += "0."
                    else:
                        hud_input_strings[hud_input_current_field] += char
                elif char == '-' and len(current_string_ref) == 0:
                    hud_input_strings[hud_input_current_field] = char
            except UnicodeDecodeError:
                pass 
        glutPostRedisplay()
        return 

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
    elif key == b'r': 
        pos_x = initial_ball_pos_x
        pos_y = initial_ball_pos_y
        pos_z = initial_ball_pos_z
        vel_x, vel_y, vel_z = 0.0, 0.0, 0.0
        spin, spin_speed = 0.0, 0.0
        rot_x_ball, rot_z_ball = 0.0, 0.0
        is_aiming_throw = False
        is_hud_input_mode = False
        print("Bola direset ke posisi awal.")
    elif key == b't': 
        if not is_hud_input_mode:
            is_hud_input_mode = True
            is_aiming_throw = True
            throw_start_ball_pos_x = pos_x
            throw_start_ball_pos_y = pos_y
            throw_start_ball_pos_z = pos_z
            hud_input_strings = ["0.0", "0.0", "0.0"] 
            hud_input_current_field = 0
            print("Mode input HUD untuk lempar diaktifkan.")
        else:
            is_hud_input_mode = False
            is_aiming_throw = False
            print("Mode input HUD untuk lempar dibatalkan.")
    elif key == b'm': #Toggle Multisampling
        multisampling_enabled = not multisampling_enabled
        if multisampling_enabled:
            glEnable(GL_MULTISAMPLE)
            print("Multisampling: ON")
        else:
            glDisable(GL_MULTISAMPLE)
            print("Multisampling: OFF")
    elif key == b'n': #Toggle Anisotropic Filtering
        anisotropic_filtering_enabled = not anisotropic_filtering_enabled
        update_anisotropic_filtering_setting()
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
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_MULTISAMPLE) 
glutInitWindowSize(win_w, win_h)
glutCreateWindow(b"Bola FPS: WASD+IJKL | Mouse: Lempar (Kiri), Geser (Kanan)")
init()
throw_start_ball_pos_x = pos_x
throw_start_ball_pos_y = pos_y
throw_start_ball_pos_z = pos_z

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
