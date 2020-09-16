import pybullet as p
import roboverse.bullet as bullet
import roboverse.bullet.control as control
import numpy as np


def open_drawer(drawer):
    return slide_drawer(drawer, -1)


def close_drawer(drawer):
    return slide_drawer(drawer, 1)


def get_drawer_base_joint(drawer):
    joint_names = [control.get_joint_info(drawer, j, 'jointName')
                   for j in range(p.getNumJoints(drawer))]
    drawer_frame_joint_idx = joint_names.index('base_frame_joint')
    return drawer_frame_joint_idx


def get_drawer_bottom_pos(drawer):
    drawer_bottom_pos, _ = bullet.get_link_state(
        drawer, get_drawer_base_joint(drawer))
    return np.array(drawer_bottom_pos)


def slide_drawer(drawer, direction):
    assert direction in [-1, 1]
    # -1 = open; 1 = close
    drawer_frame_joint_idx = get_drawer_base_joint(drawer)

    num_ts = 20 if direction == -1 else 30

    command = np.clip(10 * direction,
                      -10 * np.abs(direction), np.abs(direction))
    # enable fast opening; slow closing

    # Wait a little before closing
    wait_ts = 30  # 0 if direction == -1 else 30
    control.step_simulation(wait_ts, t_sleep=0.01)

    p.setJointMotorControl2(
        drawer,
        drawer_frame_joint_idx,
        controlMode=p.VELOCITY_CONTROL,
        targetVelocity=command,
        force=10
    )

    drawer_pos = get_drawer_bottom_pos(drawer)

    control.step_simulation(num_ts, t_sleep=0.01)
    p.setJointMotorControl2(
        drawer,
        drawer_frame_joint_idx,
        controlMode=p.VELOCITY_CONTROL,
        targetVelocity=0,
        force=10
    )

    return drawer_pos
