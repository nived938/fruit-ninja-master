import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math

class FruitObj:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.radius = random.randint(60, 95)

        self.x = random.randint(self.radius, w - self.radius)
        self.y = h + self.radius
        
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-28, -20)
        
        choices = [0, 1, 2, 3]
        weights = [0.3, 0.3, 0.25, 0.15]
        self.type = random.choices(choices, weights)[0]
        
        self.is_bomb = (self.type == 3)
        self.cut = False
        
        self.half_offset = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.7
        if self.cut:
            self.half_offset += 6
            self.vx *= 0.95
        
    def draw(self, frame):
        x, y, r = int(self.x), int(self.y), self.radius
        
        if self.cut:
            offset = self.half_offset

            self._draw_half(frame, x - offset, y + offset, r, angle=45)
            self._draw_half(frame, x + offset, y - offset, r, angle=225)
        else:
            self._draw_full(frame, x, y, r)

    def _draw_full(self, frame, x, y, r):
        if self.type == 0:
            cv2.circle(frame, (x, y), r, (34, 139, 34), -1)
            cv2.circle(frame, (x, y), int(r*0.9), (144, 238, 144), -1)
            cv2.circle(frame, (x, y), int(r*0.8), (0, 0, 200), -1)

            cv2.circle(frame, (x - int(r*0.3), y), 3, (0, 0, 0), -1)
            cv2.circle(frame, (x + int(r*0.3), y), 3, (0, 0, 0), -1)
            cv2.circle(frame, (x, y - int(r*0.3)), 3, (0, 0, 0), -1)
            cv2.circle(frame, (x, y + int(r*0.3)), 3, (0, 0, 0), -1)
        elif self.type == 1:
            cv2.circle(frame, (x, y), r, (0, 140, 255), -1)
            cv2.circle(frame, (x, y), int(r*0.8), (0, 180, 255), -1)
            cv2.line(frame, (x, y-int(r*0.8)), (x, y+int(r*0.8)), (0, 140, 255), 2)
            cv2.line(frame, (x-int(r*0.8), y), (x+int(r*0.8), y), (0, 140, 255), 2)
        elif self.type == 2:
            cv2.circle(frame, (x, y), r, (0, 230, 255), -1)
            cv2.circle(frame, (x, y), int(r*0.8), (153, 255, 255), -1)
            cv2.line(frame, (x, y-int(r*0.8)), (x, y+int(r*0.8)), (0, 230, 255), 2)
            cv2.line(frame, (x-int(r*0.8), y), (x+int(r*0.8), y), (0, 230, 255), 2)
        elif self.type == 3:
            cv2.circle(frame, (x, y), r, (20, 20, 20), -1)
            cv2.circle(frame, (x - int(r*0.3), y - int(r*0.3)), int(r*0.2), (100, 100, 100), -1)
            cv2.rectangle(frame, (x - int(r*0.2), y - r - 10), (x + int(r*0.2), y - r), (50, 50, 50), -1)
            cv2.line(frame, (x, y - r - 10), (x + 15, y - r - 30), (0, 100, 255), 3)
            cv2.circle(frame, (x + 15, y - r - 30), random.randint(3, 8), (0, 255, 255), -1)

    def _draw_half(self, frame, x, y, r, angle):
        if self.type == 0:
            cv2.ellipse(frame, (x, y), (r, r), angle, 0, 180, (34, 139, 34), -1)
            cv2.ellipse(frame, (x, y), (int(r*0.9), int(r*0.9)), angle, 0, 180, (144, 238, 144), -1)
            cv2.ellipse(frame, (x, y), (int(r*0.8), int(r*0.8)), angle, 0, 180, (0, 0, 200), -1)
        elif self.type == 1:
            cv2.ellipse(frame, (x, y), (r, r), angle, 0, 180, (0, 140, 255), -1)
            cv2.ellipse(frame, (x, y), (int(r*0.8), int(r*0.8)), angle, 0, 180, (0, 180, 255), -1)
        elif self.type == 2:
            cv2.ellipse(frame, (x, y), (r, r), angle, 0, 180, (0, 230, 255), -1)
            cv2.ellipse(frame, (x, y), (int(r*0.8), int(r*0.8)), angle, 0, 180, (153, 255, 255), -1)

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def main():
    cap = cv2.VideoCapture(1)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    objects = []
    score = 0
    game_over = False
    
    trail = []
    trail_length = 15
    
    last_spawn_time = time.time()
    spawn_interval = 1.2
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        if not game_over:
            if time.time() - last_spawn_time > spawn_interval:
                objects.append(FruitObj(w, h))
                last_spawn_time = time.time()
                spawn_interval = max(0.4, spawn_interval - 0.02)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)
        
        finger_pos = None
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:

                x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * w)
                y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * h)
                finger_pos = (x, y)
                break
                
        if finger_pos:
            trail.append(finger_pos)
            if len(trail) > trail_length:
                trail.pop(0)
        else:
            if trail:
                trail.pop(0)
                
        if len(trail) > 1:
            for i in range(1, len(trail)):
                thickness = int((i / len(trail)) * 6)

                cv2.line(frame, trail[i-1], trail[i], (200, 200, 255), thickness + 2)
                cv2.line(frame, trail[i-1], trail[i], (255, 255, 255), max(1, thickness))

        if not game_over:
            new_objects = []
            for obj in objects:
                obj.update()
                obj.draw(frame)
                
                if not obj.cut:
                    for p in trail:
                        if distance(p[0], p[1], obj.x, obj.y) < obj.radius:
                            if obj.is_bomb:
                                game_over = True
                            else:
                                obj.cut = True
                                score += 1
                            break
                            
                if obj.y < h + obj.radius * 2:
                    new_objects.append(obj)
                    
            objects = new_objects
        else:
            frame[:] = (255, 255, 255)
            
            text1 = "GAME OVER"
            text_size1 = cv2.getTextSize(text1, cv2.FONT_HERSHEY_SIMPLEX, 3.0, 8)[0]
            cv2.putText(frame, text1, ((w - text_size1[0]) // 2, h // 2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (0, 0, 255), 8)
            
            text2 = "Press 'R' to Restart"
            text_size2 = cv2.getTextSize(text2, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 4)[0]
            cv2.putText(frame, text2, ((w - text_size2[0]) // 2, h // 2 + 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 4)

            text3 = f"Score: {score}"
            text_size3 = cv2.getTextSize(text3, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 4)[0]
            cv2.putText(frame, text3, ((w - text_size3[0]) // 2, h // 2 + 130), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 4)
            
        if not game_over:
            cv2.putText(frame, f"Score: {score}", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 4)
        
        cv2.imshow("Fruits Crash", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r') and game_over:
            game_over = False
            score = 0
            objects = []
            trail = []
            spawn_interval = 1.2
            last_spawn_time = time.time()
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

