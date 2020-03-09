<template>
  <el-aside width="280px" class="scrollable-div">
    <el-scrollbar ref="deepLearningMenuScrollBar">
      <el-menu
        router
        @select=""
        @open=""
        @close=""
        :default-active="this.$route.path"
        :default-openeds="['2']">
        <el-menu-item index="/deepLearning/deepModels">Deep Models</el-menu-item>
<!--        <el-submenu index="1">-->
<!--          <template slot="title">Deep Models</template>-->
<!--          <el-submenu index="1-1">-->
<!--            <template slot="title">Feature-based</template>-->
<!--            <el-menu-item-group>-->
<!--              <el-menu-item index="/deepLearning/featureBasedHAR">HAR</el-menu-item>-->
<!--              <el-menu-item index="1-1-2">ANMM</el-menu-item>-->
<!--              <el-menu-item index="1-1-3">CDSSM</el-menu-item>-->
<!--              <el-menu-item index="1-1-4">Arc-I</el-menu-item>-->
<!--              <el-menu-item index="1-1-5">Arc-II</el-menu-item>-->
<!--              <el-menu-item index="1-1-6">Conv-KNRM</el-menu-item>-->
<!--              <el-menu-item index="1-1-7">MV-LSTM</el-menu-item>-->
<!--              <el-menu-item index="1-1-8">MatchPyramid</el-menu-item>-->
<!--            </el-menu-item-group>-->
<!--          </el-submenu>-->
<!--          <el-submenu index="1-2">-->
<!--            <template slot="title">Fine-tune</template>-->
<!--            <el-menu-item-group>-->
<!--              <el-menu-item index="1-2-1">DRMMTKS(BERT)</el-menu-item>-->
<!--              <el-menu-item index="1-2-2">DRMMTKS(SciBERT)</el-menu-item>-->
<!--              <el-menu-item index="1-2-3">KNRM(BERT)</el-menu-item>-->
<!--              <el-menu-item index="1-2-4">KNRM(SciBERT)</el-menu-item>-->
<!--              <el-menu-item index="1-2-5">PACRR(BERT)</el-menu-item>-->
<!--              <el-menu-item index="1-2-6">PACRR(SciBERT)</el-menu-item>-->
<!--            </el-menu-item-group>-->
<!--          </el-submenu>-->
<!--          <el-submenu index="1-3">-->
<!--            <template slot="title">Knowledge-embedding</template>-->
<!--            <el-menu-item-group>-->
<!--              <el-menu-item index="1-3-1">DRMMTKS(KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-2">KNRM(KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-3">PACRR(KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-4">DRMMTKS(BERT + KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-5">DRMMTKS(SciBERT + KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-6">KNRM(BERT + KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-7">KNRM(SciBERT + KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-8">PACRR(BERT + KG)</el-menu-item>-->
<!--              <el-menu-item index="1-3-9">PACRR(SciBERT + KG)</el-menu-item>-->
<!--            </el-menu-item-group>-->
<!--          </el-submenu>-->
<!--        </el-submenu>-->
        <el-submenu index="2">
          <template slot="title">Data Preparation</template>
          <el-menu-item-group>
            <el-menu-item index="/deepLearning/uploadDataset">Upload Dataset</el-menu-item>
            <el-menu-item index="/deepLearning/uploadKnowledgeGraph">Upload Knowledge Graph</el-menu-item>
          </el-menu-item-group>
        </el-submenu>
        <el-menu-item index="/deepLearning/modelEvaluation">Model Evaluation</el-menu-item>
        <el-menu-item index="/deepLearning/autoSelection">Auto Selection</el-menu-item>
      </el-menu>
    </el-scrollbar>
  </el-aside>
</template>

<script>
    export default {
        name: "DeepLearningMenu",
        data() {
            return {
                category: []
            };
        },
        methods: {
        },
        created() {
        }
    }
</script>

<style scoped>
  .el-aside {
    position: fixed;
    top: 80px;
    bottom: 0;
    background-color: rgb(238, 241, 246);
    z-index: 999;
  }

  .el-scrollbar {
    height: 100%;
  }
</style>
