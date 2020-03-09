<template>
  <div>
    <el-container>
      <NavigationBar/>
      <el-container>
        <el-main>
          <div class="btn-div">
            <el-button @click="initGraph">Reset</el-button>
            <el-button type="primary" @click="downloadKg">Download</el-button>
          </div>
          <div class="parent-div">
            <div class="svg-div" ref="svgDiv">
              <svg width="100%" height="100%">
              </svg>
            </div>
          </div>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
    import NavigationBar from "../components/NavigationBar";

    import * as d3 from 'd3';
    // import d3tooltip from 'd3-tooltip';

    import GraphData from "../assets/GraphData";

    export default {
        name: "knowledgeGraph",
        components: {
            NavigationBar
        },
        data() {
            return {
            };
        },
        methods: {
            initGraph() {
            },
            downloadKg() {
            }
        },
        mounted() {
            // 获取 svg 元素所在块元素（svgDiv）的长度和高度，用来确定画布中心点
            let width = this.$refs.svgDiv.offsetWidth;
            let height = this.$refs.svgDiv.offsetHeight;

            // let names = ['Films', 'Characters', 'Planets', 'Starships', 'Vehicles', 'Species'];
            // 设置不同组的节点颜色
            let colors = ['#6ca46c', '#4e88af', '#ca635f', '#d2907c', '#d6744d', '#ded295', '#b4c6e7', '#cdb4e6'];
            // 获取图谱数据
            let graph = GraphData.graph();
            // console.log(graph); //(test)

            // 设置节点半径
            for (let i = 0; i < graph.nodes.length; i++) {
                let nd = graph.nodes[i];
                nd.r = nd.id.length * 1.6 + 20;
                // nd.r = nd.id.length * 3; //(test)
            }

            // 创建一个力学模拟器（force 力学图）
            let simulation = d3.forceSimulation()
                .force("link", d3.forceLink().id(function (d) {
                    return d.id;
                }))
                // 设置万有引力，设置引力强度
                .force("charge", d3.forceManyBody().strength(100))
                // 设置居中力，中心点为画布中心点
                .force("center", d3.forceCenter(width / 2, height / 2))
                // 设置碰撞作用力，指定一个 radius 区域来防止节点重叠；设置碰撞力强度，范围是[0,1]，默认为0.7；设置迭代次数，默认为1（迭代次数越多最终的布局效果越好，但是计算复杂度更高）
                .force("collide", d3.forceCollide(80).strength(0.2).iterations(5))
                // .force("collide", d3.forceCollide(100).strength(0.2).iterations(5)) //(test)
                // // 设置 alpha 系数，在计时器的每一帧中，仿真的 alpha 系数会不断削减，当 alpha 到达一个系数时，仿真将会停止，也就是 alpha 的目标系数 alphaTarget，该值区间为[0,1]，默认为0，控制力学模拟衰减率区间为[0-1]，设为0则不停止，默认0.0228，直到0.001
                // .alphaDecay(0.0228)
                // // 设置监听事件，例如监听 tick 滴答事件
                // .on("tick", ()=>this.ticked())
            ;

            // 获取 svg 元素
            let svg = d3.select("svg");
            // 设置鼠标滚轮缩放
            svg.call(d3.zoom().on("zoom", function () {
                svg.selectAll("g").attr("transform", d3.event.transform);
            }));
            // 禁止双击缩放
            svg.on("dblclick.zoom", null);

            // 添加 line
            let link = svg.append("g").attr("class", "links")
                .selectAll("line").data(graph.links).enter().append("line")
                .attr("stroke-width", 1)
                .style("stroke", "rgba(240, 240, 240, 0.8)");

            // 添加 circle
            let node = svg.append("g").attr("class", "nodes")
                .selectAll("circle").data(graph.nodes).enter().append("circle")
                .attr("r", function (d) {
                    return d.r;
                })
                .attr("fill", function (d) {
                    return colors[d.group];
                    // return 'rgb(140, 197, 255)';
                })
                .style("stroke", "#fff")
                .style("stroke-width", "2px")
                .style("cursor", "pointer")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            node.append("title").text(d=>{return d.id});

            // 添加 text
            let text = svg.append("g").attr("class", "texts")
                .selectAll("text").data(graph.nodes).enter().append("text")
                .text(d=>{return d.id})
                .attr("dy", 4)
                // 设置文本对齐方式为居中（start | middle | end）
                .attr("text-anchor", "middle")
                .attr("fill", "white")
                // .style("display", "none") //(test)
                // .style("display", "inline-block")
                // .style("max-width", "15px")
                // .style("white-space", "nowrap")
                // .style("overflow", "hidden")
                // .style("text-overflow", "ellipsis")
                // .style("vertical-align", "middle")
                .style("cursor", "pointer")
                .call(d3.drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended));

            simulation.nodes(graph.nodes).on("tick", ticked);
            simulation.force("link").links(graph.links);

            //ticked()函数确定link线的起始点x、y坐标 node确定中心点 文本通过translate平移变化
            function ticked() {
                link
                    .attr("x1", function(d) {return d.source.x;})
                    .attr("y1", function(d) {return d.source.y;})
                    .attr("x2", function(d) {return d.target.x;})
                    .attr("y2", function(d) {return d.target.y;});
                node
                    .attr("cx", function(d) {return d.x;})
                    .attr("cy", function(d) {return d.y;});
                text
                    .attr("x", function(d) { return d.x; })
                    .attr("y", function(d) { return d.y; });
            }

            function dragstarted(d) {
                if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
                //dragging = true;
            }

            //拖动进行中
            function dragged(d) {
                d.fx = d3.event.x;
                d.fy = d3.event.y;
            }

            //拖动结束
            function dragended(d) {
                if (!d3.event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
                //dragging = false;
            }
        }
    }
</script>

<style scoped>
  .el-main {
    position: fixed;
    top: 80px;
    left: 30px;
    right: 30px;
    bottom: 0;
    margin: 20px;
    padding: 10px;
  }

  .btn-div {
    float: right;
  }

  .parent-div {
    position: fixed;
    top: 160px;
    left: 30px;
    right: 30px;
    bottom: 0;
    margin: 20px;
    border: 3px solid #272b30;
    border-radius: 8px;
    padding: 10px;
  }

  .svg-div {
    width: 100%;
    height: 100%;
    /*background-color: cadetblue;*/
  }

  svg {
    background-color: #272b30;
  }
</style>
