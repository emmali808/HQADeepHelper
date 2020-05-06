#!/usr/bin/env python
# coding: utf-8
from __future__ import  print_function

import os
import sys
import random
random.seed(49999)
import numpy
numpy.random.seed(49999)

sys.path.append('../../matchzoo/inputs/')
sys.path.append('../../matchzoo/utils/')

from preparation import Preparation
from preprocess import Preprocess, NgramUtil
import json


def read_dict(infile):
    word_dict = {}
    for line in open(infile):
        r = line.strip().split()
        word_dict[r[1]] = r[0]
    return word_dict


def read_doc(infile):
    doc = {}
    for line in open(infile):
        r = line.strip().split()
        doc[r[0]] = r[1:]
        #assert len(doc[r[0]]) == int(r[1])
    return doc


def filter_triletter(tri_stats, min_filter_num=5, max_filter_num=10000):
    tri_dict = {}
    tri_stats = sorted(tri_stats.items(), key=lambda d:d[1], reverse=True)
    for triinfo in tri_stats:
        if min_filter_num <= triinfo[1] <= max_filter_num:
            if triinfo[0] not in tri_dict:
                tri_dict[triinfo[0]] = len(tri_dict)
    return tri_dict

def save_run_trec(rel_file,rel_trec_file):
    relation_file = open(rel_file,'r',encoding='utf-8')
    rel_writer = open(rel_trec_file,'w',encoding='utf-8')
    for line in relation_file.readlines():
        tokens = line.strip().split()
        label = tokens[0]
        q_id = tokens[1]
        d_id = tokens[2]
        rel_writer.write(q_id+' 0 '+d_id+' '+label+'\n')
    rel_writer.close()


def save_corpus(corpus_file,save_corpus_file):
    corpus_f = open(corpus_file,'r',encoding='utf-8')
    save_corpus_f = open(save_corpus_file, 'w', encoding='utf-8')
    for line in corpus_f.readlines():
        tokens = line.strip().split()
        id = tokens[0]
        text = ' '.join(tokens[1:])
        save_corpus_f.write(id+'\t'+text+"\n")
    save_corpus_f.close()




if __name__ == '__main__':
    config = json.load(open('config.py','r'))
    #srcdir = config["srcdir"]
    dstdir = config["dstdir"]
    traindir = config["traindir"]
    testdir = config["testdir"]
    devdir = config["devdir"]

    if not os.path.exists(dstdir):
        os.mkdir(dstdir)

    prepare = Preparation()
    # srcdir = './'
    # dstdir = './'

    infiles = [ traindir + 'pinfo-mz-train.txt', devdir + 'pinfo-mz-dev.txt', testdir + 'pinfo-mz-test.txt']
    # infiles = [traindir, devdir, testdir]
    corpus, rel_train, rel_valid, rel_test = prepare.run_with_train_valid_test_corpus(infiles[0], infiles[1], infiles[2])
    print('total corpus : %d ...' % (len(corpus)))
    print('total relation-train : %d ...' % (len(rel_train)))
    print('total relation-valid : %d ...' % (len(rel_valid)))
    print('total relation-test: %d ...' % (len(rel_test)))
    prepare.save_corpus(dstdir + 'corpus.txt', corpus)

    prepare.save_relation(dstdir + 'relation_train.txt', rel_train)
    prepare.save_relation(dstdir + 'relation_valid.txt', rel_valid)
    prepare.save_relation(dstdir + 'relation_test.txt', rel_test)
    save_run_trec(dstdir + 'relation_train.txt', dstdir + 'relation_train_trec.txt')
    save_run_trec(dstdir + 'relation_valid.txt', dstdir + 'relation_valid_trec.txt')
    save_run_trec(dstdir + 'relation_test.txt', dstdir + 'relation_test_trec.txt')


    print('Preparation finished ...')

    preprocessor = Preprocess(word_stem_config={'enable': False}, word_filter_config={'min_freq': 2})
    dids, docs = preprocessor.run(dstdir + 'corpus.txt')
    preprocessor.save_word_dict(dstdir + 'word_dict.txt', True)
    preprocessor.save_words_stats(dstdir + 'word_stats.txt', True)

    fout = open(dstdir + 'corpus_preprocessed.txt', 'w')
    for inum, did in enumerate(dids):
        fout.write('%s %s %s\n' % (did, len(docs[inum]), ' '.join(map(str, docs[inum]))))
    fout.close()
    print('Preprocess finished ...')

    save_corpus(dstdir + 'corpus.txt', dstdir + 'corpus_t.txt')
    save_run_trec(dstdir + 'relation_train.txt', dstdir + 'relation_train_trec.txt')
    save_run_trec(dstdir + 'relation_valid.txt', dstdir + 'relation_valid_trec.txt')
    save_run_trec(dstdir + 'relation_test.txt', dstdir + 'relation_test_trec.txt')

    # dssm_corp_input = dstdir + 'corpus_preprocessed.txt'
    # dssm_corp_output = dstdir + 'corpus_preprocessed_dssm.txt'
    word_dict_input = dstdir + 'word_dict.txt'
    triletter_dict_output = dstdir + 'triletter_dict.txt'
    word_triletter_output = dstdir + 'word_triletter_map.txt'
    word_dict = read_dict(word_dict_input)
    word_triletter_map = {}
    triletter_stats = {}
    for wid, word in word_dict.items():
        nword = '#' + word + '#'
        ngrams = NgramUtil.ngrams(list(nword), 3, '')
        word_triletter_map[wid] = []
        for tric in ngrams:
            if tric not in triletter_stats:
                triletter_stats[tric] = 0
            triletter_stats[tric] += 1
            word_triletter_map[wid].append(tric)
    triletter_dict = filter_triletter(triletter_stats, 5, 10000)
    with open(triletter_dict_output, 'w') as f:
        for tri_id, tric in triletter_dict.items():
            print(tri_id, tric, file=f)
    with open(word_triletter_output, 'w') as f:
        for wid, trics in word_triletter_map.items():
            print(wid, ' '.join([str(triletter_dict[k]) for k in trics if k in triletter_dict]), file=f)

    print('Triletter Processing finished ...')

