import argparse
import glob
import multiprocessing
from functools import partial
from math import ceil
from os import mkdir, path
from shutil import rmtree
import os

import librosa
import numpy as np


class Params:
    """
    SY's parameters for MTT tagging
    """
    audio_len = 90
    srt = 44100
    wsz = 2048
    mels = 128
    hop_length = wsz / 4
    feat_len = int(ceil(srt * audio_len / float(hop_length)))


class ParamsR:
    """
    Richard's parameters
    """
    audio_len = 90
    srt = 22050
    wsz = 4096
    mels = 128
    hop_length = wsz // 2
    feat_len = int(ceil(srt * audio_len / float(hop_length)))


class ParamsA2V:
    """
    SY's parameters for Audio2Vec
    """
    audio_len = 90
    srt = 22050
    wsz = 4096
    mels = 128
    hop_length = wsz / 2
    feat_len = int(ceil(srt * audio_len / float(hop_length)))


params = ParamsA2V   #ParamsR


def feat_extract(fn, out_p):
    sid = fn.split('/')[-1].split('.')[0]

    try:
        y, _ = librosa.load(fn, sr=params.srt)
    except EOFError:
        return -2
        
    song_len = len(y) / float(params.srt)
    if song_len == 0:
        return -2  # read file error
    if song_len < params.audio_len / 2:
        # return -3  # less than a half
        pass

    feat = librosa.feature.melspectrogram(
        y=y, sr=params.srt, n_fft=params.wsz,
        hop_length=params.hop_length, n_mels=params.mels)
    if song_len == params.audio_len:
        ret = feat
#     elif song_len > params.audio_len:
#         start = feat.shape[1] // 2 - params.feat_len // 2
#         end = feat.shape[1] // 2 + params.feat_len // 2
#         if params.feat_len % 2 == 1:
#             end += 1
#         ret = feat[:, start:end]
    elif song_len > params.audio_len:
        start = 0  #0-60s  if wanna start from 10s, change ParamsA2V.audio_len to 10 and get ParamsA2V.feat_len
        end = params.feat_len
        ret = feat[:, start:end]

    else:
        ret = np.zeros((params.mels, params.feat_len))
        ret[:, :feat.shape[1]] = feat.copy()
    np.save(
        path.join(out_p, sid), ret.reshape(1, params.mels, params.feat_len)) #(1,128,feat_len)
    return 0  # success


def main():
    parser = argparse.ArgumentParser(
        description='Song Feat. Extraction')
    parser.add_argument(
        "-i", "--song-dir", help="input song dir", required=True)
    parser.add_argument(
        "-o", "--feat-dir", help="output feat dir", required=True)
    args = parser.parse_args()

    song_dir = args.song_dir
    feat_dir = args.feat_dir
    # if path.exists(feat_dir):
    #     rmtree(feat_dir)
    # mkdir(feat_dir)
    savedlist = [i for i in os.listdir(feat_dir)]

    for f in os.listdir(song_dir):
        f = f.split('.')[0] + '.npy'
        if f not in savedlist:
            # name = f.split('/')[-1][:-4]
            song = os.path.join(song_dir,f)

            # songs = glob.glob('{}/*mp3'.format(song_dir))
            pool = multiprocessing.Pool(90) #from 30s to 60s
            feat_extract(song,out_p=feat_dir)
            excpt = pool.map(partial(feat_extract, out_p=feat_dir), songs[:])
            pool.close()
            pool.join()

            try:
                wavtomp3('HL_data/tmp.wav', ('HL_output/audio/{}').format(f))
            except:
                print(f)
                continue

    song_dir = args.song_dir
    feat_dir = args.feat_dir
    # if path.exists(feat_dir):
    #     rmtree(feat_dir)
    # mkdir(feat_dir)
    savedlist = [i for i in os.listdir(feat_dir)]

    songs = glob.glob('{}/*mp3'.format(song_dir))
    pool = multiprocessing.Pool(90) #from 30s to 60s
    excpt = pool.map(partial(feat_extract, out_p=feat_dir), songs[:])
    pool.close()
    pool.join()



if __name__ == "__main__":
    main()
