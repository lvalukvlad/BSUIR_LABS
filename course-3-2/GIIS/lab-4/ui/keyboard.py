import state
import algorithms.transformations as transforms
from ui.canvas import redraw, update_status


STEP = 10
ROTATION_STEP = 5
SCALE_STEP = 0.1


def reset_transform():
    state.transform_matrix = transforms.multiply_matrices()
    state.translation = [0.0, 0.0, 0.0]
    state.rotation = [0.0, 0.0, 0.0]
    state.scale = [1.0, 1.0, 1.0]
    state.use_perspective = False
    redraw()
    update_status("Преобразования сброшены")


def rebuild_transform_matrix():
    t = transforms.create_translation(*state.translation)
    rx = transforms.create_rotation_x(state.rotation[0])
    ry = transforms.create_rotation_y(state.rotation[1])
    rz = transforms.create_rotation_z(state.rotation[2])
    s = transforms.create_scaling(*state.scale)
    
    state.transform_matrix = transforms.multiply_matrices(t, rx, ry, rz, s)


def handle_key(event):
    key = event.keysym.lower()
    print(f"Key pressed: {key}")  # Debug
    
    if key == 'escape':
        reset_transform()
        return
    
    changed = False
    need_rebuild = True
    
    if key == 'up':
        state.translation[1] += STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    elif key == 'down':
        state.translation[1] -= STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    elif key == 'right':
        state.translation[0] += STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    elif key == 'left':
        state.translation[0] -= STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    elif key == 'page_up':
        state.translation[2] += STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    elif key == 'page_down':
        state.translation[2] -= STEP
        changed = True
        msg = f"Перемещение: ({state.translation[0]}, {state.translation[1]}, {state.translation[2]})"
    
    elif key == 'q':
        state.rotation[0] += ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    elif key == 'a':
        state.rotation[0] -= ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    elif key == 'w':
        state.rotation[1] += ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    elif key == 's':
        state.rotation[1] -= ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    elif key == 'e':
        state.rotation[2] += ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    elif key == 'd':
        state.rotation[2] -= ROTATION_STEP
        changed = True
        msg = f"Поворот: X={state.rotation[0]}°, Y={state.rotation[1]}°, Z={state.rotation[2]}°"
    
    elif key == 'equal' or key == '+':
        state.scale = [s + SCALE_STEP for s in state.scale]
        changed = True
        msg = f"Масштаб: ({state.scale[0]:.2f}, {state.scale[1]:.2f}, {state.scale[2]:.2f})"
    elif key == 'minus':
        state.scale = [max(0.1, s - SCALE_STEP) for s in state.scale]
        changed = True
        msg = f"Масштаб: ({state.scale[0]:.2f}, {state.scale[1]:.2f}, {state.scale[2]:.2f})"
    
    elif key == 'x':
        m = transforms.create_reflection_x()
        print(f"Reflection X matrix:\n{m}")
        state.transform_matrix = transforms.multiply_matrices(state.transform_matrix, m)
        print(f"Combined matrix after reflection X:\n{state.transform_matrix}")
        changed = True
        need_rebuild = False
        msg = "Отражение по оси X"
    elif key == 'y':
        m = transforms.create_reflection_y()
        print(f"Reflection Y matrix:\n{m}")
        state.transform_matrix = transforms.multiply_matrices(state.transform_matrix, m)
        print(f"Combined matrix after reflection Y:\n{state.transform_matrix}")
        changed = True
        need_rebuild = False
        msg = "Отражение по оси Y"
    elif key == 'z':
        m = transforms.create_reflection_z()
        print(f"Reflection Z matrix:\n{m}")
        state.transform_matrix = transforms.multiply_matrices(state.transform_matrix, m)
        print(f"Combined matrix after reflection Z:\n{state.transform_matrix}")
        changed = True
        need_rebuild = False
        msg = "Отражение по оси Z"
    
    elif key == 'p':
        state.use_perspective = not state.use_perspective
        changed = True
        need_rebuild = False
        msg = f"Перспектива: {'ВКЛ' if state.use_perspective else 'ВЫКЛ'}"
    
    else:
        msg = None
        need_rebuild = True
    
    if changed:
        if need_rebuild:
            rebuild_transform_matrix()
        redraw()
        if msg:
            update_status(msg)
    elif msg:
        update_status(msg)


def bind_keys(canvas):
    canvas.bind('<Key>', handle_key)
    canvas.focus_set()
