#This code is modified based on 'https://github.com/OckhamsRazor/HSP_CNN'
rm -rf test_data/*
[ -d HL_output ] || mkdir HL_output  #[ ] if HL_output not exist, mkdir
[ -d HL_output/audio ] || mkdir HL_output/audio_train #put trainning audios inside this fold
[ -d HL_output/audio ] || mkdir HL_output/audio_test #put test audios inside this fold

#processing data,to get melspectrum and tags
##########################################################################################################
#MELSPECTRUM:
python get_clip.py #get 90s clip, time is set from 0 to 60 #hpc lib problem, can run on local.
python mel_extract.py -i HL_output/audio -o mels #get mel spectrum,  shape is (1,128,feat_len)  python2.7
#TAGS
python extract_feats.py #transfer mel spectrum, 6 window sizes  很耗时间，试试hpc:works
python make_ex_data.py #make batch mel spectrum for the tag extraction, 4d [x,1,911,128], first dimension is the number of songs; python 2.7
python standardize.py #standardize, remain same dimension
python2.7 test_model.py #return tags for 90s clip, [x,50], x is the number of songs

#training and test model
##########################################################################################################
#for train 
python cnn.ret30.fc.py -i train_data/ -o ret30 -tg -t incept -ep 1 #input is just pure mel spectrum and tags
#for test 
python cnn.ret30.fc.py -i test_data/ -test -o ret30 -tg -t incept  #input is just pure mel spectrum and tags

# rm -rf jy_feat/* ex_data/* std/* HL_output/* mels/
