from pydub import AudioSegment
from pydub.playback import play
from simpleaudio.shiny import play_buffer
import sys
from playsound import playsound
import subprocess
#song=AudioSegment
#song=AudioSegment.from_file("F:/python_space/bs_project/Coby/music/빠빠빠.mp3")
#playsound("music/Better Off Alone.wav")
#song.export("F:/python_space/bs_project/Coby/music/빠빠빠.mp3")
#play(song)
ffmpegPath=r"F:\ffmpeg-4.1\ffmpeg\bin\ffmpeg.exe"
ffplayPath=r"F:\ffmpeg-4.1\ffmpeg\bin\ffplay.exe"
ffprobePath=r"F:\ffmpeg-4.1\ffmpeg\bin\ffprobe.exe"

def getVideoData(path):
    cmd= ffplayPath + "  -nodisp " + path
    cmd=cmd.encode(sys.getfilesystemencoding())
    if "?" in str(cmd):
        cmd=cmd.replace("?","")
    print(cmd)
    subprocess.call(cmd , shell=True)
Path="F:\\python_space\\bs_project\\Coby\\music\\빠빠빠.mp3"
getVideoData(Path)