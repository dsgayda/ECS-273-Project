<script lang="ts">
import Notes from './components/Notes.vue'
import Example from './components/Example.vue'
import ExampleWithLegend from './components/ExampleWithLegend.vue';
import ExampleWithInteractions from './components/ExampleWithInteractions.vue';

export default {
  components: {
    Notes,
    Example,
    ExampleWithLegend,
    ExampleWithInteractions
  }
}
</script>

<!--This is using the grid component from Vuetify to do layout design-->
<template>
  <v-container id="main-container" class="d-flex flex-column flex-nowrap" fluid>
    <v-row no-gutters style="background-color: pink;">
      <v-row style="background-color: grey;">
        <v-col cols="12" >Nested Row 1, Column 1</v-col>
        <v-col cols="12" style="background-color: red;">Nested Row 1, Column 2</v-col>
      </v-row>
        <!-- <ExampleWithInteractions/> -->
      <v-col cols="5" style="background-color: green;">
        <!-- <ExampleWithLegend/> -->
      </v-col>
    </v-row>
    <!-- <v-row no-gutters>
      <v-col>
        <Notes msg="This message is showcasing how to pass down the props"/>
      </v-col>
    </v-row> -->
  </v-container>
</template>

<style scoped>
#main-container{
  height: 100%;
}
</style>
