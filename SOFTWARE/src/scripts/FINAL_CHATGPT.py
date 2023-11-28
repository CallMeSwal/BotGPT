#CREDIT TO Michelangeloconcina for making this very useful tool!!
from THIRD_PARTY_LIB.chatgpt_selenium_automation.handler.chatgpt_selenium_automation import ChatGPTAutomation
from webdriver_manager.chrome import ChromeDriverManager
import time

#import ROS libs
import rospy
from std_msgs.msg import String

#publish chatGPT responses to this topic
gpt_response = rospy.Publisher('/gpt_response', String, queue_size=10)
rospy.init_node('GPT_CLIENT', anonymous=True)
rate = rospy.Rate(100)

# Create an instance
CHROME_LOCATION = "/usr/bin/google-chrome"
CHROME_DRIVER_LOCATION = ChromeDriverManager().install() #must pip install webdriver
chatgpt = ChatGPTAutomation(CHROME_LOCATION, CHROME_DRIVER_LOCATION)
prompt = "Can you please limit any future response to 15 words?"
chatgpt.send_prompt_to_chatgpt(prompt)
prompt = "Can you please finish responding to any prompt within 3 seconds? Can you please conclude the end of your response with ###. Do not use ### anywhere else in the response? Please do this for all future prompts."
chatgpt.send_prompt_to_chatgpt(prompt)

def voiceinput_cb(prompt):
    global chatgpt
    global gpt_response
    global rate
    
    prompt.data = prompt.data.replace("'", "") #apostrophes causing issue, not sure why, bad fix
    print(prompt.data)
    chatgpt.send_prompt_to_chatgpt(prompt.data)
    response = chatgpt.return_last_response()
    response = response.split(" ###")[0] # remove hash with space before it
    response = response.split("###")[0] # remove hash
    print(response.split(" "))
    gpt_response.publish(response)
    print(response)
    rate.sleep()
    
def voiceinput():
    rospy.Subscriber("/input_speech", String, voiceinput_cb)

if __name__ == '__main__':
    try:
        voiceinput()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass

# Close the browser and terminate the WebDriver session
chatgpt.quit()
