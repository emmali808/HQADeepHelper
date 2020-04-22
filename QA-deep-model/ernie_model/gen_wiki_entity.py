#from umls_embed import data_utils
#import modeling
#import torch
import argparse
import json
import tagme
tagme.GCUBE_TOKEN = "75287334-5eb6-4c27-b611-b2fdef19bf48-843339462"#kg
import torch
import modeling
import modeling_util
import tqdm
import knowledge_bert as kb
import io
import gen_w2v

def  load_kg_file(kg_dir):
    # Read entity map
    global ent_map
    ent_map = {}
    with open(kg_dir+"entity_map.txt") as fin:
        for line in fin:
            name, qid = line.strip().split("\t")
            ent_map[name] = qid
    
    # Convert ents
    global entity2id
    entity2id = {}
    with open(kg_dir+"entity2id.txt") as fin:
        fin.readline()
        for line in fin:
            qid, eid = line.strip().split('\t')
            entity2id[qid] = int(eid)
        
class Entity():
    def __init__(self,eid,entity):
        self.id = eid
        self.entity = entity
   

def get_ent(text):
    try:
        text_ann = tagme.annotate(text)
        if text_ann:
            ents = modeling_util.get_ents(text_ann,ent_map)
        else:
            print('request error!')
            ents = []
        return ents
    except:
        print('connection timeout error! Please retry this.')
        return []
      
def generate_ent(input_file,output_file)  :
    reader = open(input_file,'r',encoding='utf-8')
    
    entities = []
    for line in tqdm.tqdm(reader.readlines()):
        content = line.strip().split('\t')
        ex = Entity(content[0],get_ent(content[1]))
        entities.append(ex)
    torch.save(entities,output_file)    
      
# def getcontentid2entity():
#     contentid2entity = {}
#     id2entities = torch.load('nf_content2entity.f')
#     for id2entity in id2entities:
#         if id2entity.id not in contentid2entity:
#             contentid2entity[id2entity.id] = id2entity.entity
#     return contentid2entity
#
def get_corpus(file_path):
    id_corpus = {}
    with open(file_path,'r',encoding='utf-8') as reader:
        for line in reader:
            contents = line.rstrip().split('\t')
            c_id = contents[0]
            c_content = contents[1]
            if c_id not in id_corpus:
                id_corpus[c_id] = c_content
    return id_corpus

def load_word_dict(word_map_file):
    """ file -> {word: index} """
    word_dict = {}
    for line in io.open(word_map_file, encoding='utf8'):
        line = line.split()
        try:
            word_dict[line[0]] = int(line[1])
        except:
            print(line+"........")
            continue
    return word_dict

def generate_id_ent(corpus_path,word_dict_path,tok_save_path,ent_save_path):
    tokenizer = kb.BasicTokenizer()
    id_corpus = get_corpus(corpus_path)
    tok_writer = open(tok_save_path, 'w', encoding='utf-8')

    corpus_toks = []
    corpus_ents = []
    for c_id,c_content in tqdm.tqdm(id_corpus.items()):
        cur_entities = []
        for split_tok,split_entity in tokenizer.tokenize(c_content,get_ent(c_content)):
            if split_entity != "UNK" and split_entity in entity2id:
                cur_entities.append(entity2id[split_entity])
            else:
                cur_entities.append(-1)
            if split_tok not in corpus_toks:
                corpus_toks.append(split_tok)
        ex = Entity(c_id,cur_entities)
        corpus_ents.append(ex)
    torch.save(corpus_ents,ent_save_path)
    with open(word_dict_path,'w',encoding='utf-8') as writer:
        for idx,tok in enumerate(corpus_toks):
            writer.write(tok+' '+(str)(idx)+'\n')

    word_dict = load_word_dict(word_dict_path)
    for c_id,c_content in tqdm.tqdm(id_corpus.items()):
        cur_toks = []
        for split_tok,split_entity in tokenizer.tokenize(c_content,get_ent(c_content)):
            cur_toks.append(word_dict[split_tok])
        cur_tok_str = ' '.join([str(cur_tok) for cur_tok in cur_toks])
        tok_writer.write(c_id+' '+cur_tok_str+'\n')

        
if __name__=='__main__':
    #generate entity for our bert
    # hqa_data_dir = '../HAR-master/data/pinfo/hqa_sample/'
    # nf_data_dir = '../HAR-master/data/pinfo/nf_sample/'
    # generate_ent(nf_data_dir+'corpus_t.txt',nf_data_dir+'content2entity.f')
    # generate_ent(hqa_data_dir + 'corpus_t.txt', hqa_data_dir + 'content2entity.f')



    #generate entity for our glove
    parser = argparse.ArgumentParser('wikidata entity base config')
    parser.add_argument('--data_dir', required=True, help='the dataset and kg directory.')
    parser.add_argument('--kg_embed_dir', required=True, help='the raw kg embedding folder.')
    args = parser.parse_args()

    #config = json.load(open(args.config, 'r'))
    load_kg_file(args.kg_embed_dir)
    data_dir = args.data_dir
    generate_ent(data_dir + 'corpus_t.txt', data_dir + 'content2entity.f')

    generate_id_ent(data_dir + 'corpus_t.txt', data_dir + 'ent_word_dict.txt', data_dir + 'id2tok.txt', data_dir + 'id2entity.f')
    gen_w2v.save_tok_ent_embed(data_dir +"embed_glove_d300", data_dir + 'ent_word_dict.txt', data_dir +"ent_embed_glove_d300")

    # tokenizer = kb.BasicTokenizer()
    # id_corpus = get_corpus('corpus.txt')
    # word glove plus entity
    # ent_save_path = 'nf_data/id2entity.f'
    # tok_save_path = 'nf_data/id2tok.txt'
    # tok_writer = open(tok_save_path,'w',encoding='utf-8')
    # word_dict_path = 'nf_data/word_dict.txt'
    # word_dict = load_word_dict(word_dict_path)
    # for c_id,c_content in tqdm.tqdm(id_corpus.items()):
    #     cur_toks = []
    #     for split_tok,split_entity in tokenizer.tokenize(c_content,get_ent(c_content)):
    #         cur_toks.append(word_dict[split_tok])
    #     cur_tok_str = ' '.join([str(cur_tok) for cur_tok in cur_toks])
    #     tok_writer.write(c_id+' '+cur_tok_str+'\n')

    # corpus_toks = []
    # corpus_ents = []
    # for c_id,c_content in tqdm.tqdm(id_corpus.items()):
    #     cur_entities = []
    #     for split_tok,split_entity in tokenizer.tokenize(c_content,get_ent(c_content)):
    #         if split_entity != "UNK" and split_entity in entity2id:
    #             cur_entities.append(entity2id[split_entity])
    #         else:
    #             cur_entities.append(-1)
    #         if split_tok not in corpus_toks:
    #             corpus_toks.append(split_tok)
    #     ex = Entity(c_id,cur_entities)
    #     corpus_ents.append(ex)
    # torch.save(corpus_ents,ent_save_path)
    # with open(word_dict_path,'w',encoding='utf-8') as writer:
    #     for idx,tok in enumerate(corpus_toks):
    #         writer.write(tok+' '+(str)(idx)+'\n')