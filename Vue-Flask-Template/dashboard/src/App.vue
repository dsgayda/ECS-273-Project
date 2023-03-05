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
      <v-row no-gutters>
        
        <v-col cols="12">
          Nested Row 1, Column 1
          <PolicyScatterplot></PolicyScatterplot>
        </v-col>
         
        <v-col cols="12" style="background-color: red;">
          <!-- <v-row no-gutters style="background-color: grey;"> -->
            <v-col cols="6" style="background-color: blue;">
              
              </v-col>
              <v-col cols="6" style="background-color: green;">
              
            </v-col>
          <!-- </v-row> -->

        </v-col>
      </v-row>

      <!-- <ExampleWithInteractions/> -->
      <v-row no-gutters style="background-color: blue;">
        <v-col cols="8">Nested Row 1, Column 9</v-col>

        <v-col cols="4" style="background-color: purple;">Nested Row 1, Column 1</v-col>
        <v-col cols="12" style="background-color: orange;">Nested Row 1, Column 2</v-col>
      </v-row>
    </v-row>
    <!-- <v-row no-gutters>
        <v-col>
          <Notes msg="This message is showcasing how to pass down the props"/>
        </v-col>
      </v-row> -->
  </v-container>
</template>

<style scoped>
#main-container {
  height: 100%;
}
</style>
