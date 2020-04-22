###Introduction for our HQADeepHelper code.

“adds” is the system rear end，“adds-frontend” is the system front end，“QA-deep-model” is the deep learning library for the system.

To use our system, you should first configure the deep learning libaray, for this you can refer to the README.md in the “QA-deep-model”, make sure you have install the anaconda and the deep learning requirements. 


Then configure the system rear end and front end as follows:
The system rear end was a springboot project, just open and add related dependencies in IDEA, then you need to configure the following in the application.properties file:

####Database related configuration
This project uses mysql database.

Modify the following configuration to your database information:

*   spring.datasource.url;a
*   spring.datasource.username；
*   spring.datasource.password

####Neo4j related configuration

This project uses Neo4j to store our knowledge graph.

Modify the following configuration to your Neo4j account information:

* spring.data.neo4j.uri; 
* spring.data.neo4j.username; 
* spring.data.neo4j.password

####Other path configuration
*   file.path.deep-model-project
    >this is a foler path saved for QA-deep-model，change it to the folder and ends with '/'，such as：/home/QA-deep-model/ ;
*   file.path.conda-path
    >this is a parent folder path for your conda.sh (which is the conda shell for anaconda, find from your anaconda path) and ends with '/'，such as：/home/anaconda3/etc/profie.d/


The front end of the project is a project based on Vue.js and Element-ui component library. We also provide the source code and packaged front end code of the entire Vue project.


If you don't need to know the front-end implementation, the packaged front-end code can be used directly without any additional configuration. The packaged code can be found in the /adds/src/resources/static.


If you need to read the Vue project code, the code is located in the /adds-frontend directory in the project, and our project uses axios, d3.js, v-chats, vuex and other dependencies, you need these dependencies before running .