<template>
  <el-main>
    <div class="top-bar">
      <div class="option-bar">
        <div class="header-bar">
          <span>Auto Selection Tasks</span>
        </div>
        <div class="operation-btn-bar">
          <el-button type="primary" @click="dialogFormVisible = true">Add New Task</el-button>
        </div>
      </div>
    </div>
    <el-dialog title="Add New Task" :visible.sync="dialogFormVisible" width="640px"
               append-to-body :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
      <el-form ref="addAutoSelectionTaskForm" :model="addAutoSelectionTaskForm" :rules="rules" label-position="left" label-width="130px">
        <el-form-item label="Dataset" prop="dataset">
          <el-select v-model="addAutoSelectionTaskForm.dataset" placeholder="Choose dataset">
            <el-option v-for="item in datasetList" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Metric" prop="metric">
          <el-select v-model="addAutoSelectionTaskForm.metric" placeholder="Choose Metric">
            <el-option v-for="item in metricList" :key="item.value" :label="item.label" :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Remark" prop="remark">
          <!--          Remark 或者 Desc-->
          <el-input v-model="addAutoSelectionTaskForm.remark" placeholder="Add remark"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="">Submit</el-button>
        <el-button @click="dialogFormVisible = false">Cancel</el-button>
      </div>
    </el-dialog>
    <div class="content-div scrollable-div">
      <el-scrollbar>
        <div class="content-parent">
          <div class="content">
            <div class="item-list">
              <el-table ref="autoSelectionTaskTable" :data="autoSelectionTaskTableData" :max-height="autoSelectionTaskTableHeight">
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
                    <el-button type="primary" plain size="small" @click="showAutoSelectionResult(scope.row.id)">Show Result</el-button>
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
        name: "AutoSelection",
        data() {
            return {
                autoSelectionTaskTableHeight: 200,
                autoSelectionTaskTableData: [
                    {
                        id: '1',
                        name: 'name1name1name1name1name1name1',
                        desc: 'desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1',
                        status: 1
                    },
                    {
                        id: '2',
                        name: 'name2',
                        desc: 'desc2',
                        status: 0
                    },
                    {
                        id: '3',
                        name: 'name3',
                        desc: 'desc3',
                        status: 1
                    },
                    {
                        id: '4',
                        name: 'name4',
                        desc: 'desc4',
                        status: 0
                    }
                ],
                dialogFormVisible: false,
                datasetList: [
                    {
                        value: '1',
                        label: 'Dataset 01'
                    }, {
                        value: '2',
                        label: 'Dataset 02'
                    }
                ],
                metricList: [
                    {
                        value: '1',
                        label: 'Metric 01'
                    }, {
                        value: '2',
                        label: 'Metric 02'
                    }
                ],
                addAutoSelectionTaskForm: {
                    dataset: '',
                    metric: '',
                    remark: ''
                },
                rules: {
                    dataset: [
                        {required: true, message: 'Please input name', trigger: 'blur'}
                    ],
                    metric: [
                        {required: true, message: 'Please input name', trigger: 'blur'}
                    ]
                }
            };
        },
        methods: {
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
            showAutoSelectionResult(taskId) {
                alert("This is the result of Task "+ taskId);
            }
        },
        mounted() {
            this.$nextTick(function () {
                this.autoSelectionTaskTableHeight = window.innerHeight - this.$refs.autoSelectionTaskTable.$el.offsetTop - 190;
                let self = this;
                window.onresize = function() {
                    self.autoSelectionTaskTableHeight = window.innerHeight - self.$refs.autoSelectionTaskTable.$el.offsetTop - 190;
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
