import subprocess
import ast
import stream_manager
import urllib2


def CmdRecord(commandType):
    gSpeechResponse = DecodeGoogleSpeech()
    gSpeechDict = ast.literal_eval(gSpeechResponse)
    utterance = gSpeechDict['hypotheses'][0]['utterance']
    print 'Utterance 2: ' + utterance
    stream_manager.CheckSecondCommand(utterance, commandType)


def DecodeGoogleSpeech():
    """
    Google speech
    run command to record flac file and returns it as string
    """
    speech = subprocess.Popen(["rec", "-c", "1", "-r", "16000", "-b", "16", "../media/audio/spch.flac", "trim", "0", "5"],
                              stdout=subprocess.PIPE)

    output, err = speech.communicate()
    # TODO: check if output is correct

    url = "https://www.google.com/speech-api/v1/recognize?xjerr=1&client=chromium&lang=en-US"
    audio = open('../media/audio/spch.flac','rb').read()
    headers = {'Content-Type': 'audio/x-flac; rate=16000', 'User-Agent':'Mozilla/5.0'}
    request = urllib2.Request(url, data=audio, headers=headers)
    response = urllib2.urlopen(request)

    return response.read()

