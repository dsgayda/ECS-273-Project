<script lang="ts">
import Notes from './components/Notes.vue'
import Example from './components/Example.vue'
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';
import PolicyScatterplot from './components/PolicyScatterplot.vue';
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

            <!-- Top-left box -->
            <v-row style="height: 50%; border: 1px solid #BBBBBB;">
              <v-col cols="12" style=" overflow-y: auto; ">
                <MapViz></MapViz>
              </v-col>
            </v-row>

            <!-- Bottom-left box -->
            <v-row style="height: 50%; ">
              <!-- Bottom-left box -->
              <v-col cols="12" style="border: 1px solid #BBBBBB; overflow-y: auto;">
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
                
                  Right column of top-right box
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
</style>