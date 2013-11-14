import pyaudio
import math
import struct
import webbrowser
import recorder
import ui_manager


def Listen():

    #Assuming Energy threshold upper than 30 dB
    threshold = 30

    chunk = 4096
    frmat = pyaudio.paInt16 # format
    chnls = 1
    rate = 16000
    silence = True

    p = pyaudio.PyAudio()
    p = pyaudio.PyAudio()

    #PyAudio is a Python interface to PortAudio. Provides methods to:
    #initialize and terminate PortAudio
    #open and close streams
    #PortAudio is a free, cross-platform, open-source, audio I/O library.


    stream = p.open(format=frmat,
                    channels=chnls,
                    rate=rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)

    print 'Listening'

    while silence:

        try:
            # read stream chunk
            inpt = GetStream(chunk, stream)
        except:
            continue
        # get the value of db
        rms_value = rms(inpt)
        print "RMS 1-1: " + str(rms_value)

        if rms_value > threshold:
            # clap num two
            inpt = GetStream(chunk, stream)
            # check if input db is > than Threshold
            rms_value = rms(inpt)
            print "RMS 1-2: " + str(rms_value)

            if rms_value > threshold:
                silence = False
                print "Recording...."
                # if the second clap is also record the input
                recorder.Record(stream)


def GetStream(chunk, stream):
    """
    Returns a chunk of the stream
    """
    return stream.read(chunk)


def rms(frame):
    """
    Returns the db of the mic as int
    """

    swidth = 2
    shortNormalize = 1.0/32768.0
    count = len(frame)/swidth
    frmat = "%dh" % count
    shorts = struct.unpack(frmat, frame)
    sum_squares = 0.0

    for sample in shorts:
        n = sample * shortNormalize
        sum_squares += n*n

    rms = math.pow(sum_squares/count, 0.5)

    return rms * 1000



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


def CheckSecondCommand(utterance, commandType):

    moviesEnum = {
    'one':'1',
    'two':'2',
    'three':'3',
    'four':'4',
    'five':'5',
    'six':'6',
    'seven':'7'
    }

    if commandType == "movie":
        if 'number' in utterance:
            movieNumber = utterance.rsplit(' ', 1)[1]
            if movieNumber in moviesEnum.values():
                print 'Movie number in moviesEnum'
                #TODO check what to do woth the dict values
                ui_manager.ReproduceVideo(movieNumber)
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
