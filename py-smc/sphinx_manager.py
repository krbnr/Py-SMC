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

