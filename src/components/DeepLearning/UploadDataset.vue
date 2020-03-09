<template>
  <el-main>
    <div class="top-bar">
      <div class="option-bar">
        <div class="header-bar">
          <span>My Dataset</span>
        </div>
        <div class="operation-btn-bar">
          <el-button type="primary" @click="dialogFormVisible = true">Upload Dataset</el-button>
        </div>
      </div>
    </div>
    <el-dialog title="New Dataset" :visible.sync="dialogFormVisible" width="640px"
               append-to-body :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
      <el-form ref="uploadDatasetForm" :model="uploadDatasetForm" :rules="rules" label-position="left" label-width="130px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="uploadDatasetForm.name"></el-input>
        </el-form-item>
        <el-form-item label="Description" prop="desc">
          <el-input type="textarea" :rows="7" v-model="uploadDatasetForm.desc"></el-input>
        </el-form-item>
<!--        <el-form-item label="Dataset Format" prop="datasetFormat">-->
<!--          <span><b>label \t query \t document.txt</b></span>&emsp;-->
<!--          <el-button type="primary" @click="">Sample.txt</el-button>-->
<!--        </el-form-item>-->
<!--        <el-form-item label="File Upload" prop="fileUpload">-->
<!--          <div>-->
<!--            <div style="margin-bottom: 20px">-->
<!--              <el-upload-->
<!--                :action="'/doctor/' + this.$store.state.user.id + '/dataSets'"-->
<!--                :on-success="aaa"-->
<!--                :on-error="bbb"-->
<!--                :on-preview="handlePreview"-->
<!--                :on-remove="handleRemove"-->
<!--                :before-remove="beforeRemove"-->
<!--                multiple-->
<!--                :limit="3"-->
<!--                :on-exceed="handleExceed"-->
<!--                :file-list="fileList"-->
<!--              >-->
<!--                <el-button type="primary">TrainSet</el-button>-->
<!--                <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>-->
<!--              </el-upload>-->
<!--            </div>-->
<!--            <div style="margin-bottom: 20px">-->
<!--              <el-upload :action="'/doctor/' + this.$store.state.user.id + '/dataSets'">-->
<!--                <el-button type="primary">TestSet</el-button>-->
<!--              </el-upload>-->
<!--            </div>-->
<!--            <div style="margin-bottom: 20px">-->
<!--              <el-upload :action="'/doctor/' + this.$store.state.user.id + '/dataSets'">-->
<!--                <el-button type="primary">DevSet</el-button>-->
<!--&lt;!&ndash;                <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div>&ndash;&gt;-->
<!--              </el-upload>-->
<!--            </div>-->
<!--          </div>-->




<!--&lt;!&ndash;          <el-button type="primary" @click="">TrainSet</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-button type="primary" @click="">TestSet</el-button>&ndash;&gt;-->
<!--&lt;!&ndash;          <el-button type="primary" @click="">DevSet</el-button>&ndash;&gt;-->
<!--        </el-form-item>-->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="addDataset">Submit</el-button>
        <el-button @click="cancelAddDataset">Cancel</el-button>
      </div>
    </el-dialog>
    <div class="content-div scrollable-div">
      <el-scrollbar>
        <div class="content-parent">
          <div class="content">
            <div class="item-list">
              <el-table ref="datasetTable" :data="datasetTableData" :max-height="datasetTableHeight">
                <el-table-column prop="name" label="Name" min-width="20%" :show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="desc" label="Description" min-width="30%" :show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="status" label="Status" min-width="15%">
                  <template slot-scope="scope">
                    <el-tag v-if="scope.row.status === 0" type="info" @click="showMsg(false)">Running</el-tag>
                    <el-tag v-else type="success" @click="showMsg(true)">Finished</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="operations" label="Operations" min-width="35%">
                  <template slot-scope="scope" v-if="scope.row.status === 1">
                    <el-button type="primary" plain size="small" @click="goToModelEvaluation(scope.row.id)">Model Evaluation</el-button>
                    <el-button type="primary" plain size="small" @click="goToAutoSelection(scope.row.id)">Auto Selection</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </el-main>
</template>

<script>
    export default {
        name: "UploadDataset",
        data() {
            return {
                datasetTableHeight: 200,
                datasetTableData: [
                    // {
                    //     id: '1',
                    //     name: 'name1name1name1name1name1name1name1name1name1name1name1name1',
                    //     desc: 'desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1',
                    //     status: 1
                    // },
                    // {
                    //     id: '2',
                    //     name: 'name2',
                    //     desc: 'desc2',
                    //     status: 0
                    // },
                    // {
                    //     id: '3',
                    //     name: 'name3',
                    //     desc: 'desc3',
                    //     status: 1
                    // },
                    // {
                    //     id: '4',
                    //     name: 'name4',
                    //     desc: 'desc4',
                    //     status: 0
                    // }
                ],
                dialogFormVisible: false,
                uploadDatasetForm: {
                    name: '',
                    desc: ''
                },
                rules: {
                    name: [
                        {required: true, message: 'Please input name', trigger: 'blur'}
                        // {min: 1, max: 10, message: 'Name length is between 1 and 10', trigger: 'blur'}
                    ],
                    desc: [
                        {required: true, message: 'Please input description', trigger: 'blur'}
                    ]
                },
                fileList: []
            };
        },
        methods: {
            loadDataset() {
                this.$axios({
                    method: 'get',
                    url: '/doctor/' + this.$store.state.user.id + '/dataSets'
                }).then(res => {
                    console.log(res.data);
                    this.datasetTableData.length = 0;
                    for (let dataset in res.data) {
                        if (res.data.hasOwnProperty(dataset)) {
                            this.datasetTableData.push({
                                id: res.data[dataset].id,
                                name: res.data[dataset].dataset_name,
                                desc: res.data[dataset].dataset_desc
                                // status: res.data[dataset].id
                            });
                        }
                    }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR  in function \"loadDataset( )\" [UploadDataset]! Check Console plz! ");
                });
            },
            addDataset() {
                // console.log(
                //     'Name: ' + this.uploadDatasetForm.name + '\n' +
                //     'Desc: ' + this.uploadDatasetForm.desc
                // );

                this.$axios({
                    method: 'post',
                    url: '/doctor/' + this.$store.state.user.id + '/dataSet',
                    data: {
                        dataset_name: this.uploadDatasetForm.name,
                        dataset_desc: this.uploadDatasetForm.desc
                    }
                }).then(res => {
                    // console.log(res.data);
                    if (res.data > 0) {
                        this.closeDialogForm();
                        this.loadDataset();
                    } else {
                        this.$message({
                            message: 'ERROR to Add Dataset! ',
                            type: 'error',
                            showClose: true
                        });
                    }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR  in function \"addDataset( )\" [UploadDataset]! Check Console plz! ");
                });
            },
            cancelAddDataset() {
                this.closeDialogForm();
            },
            closeDialogForm() {
                this.dialogFormVisible = false;
                this.$refs['uploadDatasetForm'].resetFields();
            },
            showMsg(status) {
                if (status === true) {
                    this.$message({
                        type: 'success',
                        message: 'Finished running! '
                    });
                } else {
                    this.$message("Still running! ");
                }
            },
            goToModelEvaluation(datasetId) {
                this.$message({
                    type: 'success',
                    message: 'Dataset id: ' + datasetId + ', go to Model Evaluation page'
                });
            },
            goToAutoSelection(datasetId) {
                this.$message({
                    type: 'success',
                    message: 'Dataset id: ' + datasetId + ', go to Auto Selection page'
                });
            },
            aaa(file) {
                this.fileList.push(file);
            },
            bbb(file) {
                alert("Upload file ERROR! ");
                console.log(file);
            },
            handleRemove(file, fileList) {
                console.log(file, fileList);
            },
            handlePreview(file) {
                console.log(file);
            },
            handleExceed(files, fileList) {
                this.$message.warning(`当前限制选择 3 个文件，本次选择了 ${files.length} 个文件，共选择了 ${files.length + fileList.length} 个文件`);
            },
            beforeRemove(file, fileList) {
                return this.$confirm(`确定移除 ${ file.name }？`);
            }
        },
        created() {
            this.loadDataset();
        },
        mounted() {
            this.$nextTick(function () {
                this.datasetTableHeight = window.innerHeight - this.$refs.datasetTable.$el.offsetTop - 190;
                let self = this;
                window.onresize = function() {
                    self.datasetTableHeight = window.innerHeight - self.$refs.datasetTable.$el.offsetTop - 190;
                }
            });
        }
    }
</script>

<style scoped>
  .el-main {
    position: fixed;
    top: 80px;
    left: 300px;
    right: 30px;
    bottom: 0;
    margin: 20px;
    padding: 10px;
  }

  .option-bar {
    display: inline-block;
    position: fixed;
    left: 330px;
    right: 60px;
  }

  .header-bar {
    float: left;
    margin: 0 20px;
  }

  .header-bar span {
    font-size: 20px;
    font-weight: bold;
    float: left;
  }

  .operation-btn-bar {
    float: right;
    margin: 0 20px;
    overflow: hidden;
  }

  .el-form {
    padding: 0 10px;
  }

  /*.el-upload {*/
  /*  display: inline-block;*/
  /*}*/

  .content-div {
    position: fixed;
    top: 130px;
    left: 330px;
    right: 60px;
    bottom: 20px;
    z-index: -100;
  }

  .content {
    margin: 10px;
    padding: 30px;
  }
</style>
