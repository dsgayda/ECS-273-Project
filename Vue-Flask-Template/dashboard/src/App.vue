<script lang="ts">
import Notes from './components/Notes.vue'
import Example from './components/Example.vue'
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';
import PolicyScatterplot from './components/PolicyScatterplot.vue';

export default {
  components: {
    Notes,
    Example,
    ExampleWithLegend,
    ExampleWithInteractions,
    PolicyScatterplot
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>

    <v-row no-gutters>

      <!-- Left column -->
      <v-col cols="6">

        <!-- Top-left box -->
        <v-row no-gutters style="height: 50%; padding-right: 5px; padding-bottom: 5px;">
          <v-col cols="12" style="background-color: #FFD700; padding: 10px;">
            Top-left box
            <PolicyScatterplot></PolicyScatterplot>
          </v-col>
        </v-row>

        <!-- Bottom-left box -->
        <v-row no-gutters style="height: 50%; padding-right: 5px; padding-top: 5px; padding-bottom: 5px;">

          <!-- Left column of bottom-left box -->
          <v-col cols="8" style="height: 100%; padding: 0px;">

            <!-- Top row of left column of bottom-left box -->
            <v-row no-gutters style="height: 80%; padding-right: 5px; padding-bottom: 5px; padding-left: 5px;">
              <v-col cols="12" style="background-color: #FFA07A; padding: 10px;">
                Top row of left column of bottom-left box
              </v-col>
            </v-row>

            <!-- Bottom row of left column of bottom-left box -->
            <v-row no-gutters style="height: 20%; padding-right: 5px; padding-left: 5px;">
              <v-col cols="12" style="background-color: #87CEFA; height: 100%; overflow-y: auto; padding: 10px;">
                Bottom row of left column of bottom-left box
                <br />
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam at sagittis justo. Aliquam blandit nibh
                non dolor placerat viverra. Aenean euismod erat quis sem elementum pharetra. Donec molestie a nulla ut
                bibendum. Proin sit amet aliquet eros, ut pretium lorem. Fusce id ipsum at ante elementum pulvinar. In hac
                habitasse platea dictumst. Duis accumsan elit enim, vel pharetra magna finibus quis. Maecenas vel volutpat
                libero. Donec ultrices lorem quis nisl gravida, sed scelerisque enim euismod.
              </v-col>
            </v-row>

          </v-col>

          <!-- Right column of bottom-left box -->
          <v-col cols="4" style="background-color: #7B68EE; height: 100%; padding: 10px;">
            <v-row no-gutters>
              <v-col cols="12">
                Right column of bottom-left box
              </v-col>
            </v-row>
          </v-col>

        </v-row>

      </v-col>

      <!-- Right column -->
      <v-col cols="6">

        <!-- Top-right box -->
        <v-row no-gutters style="height: 50%; padding-left: 5px; padding-bottom: 5px;">
          <!-- Left column of top-right box -->
          <v-col cols="8" style="background-color: #00FA9A; height: 100%; padding-left: 5px; padding: 10px;">
            <v-row no-gutters>
              <v-col cols="12">
                Left column of top-right box
              </v-col>
            </v-row>
          </v-col>

          <!-- Right column of top-right box -->
          <v-col cols="4" style="background-color: #DC143C; height: 100%; padding: 10px;">
            <v-row no-gutters>
              <v-col cols="12">
                Right column of top-right box
              </v-col>
            </v-row>
          </v-col>
        </v-row>

        <!-- Bottom-right box -->
        <v-row no-gutters style="height: 50%; padding-left: 5px; padding-top: 5px;">
          <v-col cols="12" style="background-color: #FFA07A; padding: 10px;">
            Bottom-right box
          </v-col>
        </v-row>

      </v-col>

    </v-row>
  </v-container>
</template>










    <style scoped>
      #main-container {
      height: 100%;
    }
  </style>