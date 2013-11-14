import pyaudio
import math
import struct
import wave
import sys
import subprocess
import urllib2
import webbrowser
import ast
import glob
import os
import time



#Assuming Energy threshold upper than 30 dB
threshold = 30

shortNormalize = 1.0/32768.0
chunk = 4096 # num of frames
frmat = pyaudio.paInt16 # format
CHANNELS = 1
RATE = 16000
swidth = 2
Max_Seconds = 5
timeoutSignal = ((RATE / chunk * Max_Seconds) + 2)
silence = True
FileNameTmp = 'tmp.wav'
all = []

moviesEnum = {
    'one':'1',
    'two':'2',
    'three':'3',
    'four':'4',
    'five':'5',
    'six':'6',
    'seven':'7'
    }



def GetStream(chunk):
    """
    Returns a chunk of the stream
    """
    return stream.read(chunk)


def rms(frame):
    """
    Returns the db of the mic as int
    """
    count = len(frame)/swidth
    frmat = "%dh" % count
    shorts = struct.unpack(frmat, frame)
    sum_squares = 0.0
    for sample in shorts:
        n = sample * shortNormalize
        sum_squares += n*n

    rms = math.pow(sum_squares/count, 0.5)

    return rms * 1000


def WriteSpeech(WriteData):
    """
    Write stream into disk .wav file
    """
    stream.stop_stream()
    p.terminate()
    # write to file
    wf = wave.open(FileNameTmp, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(frmat))
    wf.setframerate(RATE)
    wf.writeframes(WriteData)
    wf.close()


def Record():

    # TODO: turn on the green light
    global p
    global stream
    global all

    all = []
    inputFound = False
    utterance = ''
    success = False

    # Doc here
    gSpeechResponse = DecodeGoogleSpeech()
    gSpeechDict = ast.literal_eval(gSpeechResponse)

    if len(gSpeechDict['hypotheses']) > 0:
        utterance = gSpeechDict['hypotheses'][0]['utterance']
        success = CheckCommand(utterance)
    else:
        inputFound = True

    silence = True

    # not success - command not found or not input
    if not success:

        if inputFound:
            # voice not found
            print 'Input not found'
        else:
            # command didn't match
            print 'Command did not match'
        time.sleep(2)
        Listen()
    else:
        if success == "sleep":
            #TODO go to sleep
            # TODO: configure command to run the images screenSaver
            pass
        else:
            if success == "movie":
                GenerateHtml()
            elif success == "music":
                # TODO: Run music on Raspian http://www.raspberrypi.org/phpBB3/viewtopic.php?f=26&t=12089
                # TODO call genre
                pass
            elif success == "search":
                print "Search in browser..."

            # timer
            # two minutes to select the movie
            timeNow = time.time()

            while silence and timeNow + 120 > time.time():
                try:
                    inpt = GetStream(chunk)
                except:
                    continue

                rms_value = rms(inpt)
                print "RMS 2-1: " + str(rms_value)

                if rms_value > threshold:
                    inpt = GetStream(chunk)
                    rms_value = rms(inpt)
                    print "RMS 2-2: " + str(rms_value)

                    if rms_value > threshold:
                        silence = False
                        print "Recording...."
                        # TODO this method should no be the same as record, and check if not recording the audio is possible
                        CmdRecord(success)
            # if the user does not select any movie listen again
            Listen()


def CmdRecord(commandType):
    gSpeechResponse = DecodeGoogleSpeech()
    gSpeechDict = ast.literal_eval(gSpeechResponse)
    utterance = gSpeechDict['hypotheses'][0]['utterance']
    print 'Utterance 2: ' + utterance
    CheckSecondCommand(utterance, commandType)


def Listen():

    silence = True
    print 'Listening'

    while silence:

        try:
            # read stream chunk
            inpt = GetStream(chunk)
        except:
            continue

        # get the value of db
        rms_value = rms(inpt)
        print "RMS 1-1: " + str(rms_value)

        if rms_value > threshold:
            # clap num two
            inpt = GetStream(chunk)
            # check if input db is > than Threshold
            rms_value = rms(inpt)
            print "RMS 1-2: " + str(rms_value)

            if rms_value > threshold:
                silence = False
                print "Recording...."
                # if the second clap is also record the input
                Record()


def SphinxDecode():
    """
    Sphinx
    """
    hmdir = "/usr/share/pocketsphinx/model/hmm/wsj1"
    lmd = "/usr/share/pocketsphinx/model/lm/wsj/wlist5o.3e-7.vp.tg.lm.DMP"
    dictd = "/usr/share/pocketsphinx/model/lm/wsj/wlist5o.dic"
    recognised = DecodeSpeech(hmdir, lmd, dictd)

    return recognised


def DecodeSpeech( hmmd, lmdir, dictp):
    """
    Decodes a speech file
    """
    try:
        import pocketsphinx as ps
        import sphinxbase
    except:
        print """Pocket sphinx and sphixbase is not installed in your system. Please install it with package manager. """

    wavfile = "tmp.wav"
    speechRec = ps.Decoder(hmm=hmmd, lm=lmdir, dict=dictp)
    wavFile = file(wavfile, 'rb')
    wavFile.seek(44)
    speechRec.decode_raw(wavFile)
    result = speechRec.get_hyp()

    return result[0]


def DecodeGoogleSpeech():
    """
    Google speech
    run command to record flac file and returns it as string
    """
    speech = subprocess.Popen(["rec", "-c", "1", "-r", "16000", "-b", "16", "media/audio/spch.flac", "trim", "0", "5"],
                              stdout=subprocess.PIPE)

    output, err = speech.communicate()
    # TODO: check if output is correct

    url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
    audio = open('media/audio/spch.flac','rb').read()
    headers = {'Content-Type': 'audio/x-flac; rate=16000', 'User-Agent':'Mozilla/5.0'}
    request = urllib2.Request(url, data=audio, headers=headers)
    response = urllib2.urlopen(request)

    return response.read()


#Filter command
def CheckCommand(utterance):
    """
    Checks for predefined command
    TODO:
        Read from file so the user can set the commands
        Install lightwheight web browser http://www.codingepiphany.com/2013/04/02/raspberry-pi-faster-and-lighter-web-browsing-with-luakit/
    """
    if "movie" in utterance:
        # Check if movie exist(file) and open
        return "movie"

    elif "music" in utterance:
        return "music"

    elif "search" in utterance and "browser" in utterance:
        return "search"
    elif "sleep" in utterance:
        return "sleep"

    return ""


def GenerateHtml():
    """
    Generate html from the images on the media/movie-images folder
    """
    images = ""
    movieNumber = {}
    containerBlock = """
                    <div id="container">
                        <img style="width:184px; height:278px" id="image" src="{0}"/>
                        <p id="Title"><span class="Num">{1}</span>
                        </p>
                    </div>
                    """
    i = 1
    # for each image in folder create an html block
    for imgFile in glob.glob("media/movies-images/*.jpg"):
        fileName, fileExension = os.path.splitext(imgFile)
        movieNumber[i] = fileName
        images += containerBlock.format(imgFile.replace("media", ".."), "N " + str(i))
        i += 1

    htmlFile = open("media/html/html.txt")
    htmlM = htmlFile.read()
    htmlFile.close()

    # format list of images into the html
    htmlM = htmlM.format(images)

    fh = open("media/html/template.html", "w")
    fh.write(htmlM)
    fh.close()
    # open web browser
    webbrowser.open('file://'+os.getcwd()+'/media/html/template.html')
    #TODO: omxplayer with subs = http://www.raspberrypi.org/phpBB3/viewtopic.php?p=131004


def CheckSecondCommand(utterance, commandType):
    if commandType == "movie":
        if 'number' in utterance:
            movieNumber = utterance.rsplit(' ', 1)[1]
            if movieNumber in moviesEnum.values():
                print 'Movie number in moviesEnum'
                #TODO check what to do woth the dict values
                ReproduceVideo(movieNumber)
    elif commandType == "music":
        # TODO run music album
        pass
    elif commandType == "search":
        q = ""
        words = utterance.split()
        for word in words:
            q += word + "+"
        webbrowser.open("https://www.google.com.uy/search?q=" + q[:-1])

    elif commandType == "sleep":
        # TODO go to sleep
        pass

def ReproduceVideo(movieNumber):

    os.chdir('media/movies/')
    playMovieCommand = subprocess.Popen(["vlc", "-vvv", "--fullscreen", movieNumber + ".mp4"], stdout=subprocess.PIPE)
    output, err = playMovieCommand.communicate()
    #TODO chekc if the movie run correctly



p = pyaudio.PyAudio()
#With PyAudio, you can easily use Python to play and record audio on a variety of platforms.
#PyAudio is a Python interface to PortAudio. Provides methods to:
    #initialize and terminate PortAudio
    #open and close streams
#PortAudio is a free, cross-platform, open-source, audio I/O library.



#Stream Management
#Use this method to open and close streams.
#read several bytes from the stream into an array
#seek (move your current position in the stream, so that next time you read you get bytes from the new position)
#write one byte
#write several bytes from an array into the stream
#skip bytes from the stream (this is like read, but you ignore the data. Or if you prefer it's like seek but can only go forwards.)
#push back bytes into an input stream (this is like "undo" for read - you shove a few bytes back up the stream, so that next time you read that's what you'll see. It's occasionally useful for parsers, as is:
#peek (look at bytes without reading them, so that they're still there in the stream to be read later)

#continously chunk reader
stream = p.open(format=frmat,       # pyaudio.paInt16
                channels=CHANNELS,  # 1
                rate=RATE,
                input=True,
                output=True,
                frames_per_buffer=chunk)


if __name__ == "__main__":
    #Main funct
    Listen()


