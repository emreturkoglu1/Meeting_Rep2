import cv2
import numpy as np
import csv
import os
import random  # Duygu çeşitliliği için
from datetime import datetime
import collections  # Duygu anımsama için

# Output paths with absolute paths
OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "custom_output"))
VIDEO_PATH = os.path.join(OUTPUT_PATH, "output_video.mp4")
PROCESSED_VIDEO_PATH = os.path.join(OUTPUT_PATH, "output_processed.mp4")
CSV_PATH = os.path.join(OUTPUT_PATH, "emotion_analysis.csv")

print(f"Using absolute paths:")
print(f"OUTPUT_PATH: {OUTPUT_PATH}")
print(f"VIDEO_PATH: {VIDEO_PATH}")
print(f"PROCESSED_VIDEO_PATH: {PROCESSED_VIDEO_PATH}")
print(f"CSV_PATH: {CSV_PATH}")

# Emotion labels for detected facial expressions
EMOTION_LABELS = {
    0: "NEUTRAL",
    1: "HAPPY",
    2: "SAD",
    3: "SURPRISED",
    4: "ANGRY"
}

# Load face cascades from OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')

# Yüz tanıma için ek parametreler
face_detection_params = {
    'scaleFactor': 1.05,  # Daha düşük scaleFactor daha hassas tanıma yapar
    'minNeighbors': 4,    # Daha düşük minNeighbors daha fazla yüz tanır
    'minSize': (30, 30),
    'flags': cv2.CASCADE_SCALE_IMAGE
}

# Göz tanıma için ek parametreler
eye_detection_params = {
    'scaleFactor': 1.1,
    'minNeighbors': 5,
    'minSize': (20, 20)
}

# Gülümseme tanıma için ek parametreler
smile_detection_params = {
    'scaleFactor': 1.3,
    'minNeighbors': 15,
    'minSize': (25, 25)
}

def analyze_video(video_path, output_video_path, csv_path):
    # Check if video file exists
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
        return False
    
    # Capture video from file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return False
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video properties: {width}x{height}, {fps} fps, {frame_count} frames")
    
    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    
    # Duygu anımsama için sözlük: {face_id: deque([recent_emotions])}
    emotion_memory = {}
    memory_size = int(fps) # 1 saniyelik bellek
    
    # Yüz analizi için ölçütler
    emotion_thresholds = {
        "neutral": 0.4,
        "happy": 0.6,
        "sad": 0.5,
        "surprised": 0.5,
        "angry": 0.45
    }
    
    # Çeşitlilik için rastgele duygu ataması - düşük ihtimalle
    def assign_random_emotion(frame_number):
        # Devre dışı bırakıldı - daha gerçekçi sonuçlar için
        # if frame_number % 50 == 0 and random.random() < 0.2:  # Her 50 karede ve %20 ihtimalle
        #     emotions = list(EMOTION_LABELS.keys())
        #     return random.choice(emotions), 0.4 + random.random() * 0.3
        return None, None
    
    # Prepare CSV file for emotion analysis
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'frame_number', 'face_id', 'emotion', 'confidence', 'face_x', 'face_y', 'face_width', 'face_height']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        frame_number = 0
        total_faces_detected = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Create a copy to draw on
            display_frame = frame.copy()
            
            # Convert frame to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Timestamp for this frame
            timestamp = frame_number / fps
            
            # Detect faces using cascade classifier with geliştirilmiş parametreler
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=face_detection_params['scaleFactor'],
                minNeighbors=face_detection_params['minNeighbors'],
                minSize=face_detection_params['minSize'],
                flags=face_detection_params['flags']
            )
            
            # Track emotions for each detected face
            face_count = 0
            
            for face_id, (x, y, w, h) in enumerate(faces):
                # Draw rectangle around face
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Extract the face region of interest
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = display_frame[y:y+h, x:x+w]
                
                # Calculate brightness and contrast of face region
                brightness = np.mean(roi_gray)
                contrast = np.std(roi_gray)
                
                # Detect eyes in the face region with geliştirilmiş parametreler
                eyes = eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=eye_detection_params['scaleFactor'],
                    minNeighbors=eye_detection_params['minNeighbors'],
                    minSize=eye_detection_params['minSize']
                )
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
                
                # Detect smile in the face region with geliştirilmiş parametreler
                smile = smile_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=smile_detection_params['scaleFactor'],
                    minNeighbors=smile_detection_params['minNeighbors'],
                    minSize=smile_detection_params['minSize']
                )
                
                # Initialize emotion variables
                emotion_id = 0  # Default: neutral
                confidence = 0.0
                
                # Belirli aralıklarda rastgele duygu ataması yapalım
                random_emotion_id, random_confidence = assign_random_emotion(frame_number)
                if random_emotion_id is not None:
                    emotion_id = random_emotion_id
                    confidence = random_confidence
                else:  # Normal duygu tespiti
                    # Analyze facial features to determine emotion
                    has_smile = len(smile) > 0
                    has_eyes = len(eyes) >= 2
                    
                    # Additional face feature checks based on brightness and contrast
                    is_bright_face = brightness > 130
                    is_high_contrast = contrast > 50
                    
                    if has_smile:
                        # Draw rectangle around smile
                        for (sx, sy, sw, sh) in smile:
                            cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 0, 255), 2)
                        
                        # If smiling, likely happy
                        emotion_id = 1  # Happy
                        confidence = 0.8
                    elif has_eyes and len(eyes) > 2:
                        # Multiple eyes detected could indicate surprise
                        emotion_id = 3  # Surprised
                        confidence = 0.6
                    elif has_eyes:
                        # Basic eye analysis
                        eye_heights = [eh for (_, _, _, eh) in eyes]
                        avg_eye_height = sum(eye_heights) / len(eye_heights)
                        
                        # Eye aspect ratio calculation (approximate)
                        eye_widths = [ew for (_, _, ew, _) in eyes]
                        avg_eye_width = sum(eye_widths) / len(eye_widths)
                        ear = avg_eye_height / max(avg_eye_width, 1)  # Eye aspect ratio
                        
                        if avg_eye_height < 0.12 * h:  # Small eyes might indicate sad
                            emotion_id = 2  # Sad
                            confidence = 0.6
                        elif ear < 0.45 and not is_bright_face:  # Wide eyes with low brightness might indicate anger
                            emotion_id = 4  # Angry
                            confidence = 0.6
                        elif is_high_contrast and brightness < 100:  # High contrast with low brightness could indicate sadness
                            emotion_id = 2  # Sad
                            confidence = 0.55
                        else:
                            # Zaman zaman diğer duygulara da şans verelim
                            # Devre dışı bırakıldı - daha gerçekçi sonuçlar için
                            # if frame_number % 30 == 0 and random.random() < 0.4:  # Her 30 karede %40 ihtimalle
                            #     possible_emotions = [1, 2, 3, 4]  # Happy, Sad, Surprised, Angry
                            #     weights = [0.3, 0.2, 0.3, 0.2]  # Ağırlıklar
                            #     emotion_id = random.choices(possible_emotions, weights=weights, k=1)[0]
                            #     confidence = 0.5 + random.random() * 0.2
                            # else:
                            emotion_id = 0  # Neutral
                            confidence = 0.6
                    else:
                        # If no clear indicators, default to neutral
                        emotion_id = 0  # Neutral
                        confidence = 0.4
                
                # Duygu anımsama için belleği güncelle
                face_key = f"{face_id+1}"
                if face_key not in emotion_memory:
                    emotion_memory[face_key] = collections.deque(maxlen=memory_size)
                
                emotion_memory[face_key].append(emotion_id)
                
                # En çok tekrarlanan duyguyu bul
                if len(emotion_memory[face_key]) >= 3:  # En az 3 örnek olduğunda belleği kullan
                    counter = collections.Counter(emotion_memory[face_key])
                    # En çok tekrarlanan duyguyu al
                    emotion_id = counter.most_common(1)[0][0]
                    # Eğer son tespit en yaygın duyguyla aynıysa güveni artır
                    if emotion_memory[face_key][-1] == emotion_id:
                        confidence = min(0.9, confidence + 0.1)
                
                # Get emotion label
                emotion_label = EMOTION_LABELS[emotion_id]
                
                # Display emotion on frame
                cv2.putText(display_frame, f"Face {face_id+1}: {emotion_label}", 
                           (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Write emotion to CSV
                writer.writerow({
                    'timestamp': f"{timestamp:.2f}",
                    'frame_number': frame_number,
                    'face_id': face_id + 1,
                    'emotion': emotion_label.lower(),
                    'confidence': f"{confidence:.2f}",
                    'face_x': x,
                    'face_y': y,
                    'face_width': w,
                    'face_height': h
                })
                csvfile.flush()  # Force writing to disk
                
                face_count += 1
                total_faces_detected += 1
            
            # Display total face count on frame
            cv2.putText(display_frame, f"Faces detected: {face_count}", 
                       (width - 200, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display progress
            if frame_number % 30 == 0:
                progress = (frame_number / frame_count) * 100
                print(f"Progress: {progress:.1f}% ({frame_number}/{frame_count} frames), Faces in this frame: {face_count}")
            
            # Write frame to output video
            out.write(display_frame)
            
            frame_number += 1
        
        print(f"Analysis complete! {frame_number} frames processed.")
        print(f"Total faces detected across all frames: {total_faces_detected}")
        print(f"Emotions data saved to {csv_path}")
        print(f"Processed video saved to {output_video_path}")
    
    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    print(f"Starting facial expression analysis on video: {VIDEO_PATH}")
    print(f"Output will be saved to: {PROCESSED_VIDEO_PATH}")
    print(f"Emotion data will be saved to: {CSV_PATH}")
    
    success = analyze_video(VIDEO_PATH, PROCESSED_VIDEO_PATH, CSV_PATH)
    
    if success:
        print("Analysis completed successfully!")
    else:
        print("Analysis failed. Please check the error message above.")
