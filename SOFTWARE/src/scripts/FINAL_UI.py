import pygame
import pygame.display
import matplotlib
import numpy as np
import pylab
import wave
import pyaudio 
import struct
from std_msgs.msg import Bool
import time
from std_srvs.srv import Trigger, TriggerRequest
import re

from gtts import gTTS
from io import BytesIO

#for matplotlib-pygame backend
matplotlib.use('module://pygame_matplotlib.backend_pygame')

import matplotlib.pyplot as plt

#import ros stuff
import rospy
from std_msgs.msg import String

# transltor
from deep_translator import GoogleTranslator

clock = pygame.time.Clock()

start_time = 0
word_interval = 0

def count_syllables(w):
    return len(
        re.findall('(?!e$)[aeiouy]+', w, re.I) +
        re.findall('^[^aeiouy]*e$', w, re.I)
    )

#set pygame screen size
screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
SCREEN_HEIGHT = pygame.display.get_surface().get_size()[1]
SCREEN_WIDTH = pygame.display.get_surface().get_size()[0]
white = [255, 255, 255]
red = [255, 0, 0]
screen.fill(white)


#mic recording values
CHUNK = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000

#pyaudio setup
p = pyaudio.PyAudio()

device_id = 8
device_info = p.get_device_info_by_index(device_id)
#print("hi1", device_info) check to ensure it is calling the right device, should probably be last device in list
channels = device_info["maxInputChannels"] if (device_info["maxOutputChannels"] < device_info["maxInputChannels"]) else device_info["maxOutputChannels"]

print(CHANNELS)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=int(device_info["defaultSampleRate"]),
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=device_info["index"]
                )


#matplot fig of sin wav graph
fig, ax = plt.subplots(1, figsize=(20, 4))

#setting up plot
x = np.arange(0, 2 * CHUNK, 2)
line = ax.plot(x, np.random.rand(CHUNK), '-', lw=20)[0]
#graph setup
#ax.set_title('AUDIO WAVEFORM')
#ax.set_xlabel('samples')
#ax.set_ylabel('volume')
#ax.set_xlim(0, 2 * CHUNK)
line_scaler = 3
plt.grid(False)
plt.axis('off')
plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[-1000, 1000])
plt.margins(x=0)
ax.margins(x=0) 
fig.canvas.draw()

#setup text
pygame.font.init()
main_font_lg = pygame.font.Font("./FONTS/Tanugo-TTF-Bold.ttf",60)
main_font_md = pygame.font.Font("./FONTS/Tanugo-TTF-Bold.ttf",40)
main_font_sm = pygame.font.Font("./FONTS/Tanugo-TTF-Bold.ttf",20)
cn_font_lg = pygame.font.Font("./FONTS/NotoSansTC-Black.ttf",60)
cn_font_md = pygame.font.Font("./FONTS/NotoSansTC-Black.ttf",40)
cn_font_sm = pygame.font.Font("./FONTS/NotoSansTC-Black.ttf",20)
##English word chatgpt line
english_line_text = 'Ask a question!'
english_line = main_font_lg.render(english_line_text, False, (0, 0, 0))
english_line_rect = english_line.get_rect(center=(SCREEN_WIDTH/2, 200))
screen.blit(english_line, english_line_rect)
##Chinese word chatgpt line
chinese_line_text='問一個問題！'
chinese_line = cn_font_lg.render(chinese_line_text, False, (0, 0, 0))
chinese_line_rect = chinese_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-200))
screen.blit(chinese_line, chinese_line_rect)
##English complete chatgpt line
english_full_line_text = 'Ask a question!'
old_english_full_line_text = english_full_line_text
words_to_speak = []
english_full_line = main_font_sm.render(english_full_line_text, False, (0, 0, 0))
english_full_line_rect = english_full_line.get_rect(center=(SCREEN_WIDTH/2, 75))
screen.blit(english_full_line, english_full_line_rect)
##Chinese complete chatgpt line
chinese_full_line_text='問一個問題！'
chinese_full_line = cn_font_sm.render(chinese_full_line_text, False, (0, 0, 0))
chinese_full_line_rect = chinese_full_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-75))
screen.blit(chinese_full_line, chinese_full_line_rect)
##language lines
lang_select_font = pygame.font.Font("./FONTS/Tanugo-TTF-Bold.ttf",20)
#lang_select_font = pygame.font.SysFont("Arial", 20)
lang_line_english = lang_select_font.render('English', False, (0, 0, 0))
screen.blit(lang_line_english, (10, 10))
lang_line_slash = lang_select_font.render('/', False, (0, 0, 0))
screen.blit(lang_line_slash, (90, 10))
lang_line_chinese = lang_select_font.render('Chinese', False, (0, 0, 0))
screen.blit(lang_line_chinese, (110, 10))
##user input text
input_font = pygame.font.Font("./FONTS/Tanugo-TTF-Bold.ttf",20)
input_line_text = 'User Input:'
input_line = input_font.render(input_line_text, False, (0, 0, 0))
input_line_rect = input_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-25))
screen.blit(input_line, input_line_rect)
'''
pygame.font.init() # you have to call this at the start, 
                   # if you want to use this module.
my_font = pygame.font.SysFont('Comic Sans MS', 30)
text_surface = my_font.render('Some Text', False, (0, 0, 0))
screen.blit(text_surface, (0,0))
'''


#blitting plot at fig to screen
FIG_POSX=-300
FIG_POSY=SCREEN_HEIGHT/2-225
screen.blit(fig, (FIG_POSX, FIG_POSY))

#setup ros subscribers

#ui_client = rospy.Publisher('/gpt_response', String, queue_size=10)
rospy.init_node('UI_CLIENT', anonymous=True)
rate = rospy.Rate(100)

#check if user is still speaking for this prompt
is_responding_prompt = "OFF"
change_prompt_start_time = 0
is_responding = rospy.Publisher('/is_responding', String, queue_size=10)

first_speech = False
SPEECH_END = pygame.USEREVENT+1

pygame.mixer.init()
pygame.mixer.music.set_endevent(SPEECH_END)

# wait for this sevice to be running
rospy.wait_for_service('/change_prompt')

# Create the connection to the service. Remember it's a Trigger service
sos_service = rospy.ServiceProxy('/change_prompt', Trigger)

# Create an object of the type TriggerRequest. We nned a TriggerRequest for a Trigger service
sos = TriggerRequest()

speech_has_ended=False


def speechoutput_cb(prompt):
    global is_responding_prompt
    global line_scaler
    is_responding_prompt = "ON" #no need to subscribe to /is_responding, can assume that if speech received is_responding set to True
    global first_speech
    global english_full_line_text
    first_speech = True
    prompt.data = prompt.data[8:]
    prompt.data = prompt.data.replace("\\", "")
    prompt.data = prompt.data.replace("\n", "")
    #print(repr(prompt.data), is_responding_prompt)
    english_full_line_text = prompt.data

def userinput_cb(prompt):
    global input_line_text
    input_line_text = ''.join(i if i.isalpha() or i==" " or i=="." else '' for i in prompt.data)

def speechoutput():
    rospy.Subscriber("/gpt_response", String, speechoutput_cb)

def userinput():
    rospy.Subscriber("/input_speech", String, userinput_cb)

if __name__ == '__main__':
    try:
        speechoutput()
        userinput()

        show = True
        #main loop
        while show:
            #refresh screen
            screen.fill((255, 255, 255))
            #is_responding.publish("hi1"+is_responding_prompt)
            for event in pygame.event.get():
                # Now send the request through the connection
                #is_responding.publish("hi2"+is_responding_prompt)
                if event.type == pygame.QUIT:
                    #Stop showing when quit
                    show = False
                elif event.type == SPEECH_END and is_responding_prompt=="OFF":
                    speech_has_ended=True

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                    #reset pygame key values
                    elif event.key == pygame.K_r:
                        #resetting is_responding_prompt
                        sos_result = sos_service(sos)
                        pass
            #redrawing mouth line
            data = stream.read(CHUNK)  
            result = np.frombuffer(data, dtype=np.int16)/line_scaler
            line.set_ydata(result)
            fig.canvas.draw()
            screen.blit(fig, (FIG_POSX, FIG_POSY))
            if speech_has_ended and is_responding_prompt=="OFF" and change_prompt_start_time!=0 and pygame.time.get_ticks()-change_prompt_start_time>2000:
                #Stop showing when quit
                sos_result = sos_service(sos)
                line_scaler=3
                change_prompt_start_time=0
                speech_has_ended=False
                #print("called sos", sos_result)
            if english_full_line_text!=old_english_full_line_text:
                english_words = english_full_line_text.split(" ")
                old_english_full_line_text=english_full_line_text
                chinese_full_line_text=GoogleTranslator(source='auto', target='zh-TW').translate(english_full_line_text)
                tts = gTTS(text=english_full_line_text, lang='en')
                mp3 = BytesIO()
                tts.write_to_fp(mp3)
                mp3.seek(0)
                
                for word in english_words:
                    chinese_word = GoogleTranslator(source='auto', target='zh-TW').translate(word)
                    num_of_syl = count_syllables(word)
                    words_to_speak +=[{"english_word":word, "num_of_syl":num_of_syl, "chinese_word":chinese_word}]

                line_scaler=1
                # Play from Buffer
                pygame.mixer.music.load(mp3)
                pygame.mixer.music.play()

            if words_to_speak and (start_time==0 or pygame.time.get_ticks()-start_time > word_interval):
                english_line_text = words_to_speak[0]["english_word"] # set engline line to first word
                chinese_line_text=words_to_speak[0]["chinese_word"]
                word_interval=words_to_speak[0]["num_of_syl"]*200
                #print("english_line_text", english_line_text)
                #print(words_to_speak)
                #speak word
                start_time = pygame.time.get_ticks()
                if len(words_to_speak)==1:
                    words_to_speak=[]
                    is_responding_prompt = "OFF"
                    change_prompt_start_time=pygame.time.get_ticks()
                    #print("set prompt to off", is_responding_prompt)
                    word_interval=0
                else:    
                    words_to_speak = words_to_speak[1:] # remove word form list

            ##reblit English complete chatgpt line
            english_full_line = main_font_sm.render(english_full_line_text, False, (0, 0, 0))
            english_full_line_rect = english_full_line.get_rect(center=(SCREEN_WIDTH/2, 75))
            screen.blit(english_full_line, english_full_line_rect)

            line_scaler_print = main_font_sm.render(str(line_scaler), False, (0, 0, 0))
            line_scaler_rect = line_scaler_print.get_rect(center=(SCREEN_WIDTH/2+100, 10))
            screen.blit(line_scaler_print, line_scaler_rect)

            ##reblit Chinese complete chatgpt line
            chinese_full_line = cn_font_sm.render(chinese_full_line_text, False, (0, 0, 0))
            chinese_full_line_rect = chinese_full_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-75))
            screen.blit(chinese_full_line, chinese_full_line_rect)

            #update main english text
            english_line = main_font_lg.render(english_line_text, False, (0, 0, 0))
            english_line_rect = english_line.get_rect(center=(SCREEN_WIDTH/2, 200))
            screen.blit(english_line, english_line_rect)
            ##Chinese chatgpt line
            chinese_line = cn_font_lg.render(chinese_line_text, False, (0, 0, 0))
            chinese_line_rect = chinese_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-200))
            screen.blit(chinese_line, chinese_line_rect)

            #reblit English/chinese selection line
            screen.blit(lang_line_english, (10, 10))
            screen.blit(lang_line_slash, (90, 10))
            screen.blit(lang_line_chinese, (110, 10))
            ##user input text
            input_line = input_font.render(input_line_text, False, (0, 0, 0))
            input_line_rect = input_line.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT-25))
            screen.blit(input_line, input_line_rect)
            
            #fig.canvas.flush_events()
            pygame.display.update()
            clock.tick(60) # code that prevents our framerate from exceeding 60 fps
        rospy.spin()
    except rospy.ROSInterruptException:
        pass




