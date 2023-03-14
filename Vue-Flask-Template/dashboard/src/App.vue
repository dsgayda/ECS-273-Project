<script lang="ts">
import Notes from './components/Notes.vue'
import Example from './components/Example.vue'
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';
import PolicyScatterplot from './components/PolicyScatterplot.vue';
import PolicyScatterplotTools from './components/PolicyScatterplotTools.vue';
import GroupedBarChart from './components/GroupedBarChart.vue';
import MapViz from './components/MapViz.vue';


export default {
  components: {
    Notes,
    Example,
    ExampleWithLegend,
    ExampleWithInteractions,
    PolicyScatterplot,
    PolicyScatterplotTools,
    GroupedBarChart,
    MapViz
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
              <v-col cols="12" style="border: 1px solid #BBBBBB;">
                Bottom-left box
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at sagittis justo. Aliquam blandit
                nibh non dolor placerat viverra. Aenean euismod erat quis sem elementum pharetra. Donec molestie a
                nulla ut bibendum. Proin sit amet aliquet eros, ut pretium lorem. Fusce id ipsum at ante elementum
                pulvinar. In hac habitasse platea dictumst. Duis accumsan elit enim, vel pharetra magna finibus quis.
                Maecenas vel volutpat libero. Donec ultrices lorem quis nisl gravida, sed scelerisque enim euismod.
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
</style>