import os
import argparse
import subprocess
import random
from tqdm import tqdm
import torch
import modeling
import data
from tensorboardX import SummaryWriter
import sys
import json
import time
import database_util as db



SEED = 42
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)
random.seed(SEED)

MODEL_MAP = {
    'pacrr': modeling.PacrrRanker,
    'drmmtks': modeling.DrmmTKSRanker,
    'knrm':modeling.KnrmRanker
}
#"ndcg@1", "ndcg@3", "ndcg@5", "ndcg@10", "map",  "recall@3", "recall@5", "recall@10", "precision@1", "precision@3", "precision@5", "precision@10"
METRIC_MAP={
    'ndcg@1':'ndcg',
    'ndcg@3':'ndcg_cut.3',
    'ndcg@5':'ndcg_cut.5',
    'ndcg@10':'ndcg_cut.10',
    'map':'map',
    'recall@3':'recall.3',
    'recall@5':'recall.5',
    'recall@10':'recall.10',
    'precision@1':'P.1',
    'precision@3':'P.3',
    'precision@5':'P.5',
    'precision@10':'P.10'
}




def main(model, toks_dataset, train_pairs,  valid_run, qrelf, model_out_dir):
    # LR = 0.0001 #arci for 0.0001
    # MAX_EPOCH = 100

    params = [v for k, v in model.named_parameters() if v.requires_grad]
    optimizer = torch.optim.Adam([{'params':params }], lr=LR)

    epoch = 0
    top_valid_score = None
    top_valid_res = None
    top_valid_kv = None
    train_time = 0
    valid_time = 0
    #writer = SummaryWriter('logs/train_arci_eval_1')
    for epoch in range(MAX_EPOCH):
        start_time = time.clock()
        loss = train_iteration(model, optimizer, toks_dataset,train_pairs)
        train_time += time.clock()-start_time
        print(f'train epoch={epoch} loss={loss}')
        #writer.add_scalar('train_loss',loss,epoch)
        start_time = time.clock()
        valid_score,valid_res,valid_k_v = validate(model, toks_dataset, valid_run, qrelf, epoch, model_out_dir)
        if epoch == MAX_EPOCH - 1:
            valid_time = time.clock() - start_time
        print(f'validation epoch={epoch} score={valid_score}')
        if top_valid_score is None or valid_score > top_valid_score:
            top_valid_score = valid_score
            top_valid_res = valid_res
            top_valid_kv = valid_k_v
            print('new top validation score, saving weights')
            model.save(os.path.join(model_out_dir, 'weights.p'))
    print('training time %s, valid time %s'%(train_time,valid_time))
    print('the best running result:%s'%top_valid_res)
    db.insert_result(task_id,model_id, top_valid_kv)


def train_iteration(model, optimizer, toks_dataset, train_pairs):
    #BATCH_SIZE = 8
    # BATCH_SIZE = 16
    # BATCHES_PER_EPOCH = 32#32
    #BATCHES_PER_EPOCH = 2
    GRAD_ACC_SIZE = 2
    total = 0
    model.train()
    total_loss = 0.
    with tqdm('training', total=BATCH_SIZE * BATCHES_PER_EPOCH, ncols=80, desc='train', leave=False) as pbar:
        for record in data.iter_train_pairs(model, toks_dataset,train_pairs, GRAD_ACC_SIZE):
            scores = model(record['query_tok'],
                           record['doc_tok'])
            count = len(record['query_id']) // 2
            scores = scores.reshape(count, 2)
            loss = torch.mean(1. - scores.softmax(dim=1)[:, 0]) # pariwse softmax
            loss.backward()
            total_loss += loss.item()
            total += count
            if total % BATCH_SIZE == 0:
                optimizer.step()
                optimizer.zero_grad()
            pbar.update(count)
            if total >= BATCH_SIZE * BATCHES_PER_EPOCH:
                return total_loss
    


def validate(model, toks_dataset, run, qrelf, epoch, model_out_dir):
    VALIDATION_METRIC = base_metric#'map'
    runf = os.path.join(model_out_dir, f'{epoch}.run')
    run_model(model, toks_dataset, run, runf)
    return trec_eval(qrelf, runf, VALIDATION_METRIC,all_metric)


def run_model(model, toks_dataset, run, runf, desc='valid'):
    BATCH_SIZE = 16
    #BATCH_SIZE = 8
    rerank_run = {}
    with torch.no_grad(), tqdm(total=sum(len(r) for r in run.values()), ncols=80, desc=desc, leave=False) as pbar:
        model.eval()
        for records in data.iter_valid_records(model, toks_dataset, run, BATCH_SIZE):
            scores = model(records['query_tok'],
                           records['doc_tok'])
            for qid, did, score in zip(records['query_id'], records['doc_id'], scores):
                rerank_run.setdefault(qid, {})[did] = score.item()
            pbar.update(len(records['query_id']))
    with open(runf, 'wt') as runfile:
        for qid in rerank_run:
            scores = list(sorted(rerank_run[qid].items(), key=lambda x: (x[1], x[0]), reverse=True))
            for i, (did, score) in enumerate(scores):
                runfile.write(f'{qid} 0 {did} {i+1} {score} run\n')


def trec_eval(qrelf, runf, metric,all_metric):
    trec_eval_f = os.path.abspath(sys.argv[0] + '/../../bin/trec_eval')
    output = subprocess.check_output([trec_eval_f, '-m', metric, qrelf, runf]).decode().rstrip()
    output = output.replace('\t', ' ').split('\n')
    assert len(output) == 1
    base_metric_res = float(output[0].split()[2])

    all_output = []
    all_k_v = {}
    for k_metric in all_metric:
        metric = METRIC_MAP[k_metric]
        output = subprocess.check_output([trec_eval_f, '-m', metric, qrelf, runf]).decode().rstrip()
        output = output.replace('\t', ' ').split('\n')
        base_res = output[0].split()[2]
        all_output.append(metric + ' is ' + base_res)
        all_k_v[k_metric]=base_res

    return base_metric_res, '\t'.join(all_output),all_k_v


def main_cli():
    parser = argparse.ArgumentParser('CEDR model training and validation')
    parser.add_argument('--model', choices=MODEL_MAP.keys())
    parser.add_argument('--config', required=True, help='the model config file')
    #parser.add_argument('--toks_datafiles', required=True)
    # parser.add_argument('--valid_trec', type=argparse.FileType('rt'))
    # parser.add_argument('--train_pairs', type=argparse.FileType('rt'))
    # parser.add_argument('--valid_run', type=argparse.FileType('rt'))
    parser.add_argument('--initial_bert_weights', type=argparse.FileType('rb'))
    parser.add_argument('--task_id', required=True,
                        help='the task id for this training task. help for insert into our database.')
    parser.add_argument('--model_id', required=True,
                        help='the model id for this training task. help for insert into our database.')
    args = parser.parse_args()

    global task_id
    task_id = args.task_id
    global model_id
    model_id = args.model_id

    config = json.load(open(args.config, 'r'))
    data_dir = config["data_dir"]
    global base_metric
    base_metric = config["base_metric"]
    global all_metric
    all_metric = config["metrics"]
    global LR
    LR = config["learning_rate"]
    global MAX_EPOCH
    MAX_EPOCH = config["MAX_EPOCH"]
    global BATCH_SIZE
    BATCH_SIZE = config["BATCH_SIZE"]
    global BATCHES_PER_EPOCH
    BATCHES_PER_EPOCH = config["BATCHES_PER_EPOCH"]

    args.text1_maxlen = config["text1_maxlen"]
    args.text2_maxlen = config["text2_maxlen"]
    data.init_qd_len(args.text1_maxlen, args.text2_maxlen)

    args.toks_datafiles = open(data_dir + 'corpus_preprocessed.txt', 'r', encoding='utf-8')
    args.valid_trec = open(data_dir + 'relation_valid_trec.txt', 'r', encoding='utf-8')
    args.train_pairs = open(data_dir + 'relation_train.txt', 'r', encoding='utf-8')
    args.valid_run = open(data_dir + 'relation_valid.txt', 'r', encoding='utf-8')
    args.model_out_dir = config["model_out_dir"]

    model = MODEL_MAP[args.model](args.config).cuda()
    toks_dataset = data.read_toks(args.toks_datafiles)
    '''qrels = data.read_qrels_dict(args.qrels)
    train_pairs = data.read_pairs_dict(args.train_pairs)
    valid_run = data.read_run_dict(args.valid_run)'''
    train_pairs = data.read_qrels_dict(args.train_pairs)
    valid_run = data.read_qrels_dict(args.valid_run)
    if args.initial_bert_weights is not None:
        model.load(args.initial_bert_weights.name)
    os.makedirs(args.model_out_dir, exist_ok=True)
    #main(model, dataset, train_pairs, qrels, valid_run, args.qrels.name, args.model_out_dir)
    main(model, toks_dataset, train_pairs, valid_run, args.valid_trec.name, args.model_out_dir)

def get_res(res_dir,metric):
    qrelf = '../nf_data/relation_valid_trec.txt'
    res_dict = {}    
    for run_file in os.listdir(res_dir):
        if run_file.endswith('run'):
            no = run_file.split('.')[0]
            runf = os.path.join(res_dir, f'{no}.run')
            res_dict[no] = trec_eval(qrelf, runf , metric)
    best_score = 0
    best_epoch = 0
    for epoch,score in res_dict.items():
        if score>best_score:
            best_score = score
            best_epoch = epoch
    print(f'epoch={best_epoch} score={best_score}')
            

if __name__ == '__main__':
    main_cli()
    # metric = 'map'
    # get_res('all-weight/nf_drmmtks_glove_weight',metric)
    #cdt = modeling.CedrDrmmTKSRanker()
    #print(cdt.tokenize('hello world',()))
    # qrelf = '../../HAR-master/data/pinfo/hqa_sample/relation_valid_trec.txt'
    # runf = 'all_weight/raw_weight/pacrr_141.run'
    # metric='map'
    # all_metric = ['map','recall.3','P.3']
    # base,output = trec_eval(qrelf, runf, metric, all_metric)
    # print(base)
    # print(output)
    
    
    
    
    
