# robot_handler.py
import os
import numpy as np
import trimesh
import trimesh.transformations as tra
import yourdfpy
import rerun as rr
from config import DEBUG_AXIS

class RerunRobotHandler:
    def __init__(self, urdf_path, root_name, offset):
        self.urdf_path = urdf_path
        self.root_name = root_name
        self.offset = offset
        
        if not os.path.exists(urdf_path):
            raise FileNotFoundError(f"URDF not found: {urdf_path}")
            
        self.urdf_dir = os.path.dirname(os.path.abspath(urdf_path))
        
        try:
            self.robot = yourdfpy.URDF.load(urdf_path, mesh_dir=self.urdf_dir)
        except Exception as e:
            raise RuntimeError(f"Failed to load URDF: {e}")
        
        self.joint_limits = {}
        for j_name, joint in self.robot.joint_map.items():
            if joint.limit:
                self.joint_limits[j_name] = (joint.limit.lower, joint.limit.upper)
        
        self.link_paths = {}
        self.base_path = f"world/{root_name}"
        rr.log(self.base_path, rr.Transform3D(translation=offset))
        
        base_link = "hand_base_link" if "hand_base_link" in self.robot.link_map else self.robot.base_link
        self._build_tree(base_link, self.base_path)

    def _build_tree(self, link_name, parent_path):
        current_path = f"{parent_path}/{link_name}"
        self.link_paths[link_name] = current_path
        
        if DEBUG_AXIS:
            rr.log(f"{current_path}/axis", rr.Arrows3D(vectors=[[0.02,0,0], [0,0.02,0], [0,0,0.02]], colors=[[255,0,0], [0,255,0], [0,0,255]]))

        link = self.robot.link_map[link_name]

        if link.visuals:
            for i, visual in enumerate(link.visuals):
                if visual.geometry.mesh:
                    mesh_meta = visual.geometry.mesh
                    filename = mesh_meta.filename
                    if os.path.isabs(filename): full_path = filename
                    else: full_path = os.path.join(self.urdf_dir, filename)
                    
                    try:
                        mesh_data = trimesh.load(full_path, force='mesh')
                    except Exception as e:
                        raise RuntimeError(f"Failed to load mesh file '{full_path}': {e}")
                    
                    if mesh_meta.scale is not None: mesh_data.apply_scale(mesh_meta.scale)
                    color = [200, 200, 200]
                    if visual.material and visual.material.color is not None:
                        color = (visual.material.color[:3] * 255).astype(int)
                    elif hasattr(mesh_data.visual, 'main_color'):
                         color = mesh_data.visual.main_color[:3]
                    
                    visual_path = f"{current_path}/geometry_{i}"
                    rr.log(
                        visual_path, 
                        rr.Mesh3D(
                            vertex_positions=mesh_data.vertices, 
                            triangle_indices=mesh_data.faces, 
                            vertex_normals=mesh_data.vertex_normals, 
                            vertex_colors=np.tile(color, (len(mesh_data.vertices), 1))
                        )
                    )
                    if visual.origin is not None:
                        rr.log(visual_path, rr.Transform3D(translation=visual.origin[:3, 3], mat3x3=visual.origin[:3, :3]))

        for joint in self.robot.joint_map.values():
            if joint.parent == link_name: self._build_tree(joint.child, current_path)

    def update_pose(self, active_cfg):
        full_cfg = active_cfg.copy()
        # Mimic 처리
        for name, joint in self.robot.joint_map.items():
            if joint.mimic:
                parent_val = full_cfg.get(joint.mimic.joint, 0.0)
                full_cfg[name] = joint.mimic.multiplier * parent_val + joint.mimic.offset
        
        # Transform 계산
        for name, joint in self.robot.joint_map.items():
            child_link = joint.child
            path = self.link_paths.get(child_link)
            if not path: continue
            
            angle = full_cfg.get(name, 0.0)
            
            T_origin = joint.origin if joint.origin is not None else np.eye(4)
            
            match joint.type:
                case 'revolute' | 'continuous':
                    T_rotation = tra.rotation_matrix(angle, joint.axis)
                case 'prismatic':
                    T_rotation = tra.translation_matrix(joint.axis * angle)
                case _:
                    T_rotation = np.eye(4)
            
            T_local = T_origin @ T_rotation
            rr.log(path, rr.Transform3D(translation=T_local[:3, 3], mat3x3=T_local[:3, :3]))

    def get_sensor_path(self, part_name, sensor_type):
        target_link = None
        
        match part_name:
            case "palm":
                target_link = "hand_base_link"

            case "thumb":
                match sensor_type:
                    case "tip" | "nail": 
                        target_link = "thumb_tip"
                    case "middle": 
                        target_link = "thumb_intermediate"
                    case "pad": 
                        target_link = "thumb_proximal"

            case "index":
                match sensor_type:
                    case "tip" | "nail": 
                        target_link = "index_tip"
                    case "pad": 
                        target_link = "index_proximal"

            case "middle":
                match sensor_type:
                    case "tip" | "nail": 
                        target_link = "middle_tip"
                    case "pad": 
                        target_link = "middle_proximal"

            case "ring":
                match sensor_type:
                    case "tip" | "nail": 
                        target_link = "ring_tip"
                    case "pad": 
                        target_link = "ring_proximal"

            case "little" | "pinky":
                match sensor_type:
                    case "tip" | "nail": 
                        target_link = "pinky_tip"
                    case "pad": 
                        target_link = "pinky_proximal"
        
        if target_link and target_link in self.link_paths:
            return f"{self.link_paths[target_link]}/sensor_{sensor_type}"
        
        return None