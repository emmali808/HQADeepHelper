# -*- coding: utf8 -*-
from __future__ import print_function
import os
import sys
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python36.zip')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/lib-dynload')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages/tensorflow/python/keras/api/_v1')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages/tensorflow_estimator/python/estimator/api/_v1')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages/tensorflow')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages/tensorflow/_api/v1')
# sys.path.append('/home/lf/.local/lib/python3.6/site-packages')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages')
# sys.path.append('/home/lf/anaconda3/envs/pytorch/lib/python3.6/site-packages/keras')
import time
import json
import argparse
import random
random.seed(49999)
import numpy
numpy.random.seed(49999)
import tensorflow
tensorflow.set_random_seed(49999)

from collections import OrderedDict

import keras
import keras.backend as K
from keras.models import Sequential, Model

from utils import *
import inputs
import metrics
from losses import *
from optimizers import *

config = tensorflow.ConfigProto()
config.gpu_options.allow_growth = True
sess = tensorflow.Session(config = config)
import time
import database_util as db

def load_model(config):
    global_conf = config["global"]
    model_type = global_conf['model_type']
    if model_type == 'JSON':
        mo = Model.from_config(config['model'])
    elif model_type == 'PY':
        model_config = config['model']['setting']
        model_config.update(config['inputs']['share'])
        sys.path.insert(0, config['model']['model_path'])

        model = import_object(config['model']['model_py'], model_config)
        mo = model.build()
    return mo


def train(config,para_path):

    print(json.dumps(config, indent=2), end='\n')
    # read basic config
    global_conf = config["global"]
    optimizer = global_conf['optimizer']
    optimizer=optimizers.get(optimizer)
    K.set_value(optimizer.lr, global_conf['learning_rate'])
    #weights_file = str(global_conf['weights_file']) + '.%d'
    display_interval = int(global_conf['display_interval'])
    num_iters = int(global_conf['num_iters'])
    save_weights_iters = int(global_conf['save_weights_iters'])

    # read input config
    input_conf = config['inputs']
    share_input_conf = input_conf['share']

    #an_config = json.load(open('./data/pinfo/config.py', 'r'))
    an_config = json.load(open(para_path, 'r'))
    dstdir = an_config["model_dst_dir"]
    if not os.path.exists(an_config['weights_dir']):
        os.mkdir(an_config['weights_dir'])
    weights_file = an_config['weights_dir']+str(global_conf['weights_file'])
    config['metrics'] = an_config["metrics"]
    config['model']['model_path'] = an_config['model_path']


    share_input_conf['embed_path']=dstdir+"embed_glove_d300"
    share_input_conf['word_triletter_map_file'] = dstdir + "word_triletter_map.txt"
    share_input_conf['vocab_size']=word_len(dstdir+"word_dict.txt")
    share_input_conf['text1_corpus'] = dstdir + "corpus_preprocessed.txt"
    share_input_conf['text2_corpus'] = dstdir + "corpus_preprocessed.txt"
    input_conf['train']['relation_file'] = dstdir+"relation_train.txt"
    input_conf['valid']['relation_file'] = dstdir+"relation_valid.txt"
    input_conf['test']['relation_file'] = dstdir + "relation_test.txt"
    input_conf['train']['hist_feats_file'] = dstdir + "relation_train.binsum-20.txt"
    input_conf['valid']['hist_feats_file'] = dstdir + "relation_valid.binsum-20.txt"
    input_conf['test']['hist_feats_file'] = dstdir + "relation_test.binsum-20.txt"




    # collect embedding
    if 'embed_path' in share_input_conf:
        embed_dict = read_embedding(filename=share_input_conf['embed_path'])
        _PAD_ = share_input_conf['vocab_size'] - 1
        embed_dict[_PAD_] = np.zeros((share_input_conf['embed_size'], ), dtype=np.float32)
        embed = np.float32(np.random.uniform(-0.2, 0.2, [share_input_conf['vocab_size'], share_input_conf['embed_size']]))
        share_input_conf['embed'] = convert_embed_2_numpy(embed_dict, embed = embed)
    else:
        # if no embed provided, use random
        embed = np.float32(np.random.uniform(-0.2, 0.2, [share_input_conf['vocab_size'], share_input_conf['embed_size']]))
        share_input_conf['embed'] = embed
    print('[Embedding] Embedding Load Done.', end='\n')

    # list all input tags and construct tags config
    input_train_conf = OrderedDict()
    input_eval_conf = OrderedDict()
    # print("input_conf", input_conf)
    # print("input_conf keys", input_conf.keys())
    for tag in input_conf.keys():
        if 'phase' not in input_conf[tag]:
            continue
        if input_conf[tag]['phase'] == 'TRAIN':
            input_train_conf[tag] = {}
            input_train_conf[tag].update(share_input_conf)
            input_train_conf[tag].update(input_conf[tag])
        elif input_conf[tag]['phase'] == 'EVAL':
            input_eval_conf[tag] = {}
            input_eval_conf[tag].update(share_input_conf)
            input_eval_conf[tag].update(input_conf[tag])
    print('[Input] Process Input Tags. %s in TRAIN, %s in EVAL.' % (input_train_conf.keys(), input_eval_conf.keys()), end='\n')
    # print("input_train_conf", input_train_conf)
    # collect dataset identification
    dataset = {}
    for tag in input_conf:
        if tag != 'share' and input_conf[tag]['phase'] == 'PREDICT':
            continue
        if 'text1_corpus' in input_conf[tag]:
            datapath = input_conf[tag]['text1_corpus']
            if datapath not in dataset:
                dataset[datapath], _ = read_data(datapath)
        if 'text2_corpus' in input_conf[tag]:
            datapath = input_conf[tag]['text2_corpus']
            if datapath not in dataset:
                dataset[datapath], _ = read_data(datapath)
    print('[Dataset] %s Dataset Load Done.' % len(dataset), end='\n')

    # initial data generator
    train_gen = OrderedDict()
    eval_gen = OrderedDict()

    for tag, conf in input_train_conf.items():
        print(conf, end='\n')
        conf['data1'] = dataset[conf['text1_corpus']]
        conf['data2'] = dataset[conf['text2_corpus']]
        generator = inputs.get(conf['input_type'])
        train_gen[tag] = generator( config = conf )

    for tag, conf in input_eval_conf.items():
        print(conf, end='\n')
        conf['data1'] = dataset[conf['text1_corpus']]
        conf['data2'] = dataset[conf['text2_corpus']]
        generator = inputs.get(conf['input_type'])
        eval_gen[tag] = generator( config = conf )
 
    ######### Load Model #########
    model = load_model(config)
    # weights_file1 = str(global_conf['weights_file']) + '.' + str(global_conf['test_weights_iters'])
    # model.load_weights(weights_file1)
    loss = []
    for lobj in config['losses']:
        if lobj['object_name'] in mz_specialized_losses:
            loss.append(rank_losses.get(lobj['object_name'])(lobj['object_params']))
        else:
            loss.append(rank_losses.get(lobj['object_name']))
    eval_metrics = OrderedDict()
    for mobj in config['metrics']:
        mobj = mobj.lower()
        if '@' in mobj:
            mt_key, mt_val = mobj.split('@', 1)
            eval_metrics[mobj] = metrics.get(mt_key)(int(mt_val))
        else:
            eval_metrics[mobj] = metrics.get(mobj)
    model.compile(optimizer=optimizer, loss=loss)

    print('[Model] Model Compile Done.', end='\n')

    base_metric = an_config["base_metric"]
    best_epoch = 0
    best_metric = -1
    best_result = ''
    start_time = time.clock()
    for i_e in range(num_iters):
        for tag, generator in train_gen.items():
            genfun = generator.get_batch_generator()
            print('[%s]\t[Train:%s] ' % (time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(time.time())), tag), end='')
            history = model.fit_generator(
                    genfun,
                    steps_per_epoch = display_interval,
                    epochs = 1,
                    shuffle=False,
                    verbose = 0
                ) #callbacks=[eval_map])
            print('Iter:%d\tloss=%.6f' % (i_e, history.history['loss'][0]), end='\n')

        for tag, generator in eval_gen.items():
            genfun = generator.get_batch_generator()
            print('[%s]\t[Eval:%s] ' % (time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(time.time())), tag), end='')
            res = dict([[k,0.] for k in eval_metrics.keys()])
            num_valid = 0
            for input_data, y_true in genfun:
                y_pred = model.predict(input_data, batch_size=len(y_true))
                if issubclass(type(generator), inputs.list_generator.ListBasicGenerator):
                    list_counts = input_data['list_counts']
                    for k, eval_func in eval_metrics.items():
                        for lc_idx in range(len(list_counts)-1):
                            pre = list_counts[lc_idx]
                            suf = list_counts[lc_idx+1]
                            res[k] += eval_func(y_true = y_true[pre:suf], y_pred = y_pred[pre:suf])
                    num_valid += len(list_counts) - 1
                else:
                    for k, eval_func in eval_metrics.items():
                        res[k] += eval_func(y_true = y_true, y_pred = y_pred)
                    num_valid += 1
            generator.reset()
            print('Iter:%d\t%s' % (i_e, '\t'.join(['%s=%f'%(k,v/num_valid) for k, v in res.items()])), end='\n')
            cur_metric = res[base_metric]/num_valid
            cur_res = '\t'.join(['%s=%f'%(k,v/num_valid) for k, v in res.items()])
            cur_metric_ls = {}
            for k,v in res.items():
                cur_metric_ls[k] = round(v/num_valid,4)
            if cur_metric>best_metric and tag=='valid':
                best_epoch = i_e
                best_metric = cur_metric
                best_result = cur_res
                best_metric_ls = cur_metric_ls
                model.save_weights(weights_file)
            sys.stdout.flush()
        #if (i_e+1) % save_weights_iters == 0:
            #model.save_weights(weights_file % (i_e+1))
    end_time = time.clock()
    print('the best running result %s the best epoch %d' % (best_result, best_epoch
                                                            ))
    print('the running time %s seconds'%(end_time-start_time))
    db.insert_result(task_id, model_id, best_metric_ls)

def _to_list(x):
    if isinstance(x, list):
        return x
    return [x]

def predict(config):
    ######## Read input config ########

    print(json.dumps(config, indent=2), end='\n')
    input_conf = config['inputs']
    share_input_conf = input_conf['share']

    # collect embedding
    if 'embed_path' in share_input_conf:
        embed_dict = read_embedding(filename=share_input_conf['embed_path'])
        _PAD_ = share_input_conf['vocab_size'] - 1
        embed_dict[_PAD_] = np.zeros((share_input_conf['embed_size'], ), dtype=np.float32)
        embed = np.float32(np.random.uniform(-0.02, 0.02, [share_input_conf['vocab_size'], share_input_conf['embed_size']]))
        share_input_conf['embed'] = convert_embed_2_numpy(embed_dict, embed = embed)
    else:
        embed = np.float32(np.random.uniform(-0.2, 0.2, [share_input_conf['vocab_size'], share_input_conf['embed_size']]))
        share_input_conf['embed'] = embed
    print('[Embedding] Embedding Load Done.', end='\n')

    # list all input tags and construct tags config
    input_predict_conf = OrderedDict()
    for tag in input_conf.keys():
        if 'phase' not in input_conf[tag]:
            continue
        if input_conf[tag]['phase'] == 'PREDICT':
            input_predict_conf[tag] = {}
            input_predict_conf[tag].update(share_input_conf)
            input_predict_conf[tag].update(input_conf[tag])
    print('[Input] Process Input Tags. %s in PREDICT.' % (input_predict_conf.keys()), end='\n')

    # collect dataset identification
    dataset = {}
    for tag in input_conf:
        if tag == 'share' or input_conf[tag]['phase'] == 'PREDICT':
            if 'text1_corpus' in input_conf[tag]:
                datapath = input_conf[tag]['text1_corpus']
                if datapath not in dataset:
                    dataset[datapath], _ = read_data(datapath)
            if 'text2_corpus' in input_conf[tag]:
                datapath = input_conf[tag]['text2_corpus']
                if datapath not in dataset:
                    dataset[datapath], _ = read_data(datapath)
    print('[Dataset] %s Dataset Load Done.' % len(dataset), end='\n')

    # initial data generator
    predict_gen = OrderedDict()

    for tag, conf in input_predict_conf.items():
        print(conf, end='\n')
        conf['data1'] = dataset[conf['text1_corpus']]
        conf['data2'] = dataset[conf['text2_corpus']]
        generator = inputs.get(conf['input_type'])
        predict_gen[tag] = generator(
                                    #data1 = dataset[conf['text1_corpus']],
                                    #data2 = dataset[conf['text2_corpus']],
                                     config = conf )

    ######## Read output config ########
    output_conf = config['outputs']

    ######## Load Model ########
    global_conf = config["global"]
    weights_file = str(global_conf['weights_file']) + '.' + str(global_conf['test_weights_iters'])

    model = load_model(config)
    model.load_weights(weights_file)
    encoder = Model(inputs=model.input, outputs=[model.get_layer('att_layer_2').output, model.get_layer('att_layer_3').output])
    # encoder = Model(inputs=model.input, outputs=model.get_layer('att_layer_2').output)
    eval_metrics = OrderedDict()
    for mobj in config['metrics']:
        mobj = mobj.lower()
        if '@' in mobj:
            mt_key, mt_val = mobj.split('@', 1)
            eval_metrics[mobj] = metrics.get(mt_key)(int(mt_val))
        else:
            eval_metrics[mobj] = metrics.get(mobj)
    res = dict([[k,0.] for k in eval_metrics.keys()])

    # 这是为了打印query和sent的attention score
    for tag, generator in predict_gen.items():
        genfun = generator.get_batch_generator()
        print('[%s]\t[Predict] @ %s ' % (time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(time.time())), tag), end='')
        num_valid = 0
        res_scores = {}
        for input_data, y_true in genfun:
            
            y_pred1, y_pred2 = encoder.predict(input_data, batch_size=len(y_true))
            y_pred1 = _to_list(np.squeeze(y_pred1).tolist())
            y_pred2 = _to_list(np.squeeze(y_pred2).tolist())
            # print("y_pred", len(y_pred), len(y_pred[0]))
            print(input_data)
            print("sent", y_pred1)
            print("query", y_pred2)
            print()

    for tag, generator in predict_gen.items():
        genfun = generator.get_batch_generator()
        print('[%s]\t[Predict] @ %s ' % (time.strftime('%m-%d-%Y %H:%M:%S', time.localtime(time.time())), tag), end='')
        num_valid = 0
        res_scores = {}
        for input_data, y_true in genfun:
            y_pred = model.predict(input_data, batch_size=len(y_true) )

            if issubclass(type(generator), inputs.list_generator.ListBasicGenerator):
                list_counts = input_data['list_counts']
                for k, eval_func in eval_metrics.items():
                    for lc_idx in range(len(list_counts)-1):
                        pre = list_counts[lc_idx]
                        suf = list_counts[lc_idx+1]
                        res[k] += eval_func(y_true = y_true[pre:suf], y_pred = y_pred[pre:suf])

                y_pred = np.squeeze(y_pred)
                for lc_idx in range(len(list_counts)-1):
                    pre = list_counts[lc_idx]
                    suf = list_counts[lc_idx+1]
                    for p, y, t in zip(input_data['ID'][pre:suf], y_pred[pre:suf], y_true[pre:suf]):
                        if p[0] not in res_scores:
                            res_scores[p[0]] = {}
                        res_scores[p[0]][p[1]] = (y, t)

                num_valid += len(list_counts) - 1
            else:
                for k, eval_func in eval_metrics.items():
                    res[k] += eval_func(y_true = y_true, y_pred = y_pred)
                for p, y, t in zip(input_data['ID'], y_pred, y_true):
                    if p[0] not in res_scores:
                        res_scores[p[0]] = {}
                    res_scores[p[0]][p[1]] = (y[1], t[1])
                num_valid += 1
        generator.reset()

        if tag in output_conf:
            if output_conf[tag]['save_format'] == 'TREC':
                with open(output_conf[tag]['save_path'], 'w') as f:
                    for qid, dinfo in res_scores.items():
                        dinfo = sorted(dinfo.items(), key=lambda d:d[1][0], reverse=True)
                        for inum,(did, (score, gt)) in enumerate(dinfo):
                            f.write('%s\tQ0\t%s\t%d\t%f\t%s\t%s\n'%(qid, did, inum, score, config['net_name'], gt))
            elif output_conf[tag]['save_format'] == 'TEXTNET':
                with open(output_conf[tag]['save_path'], 'w') as f:
                    for qid, dinfo in res_scores.items():
                        dinfo = sorted(dinfo.items(), key=lambda d:d[1][0], reverse=True)
                        for inum,(did, (score, gt)) in enumerate(dinfo):
                            f.write('%s %s %s %s\n'%(gt, qid, did, score))

        print('[Predict] results: ', '\t'.join(['%s=%f'%(k,v/num_valid) for k, v in res.items()]), end='\n')
        sys.stdout.flush()

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', default='train', help='Phase: Can be train or predict, the default value is train.')
    parser.add_argument('--model_file', default='./models/arci.config', help='Model_file: MatchZoo model file for the chosen model.')
    parser.add_argument('--parameter_config', default='./data/pinfo/config.py',
                        help='The user-defined parameters  config  file in our system')
    parser.add_argument('--task_id', required=True, default='1',
                        help='the task id for this training task. help for insert into our database.')
    parser.add_argument('--model_id', required=True, default='1',
                        help='the model id for this training task. help for insert into our database.')
    args = parser.parse_args()
    model_file =  args.model_file
    para_file = args.parameter_config
    global task_id
    task_id = args.task_id
    global model_id
    model_id = args.model_id
    #train_time=0

    with open(model_file, 'r') as f:
        config = json.load(f)
    phase = args.phase
    if args.phase == 'train':
	#start_time=time.clock()
        train(config,para_file)
	#train_time=time.clock()-start_time
	#print('training time %s' % train_time)
    elif args.phase == 'predict':
        predict(config)
    else:
        print('Phase Error.', end='\n')
    return



if __name__=='__main__':
    # print(sys.modules)
    main(sys.argv)

