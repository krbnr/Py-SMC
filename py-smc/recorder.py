import google_web_service
import stream_manager
import ui_manager
import wave
import ast
import time
import pyaudio


#Assuming Energy threshold upper than 30 dB
threshold = 30

chunk = 4096    # num of frames
frmat = pyaudio.paInt16     # format
CHANNELS = 1
RATE = 16000
Max_Seconds = 5
timeoutSignal = ((RATE / chunk * Max_Seconds) + 2)
silence = True
FileNameTmp = 'tmp.wav'


def WriteSpeech(p, stream, writeData):
    """
    Write stream .wav file
    """
    stream.stop_stream()
    p.terminate()
    # write to file
    wf = wave.open(FileNameTmp, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(frmat))
    wf.setframerate(RATE)
    wf.writeframes(writeData)
    wf.close()


def Record(stream):

    # TODO: turn on the green light
    inputFound = False

    success = False

    # Doc here
    gSpeechResponse = google_web_service.DecodeGoogleSpeech()
    gSpeechDict = ast.literal_eval(gSpeechResponse)

    if len(gSpeechDict['hypotheses']) > 0:
        utterance = gSpeechDict['hypotheses'][0]['utterance']
        success = stream_manager.CheckCommand(utterance)
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
        stream_manager.Listen()

    else:
        if success == "sleep":
            #TODO go to sleep
            # TODO: configure command to run the images screenSaver
            pass
        else:
            if success == "movie":
                ui_manager.GenerateHtml()
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
                    inpt = stream_manager.GetStream(chunk, stream)
                except:
                    continue

                rms_value = stream_manager.rms(inpt)
                print "RMS 2-1: " + str(rms_value)

                if rms_value > threshold:
                    inpt = stream_manager.GetStream(chunk, stream)
                    rms_value = stream_manager.rms(inpt)
                    print "RMS 2-2: " + str(rms_value)

                    if rms_value > threshold:
                        silence = False
                        print "Recording...."
                        # TODO this method should be the same as record with different args,
                        google_web_service.CmdRecord(success)
            # if the user does not select any movie listen again
            stream_manager.Listen()