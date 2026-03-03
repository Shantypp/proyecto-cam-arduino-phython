import cv2
import numpy as np
import mediapipe as mp
import serial
import time

# =========================
# CONFIG
# =========================
USE_SERIAL = True
SERIAL_PORT = "COM5"
BAUDRATE = 9600

# Clasificación por ángulo de rodilla:
# - < THRESHOLD  => SENTADO
# - >= THRESHOLD => PARADO
THRESHOLD = 125

# Para evitar parpadeo: exige N frames seguidos antes de cambiar estado
STABILITY_FRAMES = 5

# Cámara (Windows): CAP_DSHOW suele funcionar mejor
CAM_INDEX = 0

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils


def angle_3pts(a, b, c):
    """Ángulo ABC en grados con 3 puntos 2D."""
    ba = a - b
    bc = c - b
    denom = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-6
    cosang = np.dot(ba, bc) / denom
    cosang = np.clip(cosang, -1.0, 1.0)
    return np.degrees(np.arccos(cosang))


def xy(landmarks, idx, w, h):
    lm = landmarks[idx]
    return np.array([lm.x * w, lm.y * h], dtype=np.float32)


def classify(landmarks, w, h):
    """
    Clasifica SENTADO / PARADO usando ángulo promedio de rodillas:
    Izq: hip=23, knee=25, ankle=27
    Der: hip=24, knee=26, ankle=28
    """
    lhip, lknee, lank = xy(landmarks, 23, w, h), xy(landmarks, 25, w, h), xy(landmarks, 27, w, h)
    rhip, rknee, rank = xy(landmarks, 24, w, h), xy(landmarks, 26, w, h), xy(landmarks, 28, w, h)

    left_angle = angle_3pts(lhip, lknee, lank)
    right_angle = angle_3pts(rhip, rknee, rank)
    knee_angle = (left_angle + right_angle) / 2.0

    state = "SENTADO" if knee_angle < THRESHOLD else "PARADO"
    return state, knee_angle


def main():
    # =========================
    # Serial Arduino
    # =========================
    ser = None
    last_sent_code = None

    if USE_SERIAL:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
            time.sleep(2)  # Arduino se reinicia al abrir el puerto
            print(f"[OK] Arduino conectado en {SERIAL_PORT}")
        except Exception as e:
            print(f"[WARN] No pude abrir {SERIAL_PORT}: {e}")
            print("      Revisa: Arduino conectado, COM correcto, Serial Monitor cerrado.")
            ser = None

    # =========================
    # Cámara
    # =========================
    cap = cv2.VideoCapture(CAM_INDEX, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ No se pudo abrir la cámara.")
        if ser is not None:
            ser.close()
        return

    cv2.namedWindow("Pose - Sentado/Parado", cv2.WINDOW_NORMAL)

    # =========================
    # MediaPipe Pose
    # =========================
    stable_label = None
    candidate_label = None
    candidate_count = 0

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("❌ No se pudo leer frame.")
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            label = "SIN PERSONA"
            angle = None

            if res.pose_landmarks:
                mp_draw.draw_landmarks(frame, res.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Clasificación
                label, angle = classify(res.pose_landmarks.landmark, w, h)

                # ---------- Estabilización ----------
                if candidate_label != label:
                    candidate_label = label
                    candidate_count = 1
                else:
                    candidate_count += 1

                if candidate_count >= STABILITY_FRAMES:
                    stable_label = candidate_label

                # ---------- Enviar a Arduino ----------
                if ser is not None and stable_label in ("PARADO", "SENTADO"):
                    code = "P" if stable_label == "PARADO" else "S"
                    if code != last_sent_code:
                        ser.write((code + "\n").encode("utf-8"))
                        last_sent_code = code

            # Texto en pantalla
            show_label = stable_label if stable_label else label
            text = show_label if angle is None else f"{show_label} (rodilla={angle:.1f}°)"

            cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(frame, text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("Pose - Sentado/Parado", frame)

            k = cv2.waitKey(1) & 0xFF
            if k == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()