import webbrowser
import glob
import subprocess
import os


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
    for imgFile in glob.glob("../media/movies-images/*.jpg"):
        fileName, fileExension = os.path.splitext(imgFile)
        movieNumber[i] = fileName
        print imgFile
        images += containerBlock.format(imgFile.replace("/media", ""), "N " + str(i))
        i += 1

    htmlFile = open("../media/html/html.txt")
    htmlM = htmlFile.read()
    htmlFile.close()

    # format list of images into the html
    htmlM = htmlM.format(images)

    fh = open("../media/html/template.html", "w")
    fh.write(htmlM)
    fh.close()
    # open web browser
    webbrowser.open('file://'+os.getcwd()+'/../media/html/template.html')
    #TODO: omxplayer with subs = http://www.raspberrypi.org/phpBB3/viewtopic.php?p=131004




def ReproduceVideo(movieNumber):

    currdir = os.getcwd()
    os.chdir('../media/movies/')
    playMovieCommand = subprocess.Popen(["vlc", "-vvv", "--fullscreen", movieNumber + ".mp4"], stdout=subprocess.PIPE)
    output, err = playMovieCommand.communicate()
    os.chdir(currdir)
    #TODO chekc if the movie run correctly

