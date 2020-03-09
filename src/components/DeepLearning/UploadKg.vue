<template>
  <el-main>
    <div class="top-bar">
      <div class="option-bar">
        <div class="header-bar">
          <span>My Knowledge Graph</span>
        </div>
        <div class="operation-btn-bar">
          <el-button type="primary" @click="dialogFormVisible = true">Upload Knowledge Graph</el-button>
        </div>
      </div>
    </div>
    <el-dialog title="Upload Knowledge Graph" :visible.sync="dialogFormVisible" width="640px"
               append-to-body :close-on-click-modal="false" :close-on-press-escape="false" :show-close="false">
      <el-form ref="uploadKgForm" :model="uploadKgForm" :rules="rules" label-position="left" label-width="130px">
        <el-form-item label="Name" prop="name">
          <el-input v-model="uploadKgForm.name"></el-input>
        </el-form-item>
        <el-form-item label="Description" prop="desc">
          <el-input type="textarea" :rows="7" v-model="uploadKgForm.desc"></el-input>
        </el-form-item>
        <el-form-item label="KG Format" prop="kgFormat">
          <span><b>entity \t relation \t entity</b></span>&emsp;
          <el-button type="primary" @click="">Sample.txt</el-button>
        </el-form-item>
        <el-form-item label="File Upload" prop="fileUpload">
          <el-button type="primary" @click="">Browse</el-button>
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
              <el-table ref="kgTable" :data="kgTableData" :max-height="kgTableHeight">
                <el-table-column prop="name" label="Name" min-width="20%" :show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="desc" label="Description" min-width="30%" :show-overflow-tooltip="true"></el-table-column>
                <el-table-column prop="operations" label="Operations" min-width="50%">
                  <template slot-scope="scope">
                    <el-button type="primary" plain size="small" @click="goToKnowledgeGraph(scope.row.id)">Show this Knowledge Graph</el-button>
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
        name: "UploadKg",
        data() {
            return {
                kgTableHeight: 200,
                kgTableData: [
                    {
                        id: '1',
                        name: 'name1name1name1name1name1name1name1',
                        desc: 'desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1desc1'
                    },
                    {
                        id: '2',
                        name: 'name2',
                        desc: 'desc2'
                    },
                    {
                        id: '3',
                        name: 'name3',
                        desc: 'desc3'
                    },
                    {
                        id: '4',
                        name: 'name4',
                        desc: 'desc4'
                    }
                ],
                dialogFormVisible: false,
                uploadKgForm: {
                    name: '',
                    desc: ''
                },
                rules: {
                    name: [
                        {required: true, message: 'Please input name', trigger: 'blur'}
                    ],
                    desc: [
                        {required: true, message: 'Please input description', trigger: 'blur'}
                    ]
                }
            };
        },
        methods: {
            loadKg() {
                this.$axios({
                    method: 'get',
                    url: '/doctor/' + this.$store.state.user.id + '/kg'
                }).then(res => {
                    console.log(res.data);
                    // for (let item in res.data) {
                    //     if (res.data.hasOwnProperty(item)) {
                    //         this.deepModelsOptions.push({
                    //             value: res.data[item].id,
                    //             label: res.data[item].category,
                    //             children: []
                    //         });
                    //     }
                    // }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR  in function \"loadKg( )\" [UploadKg]! Check Console plz! ");
                });
            },
            goToKnowledgeGraph(kgId) {
                this.$message({
                    message: 'Knowledge Graph id: ' + kgId + ', go to Knowledge Graph',
                    type: 'success'
                });
            }
        },
        created() {
            this.loadKg();
        },
        mounted() {
            this.$nextTick(function () {
                this.kgTableHeight = window.innerHeight - this.$refs.kgTable.$el.offsetTop - 190;
                let self = this;
                window.onresize = function() {
                    self.kgTableHeight = window.innerHeight - self.$refs.kgTable.$el.offsetTop - 190;
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
