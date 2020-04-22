To use the deep models, you should first install those deep learning module requirements and then prepare the files. To reproduce our demo, you could download hqa_sample.zip from http://47.94.174.82:8080/HQADeepHelper/Instruction/system_require/ and place all the files in hqa_sample to our folder HAR-master/data/pinfo/hqa_sample/.

##the deep learning module requirements

####Our Environment: 
first you should using anaconda tool to create the enviroment named pytorch and install these modules in the env pytorch

*   tensorflow  1.14.0
*   keras   2.2.4
*   torch   1.3.0
*   tqdm    4.37.0
*   transformers    2.5.1
*   tagme   0.1.3
*   spacy   2.2.2
*   scispacy    0.2.4
*   tensorboardX    1.9
*   scispacy    1.3.2
*   requests    2.22.0
*   joblib 0.14.0

##Prepare all the files
####HAR-master(Feature-based models)
This is the deep learning code for our feature-based models, including (ARC-I CDSSM ARC-II MV-LSTM MatchPyramid aNMM DUET HAR CONV-KNRM). Other feature-based models are placed in the directory ernie_model.

Place the word embedding file glove.840B.300d.txt(which you could download from <https://nlp.stanford.edu/projects/glove/>) under the data/pinfo/ folder.
####Cedr-master(Context-based models)
Your should prepare two folders: bert_base and sci_bert_base. The files in bert_base such as vocab.txt, pytorch.bin, config.json are from <https://s3.amazonaws.com/models.huggingface.co/bert/bert-base-uncased.tar.gz>. The files in sci_bert_base such as vocab.txt, pytorch.bin, config.json are from are from  <https://s3-us-west-2.amazonaws.com/ai2-s2-research/scibert/huggingface_pytorch/scibert_scivocab_uncased.tar>.

####ernie_model(our joint model and knowledge-embedding model)
To implement those models, you should prepare folders from <http://47.94.174.82:8080/HQADeepHelper/Instruction/system_require/>.
*   Download kg_embed.zip and unzip the files to kg_embed. 
*   Download knowledge_bert_base.zip and unzip the files to knowledge_bert_base.
*   Download sci_knowledge_bert_base.zip and unzip the files to sci_knowledge_bert_base.
*   Download umls_embed.zip and unzip the files to umls_embed.
*   Download umls.zip and unzip the files to umls_embed/umls.






