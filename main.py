# main.py
import rerun as rr
import rerun.blueprint as rrb
import pandas as pd
import numpy as np
import os
import cv2
import argparse
from scipy.spatial.transform import Rotation as R

from config import (
    URDF_LEFT_PATH, URDF_RIGHT_PATH,
    LEFT_HAND_OFFSET, RIGHT_HAND_OFFSET,
    SENSOR_CONFIG_LEFT, SENSOR_CONFIG_RIGHT,
    JOINT_MAP_LEFT, JOINT_MAP_RIGHT,
    NORM_MIN, NORM_MAX
)
from robot_handler import RerunRobotHandler
from utils import parse_sensor_info, decode_image_bytes, load_image_from_bytes

def main(chunk: int, episode: int):
    data_path = os.path.join("data", "data", f"chunk-{chunk:03}", f"episode_{episode:06}.parquet")
    video_path = os.path.join("data", "videos", f"chunk-{chunk:03}", "observation.images.cam_left_high", f"episode_{episode:06}.mp4")
    print(f"Loading parquet from {data_path}...")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    df = pd.read_parquet(data_path)

    active_sensors = []
    left_views = []
    right_views = []

    for col_name in df.columns:
        parsed_info = parse_sensor_info(col_name)
        if parsed_info:
            part_name, sensor_type, is_left = parsed_info
            
            hand_str = "left_hand" if is_left else "right_hand"
            view_path = f"dashboard/{hand_str}/{part_name}_{sensor_type}"
            view_name = f"{part_name} {sensor_type}"
            view_obj = rrb.Spatial2DView(origin=view_path, name=view_name)
            
            if is_left: left_views.append(view_obj)
            else: right_views.append(view_obj)

            config_map = SENSOR_CONFIG_LEFT if is_left else SENSOR_CONFIG_RIGHT
            
            part_config = config_map.get(part_name)
            if not part_config:
                 raise ValueError(f"Configuration for part '{part_name}' not found in {'LEFT' if is_left else 'RIGHT'} config.")

            config = part_config.get(sensor_type)
            if not config:
                 raise ValueError(f"Configuration for sensor type '{sensor_type}' in part '{part_name}' not found.")

            active_sensors.append({
                "col_name": col_name,
                "part_name": part_name,
                "sensor_type": sensor_type,
                "is_left": is_left,
                "config": config,
                "path_2d": view_path
            })

    left_views.sort(key=lambda x: x.name)
    right_views.sort(key=lambda x: x.name)

    my_blueprint = rrb.Blueprint(
        rrb.Horizontal(
            rrb.Spatial3DView(origin="world", name="3D Robot View"),
            rrb.Vertical(
                rrb.Spatial2DView(origin="video_stream", name="Original Video"),
                rrb.Horizontal(
                    rrb.Grid(*left_views, name="LEFT HAND"),
                    rrb.Grid(*right_views, name="RIGHT HAND")
                )
            ),
            column_shares=[2, 1]
        ),
        collapse_panels=True,
    )

    rr.init("Robot_Sensors_Strict_V3", spawn=True, default_blueprint=my_blueprint)

    print("Setting up robots...")
    left_bot = RerunRobotHandler(URDF_LEFT_PATH, "left_hand", LEFT_HAND_OFFSET)
    right_bot = RerunRobotHandler(URDF_RIGHT_PATH, "right_hand", RIGHT_HAND_OFFSET)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened(): 
        raise IOError(f"Cannot open video: {video_path}")

    print(f"▶️ Starting playback ({len(df)} frames)...")

    for _, row in df.iterrows():
        rr.set_time(timeline="frame_idx", sequence=row['frame_index'])
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                rr.log('video_stream', rr.Image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

        raw_state = row['observation.state']
        if isinstance(raw_state, str):
            vals = np.fromstring(raw_state.replace('[','').replace(']','').replace('\n', ' '), sep=' ')
        else:
            vals = np.array(raw_state)

        for bot, jmap in [(left_bot, JOINT_MAP_LEFT), (right_bot, JOINT_MAP_RIGHT)]:
            cfg = {}
            for name, idx in jmap.items():
                if idx < len(vals):
                    norm = vals[idx]
                    if name in bot.joint_limits:
                        lo, up = bot.joint_limits[name]
                        ratio = (norm - NORM_MIN) / (NORM_MAX - NORM_MIN)
                        real = up - ratio * (up - lo)
                        cfg[name] = np.clip(real, lo, up)
                    else: cfg[name] = norm
            bot.update_pose(cfg)

        for sensor in active_sensors:
            target_bot = left_bot if sensor["is_left"] else right_bot
            
            path_3d = target_bot.get_sensor_path(sensor["part_name"], sensor["sensor_type"])

            if not path_3d:
                raise RuntimeError(f"Cannot find valid path for 3d world")
            
            raw_val = row[sensor["col_name"]]
            img_bytes = decode_image_bytes(raw_val)

            if not img_bytes:
                raise RuntimeError(f"Cannot find valid image for {raw_val}")

            image = load_image_from_bytes(img_bytes)
            w, h = image.size
            config = sensor["config"]

            phys_width = config["width"]
            dist = 0.001
            focal_len = (w * dist) / phys_width
            rot_mat = R.from_euler('xyz', config["rot"], degrees=True).as_matrix()

            rr.log(path_3d, rr.Pinhole(resolution=[w, h], focal_length=focal_len, image_plane_distance=dist, line_width=0.0))
            rr.log(path_3d, rr.Transform3D(translation=config["pos"], mat3x3=rot_mat))
            rr.log(path_3d, rr.TransformAxes3D(0.0))
            rr.log(f"{path_3d}/image", rr.Image(image))
            
            # 2D Dashboard
            rr.log(sensor["path_2d"], rr.Image(image))

    cap.release()
    print("✅ Playback finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--chunk", type=int, default=0)
    parser.add_argument("-e", "--episode", type=int, default=0)
    
    args = parser.parse_args()

    main(
        chunk=args.chunk,
        episode=args.episode
    )