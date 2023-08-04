#!/usr/bin/env python3
from flask import Flask,g,render_template,request,jsonify,redirect,session,url_for	
from flask_login import login_user, login_required, current_user, logout_user
#from flask_session import Session
import threading
from datetime import date,timedelta,datetime 
#import asyncio
#import argparse
#from multiprocessing import Process
from multiprocessing.pool import ThreadPool
#import logging
import os
import json
import glob
import random 
import jinja2
##import RPi.GPIO as GPIO
import subprocess
import time
import vlc

from config import Config
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_apscheduler import APScheduler

app = Flask(__name__)
app.config.from_object(Config)
boostrap = Bootstrap(app)
bcrypt = Bcrypt(app)
login = LoginManager(app)
mail = Mail(app)
db = SQLAlchemy(app)
app.app_context().push()
login.login_view ='login'
login.login_message= 'You must login to access this page'
login.login_message_category = 'info'

scheduler = APScheduler()
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()
CORS(app)

------------------------------------------------------------------
__dir__ = "./app/static/assets/"
__fileListPc__ = []
__fileListPi__ = []
#                 0       1        2       3     4       5           
__typeList__ = ["all","podcast","國語","台語","古典","張學友"]
__fileList_Rn__ = []
__indexMax__ = 0
__indexMaxPi__ = 0
__indexPi__ = 1
__cronIndexPi__ = 1
__indexPc__ = 1 
__num4dPi_i__ = 4
__num4dPi__ = [ 0, 0, 0, 0 ]
__keyTimerPi__= False
__timer_Key__ = None
__musicVlcPiDuration__ = 0
__musicPiPlaying__ = False
__radioPiPlayingNo__ =  0
__volumePi__ = 65
__volumePiMute__ = False
__musicPiPlayMode__ = 1
__down_thread__ = None
__downStatus__ = False
__return_code__ = None
__playRatePi__ = 1
__sleepTimePi__ = 0
__timer_Sleep__ = None
__cronTimeHour__ = '00'
__cronTimeMin__ = '00'
__cronStatus__= False
__baseFolderList__ = '' 
__subFolderList__ = '' 
    
radioUrl={
        "url01":"https://stream.live.vc.bbcmedia.co.uk/bbc_world_service",
        "url02":"http://stream.live.vc.bbcmedia.co.uk/bbc_london",
        "url03":"https://npr-ice.streamguys1.com/live.mp3",
        "url04":"https://prod-18-232-88-129.wostreaming.net/foxnewsradio-foxnewsradioaac-imc?session-id=0f99acd44126cef33b40ce217c9ea1ad",
        "url05":"http://stream.live.vc.bbcmedia.co.uk/bbc_radio_five_live",
        "url06":"http://stream.live.vc.bbcmedia.co.uk/bbc_asian_network",
        "url07":"http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one",
        "url08":"https://icrt.leanstream.co/ICRTFM-MP3?args=web",
        "url09":"http://stream.live.vc.bbcmedia.co.uk/bbc_radio_two",
        "url10":"http://localhost:8000/stream.ogg",
        "url11":"http://onair.family977.com.tw:8000/live.mp3",
        "url12":"https://n09.rcs.revma.com/aw9uqyxy2tzuv?rj-ttl=5&rj-tok=AAABhZollCEACdvxzVVN61ARVg",
        "url13":"https://n10.rcs.revma.com/ndk05tyy2tzuv?rj-ttl=5&rj-tok=AAABhZouFPAAQudE3-49-1PFHQ",
        "url14":"https://n09.rcs.revma.com/7mnq8rt7k5zuv?rj-ttl=5&rj-tok=AAABhZovh0cASZAucd0xcmxkvQ",
        "url15":"https://n11a-eu.rcs.revma.com/em90w4aeewzuv?rj-tok=AAABhZoyef8AtFfbdaYYtKJnaw&rj-ttl=5",
        "url16":"https://n07.rcs.revma.com/78fm9wyy2tzuv?rj-ttl=5&rj-tok=AAABhZozdbQAkV-tPDO6A5aHag",
        "url17":"http://stream.live.vc.bbcmedia.co.uk/bbc_radio_three",
        "url18":"http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm",
        "url19":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url20":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url21":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url22":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url23":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url24":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url25":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url26":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url27":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url28":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url29":"http://stream.live.vc.bbcmedia.co.uk/bbc_6music",
        "url30":"http://media-ice.musicradio.com:80/ClassicFMMP3"
        }
url_json=json.dumps(radioUrl)
__url__=json.loads(url_json)
#------------------------------------------------------------------
opt = "--aout=alsa --alsa-audio-device=hw --verbose=-1"
__musicVlcInstance__ = vlc.Instance(opt)
__radioVlcInstance__ = vlc.Instance(opt)
__vlcEnded__ = vlc.State.Ended
__vlcPaused__ = vlc.State.Paused
__vlcPlaying__ = vlc.State.Playing
__vlcmedia__ = None 
__musicVlcPi__ = __musicVlcInstance__.media_player_new()
__radioVlcPi__ = __radioVlcInstance__.media_player_new()
#------------------------------------------------------------------

def pressedNumber(channel):
    if(channel ==12):
        Number = 1
        print("1 Pressed")
    elif(channel ==16):
        Number = 2
        print("2 Pressed")
    elif(channel ==18):
        Number = 3
        print("3 Pressed")
    elif(channel ==11):
        Number = 4
        print("4 Pressed")
    elif(channel ==13):
        Number = 5
        print("5 Pressed")
    elif(channel ==15):
        Number = 6
        print("6 Pressed")
    return Number

def handleSelectedPi():
    global __musicVlcInstance__
    global __musicVlcPi__
    global __musicPiPlaying__
    global __dir__
    global __fileListPi__
    global __num4dPi__
    global __indexPi__
    global __num4dPi_i__
    global __vlcmedia__
    #file = __dir__ + __fileListPi__[__indexPi__]
    handlePlayPi(__indexPi__)
    #__musicVlcPi__.stop()
    #__vlcmedia__  = __musicVlcInstance__.media_new(file)
    #__musicVlcPi__.set_media(__vlcmedia__)
    #__musicVlcPi__.play()
    #__musicPiPlaying__ = True
    #print("play:"+file)
    __keyTimerPi__= False
    __num4dPi__ = [0, 0, 0, 0]
    __num4dPi_i__ = 4
    
#Convert int array to decimal interger
def convert(list):
    no = sum(d * 10**i for i, d in enumerate(list[::-1]))
    return(no)

def handlePlayPi(index):
    global __fileListPi__
    global __dir__
    global __musicVlcInstance__
    global __vlcmedia__
    global __musicVlcPi__
    global __musicPiPlaying__
    file = __dir__ + __fileListPi__[index]
    __musicVlcPi__.stop()
    __vlcmedia__  = __musicVlcInstance__.media_new(file)
    __musicVlcPi__.set_media(__vlcmedia__)
    __musicVlcPi__.play()
    __musicPiPlaying__ = True
    print("play: "+file)
    
def handleCronPlayPi():
    global __cronIndexPi__
    global __indexPi__
    handlePlayPi(__cronIndexPi__)
    __indexPi = __cronIndexPi__
   

#def handleCronPlayPiRadio():
#    global __radioVlcInstance__
#    global __radioPiPlayingNo__
#    global __radioVlcPi__
#    global __urlCron__
#    vlcmediaRadio  = __radioVlcInstance__.media_new(__urlCron__)
#    __radioVlcPi__.set_media(vlcmediaRadio)
#   __radioVlcPi__.play()

 
    
def handleKeyInputPi(channel):
    global __indexPi__
    global __indexMaxPi__
    global __dir__
    global __musicPiPlaying__
    global __num4dPi_i__
    global __num4dPi__
    global __timer_Key__
    if (__keyTimerPi__== True):
        __timer_Key__.cancel()
    Number = pressedNumber(channel)
    __num4dPi_i__ = __num4dPi_i__ - 1
    if(__num4dPi_i__ < 0):
        __num4dPi_i__ = 3 
    __num4dPi__[0] = __num4dPi__[1] 
    __num4dPi__[1] = __num4dPi__[2] 
    __num4dPi__[2] = __num4dPi__[3] 
    __num4dPi__[3] = Number 
    num = convert(__num4dPi__)
    __indexPi__ = ( num % __indexMaxPi__) - 1
    if (__indexPi__ == -1 ):
       __indexPi__ = __indexPi__ + __indexMaxPi__
    print("the NO."+str(__indexPi__ + 1)+" mp3 will be played")
    __timer_Key__ = threading.Timer(3, handleSelectedPi)
    __timer_Key__.start()
    __keyTimerPi__= True

def handleNextPi():
    global __indexPi__
    global __indexMaxPi__
    #global __dir__
    #global __musicVlcInstance__
    #global __musicVlcPi__
    #global __vlcmedia__
    #global __musicPiPlaying__
    #global __musicPiPlayMode__
    if (__musicPiPlayMode__ == 1):
        __indexPi__ = random.randrange(__indexMaxPi__)
    elif(__musicPiPlayMode__ == 0):
        __indexPi__ = __indexPi__ + 1
        if (__indexPi__ == __indexMaxPi__):
            __indexPi__ = 0; 
    else:
        __indexPi__ = __indexPi__
    #file = __dir__ + __fileListPi__[__indexPi__]
    handlePlayPi(__indexPi__)
    #__musicVlcPi__.stop()
    #__vlcmedia__  = __musicVlcInstance__.media_new(file)
    #__musicVlcPi__.set_media(__vlcmedia__)
    #__musicVlcPi__.play()
    #__musicPiPlaying__ = True
    print("__indexPi__:"+str(__indexPi__))
    #print("Next play:"+file)

def handlePrePi():
    global __indexPi__
    global __indexMaxPi__
    #global __fileListPi__
    #global __dir__
    #global __musicVlcInstance__
    #global __vlcmedia__
    #global __musicVlcPi__
    #global __musicPiPlaying__
    if (__musicPiPlayMode__ == 1):
        __indexPi__ = random.randrange(__indexMaxPi__)
    if (__musicPiPlayMode__ == 0):
        __indexPi__ = __indexPi__ - 1
        if (__indexPi__ < 0):
           __indexPi__= __indexMaxPi__ - 1
    else:
        __indexPi__ = __indexPi__
    #global __fileListPi__
    #file = __dir__ + __fileListPi__[__indexPi__]
    handlePlayPi(__indexPi__)
    #__vlcmedia__  = __musicVlcInstance__.media_new(file)
    #__musicVlcPi__.stop()
    #__musicVlcPi__.set_media(__vlcmedia__)
    #__musicVlcPi__.play()
    #__musicPiPlaying__ = True
    print("__indexPi__:"+str(__indexPi__))
    #print("Pre play:"+file)

def handlePlayPausePi():
    global __indexPi__
    global __musicVlcInstance__
    global __musicVlcPi__
    global __musicPiPlaying__
    global __fileListPi__
    if (__musicPiPlaying__ == True):
        time.sleep(0.1)
        __musicVlcPi__.pause()
        __musicPiPlaying__ = False
    else:
        file = __dir__ + __fileListPi__[__indexPi__]
       # vlcmedia  = __musicVlcInstance__.media_new(file)
       # __musicVlcPi__.set_media(vlcmedia)
        __musicVlcPi__.play()
        __musicPiPlaying__ = True
        print("PlayPause- Play:"+file)
        
def handlePlayRatePi():
    global __musicVlcPi__
    global __playRatePi__
    __playRatePi__ = __playRatePi__ + 0.25
    if __playRatePi__ > 2.5:
        __playRatePi__ = 0.5
    __musicVlcPi__.set_rate(__playRatePi__)
    

def handleVolCtlPi(vol):
    global __musicVlcPi__
    global __radioVlcPi__
    global __volumePi__
    __volumePi__ = __volumePi__ + vol
    if __volumePi__ < 0:
        __volumePi__ = 0 
    if __volumePi__ > 100:
        __volumePi__ = 100 
    if __volumePi__ ==  0:
        __volumePiMute__ = True
    else:      
        __volumePiMute__ = False
    vlcvolume = __volumePi__
    __radioVlcPi__.audio_set_volume(vlcvolume)
    __musicVlcPi__.audio_set_volume(vlcvolume)

#def get_files(root):
#    files = []
#    def scan_dir(dir):
#        for f in os.listdir(dir):
#            #f = os.path.join(dir, f)
#            if os.path.isdir(f):
#                scan_dir(f)
#            elif os.path.splitext(f)[1] == ".mp3":
#                files.append(f)
#   scan_dir(root)
#   return files

def continuePlaying():
    global __musicVlcPi__
    global __musicPiPlaying__
    global __vlcEnded__
    global __vlcPlaying__
    state = __musicVlcPi__.get_state()
    #print(state)
    if (__musicPiPlaying__ == True ):
        if (state == __vlcEnded__):
            handleNextPi();
        threading.Timer( 10 , continuePlaying ).start()
    else:
        threading.Timer( 10 , continuePlaying ).start()

def stopPlaying():
    global __musicVlcPi__
    global __radioVlcPi__
    global __musicPiPlaying__
    global __radioPiPlayingNo__
    global __sleepTimePi__
    if (__musicPiPlaying__ ==True or __radioPiPlayingNo__ != 0):
        __musicVlcPi__.stop()
        __radioVlcPi__.stop()
        __musicPiPlaying__ = False
        __radioPiPlayingNo__ = 0
        # set SleepTimePi to NonSleep
        __sleeTimePi__ =3
        

def get_subdirectories(folder_path):
    subdirectories = []
    for entry in os.scandir(folder_path):
        if entry.is_dir():
            subdirectories.append(entry.name)
    return subdirectories   
 
def genFileList_sh(style):
    global __fileListPc__
    global __fileListPi__
    global __dir__
    global __musicVlcPi__
    global __vlcmedia__
    global __musicPiPlaying__
    global __indexMaxPc__
    global __indexMaxPi__
    global __indexPi__
    global __typeList__
    global __baseFolderList__
    match style:
        case 0:
           subdir = __typeList__[0]
        case 1:
           subdir = __typeList__[1]
        case 2:
           subdir = __typeList__[2]
    __musicVlcPi__.stop()
    __musicPiPlaying__ = False
    songs = []; 
    for path, subdirs, files in os.walk(__dir__ + subdir, followlinks=True):
       # for name in files:
        path = path[(len(__dir__)-1):];
        path = path+"/";
        path = path[1:];
        files = [path + file for file in files];
        songs = songs + files; 
    songsPc = [ f for f in songs if f[-4:] == '.mp3' or f[-4:] =='.MP3' or f[-5:] == '.flac' or f[-5:] == '.FLAC'];
    songsPc.sort()
    __fileListPc__ = songsPc;
   # flac/ape format song  extend (for PI Vlc player, vlc support more types of formats)
    songsPi = [ f for f in songs if f[-4:] == '.ape' or f[-4:] == '.APE'];
    songsPi = songsPi +songsPc
    songsPi.sort()
    __fileListPi__ = songsPi
    
    __indexMaxPc__ = len(__fileListPc__) 
    __indexMaxPi__ = len(__fileListPi__) 
    print("indexPC:"+str(__indexMaxPc__))
    print("indexPi:"+str(__indexMaxPi__))
    
    __indexPi__ = random.randrange(__indexMaxPi__)
    file = __dir__ + __fileListPi__[__indexPi__]
    __vlcmedia__  = __musicVlcInstance__.media_new(file)
    __musicVlcPi__.set_media(__vlcmedia__)
 


def genFileList_sh2(subdir):
    global __fileListPc__
    global __fileListPi__
    global __dir__
    global __musicVlcPi__
    global __vlcmedia__
    global __musicPiPlaying__
    global __indexMaxPc__
    global __indexMaxPi__
    global __indexPi__
    global __typeList__
    global __baseFolderList__
    __musicVlcPi__.stop()
    __musicPiPlaying__ = False
    songs = []; 
    for path, subdirs, files in os.walk(__dir__ + subdir, followlinks=True):
       # for name in files:
        path = path[(len(__dir__)-1):];
        path = path+"/";
        path = path[1:];
        files = [path + file for file in files];
        songs = songs + files; 
    songsPc = [ f for f in songs if f[-4:] == '.mp3' or f[-4:] =='.MP3' or f[-5:] == '.flac' or f[-5:] == '.FLAC'];
    songsPc.sort()
    __fileListPc__ = songsPc;
   # flac/ape format song  extend (for PI Vlc player, vlc support more types of formats)
    songsPi = [ f for f in songs if f[-4:] == '.ape' or f[-4:] == '.APE'];
    songsPi = songsPi +songsPc
    songsPi.sort()
    __fileListPi__ = songsPi
    
    __indexMaxPc__ = len(__fileListPc__) 
    __indexMaxPi__ = len(__fileListPi__) 
    print("indexPC:"+str(__indexMaxPc__))
    print("indexPi:"+str(__indexMaxPi__))
    
    __indexPi__ = random.randrange(__indexMaxPi__)
    file = __dir__ + __fileListPi__[__indexPi__]
    __vlcmedia__  = __musicVlcInstance__.media_new(file)
    __musicVlcPi__.set_media(__vlcmedia__)

def downPodcastFile_sh():
    N = 3
    Ndays_ago = date.today()- timedelta(days=N)
    Ndays_ago.strftime("%Y-%m-%d")
    opt = getpodcast.options(
    root_dir = '/home/ubuntu/Music/podcast',
    date_from = str(Ndays_ago),
    deleteold = True,
    run = True)
    podcasts = {
       "BBC" : "http://podcasts.files.bbci.co.uk/p02nq0gn.rss"
    }
    getpodcast.getpodcast(podcasts, opt)

def downPodcastFile_sh2():
    try:
      command = ["/home/ubuntu/Pi_Media_Server/.venv/bin/python3", "/home/ubuntu/Pi_Media_Server/getpodcast_sh.py"]
      p = subprocess.Popen(command)
      return p
    except FileNotFoundError as e:
       raise AudioEngineUnavailable(f'AudioEngineUnavailable: {e}')

def process_monitor(p):
    global __return_code__
    global __downStatus__
    __return_code__ = p.poll()
    if __return_code__ == None:
        __return_code__ = p.wait()
    __downStatus__ = False
#----------------------------------------------------------------------------
#==============================================================================================
if(False):
    GPIO.setmode(GPIO.BOARD)
   # gpio binary  
    GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
   # PLAY NEXT PRE BACK MUTE 
    GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(31, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(33, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(37, GPIO.IN, pull_up_down=GPIO.PUD_UP)

   #callback function 
    GPIO.add_event_detect(12, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(16, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(18, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(11, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(15, GPIO.FALLING, callback=handleKeyInputPi, bouncetime=500)
    GPIO.add_event_detect(29, GPIO.FALLING, callback=handlePlayPausePi, bouncetime=500)
    GPIO.add_event_detect(31, GPIO.FALLING, callback=handleNextPi, bouncetime=500)
    GPIO.add_event_detect(33, GPIO.FALLING, callback=handlePrePi, bouncetime=500)
   #GPIO.add_event_detect(37, GPIO.FALLING, callback=handlevolumePi, bouncetime=500)
    
#---------------------------------------------------------------------
#file list Method 1
#    __fileList__ = [ f for f in os.listdir(r'./static/assets/.') if f[-4:] == '.mp3' ]
#    mp3_list.sort(key=lambda x:int(x[:-4]))
#--------------------------------------------------------------------
#file list Method 2
#    songs = []; 
#    for path, subdirs, files in os.walk(r'./static/assets'):
#       # for name in files:
#        path = path[(len(__dir__)-1):];
#        path = path+"/";
#        path = path[1:];
#        files = [path + file for file in files];
#        songs= songs + files; 
#    songs = [ f for f in songs if f[-4:] == '.mp3' ];
#    __fileList__ = songs;
#---------------------------------------------------------------------
#file list Methos 3
#    __fileListRn__ = glob.glob(r'../Music/*.mp3')
#    __fileListRn__.sort(key=lambda x:int(x[25:-4]))
#---------------------------------------------------------------------
#file list Method 4
#    __fileList__ = get_files(__dir__)
#    __fileList__.sort(key=lambda x:int(x[:-4]))
#---------------------------------------------------------------------
#==============================================================================================
#folder_path = '/media/usb1/'
folder_path = './app/static/assets/'
__baseFolderList__ = get_subdirectories(folder_path)
print(__baseFolderList__)

genFileList_sh2("國語/張學友")
if not (len(__fileListPc__) > 0):
    print ("No mp3 files found!")
print ('--- Press button #play to start playing mp3 ---')

file1 = __dir__ + __fileListPi__[__indexPi__]
__vlcmedia__  = __musicVlcInstance__.media_new(file1)
__musicVlcPi__.set_media(__vlcmedia__)
__musicVlcPiDuration__ = __vlcmedia__.get_duration()
threading.Timer( 10 , continuePlaying ).start()
#==============================================================================================

@app.route('/',methods=['get','post'])
@login_required
def index():
    global __dir__
    global __fileListPc__
    global __fileListPi__
    global __indexPi__
    global __musicPiPlaying__ 
    global __musicPiPlayMode__
    global __radioPiPlayingNo__ 
    global __volumePi__
    global __volumePiMute__
    global __playRatePi__
    global __cronStatus__
    global __cronTimeHour__
    global __cronTimeMin__
    global __cronIndexPi__
    global __musicVlcPi__
    global __baseFolderList__
    title ="Home"
    if request.method == 'GET':
        __playRatePi__ = 1
        __musicVlcPi__.set_rate(__playRatePi__)
        return render_template('index.html')
    if request.method =='POST':
        return jsonify({
        "fileListPc" : __fileListPc__,
        "fileListPi" : __fileListPi__,
        "indexPi" : __indexPi__,
        "musicPiPlaying" : __musicPiPlaying__,
        "musicPiPlayMode" : __musicPiPlayMode__,
        "radioPiPlayingNo" : __radioPiPlayingNo__,
        "volumePi" : __volumePi__,
        "volumePiMute" : __volumePiMute__,
        "playRatePi" : __playRatePi__,
        "musicPiDuration":__musicVlcPiDuration__,
        "cronStatus":__cronStatus__,
        "cronTimeHour":__cronTimeHour__,
        "cronTimeMin":__cronTimeMin__,
        "cronIndexPi":__cronIndexPi__,
        "baseFolderList":__baseFolderList__
         })
    return render_template('index.html', title=title) 

@app.route('/textpost',methods=['get','post'])
@login_required
def textpost():
    title ="Post Text"
    form = PostTextForm()
    if form.validate_on_submit():
        body = form.text.data
        post = Post(body=body)
        current_user.posts.append(post)
        db.session.commit()
        flash('Suscess Post', category='info')
    n_followers = len(current_user.followers)
    n_followed = len(current_user.followed)
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('post.html', form=form, posts=posts, title=title,  n_followers= n_followers, n_followed=n_followed) 
    
    
@app.route('/register',methods=['get','post'])
def register():
    title ="Register"
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = bcrypt.generate_password_hash(form.password.data)
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Congrats, Registration success", category='success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title= title)

 
@app.route('/login',methods=['get','post'])
def login():
    title ='Login'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember= form.remember.data
        #check if password is matched
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            #User exits and password matched
            login_user(user, remember=remember)
            flash('Login Success', category='info')
            #if request.args.get('next'):
            #    next_page = request.args.get('next')
            #    return redirect(url_for(next_page))
            return redirect(url_for('index'))
        flash('User does not exist or password not match', category='danger')
    return render_template('login.html', form=form, title= title)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reset_password_request', methods=['get','post'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    title = 'Reset Password'
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        token = user.generate_reset_password_token()
        send_reset_password_mail(user, token)
        flash('Password reset request mail is sent, please check ypur mail', category='info')
    return render_template('reset_password_request.html', form=form, title= title)

@app.route('/reset_password/<token>', methods=['get','post'])
def reset_password():
    title = 'Reset Password'
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_summit():
        user = User.check_reset_password_token(token)
        if user:
            user.password = bcrypt.generate_password(form.password.data)
            db.session.commit()
            flash('Your password has benn reset, you can login now', category='info')
            redirect(url_for('login'))
        else:
            flash('This user does not exist', category='info')
            return redirect(url_for('login'))
    return render_template('reset_password_request.html', form=form, title= title)
    

@app.route('/playPrePi', methods=['POST'])
def playPrePi():
    global __indexPi__
    global __musicPiPlaying__
    handlePrePi();
    return jsonify({ 
           "indexPi":__indexPi__,
           "musicPiPlaying" :__musicPiPlaying__
          })
        
@app.route('/playNextPi', methods=['POST'])
def playNextPi():
    global __indexPi__
    global __musicPiPlaying__
    handleNextPi();
    return jsonify({ 
           "indexPi":__indexPi__,
           "musicPiPlaying" :__musicPiPlaying__
          })
@app.route('/playIndexPi', methods=['POST'])
def playIndexPi():
    global __indexPi__
    global __musicPiPlaying__
    global __vlcmedia__
    global __musicVlcPiDuration__
    data=request.get_json()
    num=int(data["indexPi"])
    __indexPi__= num
   # file = __dir__ + __fileListPi__[__indexPi__]
    handlePlayPi(__indexPi__)
   # __musicVlcPi__.stop()
   # __vlcmedia__  = __musicVlcInstance__.media_new(file)
   # __musicVlcPi__.set_media(__vlcmedia__)
   # __musicVlcPi__.play()
   # __musicPiPlaying__ = True
   # __musicVlcPiDuration__ = __vlcmedia__.get_duration()
    print("__indexPi__:"+str(__indexPi__))
    #print("Next play:"+file)
    return jsonify({ 
           "indexPi":__indexPi__,
           "musicPiPlaying" :__musicPiPlaying__
          })
    
@app.route('/playSelectedPi', methods=['POST'])
def playSelectedPi():
    global __indexPi__
    global __musicPiPlaying__
    global __indexMaxPi__
    global __vlcmedia__
    global __musicVlcPiDuration__
    data=request.get_json()
    num=int(data["num"])
    __indexPi__= num % __indexMaxPi__
    handleSelectedPi();
    __musicVlcPiDuration__ = __vlcmedia__.get_duration()
    print("musicPiDuration")
    print(__musicVlcPiDuration__)
    return jsonify({ 
           "indexPi":__indexPi__,
           "musicPiPlaying" :__musicPiPlaying__
          })

@app.route('/playPausePi', methods=['POST'])
def playPausePi():
    global __musicPiPlaying__
    global __indexPi__
    handlePlayPausePi()
    return jsonify({
        "musicPiPlaying" : __musicPiPlaying__,
        "indexPi" : __indexPi__
         })

@app.route('/setPlayRatePi', methods=['POST'])
def setPlayRatePi():
    global __playRatePi__
    print("playRatePi: " + str(__playRatePi__))
    handlePlayRatePi()
    return jsonify({
        "playRatePi" : __playRatePi__
         })
    
@app.route('/setPlayModePi', methods=['POST'])
def setPlayModePi():
    global __musicPiPlayMode__
    data=request.get_json()
    __musicPiPlayMode__=int(data["mode"])
    return jsonify({
        "musicPiPlayMode" : __musicPiPlayMode__
         })
    
@app.route('/setTimePi', methods=['POST'])
def setTimePi():
    global __musicVlcPi__
    data=request.get_json()
    setTimePi=int(data["time"])
    __musicVlcPi__.set_time(setTimePi*1000)
    print("setTimePi:")
    return jsonify({
        "setTimePi" : setTimePi
         })
    
@app.route('/playRadioPi', methods=['POST'])
def playRadioPi():
    global __radioVlcInstance__
    global __radioPiPlayingNo__
    global __radioVlcPi__
    global __url__
    data=request.get_json()
    radioNo=int(data["radioNo"])
    match radioNo:
        case 1:
           url =__url__["url01"]
        case 2:
           url =__url__["url02"]
        case 3:
           url =__url__["url03"]
        case 4:
           url =__url__["url04"]
        case 5:
           url =__url__["url05"]
        case 6:
           url =__url__["url06"]
        case 7:
           url =__url__["url07"]
        case 8:
           url =__url__["url08"]
        case 9:
           url =__url__["url09"]
        case 10:
           url =__url__["url10"]
        case 11:
           url =__url__["url11"]
        case 12:
           url =__url__["url12"]
        case 13:
           url =__url__["url13"]
        case 14:
           url =__url__["url14"]
        case 15:
           url =__url__["url15"]
        case 16:
           url =__url__["url16"]
        case 17:
           url =__url__["url17"]
        case 18:
           url =__url__["url18"]
        case 19:
           url =__url__["url19"]
        case 20:
           url =__url__["url20"]
        case 21:
           url =__url__["url21"]
        case 22:
           url =__url__["url22"]
        case 23:
           url =__url__["url23"]
        case 24:
           url =__url__["url24"]
        case 25:
           url =__url__["url25"]
        case 26:
           url =__url__["url26"]
        case 27:
           url =__url__["url27"]
        case 28:
           url =__url__["url28"]
        case 29:
           url =__url__["url29"]
        case 30:
           url =__url__["url30"]
        case _:
           url ="https://stream.live.vc.bbcmedia.co.uk/bbc_world_service"
    if(radioNo == 0):
        __radioVlcPi__.stop()
        __radioPiPlayingNo__ = 0
    else:
        if(__radioPiPlayingNo__ != 0):
           __radioVlcPi__.stop()
        vlcmediaRadio  = __radioVlcInstance__.media_new(url)
        __radioVlcPi__.set_media(vlcmediaRadio)
        __radioVlcPi__.play()
        __radioPiPlayingNo__ = radioNo
        print("Radio Stream URL :"+url)        
    return jsonify({
        "radioPiPlayingNo" : __radioPiPlayingNo__
         })

@app.route('/volumeControlPi', methods=['POST'])
def volumeControlPi():
    global __volumePi__
    global __volumePiMute__
    data=request.get_json()
    vol=int(data["vol"])
    handleVolCtlPi(vol)
    return jsonify({
        "volumePi" : __volumePi__,
        "volumePiMute" : __volumePiMute__
         })
    
@app.route('/getMetaPi', methods=['POST'])
def getMetaPi():
    global __fileListPc__
    global __fileListPi__
    global __musicVlcPiDuration__
    global __musicVlcPi__
    global __indexPi__
    global __volumePi__
    global __volumePiMute__
    global __musicPiPlaying__
    
    musicVlcPiCurrent =__musicVlcPi__.get_time()
    __musicVlcPiDuration__ = __vlcmedia__.get_duration()
    return jsonify({
        "durationPi" : __musicVlcPiDuration__,
        "currentPi" : musicVlcPiCurrent,
        "indexPi" : __indexPi__,
        "volumePi" : __volumePi__,
        "volumePiMute" : __volumePiMute__,
        "musicPiPlaying" : __musicPiPlaying__
         })
@app.route('/refreshMetaPi', methods=['POST'])
def refreshMetaPi():
    global __dir__
    global __fileListPc__
    global __fileListPi__
    global __indexPi__
    global __musicPiPlaying__ 
    global __musicPiPlayMode__
    global __radioPiPlayingNo__ 
    global __volumePi__
    global __volumePiMute__
    global __playRatePi__
    global __cronStatus__
    global __cronTimeHour__
    global __cronTimeMin__
    global __cronIndexPi__
    global __musicVlcPiDuration__
    global __musicVlcPi__
    
    musicVlcPiCurrent =__musicVlcPi__.get_time()
    __musicVlcPiDuration__ = __vlcmedia__.get_duration()
    return jsonify({
        "fileListPc" : __fileListPc__,
        "fileListPi" : __fileListPi__,
        "indexPi" : __indexPi__,
        "musicPiPlaying" : __musicPiPlaying__,
        "musicPiPlayMode" : __musicPiPlayMode__,
        "radioPiPlayingNo" : __radioPiPlayingNo__,
        "volumePi" : __volumePi__,
        "volumePiMute" : __volumePiMute__,
        "playRatePi" : __playRatePi__,
        "musicPiDuration":__musicVlcPiDuration__,
        "currentPi" : musicVlcPiCurrent,
        "cronStatus":__cronStatus__,
        "cronTimeHour":__cronTimeHour__,
        "cronTimeMin":__cronTimeMin__,
        "cronIndexPi":__cronIndexPi__
         })
    
@app.route('/getFileList', methods=['POST'])
def getFileList():
    global __fileListPc__
    global __fileListPi__
    global __musicPiPlaying__
    global __indexPi__
    global __cronIndexPi__
    data=request.get_json()
    style=int(data["style"])
    genFileList_sh(style)
    return jsonify({
        "fileListPc" : __fileListPc__,
        "fileListPi" : __fileListPi__,
        "musicPiPlaying" : __musicPiPlaying__,
        "indexPi":__indexPi__,
        "cronIndexPi":__cronIndexPi__
         })
    
@app.route('/getFileList2', methods=['POST'])
def getFileList2():
    global __fileListPc__
    global __fileListPi__
    global __musicPiPlaying__
    global __indexPi__
    global __cronIndexPi__
    data=request.get_json()
    musictype=data["musictype"]
    musicstar=data["musicstar"]
    subdir=musictype+"/"+musicstar
    genFileList_sh2(subdir)
    return jsonify({
        "fileListPc" : __fileListPc__,
        "fileListPi" : __fileListPi__,
        "musicPiPlaying" : __musicPiPlaying__,
        "indexPi":__indexPi__,
        "cronIndexPi":__cronIndexPi__
         })

@app.route('/downPodcastFile', methods=['POST'])
def downPodcastFile():
    global __down_thread__
    global __downStatus__
    msg = "" 
    if __downStatus__ == 0:
        __downStatus__ = 1 
        print("downStatus: "+str(__downStatus__))
        #time.sleep(10)
        __down_thread__=Thread(target=downPodcastFile_sh)
        __down_thread__.start()
        print("DownPodcast thread start to run")
        __down_thread__.join()
        __downStatus__ = 0 
        print("DownPodcast thread finished--> downStatus: "+str(__downStatus__))
        msg ="DownPodcast thread finished--> downStatus: "+str(__downStatus__)
    else:
        print("DonwPodcast thread is Running, please wait")
        msg= "DonwPodcast thread is Running, please wait"
    return jsonify({
        "downStatus" : __downStatus__,
        "msg" : msg
         })

#this method fork a proceess run  getpodcast_sh.py
@app.route('/downPodcastFile2', methods=['POST'])
def downPodcastFile2():
    global __down_thread__
    global __downStatus__
    msg =""
    if __downStatus__ == False:
        __downStatus__ = True 
        print("downStatus: "+str(__downStatus__))
        #time.sleep(10)
        __p__=downPodcastFile_sh2()
        monitor_thread = Thread(target=process_monitor,args=(__p__,)) 
        monitor_thread.start()
        print("DownPodcast thread start to run")
        print("DownPodcast thread finished--> downStatus: "+str(__downStatus__))
        msg ="DownPodcast thread finished--> downStatus: "+str(__downStatus__)
    else:
        print("DonwPodcast thread is Running, please wait")
        msg="DonwPodcast thread is Running, please wait"
        
    return jsonify({
        "downStatus" : __downStatus__,
        "msg" : msg
         })

@app.route('/setSleepTimePi', methods=['POST'])
def setSleepTimePi():
    global __musicVlcPi__
    global __radioVlcPi__
    global __musicPiPlaying__
    global __radioPiPlayingNo__
    global __sleepTimePi__
    global __timer_Sleep__
    __sleepTimePi__ = (__sleepTimePi__ + 1 ) % 6
    a= [999,10,20,30,40,50]
    if (__timer_Sleep__ != None):
        __timer_Sleep__.cancel()
    __timer_Sleep__= threading.Timer( a[__sleepTimePi__]*60 , stopPlaying)
    __timer_Sleep__.start()
    return jsonify({
        "musicPiPlaying" : __musicPiPlaying__,
        "radioPiPlayingNo" : __radioPiPlayingNo__,
        "sleepTimePi" : __sleepTimePi__,
         })
    
@app.route('/setCron', methods=['POST'])
def setCron():
    global __cronTimeHour__
    global __cronTimeMin__
    global __cronStatus__
    global __cronIndexPi__
    global __dir__
    global __fileListPi__
    data=request.get_json()
    __cronStatus__=data["cronStatus"]
    __cronIndePi__=data["cronIndexPi"]
    print("__cronStatus: "+str(__cronStatus__))
    print(type(__cronStatus__))
    num=int(data["cronIndexPi"])
    file = __dir__ + __fileListPi__[num]
    print(file+"will be played")
    __cronTimeHour__=int(data["setHour"])
    __cronTimeMin__=int(data["setMin"])
    print("cronTimeHour: "+str(__cronTimeHour__))
    print("cronTimeMin: "+str(__cronTimeMin__))
    if __cronStatus__ == False:
        scheduler.remove_job('my_task')
        __cronStatus__ = False
        print("scheduler job removed")
    else:
        scheduler.add_job(id='my_task', func=handleCronPlayPi, trigger='cron', hour=__cronTimeHour__, minute=__cronTimeMin__)
        __cronStatus__ = True
        print("scheduler job added")
    return jsonify({
        "cronTimeHour" : __cronTimeHour__,
        "cronTimeMin" : __cronTimeMin__,
        "cronStatus" : __cronStatus__
         })

@app.route('/setCronSong', methods=['POST'])
def setCronSong():
    global __cronIndexPi__
    data=request.get_json()
    __cronIndexPi__=int(data["cronIndexPi"])
    return jsonify({
        "cronIndexPi" : __cronIndexPi__
         })

@scheduler.task('cron', id='myjobb', day='*', hour='06', minute='00', second='00')
def myjobb():
    downPodcastFile_sh2()
    print("myDownPodcastFileJob executed")

@app.route('/getArtistList', methods=['POST'])
def getArtistList():
    global __dir__
    global __subFolderList__
    data=request.get_json()
    musictype  = data["musictype"]
    path = __dir__ + musictype
    print(path)
    __subFolderList__ = get_subdirectories(path)
    return jsonify({
        "subFolderList" : __subFolderList__
         })


    