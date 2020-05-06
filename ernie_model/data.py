import random
from tqdm import tqdm
import torch
import argparse

def init_qd_len(text1_maxlen,text2_maxlen):
    global QLEN
    QLEN = text1_maxlen
    global DLEN
    DLEN = text2_maxlen


def read_datafiles(file):
    queries = {}
    docs = {}

    for line in tqdm(file, desc='loading datafile (by line)', leave=False):
        cols = line.rstrip().split('\t')
        if len(cols) != 2:
            tqdm.write(f'skipping line: `{line.rstrip()}`')
            continue
        c_id, c_text = cols        
        if c_id.startswith('Q') :
            queries[c_id] = c_text
        if c_id.startswith('D'):
            docs[c_id] = c_text
    return queries, docs


def read_qrels_dict(file):
    result = {}
    for line in tqdm(file, desc='loading qrels (by line)', leave=False):
        #qid, _, docid, score = line.split()
        score,qid,docid = line.split()
        result.setdefault(qid, {})[docid] = int(score)
    return result




def iter_train_pairs(model, dataset, train_pairs, batch_size,contentid2entity):
    batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': [],'query_entity': [], 'doc_entity': []}
    for qid, did, query_tok, query_entity,doc_tok,doc_entity in _iter_train_pairs(model, dataset, train_pairs,contentid2entity):
        batch['query_id'].append(qid)
        batch['doc_id'].append(did)
        batch['query_tok'].append(query_tok)
        batch['doc_tok'].append(doc_tok)
        batch['query_entity'].append(query_entity)
        batch['doc_entity'].append(doc_entity)
        if len(batch['query_id']) // 2 == batch_size:
            yield _pack_n_ship(batch)
            batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': [],'query_entity': [], 'doc_entity': []}




def _iter_train_pairs(model, dataset, train_pairs,contentid2entity):
    
    ds_queries, ds_docs = dataset
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
            
            #print(ds_queries[qid])
            #print(contentid2entity[qid])
            query_ents = tuple(contentid2entity[qid])
            query_tok,query_entity = model.tokenize(ds_queries[qid],query_ents)
            pos_doc = ds_docs.get(pos_id)
            neg_doc = ds_docs.get(neg_id)
            if pos_doc is None:
                tqdm.write(f'missing doc {pos_id}! Skipping')
                continue
            if neg_doc is None:
                tqdm.write(f'missing doc {neg_id}! Skipping')
                continue
            pos_doc_tok,pos_doc_entity = model.tokenize(pos_doc,tuple(contentid2entity[pos_id]))
            neg_doc_tok,neg_doc_entity = model.tokenize(neg_doc,tuple(contentid2entity[neg_id]))
            yield qid, pos_id, query_tok,query_entity, pos_doc_tok,pos_doc_entity
            yield qid, neg_id, query_tok,query_entity, neg_doc_tok,neg_doc_entity


def iter_valid_records(model, dataset, run, batch_size,contentid2entity):
    batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': [],'query_entity': [], 'doc_entity': []}
    for qid, did, query_tok, query_entity,doc_tok,doc_entity in _iter_valid_records(model, dataset, run,contentid2entity):
        batch['query_id'].append(qid)
        batch['doc_id'].append(did)
        batch['query_tok'].append(query_tok)
        batch['doc_tok'].append(doc_tok)
        batch['query_entity'].append(query_entity)
        batch['doc_entity'].append(doc_entity)
        if len(batch['query_id']) == batch_size:
            yield _pack_n_ship(batch)
            batch = {'query_id': [], 'doc_id': [], 'query_tok': [], 'doc_tok': [],'query_entity': [], 'doc_entity': []}
    # final batch
    if len(batch['query_id']) > 0:
        yield _pack_n_ship(batch)


def _iter_valid_records(model, dataset, run,contentid2entity):
    ds_queries, ds_docs = dataset
    for qid in run:
        query_tok,query_entity = model.tokenize(ds_queries[qid],tuple(contentid2entity[qid]))
        for did in run[qid]:
            doc = ds_docs.get(did)
            if doc is None:
                tqdm.write(f'missing doc {did}! Skipping')
                continue
            doc_tok,doc_entity = model.tokenize(doc,tuple(contentid2entity[did]))
            yield qid, did, query_tok,query_entity, doc_tok,doc_entity

def valid_toks_masks(model,query_txt,doc_txt,query_ent,doc_ent):
    query_tok = []
    doc_tok = []
    query_entity = []
    doc_entity = []
    q_t,q_e = model.tokenize(query_txt, tuple(query_ent))
    d_t,d_e = model.tokenize(doc_txt, tuple(doc_ent))
    query_tok .append(q_t)
    doc_tok .append(d_t)
    query_entity.append(q_e)
    doc_entity.append(d_e)
    qlen = len(query_tok[0])
    dlen = len(doc_tok[0])
    return {'query_tok':_pad_crop(query_tok,qlen),
            'doc_tok':_pad_crop(doc_tok,dlen),
            'query_mask':_mask(query_tok,qlen),
            'doc_mask':_mask(doc_tok,dlen),
            'query_entity': _pad_crop(query_entity, qlen),
            'doc_entity': _pad_crop(doc_entity, dlen)
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
        'doc_tok': _pad_crop(batch['doc_tok'], DLEN),
        'query_mask': _mask(batch['query_tok'], QLEN),
        'doc_mask': _mask(batch['doc_tok'], DLEN),
        'query_entity': _pad_crop(batch['query_entity'], QLEN),
        'doc_entity': _pad_crop(batch['doc_entity'], DLEN)
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


def _mask(items, l):
    result = []
    for item in items:
        if len(item) < l:
            item = [1. for _ in item] + ([0.] * (l - len(item)))
        elif len(item) >= l:
            item = [1. for _ in item[:l]]
        result.append(item)
    return torch.tensor(result).float().cuda()


if __name__=='__main__':
    '''parser = argparse.ArgumentParser('CEDR model training and validation')
    parser.add_argument('--datafiles', type=argparse.FileType('rt'))
    args = parser.parse_args()
    
    queries,docs = read_datafiles(args.datafiles)
    print(docs)'''
    file  = 'data/relation_test.txt'
    output = 'data/relation_test_trec.txt'
    with open(output,'w',encoding='utf-8') as writer:
        for line in open(file,'r',encoding='utf-8'):
            score,qid,did = line.rstrip().split()
            writer.write(qid+' 0 '+did+' '+score+'\n')
        