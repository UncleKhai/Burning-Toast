from __future__ import annotations

import json
import os
from typing import Any, Dict


DEFAULTS: Dict[str, Any] = {
    "gif_path": "", "sound_path": "", "scale": 100.0, "alpha": 100.0,
    "volume": 100.0, "frame_delay": 30.0, "use_default_delay": False, "speed": 15.0,
    "manual_flip": False, "stop_sound": True, "audio_fade_in": 0, "audio_fade_out": 300,
    "use_duration": False, "all_duration": 3.0, "end_on_loop": False,
    "dvd_mode": False, "follow_mouse": False, "gravity_mode": False,
    "dir_ltr": True, "flip_ltr": False, "dir_rtl": False, "flip_rtl": True,
    "dir_ttb": False, "flip_ttb": False, "dir_btt": False, "flip_btt": False,
    "dir_center": False, "flip_center": False, "dir_custom": False, "flip_custom": False,
    "custom_x": 100, "custom_y": 100,
    "enable_trigger": True, "action": "ทั้งหมด", "specific_key": "", "specific_mouse": "ทั้งหมด",
    "chance": 10.0, "max_instances": 3, "trigger_cooldown": 0.0, "trigger_delay": 0.0,
    "multi_spawn": False, "multi_spawn_min": 1, "multi_spawn_max": 3,
    "auto_time": False, "auto_hr": 0, "auto_min": 0, "auto_sec": 5.0,
    "auto_chance": 100.0, "auto_delay": 0.0,
    "bg_enable": False, "bg_type": "color", "bg_color": "#000000", "bg_image_path": "",
    "bg_alpha": 50.0, "bg_text": "", "bg_text_pos": "top",
    "vid_enable": False, "vid_path": "", "vid_use_chroma": True, "vid_use_default_speed": True,
    "vid_chroma": "#00FF00", "vid_volume": 100.0, "vid_speed": 33.0, "vid_duration": 0.0,
    "vid_scale": 100.0, "vid_alpha": 100.0, "vid_pos_x": 0, "vid_pos_y": 0, "vid_move_speed": 15.0,
    "vid_dvd_mode": False, "vid_gravity_mode": False, "vid_follow_mouse": False,
    "vid_dir_ltr": True, "vid_flip_ltr": False, "vid_dir_rtl": False, "vid_flip_rtl": True,
    "vid_dir_ttb": False, "vid_flip_ttb": False, "vid_dir_btt": False, "vid_flip_btt": False,
    "vid_dir_center": False, "vid_flip_center": False, "vid_dir_custom": False, "vid_flip_custom": False,
    "vid_enable_trigger": False, "vid_action": "ทั้งหมด", "vid_specific_key": "",
    "vid_specific_mouse": "ทั้งหมด", "vid_chance": 10.0, "vid_max_instances": 1,
    "vid_trigger_cooldown": 0.0, "vid_trigger_delay": 0.0, "vid_multi_spawn": False,
    "vid_multi_spawn_min": 1, "vid_multi_spawn_max": 1,
    "vid_auto_time": False, "vid_auto_hr": 0, "vid_auto_min": 0, "vid_auto_sec": 5.0,
    "vid_auto_chance": 100.0, "vid_auto_delay": 0.0,
    "vid_use_video_duration": True, "vid_loop_count": 0, "vid_replay_on_trigger": False,
    "vid_trim_start": 0.0, "vid_trim_end": 0.0, "vid_playback_speed": 1.0,
    "vid_speed_mode": "ทั้งคู่ (Both)", "vid_mute": False,
    "language": "TH",
}


class ConfigManager:
    def __init__(self, default_file="skeleton_settings.json"):
        self.default_file = default_file

    def get_settings_data(self, variables) -> Dict[str, Any]:
        data = {}
        for key, var in variables.items():
            try:
                data[key] = var.get()
            except Exception:
                pass
        return data

    def load_settings(self, filename=None) -> Dict[str, Any]:
        filename = filename or self.default_file
        data = dict(DEFAULTS)
        if not os.path.exists(filename):
            return data
        try:
            with open(filename, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if isinstance(loaded, dict):
                data.update({k: v for k, v in loaded.items() if k in DEFAULTS})
        except Exception as exc:
            print(f"Warning: failed to load settings: {exc}")
        return data

    def save_settings(self, data: Dict[str, Any], filename=None) -> bool:
        filename = filename or self.default_file
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as exc:
            print(f"Warning: failed to save settings: {exc}")
            return False
