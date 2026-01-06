import os
import time
import shutil
import cv2
import numpy as np
import logging

# ================= CONFIG =================
WAIT_WINDOW = 600  # seconds (10 minutes)
SIMILARITY_THRESHOLD = 0.75
SCAN_INTERVAL = 5  # seconds

BASE_DIR = os.getcwd()
INCOMING_DIR = os.path.join(BASE_DIR, "incoming")
FINAL_DIR = os.path.join(BASE_DIR, "final")
DUPLICATES_DIR = os.path.join(BASE_DIR, "duplicates")

for d in [INCOMING_DIR, FINAL_DIR, DUPLICATES_DIR]:
    os.makedirs(d, exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ================= INCIDENT STORE =================
incident_store = {}

# ================= SAFE MOVE =================
def safe_move(src, dst_dir):
    if not os.path.exists(src):
        logging.warning(f"Missing file: {src}")
        return
    dst = os.path.join(dst_dir, os.path.basename(src))
    shutil.move(src, dst)
    logging.info(f"MOVED → {dst}")

# ================= VIDEO UTILITIES =================
def get_video_frames(video_path, max_frames=8):
    cap = cv2.VideoCapture(video_path)
    frames = []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(1, total // max_frames)

    i = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if i % step == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (128, 128))
            frames.append(gray)
        i += 1

    cap.release()
    return frames

def frame_similarity(f1, f2):
    f1 = f1.astype(np.float32)
    f2 = f2.astype(np.float32)
    num = np.sum((f1 - f1.mean()) * (f2 - f2.mean()))
    den = np.sqrt(np.sum((f1 - f1.mean())**2) * np.sum((f2 - f2.mean())**2))
    return num / den if den != 0 else 0

def video_similarity(v1, v2):
    f1 = get_video_frames(v1)
    f2 = get_video_frames(v2)
    n = min(len(f1), len(f2))
    if n == 0:
        return 0
    return float(np.mean([frame_similarity(f1[i], f2[i]) for i in range(n)]))

def video_duration(path):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    return frames / fps if fps > 0 else 0

def motion_score(path):
    cap = cv2.VideoCapture(path)
    prev = None
    motion = 0
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev is not None:
            motion += np.sum(cv2.absdiff(prev, gray))
            count += 1
        prev = gray
    cap.release()
    return motion / max(count, 1)

def pick_best_video(videos):
    scored = []
    for v in videos:
        scored.append((v, video_duration(v), motion_score(v)))
    scored.sort(key=lambda x: (x[1], x[2]), reverse=True)
    return scored[0][0]

# ================= INCIDENT PROCESSING =================
def process_incident(location):
    incident = incident_store[location]
    items = incident["items"]

    videos = [i["path"] for i in items if i["type"] == "video" and os.path.exists(i["path"])]
    images = [i["path"] for i in items if i["type"] == "image" and os.path.exists(i["path"])]
    audios = [i["path"] for i in items if i["type"] == "audio" and os.path.exists(i["path"])]
    texts = [i["text"] for i in items if i["type"] == "text"]

    logging.info(
        f"Processing incident: {location} | "
        f"videos:{len(videos)} images:{len(images)} audios:{len(audios)} texts:{len(texts)}"
    )

    # ---------- VIDEO ----------
    if videos:
        groups, used = [], set()

        for v in videos:
            if v in used:
                continue
            group = [v]
            for o in videos:
                if o != v and o not in used:
                    sim = video_similarity(v, o)
                    logging.info(f"Similarity {os.path.basename(v)} ↔ {os.path.basename(o)} = {sim:.2f}")
                    if sim >= SIMILARITY_THRESHOLD:
                        group.append(o)
                        used.add(o)
            groups.append(group)

        main_group = max(groups, key=len)
        best = pick_best_video(main_group)
        logging.info(f"Best video selected: {os.path.basename(best)}")

        for v in videos:
            safe_move(v, FINAL_DIR if v == best else DUPLICATES_DIR)

    # ---------- IMAGE ----------
    elif images:
        safe_move(images[0], FINAL_DIR)
        for img in images[1:]:
            safe_move(img, DUPLICATES_DIR)

    # ---------- AUDIO ----------
    elif audios:
        safe_move(audios[0], FINAL_DIR)
        for a in audios[1:]:
            safe_move(a, DUPLICATES_DIR)

    # ---------- TEXT ----------
    elif texts:
        out = os.path.join(FINAL_DIR, f"{location}_text.txt")
        with open(out, "w", encoding="utf-8") as f:
            f.write(texts[0])
        logging.info(f"Saved text → {out}")

    del incident_store[location]
    logging.info(f"Incident completed: {location}")

# ================= MAIN LOOP =================
logging.info("🚀 Incident processor started")

while True:
    now = time.time()

    for filename in os.listdir(INCOMING_DIR):
        path = os.path.join(INCOMING_DIR, filename)
        if not os.path.isfile(path):
            continue

        try:
            _, location, _ = filename.split("_", 2)
        except ValueError:
            logging.warning(f"Invalid filename format: {filename}")
            continue

        ext = filename.split(".")[-1].lower()
        ctype = (
            "video" if ext in ["mp4", "m4a"]
            else "image" if ext in ["jpg", "jpeg", "png"]
            else "audio" if ext in ["wav", "mp3"]
            else "text"
        )

        if location not in incident_store:
            incident_store[location] = {
                "start_time": now,
                "items": []
            }
            logging.info(f"New incident created: {location}")

        if path not in [i["path"] for i in incident_store[location]["items"]]:
            incident_store[location]["items"].append({
                "type": ctype,
                "path": path,
                "text": None
            })
            logging.info(f"Registered file: {filename}")

    for loc in list(incident_store.keys()):
        if now - incident_store[loc]["start_time"] >= WAIT_WINDOW:
            process_incident(loc)

    time.sleep(SCAN_INTERVAL)