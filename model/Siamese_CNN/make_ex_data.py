import os
import numpy as np
from clip2frame import utils
import json
import shutil
from theano import function, config, shared, tensor
import pandas as pd

floatX = 'float32'
length = 911
win_size = 512

# #gpu usage
# import theano.gpuarray
# theano.gpuarray.use('cuda0')


def _append_zero_row(array, n_total_row):
    r, c = array.shape
    if r >= n_total_row:
        return array
    else:
        temp = np.zeros((n_total_row-r, c))
        return np.vstack([array, temp])

def make_batch_feat(feat_fp_list, length=911):
    feat = []
    a_array = []
    feat_fp_list.sort()
    for idx, term in enumerate(feat_fp_list):
        # print(term)
        np.load(term)
        a_array = _append_zero_row(np.load(term), length)[None, None, :length, :].astype(floatX)
        feat.append(a_array)

    feat = np.vstack(feat)
    return feat


dump_path = "./ex_data"
if os.path.exists(dump_path):
    shutil.rmtree(dump_path)

os.makedirs(dump_path)

#save data for trainning
save_path = "./train_data"
if os.path.exists(save_path):
    shutil.rmtree(save_path)
os.makedirs(save_path)

df_path = './finalranked_matrix_1203.csv'
df = pd.read_csv(df_path)
for win_size in [512, 1024,2048,4096,8192, 16384]:

    #path
    feat_dir = "jy_feat/out"+str(win_size)

    #get files
    fn_list = []
    for files in os.listdir(feat_dir):
        if files.endswith('.npy'):
        	fn_list.append(files.split('.')[0])
    fn_list.sort()
    
    feat_fp_list = [os.path.join(feat_dir, fn+".npy") for fn in fn_list]
    feat = make_batch_feat(feat_fp_list, length).astype(floatX)

    #save files for tag extraction
    np.save(dump_path + "/feat_train_"+str(win_size)+".npy", feat)

    # concatenate mel_feats only once
    if not os.path.isfile('./train_data/rank.npy'):
        # #make files, like the way name.npy did, concatenate  extract_feats's output:mel_feats
        # mels_path =  "./mels"
        # mels_list = [np.load(os.path.join(mels_path,fn.split('.')[0]+".npy")) for fn in fn_list]
        # mels_list = np.concatenate(mels_list, axis=0)
        # np.save( './train_data/feat.npy', mels_list)

        #save files for namelist 
        np.save('./train_data/id.npy', fn_list)

        #save ranking list
        rank_list = [df.loc[df['ISRC']==i,'rank'].values[0] for i in fn_list]
        np.save('./train_data/rank.npy', rank_list)
