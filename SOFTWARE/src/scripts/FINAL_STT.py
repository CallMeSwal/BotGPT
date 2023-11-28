import assemblyai as aai
import rospy
from std_msgs.msg import String
from std_msgs.msg import Bool
from std_srvs.srv import Trigger, TriggerResponse

#key for AssemblyAI
aai.settings.api_key = ""

import serial
import time

is_responding_prompt = "OFF"
ignore_this_message=False
#publish voice to text to this topic
input_speech = rospy.Publisher('/input_speech', String, queue_size=10)

def trigger_response(request):
    global is_responding_prompt
    is_responding_prompt = "OFF"
    print("val of is_responding_prompt", is_responding_prompt)
    return TriggerResponse(
        success=True,
        message="Hey, roger that; we'll be right there!"
    )

def check_is_responding_cb(prompt):
    global is_responding_prompt
    is_responding_prompt = prompt.data
    print("callback called", prompt.data, is_responding_prompt)

    
def check_is_responding():
    print("started function")
    rospy.Subscriber("/is_responding", String, check_is_responding_cb)
    
rospy.init_node('TRANSCRIBER_CLIENT', anonymous=True)

rate = rospy.Rate(100)


def on_open(session_opened: aai.RealtimeSessionOpened):
    "This function is called when the connection has been established."
    print("Session ID:", session_opened.session_id)


def on_data(transcript: aai.RealtimeTranscript):
    global input_speech
    global is_responding_prompt
    global ignore_this_message

    if not transcript.text:
        return
    if isinstance(transcript, aai.RealtimeFinalTranscript):
        if  ignore_this_message==False:
            if is_responding_prompt=="OFF":
                is_responding_prompt="ON"
                input_speech.publish(str(transcript.text))
                rate.sleep()
                print(transcript.text, end="\r\n")
        else:
            ignore_this_message=False
    elif is_responding_prompt=="ON":
        ignore_this_message = True

def on_error(error: aai.RealtimeError):
    "This function is called when the connection has been closed."
    print("An error occured:", error)

def on_close():
    "This function is called when the connection has been closed."
    print("Closing Session")


transcriber = aai.RealtimeTranscriber(
  on_data=on_data,
  on_error=on_error,
  sample_rate=44_100,
  on_open=on_open, # optional
  on_close=on_close, # optional
)


if __name__ == '__main__':
    try:
        check_is_responding()
        my_service = rospy.Service(                        # create a service, specifying its name,
            '/change_prompt', Trigger, trigger_response         # type, and callback
        )

        #input_speech.publish("Hiiiiii")
        # Start the connection
        transcriber.connect()

        # Open a microphone stream
        microphone_stream = aai.extras.MicrophoneStream()

        # Press CTRL+C to abort
        transcriber.stream(microphone_stream)
                
        transcriber.close()
        rospy.spin()

    except rospy.ROSInterruptException:
        pass




