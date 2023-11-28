import rospy
from std_msgs.msg import String
import cv2
import sys
import time
face_detector1 = cv2.CascadeClassifier('./CASCADES/haarcascade_frontalface_default.xml')

# reading the input image now
cam_index = 18
cap = cv2.VideoCapture(cam_index)
r, frame = cap.read()
if r == False:
    print("Webcam not opened.")
    exit()

# face publisher
face_pos = rospy.Publisher('/face_pos', String, queue_size=10)

f_max_coor = (int(640/2), int(480/2))

# start ros node
rospy.init_node('FACE_TRACKER', anonymous=True)

if __name__ == '__main__':
    try:
        while cap.isOpened():
            _, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_detector1.detectMultiScale(gray,1.1, 4 )
            w_max = 0
            for (x,y, w, h) in faces:
                if w_max < w and w>175 and w<275:
                    w_max=w
                    f_max_coor = (640-int(x+w/2), 480-int(h+y/2))
                    cv2.rectangle(frame, pt1 = (x,y),pt2 = (x+w, y+h), color = (255,0,0),thickness =  3)
            cmd = str(f_max_coor[0])+","+str(f_max_coor[1])+"-"
            face_pos.publish(cmd)

            cv2.imshow("FACE_TRACKING", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release() 
        frame.release()
        rospy.spin()

    except rospy.ROSInterruptException:
        cap.release() 
        pass
    except Exception as e:
        cap.release()
        print(e) 
        pass
