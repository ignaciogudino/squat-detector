import cv2
import mediapipe as mp
import numpy as np
import pygame, sys, time
from math import acos, degrees

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)
up = False #Estirado
wrong = False
down = False #Flexion de piernas
count = 0
start = False

pygame.init()
success = pygame.mixer.Sound("./confirmation.wav")
error = pygame.mixer.Sound("./error.wav")


with mp_pose.Pose(
     static_image_mode=False) as pose:

     while True:
          ret, frame = cap.read()
          if ret == False:
               break
          frame = cv2.flip(frame, 1)
          height, width, _ = frame.shape
          frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
          results = pose.process(frame_rgb)

          if results.pose_landmarks is not None:
               x1 = int(results.pose_landmarks.landmark[24].x * width)
               y1 = int(results.pose_landmarks.landmark[24].y * height)

               x2 = int(results.pose_landmarks.landmark[26].x * width)
               y2 = int(results.pose_landmarks.landmark[26].y * height)

               x3 = int(results.pose_landmarks.landmark[28].x * width)
               y3 = int(results.pose_landmarks.landmark[28].y * height)

               p1 = np.array([x1, y1])
               p2 = np.array([x2, y2])
               p3 = np.array([x3, y3])

               if 100 <= p3[0] <= 500 and 100 <= p3[1] <= 500 and 100 <= p2[0] <= 500 and 100 <= p2[1] <= 500 and  100 <= p1[0] <= 500 and 100 <= p1[1] <= 500:
                    start = True
               else: 
                    start = False
          
               l1 = np.linalg.norm(p2 - p3)
               l2 = np.linalg.norm(p1 - p3)
               l3 = np.linalg.norm(p1 - p2)

               # Calcular el ángulo
               angle = degrees(acos((l1**2 + l3**2 - l2**2) / (2 * l1 * l3)))

               if start:
                    if angle >= 160:
                         up = True
                    if up == True and down == False and angle <= 130:
                         wrong = True     
                    if up == True and down == False and angle <= 80:
                         down = True
                         wrong = False
                    if up == True and down == True and angle >= 160 and wrong == False:
                         count += 1
                         up = False
                         down = False
                         wrong = False
                         success.play()
                    if wrong == True and angle >= 160:
                         up = False
                         down = False
                         wrong = False
                         error.play()   
                         cv2.putText(frame, str("X"), (0, 0), 1, 5, (0, 0, 255), 2, 10,True)                     

               # Visualización
               aux_image = np.zeros(frame.shape, np.uint8)
               cv2.line(aux_image, (x1, y1), (x2, y2), (255, 0, 0), 20)
               cv2.line(aux_image, (x2, y2), (x3, y3), (255, 0, 0), 20)
               cv2.line(aux_image, (x1, y1), (x3, y3), (255, 0, 0), 5)
               contours = np.array([[x1, y1], [x2, y2], [x3, y3]])
               cv2.fillPoly(aux_image, pts=[contours], color=(128, 0, 250))

               output = cv2.addWeighted(frame, 1, aux_image, 0.8, 0)

               cv2.circle(output, (x1, y1), 6, (0, 0, 255), 4)
               cv2.circle(output, (x2, y2), 6, (0, 0, 255), 4)
               cv2.circle(output, (x3, y3), 6, (0, 0, 255), 4)
               cv2.putText(output, str(int(angle)), (x2 + 30, y2), 1, 1.5, (0, 255, 255), 2)
               if start:
                    cv2.putText(output, str(count), (10, 50), 1, 3.5, (0, 255, 255), 2)
               else: 
                    cv2.putText(output, str("UBICACION INCORRECTA"), (10, 50), 1, 2, (0, 0, 255), 2)


               cv2.imshow("output", output)
          # cv2.imshow("Frame", frame)

          if cv2.waitKey(1) & 0xFF == 27:
               break

cap.release()
cv2.destroyAllWindows()