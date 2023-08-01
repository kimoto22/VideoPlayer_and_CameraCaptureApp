import cv2
import dlib
import csv
from scipy.spatial import distance as dist
from imutils import face_utils
import math

def calculate_blink_frequency(blink_times):
    if len(blink_times) < 2:
        return 0

    time_diffs = [blink_times[i] - blink_times[i-1] for i in range(1, len(blink_times))]
    blink_frequency = 60 / (sum(time_diffs) / len(time_diffs))
    return blink_frequency

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Compute the euclidean distance between the horizontal eye landmarks
    C = dist.euclidean(eye[0], eye[3])

    # Compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_head_movement(shape):
    left_eye_indexes = [36, 37, 38, 39, 40, 41]
    right_eye_indexes = [42, 43, 44, 45, 46, 47]
    nose_bridge = shape[27]
    nose_tip = shape[30]
    mouth_left = shape[48]
    mouth_right = shape[54]

    pitch = calculate_angle(nose_bridge, nose_tip, mouth_right)
    yaw = calculate_angle(mouth_left, nose_tip, mouth_right)
    roll = calculate_angle(shape[left_eye_indexes[0]], nose_tip, shape[right_eye_indexes[5]])

    return pitch, yaw, roll

def calculate_angle(p1, p2, p3):
    vector1 = [p1[0] - p2[0], p1[1] - p2[1]]
    vector2 = [p3[0] - p2[0], p3[1] - p2[1]]
    dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
    magnitude1 = math.sqrt(vector1[0]**2 + vector1[1]**2)
    magnitude2 = math.sqrt(vector2[0]**2 + vector2[1]**2)
    angle = math.acos(dot_product / (magnitude1 * magnitude2))
    return angle

def perform_eye_tracking(shape):
    # Implement your eye tracking algorithm here
    # Update the code to analyze eye landmarks and determine eye movements

    # Example: Calculate eye aspect ratio (EAR) for blink detection
    left_eye = shape[left_eye_indexes[0]:left_eye_indexes[-1]+1]
    right_eye = shape[right_eye_indexes[0]:right_eye_indexes[-1]+1]

    left_ear = eye_aspect_ratio(left_eye)
    right_ear = eye_aspect_ratio(right_eye)

    blink_detected = left_ear < 0.2 and right_ear < 0.2  # Adjust threshold as per your requirements

    return blink_detected

left_eye_indexes = [36, 37, 38, 39, 40, 41]
right_eye_indexes = [42, 43, 44, 45, 46, 47]

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('/Users/abdullahalmamun/Desktop/PhD research/Data/shape_predictor_68_face_landmarks.dat')

csv_file = open('eye_and_head_tracking_data.csv', 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Frame', 'Pitch (radians)', 'Yaw (radians)', 'Roll (radians)', 'Blink Number', 'Blink Frequency', 'Blink Duration'])

video_capture = cv2.VideoCapture(0)

blink_times = []
blink_number = 0
blink_start_time = None
is_blinking = False
blink_duration = 0

frame_number = 0

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    frame_number += 1

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        pitch, yaw, roll = calculate_head_movement(shape)

        blink_detected = perform_eye_tracking(shape)

        if blink_detected:
            if not is_blinking:
                blink_start_time = cv2.getTickCount()
                blink_number += 1
                is_blinking = True
        else:
            if is_blinking:
                blink_end_time = cv2.getTickCount()
                blink_duration = (blink_end_time - blink_start_time) / cv2.getTickFrequency()
                blink_times.append(blink_duration)
                is_blinking = False

        blink_frequency = calculate_blink_frequency(blink_times)

        csv_writer.writerow([frame_number, pitch, yaw, roll, blink_number, blink_frequency, blink_duration])

        cv2.putText(frame, f"Frame: {frame_number}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Pitch: {pitch:.2f} radians", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Yaw: {yaw:.2f} radians", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Roll: {roll:.2f} radians", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Blinks: {blink_number}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Frequency: {blink_frequency:.2f} blinks per minute", (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Duration: {blink_duration:.2f} seconds", (10, 210), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow('Eye and Head Tracking', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
csv_file.close()
cv2.destroyAllWindows()
