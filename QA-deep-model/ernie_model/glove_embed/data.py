import random
from tqdm import tqdm
import torch
import argparse

import json

def init_qd_len(text1_maxlen,text2_maxlen):
    global QLEN
    QLEN = text1_maxlen
    global DLEN
    DLEN = text2_maxlen


def read_toks(file):
    queries = {}
    docs = {}

    for line in tqdm(file, desc='loading datafile (by line)', leave=False):
        cols = line.rstrip().split()
        c_id, c_toks = cols[0],cols[2:]
        if c_id.startswith('Q') :
            queries[c_id] = [(int)(tok) for tok in c_toks]
        if c_id.startswith('D'):
            docs[c_id] = [(int)(tok) for tok in c_toks]
    return queries, docs

def read_ents(file):
    
    
    queries = {}
    docs = {}

    id2ents = torch.load(file)

    for example in id2ents:
        c_id = example.id
        c_ents = example.entity
        if c_id.startswith('Q') :
            queries[c_id] = c_ents
        if c_id.startswith('D'):
            docs[c_id] = c_ents
    return queries, docs


def read_qrels_dict(file):
    result = {}
    for line in tqdm(file, desc='loading qrels (by line)', leave=False):
        #qid, _, docid, score = line.split()
        score,qid,docid = line.split()
        result.setdefault(qid, {})[docid] = int(score)
    return result



def iter_train_pairs(model, toks_dataset, train_pairs, batch_size):
    batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': []}
    for qid, did, query_tok, doc_tok in _iter_train_pairs(model, toks_dataset, train_pairs):
        batch['query_id'].append(qid)
        batch['doc_id'].append(did)
        batch['query_tok'].append(query_tok)
        batch['doc_tok'].append(doc_tok)
        if len(batch['query_id']) // 2 == batch_size:
            yield _pack_n_ship(batch)
            batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': []}




def _iter_train_pairs(model, toks_dataset,train_pairs):
    
    ds_queries, ds_docs = toks_dataset
    while True:
        qids = list(train_pairs.keys())
        random.shuffle(qids)
        for qid in qids:
            pos_ids = [did for did in train_pairs[qid] if train_pairs.get(qid).get(did, 0) > 0]
            if len(pos_ids) == 0:
                continue
            pos_id = random.choice(pos_ids)
            pos_ids_lookup = set(pos_ids)
            pos_ids = set(pos_ids)
            neg_ids = [did for did in train_pairs[qid] if did not in pos_ids_lookup]
            if len(neg_ids) == 0:
                continue
            neg_id = random.choice(neg_ids)
            

            query_tok = ds_queries[qid]
            pos_doc = ds_docs.get(pos_id)
            neg_doc = ds_docs.get(neg_id)
            if pos_doc is None:
                tqdm.write(f'missing doc {pos_id}! Skipping')
                continue
            if neg_doc is None:
                tqdm.write(f'missing doc {neg_id}! Skipping')
                continue
            pos_doc_tok = pos_doc
            neg_doc_tok = neg_doc
            yield qid, pos_id, query_tok,pos_doc_tok
            yield qid, neg_id, query_tok,neg_doc_tok


def iter_valid_records(model, toks_dataset,run, batch_size):
    batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': []}
    for qid, did, query_tok, doc_tok in _iter_valid_records(model, toks_dataset, run):
        batch['query_id'].append(qid)
        batch['doc_id'].append(did)
        batch['query_tok'].append(query_tok)
        batch['doc_tok'].append(doc_tok)
        if len(batch['query_id']) == batch_size:
            yield _pack_n_ship(batch)
            batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': []}
    # final batch
    if len(batch['query_id']) > 0:
        yield _pack_n_ship(batch)


def _iter_valid_records(model, toks_dataset,run):
    ds_queries, ds_docs = toks_dataset

    for qid in run:
        query_tok = ds_queries[qid]
        for did in run[qid]:
            doc = ds_docs.get(did)
            if doc is None:
                tqdm.write(f'missing doc {did}! Skipping')
                continue
            doc_tok = doc
            yield qid, did, query_tok, doc_tok

def valid_toks_masks(model,q_id,d_id,toks_dataset):
    query_tok = []
    doc_tok = []
    query_tok .append(toks_dataset[0][q_id])
    doc_tok .append(toks_dataset[1][d_id])
    qlen = len(query_tok[0])
    dlen = len(doc_tok[0])
    return {'query_tok':_pad_crop(query_tok,qlen),
            'doc_tok':_pad_crop(doc_tok,dlen)
            }

def _pack_n_ship(batch):
    #QLEN = 10
    #DLEN = 400
    #MAX_DLEN = 800
    #DLEN = min(MAX_DLEN, max(len(b) for b in batch['doc_tok']))
    return {
        'query_id': batch['query_id'],
        'doc_id': batch['doc_id'],
        'query_tok': _pad_crop(batch['query_tok'], QLEN),
        'doc_tok': _pad_crop(batch['doc_tok'], DLEN)
    }


def _pad_crop(items, l):
    result = []
    for item in items:
        if len(item) < l:
            item = item + [-1] * (l - len(item))
        if len(item) > l:
            item = item[:l]
        result.append(item)
    return torch.tensor(result).long().cuda()



if __name__=='__main__':
    class Entity():
        def __init__(self,eid,entity):
            self.id = eid
            self.entity = entity
    
    parser = argparse.ArgumentParser('CEDR model training and validation')
    parser.add_argument('--datafiles', type=argparse.FileType('rt'))
    args = parser.parse_args()
    
    queries,docs = read_toks(args.datafiles)
    print(type(queries['Q3750']))
    #print(docs.keys())
    '''file  = 'data/relation_test.txt'
    output = 'data/relation_test_trec.txt'
    with open(output,'w',encoding='utf-8') as writer:
        for line in open(file,'r',encoding='utf-8'):
            score,qid,did = line.rstrip().split()
            writer.write(qid+' 0 '+did+' '+score+'\n')'''
        