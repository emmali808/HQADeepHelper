package com.java.adds.dao;

import com.java.adds.controller.vo.FilterQuestionVO;
import com.java.adds.controller.vo.QuestionAnswerVO;
import com.java.adds.entity.*;
import com.java.adds.mapper.*;
import com.java.adds.utils.EmailUtil;
import com.java.adds.utils.FileUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;

@Component
public class DoctorDao {
    @Autowired
    DoctorMapper doctorMapper;

    @Autowired
    QuestionMapper questionMapper;

    @Autowired
    QuestionResultMapper questionResultMapper;

    @Autowired
    QuestionDetailAnswerMapper questionDetailAnswerMapper;

    @Autowired
    DataSetsMapper dataSetsMapper;

    @Autowired
    KGMapper kgMapper;

    @Autowired
    DeepModelTaskMapper deepModelTaskMapper;

    @Autowired
    EmailUtil emailUtil;

    @Autowired
    FileUtil fileUtil;

    @Autowired
    DeepModelMapper deepModelMapper;

    @Autowired
    DeepModelTaskResultMapper deepModelTaskResultMapper;

    //    @Value("E://医疗项目//大创//ADDS重构//ADDS//src//main//resources//dataSets//")
//    String dataSetsPathInServer;

    @Value("${file.path.conda-path}")
    String condaPath;  //conda.sh路径

    @Value("${file.path.deep-model-project}")
    String deepModelSamePath;  //所有深度学习模型存放的共同路径

    @Value("HAR-master/data/pinfo/hqa-sample/")
    String dataSetsPathInServer;

    @Value("HAR-master/examples/pinfo/config/")
    String featureBasedModelConfigPath;  //feature-based模型配置文件的前缀路径

    @Value("cedr-master/configs/")
    String contextBasedModelConfigPath;  //context-based模型配置文件的前缀路径

    @Value("ernie_model/glove_embed/configs/")
    String knowledgeEmbeddingModelConfigPathForFirst;  //knowledge-embedding模型配置文件的前缀路径

    @Value("ernie_model/glove_embed/kg_configs/")
    String knowledgeEmbeddingModelConfigPath;  //knowledge-embedding模型配置文件的前缀路径

    @Value("ernie_model/configs/")
    String ourJointModelConfigPath;  //our-joint模型配置文件的前缀路径

//    @Value("../SIGIR_QA/HAR-master")
//    String featureBasedPythonPath;  //运行feature-based模型命令的前缀路径
//
//    @Value("../SIGIR_QA/cedr-master")
//    String contextBasedPythonPath;  //运行context-based模型命令的前缀路径
//
//    @Value("../SIGIR_QA/ernie_model/glove_embed")
//    String knowledgeEmbeddingPythonPath;  //运行knowledge-embedding模型命令的前缀路径
//
//    @Value("../SIGIR_QA/ernie_model")
//    String ourJointPythonPath;  //运行our joint模型命令的前缀路径


    //模型运行结果路径
    //E://医疗项目//大创//ADDS重构//ADDS//src//main//resources//DMResultFile//
//    @Value("C:\\Users\\yin\\Desktop\\")
//    String deepModelResultPathInServer;

//    @Value("/ADDS/deepModelResult/**")
//    String deepModelResultPath;

    /**ljy
     * 管理员获取所有医生信息
     */
    public ArrayList<DoctorEntity> getAllDoctors()
    {
        return doctorMapper.getAllDoctors();
    }

    /**ljy
     * 医生获取问题（回答与否，问题类型）
     * @return
     */
    public ArrayList<QuestionEntity> getFilterQuestion(FilterQuestionVO filterQuestionVO, Long doctorId)
    {
        //1:已经回答，2：还未回答
        //1:选择题，2：详细解答题
        if(filterQuestionVO.getAnsweredOrNot()==1&&filterQuestionVO.getQuestionType()==1)//已经回答的选择题
            return questionMapper.getQuestionAnswered((filterQuestionVO.getStart()-1)* filterQuestionVO.getLimit(), filterQuestionVO.getLimit(),doctorId);
        else if(filterQuestionVO.getAnsweredOrNot()==1&&filterQuestionVO.getQuestionType()==2)//已经回答的详细解答题
            return questionMapper.getDetailQuestionsAnswered((filterQuestionVO.getStart()-1)* filterQuestionVO.getLimit(), filterQuestionVO.getLimit(),doctorId);
        else if(filterQuestionVO.getAnsweredOrNot()==2&&filterQuestionVO.getQuestionType()==1)//还未回答的选择题
            return questionMapper.getChoiceQuestionsNotAnswered((filterQuestionVO.getStart()-1)* filterQuestionVO.getLimit(), filterQuestionVO.getLimit(),doctorId);
        else//还未回答的详细解答题
            return questionMapper.getDetailQuestionsNotAnswered((filterQuestionVO.getStart()-1)* filterQuestionVO.getLimit(), filterQuestionVO.getLimit(),doctorId);
    }



    /**ljy
     *获取某一个科室下的未回答问题
     * @return
     */
    public ArrayList<QuestionEntity> getQuestionsInHosDepartment(Long uid, Long hdId)
    {
        ArrayList<QuestionEntity> questions=questionMapper.getQuestionsInHosDepartment(hdId);
        ArrayList<QuestionEntity> questionsAnswered=questionMapper.getAllQuestionAnswered(uid);
        for(int i=0;i<questions.size();i++) {
            for (int j = 0; j < questionsAnswered.size(); j++) {
                if (questions.get(i).getQid() == questionsAnswered.get(j).getQid()) {
                    questions.remove(i);
                    i--;
                    break;
                }
            }
        }
        return questions;
    }

    /**ljy
     * 医生回答某个问题
     * @return
     */
    public boolean insertAnswer(Long uid, Long qid, QuestionAnswerVO questionAnswerVO)
    {
        if(questionAnswerVO.getType()==1)  //选择题
        {
            int answer=0;
            if(questionAnswerVO.getAnswer().equals("yes"))  //1:yes,2:no
                answer=1;
            else
                answer=2;
            questionResultMapper.insertChoiceAnswer(uid,qid,answer, questionAnswerVO.getRemark());
        }
        else
            questionDetailAnswerMapper.insertDetailAnswer(uid,qid, questionAnswerVO.getAnswer(), questionAnswerVO.getRemark());

        return true;
    }


    /**ljy
     * 医生新建一个数据集
     * @return
     */
    public Integer newDataSet(Integer doctorId, DataSetsEntity dataSetsEntity)
    {
        dataSetsMapper.newDataSet(doctorId, dataSetsEntity);
        return Math.toIntExact(dataSetsEntity.getId());
    }


    /**ljy
     * 医生上传数据集
     * @return
     */
    public void uploadDataSet(Integer dId,Integer doctorId, String fileName,String filePath,String fileType)
    {
        if(fileType.equals("train"))
            dataSetsMapper.uploadTrainDataSet(dId,doctorId,filePath,fileName);
        else if(fileType.equals("test"))
            dataSetsMapper.uploadTestDataSet(dId,doctorId,filePath,fileName);
        else
            dataSetsMapper.uploadDevDataSet(dId,doctorId,filePath,fileName);

        //数据处理
        DataSetsEntity dataSetsEntity=dataSetsMapper.getDataSetsById(dId.longValue());
        if(!dataSetsEntity.getTrain_name().equals(null) && !dataSetsEntity.getTest_name().equals(null) && !dataSetsEntity.getDev_name().equals(null))
        {
            String train=deepModelSamePath+dataSetsPathInServer+dataSetsEntity.getTrain_name();
            String test=deepModelSamePath+dataSetsPathInServer+dataSetsEntity.getTest_name();
            String dev=deepModelSamePath+dataSetsPathInServer+dataSetsEntity.getDev_name();
            String dstdir=deepModelSamePath+dataSetsPathInServer+"data_"+dId.toString();
            String modelDstDir=deepModelSamePath+dataSetsPathInServer+"data_"+dId.toString();
            //生成处理数据的配置文件
            fileUtil.createDataSetConfig(dstdir,train,test,dev,modelDstDir);
            String cmd[]={"chmod",deepModelSamePath+"HAR-master/data/pinfo/run_data.sh"};  //运行.sh文件的命令
            Runtime rt = Runtime.getRuntime();
            try
            {
                rt.exec(cmd);
            }
            catch (Exception e)
            {
                e.printStackTrace();
            }
        }
    }

    /**ljy
     * 医生上传知识图谱
     * @return
     */
//    public Long uploadKG(Long doctorId,String fileName,String filePath)
//    {
//        return kgMapper.uploadKG(doctorId,fileName,filePath);
//    }

    /**ljy
     * 医生获取全部数据集
     * @return
     */
    public ArrayList<DataSetsEntity> getDataSets(Long doctorId) {
        return dataSetsMapper.getDataSets(doctorId);
    }

    /**ljy
     * 医生获取可用数据集
     * @return
     */
    public ArrayList<DataSetsEntity> getAvailableDataSets(Long doctorId) {
        return dataSetsMapper.getAvailableDataSets(doctorId);
    }

    /**ljy
     * 医生获获取知识图谱
     * @return
     */
//    public ArrayList<DataSetsEntity> getKGS(Long doctorId)
//    {
//        return kgMapper.getKGS(doctorId);
//    }


    /**ljy
     * 医生运行一个深度学习模型
     * @return
     */
    @Async
    public void doDeepModelTask(Long doctorId, DeepModelTaskEntity deepModelTaskEntity)  //异步线程调用
    {

        Long taskResultId=null;  //任务结果id
        String configPath="";  //配置文件路径
        String configFile="";  //配置文件名称
        String[] cmdArr=new String[3];//模型运行
        cmdArr[0]="sh";
        cmdArr[1]="-c";
        cmdArr[2]=". "+condaPath+"conda.sh;conda activate pytorch;";
        Runtime rt = Runtime.getRuntime();

        deepModelTaskEntity.setModelType(deepModelMapper.getCategoryByModelId(deepModelTaskEntity.getModelId()));

        //向数据库中插入一条深度学习模型信息
        //System.out.println("metricId:"+deepModelTaskEntity.getMetricId());
        //if(deepModelTaskEntity.getMetricId().toString().equals(null))
          //  deepModelTaskEntity.setMetricId((long)1);
        //deepModelTaskMapper.doDeepModelTask(doctorId,deepModelTaskEntity.getTaskName(),deepModelTaskEntity.getDatasetId(),deepModelTaskEntity.getQueryLength(),deepModelTaskEntity.getDocumentLength(),deepModelTaskEntity.getModelId(),deepModelTaskEntity.getMetricId(),0);
        //deepModelTaskEntity.setUserId(doctorId);
        //deepModelTaskEntity.setStatus(0);
        //deepModelTaskMapper.doDeepModelTask(deepModelTaskEntity);
        Long taskId=deepModelTaskEntity.getId();
        //System.out.println("taskId: "+taskId);
        //查找是否已经有了相同的模型运行结果
        ArrayList<DeepModelTaskEntity> tempDeepModelTask=deepModelTaskMapper.getSimilarityModelTask(deepModelTaskEntity.getDatasetId(),deepModelTaskEntity.getQueryLength(),deepModelTaskEntity.getDocumentLength(),deepModelTaskEntity.getModelId());

        if(tempDeepModelTask.size()==0)  //没有找到相同的模型结果
        {

            DeepModelEntity deepModelEntity = deepModelMapper.getModelById(deepModelTaskEntity.getModelId());  //获取模型信息
            String modelName=deepModelMapper.getModelById(deepModelTaskEntity.getModelId()).getName();  //获取模型名称

            if(deepModelTaskEntity.getModelType()==1&&!(modelName.equals("PACRR")||modelName.equals("KNRM")||modelName.equals("DRMMTKS")))  //first type Feature-based
            {
                configPath=deepModelSamePath+"HAR-master/data/pinfo/";
                configFile="config.py";
                cmdArr[2] +="python "+ deepModelSamePath+"HAR-master/matchzoo/main.py --phase train --model_file "+deepModelSamePath+featureBasedModelConfigPath + deepModelEntity.getConfigFile();//+ " >>" + outputPath;
            }
            else if(deepModelTaskEntity.getModelType()==1&&(modelName.equals("PACRR")||modelName.equals("KNRM")||modelName.equals("DRMMTKS")))  //first type Feature-based
            {
                String dataset="";
                if(deepModelTaskEntity.getDatasetId()==2)  //不同数据集的配置
                    dataset="nf_";
                configPath=deepModelSamePath+knowledgeEmbeddingModelConfigPathForFirst;
                configFile=dataset+deepModelEntity.getConfigFile();
                cmdArr[2] +="python "+deepModelSamePath+"ernie_model/glove_embed/train.py --model "+deepModelEntity.getModelPy() +" --config "+ configPath +configFile;//+ " >>" + outputPath;
            }
            else if(deepModelTaskEntity.getModelType()==2) //context-based
            {
                configPath=deepModelSamePath+contextBasedModelConfigPath;
                configFile=deepModelEntity.getConfigFile();
                System.out.println("modelType: 2");
                cmdArr[2] +="python "+deepModelSamePath+"cedr-master/train.py --model "+deepModelEntity.getModelPy()+" --config " + configPath + configFile;// + " >>" + outputPath+" | echo 'done'";

            }
            else if(deepModelTaskEntity.getModelType()==3)//knowledge-embedding
            {
                String dataset="";
                if(deepModelTaskEntity.getDatasetId()==2)  //不同数据集的配置
                    dataset="nf_";
                configPath=deepModelSamePath+knowledgeEmbeddingModelConfigPath;
                configFile=dataset+deepModelEntity.getConfigFile();

                cmdArr[2]+="python "+deepModelSamePath+"ernie_model/glove_embed/train_kg.py --model "+deepModelEntity.getModelPy() +" --config "+ configPath +configFile;// + " >>" + outputPath;

            }
            else   //our joint model
            {
                configPath=deepModelSamePath+ourJointModelConfigPath+deepModelEntity.getConfigFile().split("/")[0]+"/";
                configFile=deepModelEntity.getConfigFile().split("/")[1];
                if(deepModelTaskEntity.getDatasetId()==2)
                {
                    String tempPath[]=deepModelEntity.getConfigFile().split("/");
                    String confFile[]=tempPath[1].split("_");
                    configFile=confFile[0];
                    for(int i=1;i<confFile.length;i++)
                    {
                        if(i==confFile.length-2)
                            configFile+="_nf";
                        else
                            configFile+="_"+confFile[i];
                    }
                }
                cmdArr[2]+="python "+deepModelSamePath+"ernie_model/train.py --model "+deepModelEntity.getModelPy()+" --config "+configPath+configFile;//+ " >>" + outputPath;

            }


            try
            {
                fileUtil.createPythonConfig(deepModelSamePath,configPath,configFile,deepModelTaskEntity,deepModelEntity);   //生成配置文件
                cmdArr[2]+=" --task_id "+taskId.toString()+" --model_id "+deepModelTaskEntity.getModelId().toString();
                if(deepModelTaskEntity.getModelType()==1&&!(modelName.equals("PACRR")||modelName.equals("KNRM")||modelName.equals("DRMMTKS")))
                    cmdArr[2]+=" --parameter_config "+deepModelSamePath+"HAR-master/data/pinfo/config.py";
                System.out.println(cmdArr[2]);

                Process prc=rt.exec(cmdArr);  //运行深度学习模型
                InputStream errorStream=prc.getErrorStream();
                BufferedReader err=new BufferedReader((new InputStreamReader(errorStream)));
                String line=null;
                while((line=err.readLine())!=null)
                {
                    if(line!=null)
                        System.out.println(line);
                }

            }
            catch (Exception e)
            {
                e.printStackTrace();
            }

            //修改数据库信息
            //deepModelTaskMapper.updateTask(taskId,1,taskResultId);
        }
        else
        {
            System.out.println("find same result");
            System.out.println("result id:"+tempDeepModelTask.get(0).getResultId());
            deepModelTaskMapper.updateTask(taskId,1,tempDeepModelTask.get(0).getResultId());
        }


        //向用户发送模型运行完毕的邮件
//        DoctorEntity doctorEntity=doctorMapper.getDoctorById(doctorId);
//        emailUtil.sendSimpleEmail("ADDS system task completion notification","You have a new completed task, please log in the ADDS system for viewing!",doctorEntity.getEmail());
    }

    /**
     * 医生获取所有任务
     * @author ljy
     * @return
     */
    public ArrayList<DeepModelTaskEntity> getDMTasks(Integer doctorId)
    {
        return deepModelTaskMapper.getDMTasks(doctorId);
    }
}
