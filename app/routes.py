
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, login_required, current_user, logout_user

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
    title ="Home"
    
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
