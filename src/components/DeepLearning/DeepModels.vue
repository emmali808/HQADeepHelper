<template>
  <el-main>
    <div class="top-bar">
      <div class="option-bar">
        <div class="selector-bar">
          <span>Select Model: </span>
          <el-cascader
            ref="selectedDeepModelOptions"
            v-model="selectedDeepModel"
            :options="deepModelsOptions"
            :props="{ expandTrigger: 'hover' }"
            @change="selectModel"
            placeholder="Please select a model">
          </el-cascader>
        </div>
      </div>
    </div>
    <div class="content-div scrollable-div">
      <el-scrollbar>
        <div class="content-parent">
          <div class="content">
            <el-card class="">
              <div slot="header">
                <span><b>Model:</b>&ensp;{{selectedDeepModelName}}</span>
              </div>
              <div class="">
                <div v-if="selectedDeepModelName === ''">
                  <span>Please select a model. </span>
                </div>
                <div v-else>
                  <el-form :model="modelInfoForm" label-position="left" label-width="110px">
                    <el-form-item label="Article" prop="articleTitle">
                      <span>{{modelInfoForm.articleTitle}}</span>&emsp;&emsp;
                      <el-button type="primary" @click="downloadArticle">Download</el-button>
                    </el-form-item>
                    <el-form-item label="Introduction" prop="introduction">
                      <span>{{modelInfoForm.introduction}}</span>
                    </el-form-item>
                    <el-form-item label="Architecture" prop="architecture">
                      <el-image :src="modelInfoForm.url" :fit="'scale-down'" :z-index="2000" style="width: 90%"></el-image>
<!--                      :preview-src-list="[modelInfoForm.url]"-->
                    </el-form-item>
                    <el-form-item label="Code" prop="code">
                      <el-button type="primary" @click="downloadCode">Download</el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </el-scrollbar>
    </div>
  </el-main>
</template>

<script>
    export default {
        name: "DeepModels",
        data() {
            return {
                deepModelsOptions: [],
                categoryNames: [],
                modelNames: [],

                selectedDeepModel: [],
                selectedDeepModelId: 0,
                selectedDeepModelName: '',

                modelInfoForm: {
                    articleTitle: '',
                    introduction: '',
                    // url: require('@/assets/logo_adds.jpg'),
                    url1: '@/assets/logo_adds.jpg'
                }
            };
        },
        methods: {
            getDeepModels() {
                this.$axios({
                    method: 'get',
                    url: '/modelCategory'
                }).then(res => {
                    // console.log(res.data);
                    for (let item in res.data) {
                        if (res.data.hasOwnProperty(item)) {
                            this.deepModelsOptions.push({
                                value: res.data[item].id,
                                label: res.data[item].category,
                                children: []
                            });
                            this.categoryNames.push({
                                id: res.data[item].id,
                                name: res.data[item].category
                            });
                            this.getModelsOfCategory(res.data[item].id);
                        }
                    }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR! Check Console plz! ");
                });
            },
            getModelsOfCategory(modelCategoryId) {
                this.$axios({
                    method: 'get',
                    url: '/modelCategory/' + modelCategoryId + '/deepModel'
                }).then(res => {
                    console.log(res.data);
                    for (let model in res.data) {
                        if (res.data.hasOwnProperty(model)) {
                            let modelCategoryIndex = 0;
                            for (let category in this.deepModelsOptions) {
                                if (this.deepModelsOptions.hasOwnProperty(category)) {
                                    if (this.deepModelsOptions[category].value === modelCategoryId) {
                                        modelCategoryIndex = category;
                                        break;
                                    }
                                }
                            }
                            let modelCategory = this.deepModelsOptions[modelCategoryIndex];
                            modelCategory.children.push({
                                value: res.data[model].id,
                                label: res.data[model].modelName,
                            });
                            this.modelNames.push({
                                id: res.data[model].id,
                                name: res.data[model].modelName,
                            });
                        }
                    }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR! Check Console plz! ");
                });
            },
            selectModel(value) {
                // console.log(value);
                for (let model in this.modelNames) {
                    if (this.modelNames.hasOwnProperty(model)) {
                        if (this.modelNames[model].id === value[value.length-1]) {
                            // console.log(this.modelNames[model].name);
                            this.selectedDeepModelId = this.modelNames[model].id;
                            this.selectedDeepModelName = this.modelNames[model].name;
                            this.getModelInfo();
                        }
                    }
                }
            },
            getModelInfo() {
                this.$axios({
                    method: 'get',
                    url: '/modelCategory/model/' + this.selectedDeepModelId
                }).then(res => {
                    console.log(res.data);

                    this.modelInfoForm.articleTitle = res.data.modelArticleTitle;
                    if (this.modelInfoForm.articleTitle === '' || this.modelInfoForm.articleTitle === null) {
                        this.modelInfoForm.articleTitle = '[NO Article FOR NOW... ]';
                    }
                    this.modelInfoForm.introduction = res.data.modelIntroduction;
                    if (this.modelInfoForm.introduction === '' || this.modelInfoForm.introduction === null) {
                        this.modelInfoForm.introduction = '[NO Introduction FOR NOW... ]';
                    }
                }).catch(error => {
                    console.log(error);
                    alert("ERROR  in function \"getModelInfo( )\" [DeepModels]! Check Console plz! ");
                });
            },
            downloadArticle() {
            },
            downloadCode() {
            }
        },
        created() {
            this.getDeepModels();
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

  .top-bar {
  }

  .option-bar {
    display: inline-block;
    position: fixed;
    left: 330px;
    right: 60px;
  }

  .selector-bar {
    float: left;
    margin: 0 20px;
  }

  .selector-bar span {
    margin-right: 20px;
  }

  .el-cascader {
    width: 400px;
  }

  .content-div {
    position: fixed;
    top: 180px;
    left: 330px;
    right: 60px;
    bottom: 20px;
  }

  .content {
    padding-left: 30px;
    padding-right: 30px;
  }
</style>
