# Burning Toast

โครงสร้างไฟล์

```text
burning_toast_soc/
├── main.py
├── requirements.txt
├── utils/
│   ├── i18n.py
│   ├── config_manager.py
│   └── path_utils.py
├── core/
│   ├── video_player.py
│   ├── image_loader.py
│   └── image_animator.py
├── controllers/
│   ├── application_controller.py
│   ├── spawn_controller.py
│   ├── input_controller.py
│   └── preview_controller.py
├── ui/
│   ├── app_window.py
│   ├── theme.py
│   └── background_window.py
└── tabs/
    ├── tab_image.py
    ├── tab_video.py
    └── tab_background.py
```

## หน้าที่ของแต่ละชั้น

- `utils/i18n.py` — Dictionary ภาษาและ `t()`
- `utils/config_manager.py` — load/save JSON และค่า default
- `core/video_player.py` — เล่น/แสดงวิดีโอโดยรับ `config` เป็น Dictionary ไม่อ้าง `app_ref`
- `core/image_loader.py` — โหลดและ cache GIF/รูป
- `core/image_animator.py` — animation ของรูป
- `controllers/input_controller.py` — keyboard/mouse listeners
- `controllers/spawn_controller.py` — trigger, cooldown, chance, auto spawn, counters และสั่ง core ให้สร้าง object
- `controllers/preview_controller.py` — image/video preview
- `controllers/application_controller.py` — RUN/Tray/Clear/Exit
- `ui/app_window.py` — สร้าง root, Notebook, state (`tk.Variable`) และเชื่อม components
- `tabs/*` — UI เฉพาะแต่ละแท็บ
- `ui/background_window.py` — หน้าต่าง background overlay
- `main.py` — entry point

## วิธีรัน

1. ติดตั้ง dependency:
   `pip install -r requirements.txt`
2. วาง `burningToast.ico` ไว้ข้าง `main.py` ได้ (ถ้าไม่มี โปรแกรมยังใช้ fallback icon)
3. รัน:
   `python main.py`

ไฟล์ settings ยังคงใช้ชื่อ `skeleton_settings.json` ตามโปรแกรมเดิม

## หมายเหตุ

`pygame` ไม่ได้ติดตั้งอยู่ใน environment ที่ใช้ตรวจ syntax ของไฟล์นี้ จึงตรวจได้ถึงระดับ `py_compile` แต่ไม่สามารถเปิด GUI จริงใน environment ดังกล่าวได้ การรันจริงควรทำบนเครื่องที่ติดตั้ง dependency ครบและมี display/desktop environment
