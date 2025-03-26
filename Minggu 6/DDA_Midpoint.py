from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

window_width = 800
window_height = 800

shapes = []

focal_length = 10
object_distance = 20
object_size = 20

def draw_text(x, y, text):
    glRasterPos2f(x, y)
    for c in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(c))

def add_point_to_shape(shape_index, x, y):
    global shapes
    while len(shapes) <= shape_index:
        shapes.append([])
    shapes[shape_index].append((x, y))
    glutPostRedisplay()

current_slider = -1
sliders = [
    {"label": "Ukuran Benda", "value": lambda: object_size, "setter": lambda v: set_object_size(v), "min": 1, "max": 100},
    {"label": "Jarak Benda", "value": lambda: object_distance, "setter": lambda v: set_object_distance(v), "min": 1, "max": 200},
    {"label": "Titik Fokus", "value": lambda: focal_length, "setter": lambda v: set_focal_length(v), "min": 1, "max": 50},
]

def set_object_size(v):
    global object_size, shapes
    object_size = v
    if len(shapes) == 0:
        shapes.append([])
    shapes[0].clear()
    draw_star(object_size)

def set_object_distance(v):
    global object_distance
    object_distance = v

def set_focal_length(v):
    global focal_length
    focal_length = v

def draw_slider(slider_index, x, y, width=200, height=15):
    s = sliders[slider_index]
    val  = s["value"]()
    vmin = s["min"]
    vmax = s["max"]
    frac = (val - vmin) / float(vmax - vmin)

    glColor3f(0.7, 0.7, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x+width, y)
    glVertex2f(x+width, y+height)
    glVertex2f(x, y+height)
    glEnd()

    handle_x = x + frac * width
    glColor3f(0, 0, 1)
    glBegin(GL_QUADS)
    glVertex2f(handle_x-5, y)
    glVertex2f(handle_x+5, y)
    glVertex2f(handle_x+5, y+height)
    glVertex2f(handle_x-5, y+height)
    glEnd()

    draw_text(x, y+height+5, f"{s['label']}: {int(val)}")

def update_slider_value(mx, my):
    global current_slider
    if current_slider < 0:
        return
    s = sliders[current_slider]
    slider_x = 190
    slider_y = 350 - current_slider * 60
    slider_width  = 200
    slider_height = 15

    if mx < slider_x:
        mx = slider_x
    if mx > slider_x + slider_width:
        mx = slider_x + slider_width

    frac = (mx - slider_x) / slider_width
    new_val = s["min"] + frac * (s["max"] - s["min"])
    s["setter"](new_val)
    glutPostRedisplay()

def mouse_func(button, state, x, y):
    global current_slider
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        ortho_x = x - (window_width/2)
        ortho_y = (window_height/2) - y
        for i in range(len(sliders)):
            sx = 190
            sy = 350 - i * 60
            sw = 200
            sh = 15
            if sx <= ortho_x <= sx+sw and sy <= ortho_y <= sy+sh:
                current_slider = i
                update_slider_value(ortho_x, ortho_y)
                break
    elif button == GLUT_LEFT_BUTTON and state == GLUT_UP:
        current_slider = -1

def motion_func(x, y):
    if current_slider < 0:
        return
    ortho_x = x - (window_width/2)
    ortho_y = (window_height/2) - y
    update_slider_value(ortho_x, ortho_y)


def draw_star(size):
    original_points = [
        (40, 72), (45, 52), (52, 56), (48, 49), (68, 43),
        (48, 39), (52, 31.5), (45, 35), (40, 15), (35, 35),
        (28, 31.5), (32, 39), (12, 43), (32, 49), (28, 56),
        (35, 52), (40, 72), (40, 80)
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

def get_shapes_bounds():
    if not shapes or not any(len(s) for s in shapes):
        return 0, 0
    all_points = [p for shape in shapes for p in shape]
    minY = min(pt[1] for pt in all_points)
    maxY = max(pt[1] for pt in all_points)
    return minY, maxY

def draw_circle(radius, x_center=0, y_center=0):
    x = radius
    y = 0
    p = 1 - radius

    glBegin(GL_POINTS)
    while x >= y:
        glVertex2f(x_center + x, y_center + y)
        glVertex2f(x_center - x, y_center + y)
        glVertex2f(x_center + x, y_center - y)
        glVertex2f(x_center - x, y_center - y)
        glVertex2f(x_center + y, y_center + x)
        glVertex2f(x_center - y, y_center + x)
        glVertex2f(x_center + y, y_center - x)
        glVertex2f(x_center - y, y_center - x)

        y += 1
        if p <= 0:
            p = p + 2*y + 1
        else:
            x -= 1
            p = p + 2*(y - x) + 1
    glEnd()

def draw_lensa():
    glLineWidth(1.5)
    glColor3f(1, 0.5, 0)
    fixed_height = 45
    
    radius_horizontal = 2 + (15 / max(1, focal_length)) * 8
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        theta = math.pi * 2 * i / 360
        x = radius_horizontal * math.cos(theta) * 0.2 
        y = fixed_height * math.sin(theta) 
        glVertex2f(x, y)
    glEnd()

    glBegin(GL_LINES)
    glColor3f(0, 1, 0)
    glVertex2f(0, -fixed_height*1.5)
    glVertex2f(0, fixed_height*1.5)
    glEnd()

def draw_rays():
    EXT = 1000 
    minY, maxY = get_shapes_bounds()
    obj_top = maxY - minY

    di, m = calculate_image()
    obj_tip = (-object_distance, obj_top)
    img_tip = (di, m * obj_top)
    
    # Sinar 1
    glColor3f(1, 0, 0) 
    glBegin(GL_LINES)
    glVertex2f(-EXT, obj_tip[1])
    glVertex2f(0, obj_tip[1])
    glEnd()

    m_r = (img_tip[1] - obj_tip[1]) / (img_tip[0] - 0)
    y_EXT = obj_tip[1] + m_r * (EXT - 0)

    glColor3f(1, 0, 1) 
    glBegin(GL_LINES)
    glVertex2f(0, obj_tip[1])
    glVertex2f(EXT, y_EXT)
    glEnd()

    # Sinar 2
    t0 = -obj_tip[0] / (img_tip[0] - obj_tip[0])
    intersect_y = obj_tip[1] + t0 * (img_tip[1] - obj_tip[1])
    y_left = obj_tip[1] + (img_tip[1] - obj_tip[1]) * ((-EXT) - obj_tip[0]) / (img_tip[0] - obj_tip[0])
    y_right = obj_tip[1] + (img_tip[1] - obj_tip[1]) * ((EXT) - obj_tip[0]) / (img_tip[0] - obj_tip[0])
    glColor3f(1, 0, 0) 
    glBegin(GL_LINES)
    glVertex2f(-EXT, y_left)
    glVertex2f(0, intersect_y)
    glEnd()
    glColor3f(1, 0, 1)
    glBegin(GL_LINES)
    glVertex2f(0, intersect_y)
    glVertex2f(EXT, y_right)
    glEnd()

    # Sinar 3
    t = object_distance / (object_distance - focal_length)
    y_int = obj_top + t * (0 - obj_top)
    y_left_ray3 = obj_tip[1] + (y_int - obj_tip[1]) * ((-EXT) - obj_tip[0]) / (0 - obj_tip[0])
    glColor3f(1, 0, 0) 
    glBegin(GL_LINES)
    glVertex2f(-EXT, y_left_ray3)
    glVertex2f(0, y_int)
    glEnd()
    glColor3f(1, 0, 1) 
    glBegin(GL_LINES)
    glVertex2f(0, y_int)
    glVertex2f(EXT, y_int)
    glEnd()

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    for i in range(len(sliders)):
        draw_slider(i, 190, 350 - i*60)

    di, m = calculate_image()
    draw_text(-390, 350, f"Ukuran Benda: {round(object_size, 1)}")
    draw_text(-390, 320, f"Jarak Benda: {round(object_distance, 1)}")
    draw_text(-390, 290, f"Titik Fokus: {round(focal_length, 1)}")
    draw_text(-390, 260, f"Jarak Bayangan: {round(di, 1)}")
    draw_text(-390, 230, f"Ukuran Bayangan: {round(m*object_size, 1)}")

    glScalef(10, 10, 1)

    draw_lensa()
    
    glColor3f(0, 0, 0)
    glBegin(GL_LINES)
    glVertex2f(-100, 0)
    glVertex2f(100, 0)
    glEnd()

    glColor3f(0, 0, 0)
    glBegin(GL_LINES)
    glVertex2f(-100, 0)
    glVertex2f(100, 0)
    glEnd()

    r = 2 * focal_length
    glColor3f(1, 0, 0)
    draw_text(focal_length, 1, "f")
    draw_text(-focal_length, 1, "f")
    draw_text(r, 1, "r") 
    draw_text(-r, 1, "r")

    glBegin(GL_LINES)
    glVertex2f(focal_length, 0)
    glVertex2f(focal_length, 0.5)
    glVertex2f(-focal_length, 0)
    glVertex2f(-focal_length, 0.5)
    glVertex2f(r, 0)
    glVertex2f(r, 0.5)
    glVertex2f(-r, 0)
    glVertex2f(-r, 0.5)
    glEnd()

    draw_rays()

    minY, maxY = get_shapes_bounds()

    glColor3f(0, 0, 0)
    glPushMatrix()

    glTranslatef(-object_distance, -minY, 0)
    for shape in shapes:
        if len(shape) >= 2:
            glBegin(GL_LINE_STRIP)
            for (x, y) in shape:
                glVertex2f(x, y)
            glEnd()
    glPopMatrix()

    glColor3f(1, 0, 0)
    glPushMatrix()

    glTranslatef(di, +(m * maxY), 0)
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
    glutCreateWindow(b"Grafikom K8 - DDA and Midpoint")
    
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)

    glutMouseFunc(mouse_func)
    glutMotionFunc(motion_func)

    draw_star(object_size)
    
    glutMainLoop()

if __name__ == '__main__':
    main()
