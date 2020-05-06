import pymysql

#init the database connection
def init_connection():
    connection = pymysql.connect(host='47.94.174.82', port=3306, user='root', passwd='Tan980712', db='ADDSTest')
    return connection



def insert_result(task_id,model_id,top_valid_kv):
    connection = init_connection()
    cursor = connection.cursor()
    valid_metric = [task_id,model_id,top_valid_kv['ndcg@1'],top_valid_kv['ndcg@3'],top_valid_kv['ndcg@5'],\
                    top_valid_kv['ndcg@10'],top_valid_kv['map'],top_valid_kv['recall@3'],\
                    top_valid_kv['recall@5'],top_valid_kv['recall@10'],top_valid_kv['precision@1'],\
                    top_valid_kv['precision@3'],top_valid_kv['precision@5'],top_valid_kv['precision@10']]
    #insert the result into database result
    insert_sql = "insert into deep_model_task_result (task_id,model_id,`ndcg@1`,`ndcg@3`,`ndcg@5`,`ndcg@10`, map,`recall@3`,`recall@5`,`recall@10`,`pre@1`,`pre@3`,`pre@5`,`pre@10`) \
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(insert_sql,valid_metric)
    result_id = cursor.lastrowid
    #update the task status
    connection.commit()
    update_sql = "update model_evaluation_task set status=status+1,result_id=%s where id=%s"
    cursor.execute(update_sql,[result_id,task_id])
    connection.commit()
    connection.close()
    cursor.close()
