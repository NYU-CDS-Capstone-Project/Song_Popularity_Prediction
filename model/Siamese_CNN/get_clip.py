import numpy as np, sys
sys.path.append('HL_lib')
from glob import glob
from find import find_go
from shutil import rmtree
import librosa, subprocess as subp, os
import subprocess
from pydub import AudioSegment
from pydub.utils import which

# AudioSegment.converter = which("ffmpeg")


def wavtomp3(fn4, fn3):
    sound = AudioSegment.from_wav(fn4)
    # startupinfo = None
    # command = ['ffmpeg',
    #  '-y', '-i', fn4,
    #  '-b:a', '128k',
    #  '-vn', fn3]
    # pipe = subp.Popen(command, stdout=subp.PIPE, startupinfo=startupinfo)
    return sound.export(fn3, format='mp3') #,codec="libavcodec"

def ext_fea(name):
    y, _ = librosa.core.load(name, 22050)
    yt, index = librosa.effects.trim(y) #remove silent part of head and tail
    S = librosa.feature.melspectrogram(yt, sr=22050, n_fft=2048, hop_length=512, n_mels=128)
    return (
     yt, np.transpose(np.log(1 + 10000 * S)))

# this is for new sample test
# if os.path.exists('HL_output'):
#     rmtree('HL_output')
# os.mkdir('HL_output')
# os.mkdir('HL_output/audio')


p = '/Volumes/Seagate Backup Plus Drive/MP3'
filepath = 'HL_output/audio'
savedlist = [i for i in os.listdir(filepath)]

# fs = sorted(glob(p))
j = 0
for f in os.listdir(p):
    if f not in savedlist:
        j+=1
        print(j) 
        # name = f.split('/')[-1][:-4]
        fullname = os.path.join(p,f)
        y, target = ext_fea(fullname)
        start = 0
        end = 90
        librosa.output.write_wav('HL_data/tmp.wav', y[start * 22050:end * 22050], 22050)
        try:
            wavtomp3('HL_data/tmp.wav', ('HL_output/audio/{}').format(f))
        except:
            print(f)
            continue

    # cmd = 'lame --preset insane %s' % 'HL_data/tmp.wav'
    # subprocess.call(cmd, shell=True)

os.remove('HL_data/tmp.wav')