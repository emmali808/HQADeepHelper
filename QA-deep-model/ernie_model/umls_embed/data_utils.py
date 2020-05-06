import scispacy
import spacy
from scispacy.umls_linking import UmlsEntityLinker
from scispacy.candidate_generation import CandidateGenerator
from scispacy.file_cache import cached_path
from scispacy.candidate_generation  import load_approximate_nearest_neighbours_index
from scispacy.umls_utils import UmlsKnowledgeBase
import joblib
import json
import torch
import tqdm
import os
import json
import argparse

nlp = spacy.load('en_core_sci_sm')


def init_umls_nlp_linker():
    base_dir = ''
    tfidf_path = base_dir+'tfidf_vectors_sparse.npz'
    ann_path = base_dir+'nmslib_index.bin'
    ann_index = load_approximate_nearest_neighbours_index(tfidf_vectors_path=tfidf_path,ann_index_path=ann_path)
    vec = joblib.load(cached_path(base_dir+'tfidf_vectorizer.joblib'))
    ann_concept = json.load(open(cached_path(base_dir+'concept_aliases.json')))
    umlsknowlegebase = UmlsKnowledgeBase(file_path=base_dir+'umls_2017_aa_cat0129.json',types_file_path=base_dir+'umls_semantic_type_tree.tsv')
    cg = CandidateGenerator(ann_index=ann_index,tfidf_vectorizer=vec,ann_concept_aliases_list=ann_concept,umls=umlsknowlegebase)
    linker = UmlsEntityLinker(candidate_generator=cg,max_entities_per_mention=1)
    nlp.add_pipe(linker)
    return linker

class Entity():
    def __init__(self,eid,entity):
        self.id = eid
        self.entity = entity

def get_corpus(filepath):
    reader =  open(filepath,'r',encoding='utf-8')
    lines = [line for line in reader]
    return lines

def get_limit_corpus(lines,start,end):
    corpus_dict ={}
    for line in lines[start:end]:
        cols = line.rstrip().split('\t')
        c_id, c_text = cols 
        corpus_dict[c_id] = c_text
    return corpus_dict


#NER and entity linking to UMLS
def get_ents(text):
    linker = init_umls_nlp_linker()
    doc = nlp(text)
    ents = []
    for entity in doc.ents:
        if len(entity._.umls_ents)>0:
            umls_ent=entity._.umls_ents[0]
            concept_id = linker.umls.cui_to_entity[umls_ent[0]].concept_id
            start = entity.start_char
            end = entity.end_char
            ents.append(tuple([concept_id,start,end]))
    return ents

def get_universe_ents(text):
    doc = nlp(text)
    ents = []
    for entity in doc.ents:
        start = entity.start_char
        end = entity.end_char
        ents.append(tuple([entity.text, start, end]))
    return ents

    
def save_ent(corpus_dict,save_path):

    ex_list = []
    for c_id,c_text in tqdm.tqdm(corpus_dict.items()):
        c_ents = get_ents(c_text)
        ex = Entity(c_id,c_ents)
        ex_list.append(ex)
        
    torch.save(ex_list,save_path)

def save_universe_ent(corpus_dict, save_path):
    ex_list = []
    for c_id, c_text in tqdm.tqdm(corpus_dict.items()):
        c_ents = get_universe_ents(c_text)
        ex = Entity(c_id, c_ents)
        ex_list.append(ex)

    torch.save(ex_list, save_path)

def load_ent(file_path):
    all_ex_list = []
    for file in os.listdir(file_path):
        if file.endswith('.f'):
            ex_list = torch.load(file_path+'/'+file)
            all_ex_list.extend(ex_list)
    return all_ex_list
    
if __name__=='__main__':
    #res = load_ent('umls_entity')
    #torch.save(res,'umls_entity.f')
    parser = argparse.ArgumentParser('umls entity base config')
    parser.add_argument('--data_dir', required=True, help='the dataset and kg directory')
    parser.add_argument('--kg_name', default="umls", required=True, help='the knowledge graph name, default is umls')
    args = parser.parse_args()

    # config = json.load(open(args.config, 'r'))
    data_dir = args.data_dir
    kg_name = args.kg_name

    lines = get_corpus(data_dir+'corpus_t.txt')
    corpus_dict = get_limit_corpus(lines,0,len(lines))
    if kg_name == 'umls':
        save_ent(corpus_dict,data_dir+'umls_entity.f')
    else:
        save_universe_ent(corpus_dict,data_dir
                 +kg_name+'_entity.f')