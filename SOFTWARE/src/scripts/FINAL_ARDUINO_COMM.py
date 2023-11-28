import rospy
from std_msgs.msg import String
import serial
import time

ser = serial.Serial('/dev/ttyUSB1', 115200) #sfjudy yhid sd nrrfrf

face_pos_coor = ""
old_face_pos_coor = ""
def face_pos_cmd_cb(prompt):
    global face_pos_coor
    face_pos_coor = prompt.data
    #print("callback called", face_pos_coor)

    
def face_pos_cmd():
    print("started function1")
    rospy.Subscriber("/face_pos", String, face_pos_cmd_cb)

# start ros node
rospy.init_node('FACE_TRACKER', anonymous=True)

if __name__ == '__main__':
    try:
        face_pos_cmd()
        while True:
            if face_pos_coor!="" and face_pos_coor!=old_face_pos_coor:
                ser.write(face_pos_coor.encode())
                old_face_pos_coor = face_pos_coor
                print(face_pos_coor)
                time.sleep(.1)
        rospy.spin()

    except rospy.ROSInterruptException:
        print("rospy exception1")
        pass
