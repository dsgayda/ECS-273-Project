<script lang="ts">
import Notes from './components/Notes.vue'
import Example from './components/Example.vue'
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';
import PolicyScatterplot from './components/PolicyScatterplot.vue';
import PolicyScatterplotTools from './components/PolicyScatterplotTools.vue';
import GroupedBarChart from './components/GroupedBarChart.vue';
import MapViz from './components/MapViz.vue';
import Table from './components/Table.vue';


export default {
  components: {
    Notes,
    Example,
    ExampleWithLegend,
    ExampleWithInteractions,
    PolicyScatterplot,
    PolicyScatterplotTools,
    GroupedBarChart,
    MapViz,
    Table
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <div class="scrollable-container">
    <div class="scrollable-content">
      <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
        <v-row>

          <!-- Left column -->
          <v-col cols="6">
            <!-- Left-Top Box -->
            <v-row style="height: 4%; border-top: 1px solid #BBBBBB;  border-left: 1px solid #BBBBBB; border-right: 1px solid #BBBBBB;" class="middle-box">
              <v-col cols="12" style=" overflow-y: auto; ">
                <h6 style="word-wrap: break-word;">Map (below), has state size based on the number of gun control policies implemented (0-135), background color based on cluster, and interior
                  color based on the amount of gun violence per capita.</h6>
              </v-col>
            </v-row>
            <!-- Top-left box -->
            <v-row style="height: 46%; border: 1px solid #BBBBBB; border-top-color: #FFFFFF;">

              <v-col cols="12" style=" overflow-y: auto; ">
                <MapViz></MapViz>
              </v-col>
            </v-row>
            <!-- Left-Middle Box -->
            <v-row style="height: 4%; border-left: 1px solid #BBBBBB; border-right: 1px solid #BBBBBB;" class="middle-box">
              <v-col cols="12" style=" overflow-y: auto; ">
                <h6 style="word-wrap: break-word;">Table (below) provides policy types, the correlation between that policy and an incidence types, and avg. percentage of policies
                  implemented in that category for each cluster. </h6>
              </v-col>
            </v-row>

            <!-- Bottom-left box -->
            <v-row style="height: 46%; ">
              <!-- Bottom-left box -->
              <v-col cols="12" style="border: 1px solid #BBBBBB; border-top-color: #FFFFFF; overflow-y: auto;">
                <Table></Table>
              </v-col>
            </v-row>
          </v-col>

          <!-- Right column -->
          <v-col cols="6">

            <!-- Top-right box -->
            <v-row style="height: 50%; border: 1px solid #BBBBBB;">
              <!-- Left column of top-right box -->
              <v-col cols="10" style="">
                <PolicyScatterplot></PolicyScatterplot>
              </v-col>

              <!-- Right column of top-right box -->
              <v-col cols="2" style="border: 1px solid #BBBBBB; overflow-y: auto;">
                <PolicyScatterplotTools></PolicyScatterplotTools>
              </v-col>
            </v-row>

            <!-- Bottom-right box -->
            <v-row style="height: 50%;">
              <v-col cols="10" style=" border: 1px solid #BBBBBB;">
                <GroupedBarChart></GroupedBarChart>
              </v-col>

              <!-- Right column of bottom-right box -->
              <v-col cols="2" style="border: 1px solid #BBBBBB; overflow-y: auto;">
                Right column of bottom-right box
              </v-col>
            </v-row>

          </v-col>

        </v-row>
      </v-container>

    </div>
  </div>
</template>


<style scoped>
#main-container {
  height: 100%;
}

.scrollable-container {
  overflow-x: auto;
  height: 100%;
}

.scrollable-content {
  min-width: 1150px;

  min-height: 500px;
  /* Set the width of the content to be larger than the container to enable horizontal scrolling */
  height: 100%;
}

.middle-box {
  font-size: 1rem;
  /* Adjust the font size to fit within the container */
  line-height: 1rem;
  /* Control the space between lines of text */
  /* padding: 0rem; */
  /* Add padding inside the container */

  white-space: nowrap;
  /* Prevent text from wrapping to the next line */
  overflow: hidden;
  /* Hide any overflowing text */
  text-overflow: ellipsis;
  /* Add ellipsis (...) to the end of the overflowing text */
}</style>