<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce } from 'lodash';
import * as d3Slider from 'd3-simple-slider';

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
// For importing a store. See how it's set up in ./dashboard/stores/ and ./dashboard/main.ts
import { mapState, storeToRefs } from 'pinia';
import { ref } from 'vue';
import { useDataStore } from '../stores/dataStore';

export default {
    setup() { // Composition API syntax
        const store = useDataStore();
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);

        const {methods} = storeToRefs(store);
        const { numClusters } = storeToRefs(store);
        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
            size,
            margin,
            methods,
            numClusters,
        }
    },
    data() {
        return {
            selectedDimensionReduction: 3,
        }
    },
    computed: {
        ...mapState(useDataStore, []) // Traditional way to map the store state to the local state
    },
    created() {
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterToolsContainer as HTMLElement
            if (!target) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let sc = this.$refs.scatterToolsContainer as HTMLElement;

            let svg = d3.select('.scatter-tools-container')
                .append('svg')
                .attr('id', 'scatter-tools-svg')
                .attr('width', '100%')
                .attr('height', '100%')

            // get the size of the parent container
            const parentRect = { width: sc.clientWidth, height: sc.clientHeight };
            
            // MAKE SLIDER
            const slider = d3Slider
                .sliderRight()
                .min(2)
                .max(6)
                .width(parentRect.height) // Adjust the height based on the parent container
                .ticks(5)
                .tickFormat(d3.format(',.0f'))
                .step(1)
                .default(this.numClusters)
                .fill('#66c2a5')
                .on('end', val => {
                    this.numClusters = val;
                    console.log('Slider value:', this.numClusters);
                    d3.select('.track-fill') // Select the handle element
                        
                        .attr('y1', '108')
                })
                .on('start', val => {
                    d3.select('.track-fill') // Select the handle element
                        .attr('y1', '108');

                })
                .on('drag', val => {
                    d3.select('.track-fill') // Select the handle element
                        .attr('y1', '108');

                })
                ;


                const centerX = (parentRect.width / 2) - this.margin.right;
                const centerY = parentRect.height - parentRect.height + this.margin.top + this.margin.bottom * 2;
                const sliderGroup = svg
                    .append('g')
                    .attr('transform', `translate(${centerX}, ${centerY})`)
                    .call(slider);

            svg.append('g').append('text') // adding the text
                .attr('transform', `translate(${centerX}, ${centerY - this.margin.top})`)
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '12px') 
                .text('Clusters') // text content
            
            // MAKE BUTTON
            d3.select("#dimensionButton")
                .selectAll('myOptions')
                .data(this.methods)
                .enter()
                .append('option')
                .text(function (d) { return d; }) // text showed in the menu
                .attr("value", function (d) { return d; }) // corresponding value returned by the button


        },
        rerender() {
            d3.selectAll('.scatter-tools-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        }

    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.numClusters'(newNumClusters) {
            console.log('new num!', newNumClusters);
            // Trying to update by fetching new data but it's not working yet...
            // this.store.fetchData(newNumClusters);
            this.rerender();
        },
        selectedDimensionReduction: {
            async handler(newDimensionReductionMethod) {
                // for when the user chooses a new num clusters
                // data to pass into backend
                const data = {
                    clusters: this.numClusters,
                    dimension_reduction: newDimensionReductionMethod,
                }
                // now what??
            },
            immediate: true
        }
    },
    // The following are general setup for resize events.
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.onResize)
    }
}
</script>

<!-- "ref" registers a reference to the HTML element so that we can access it via the reference in Vue.  -->
<!-- We use flex to arrange the layout-->
<template>
    <select id="dimensionButton" 
            label="DimensionReduction"
            v-model="selectedDimensionReduction">
    </select>
    <div class="scatter-tools-container d-flex" ref="scatterToolsContainer"></div>
</template>

<style scoped>
.slider-group {
    transform-origin: top left;
    transform: rotate(90deg) translateY(-100%);
}

.scatter-tools-container {
    height: calc(100%);
}

#dimensionButton {
  background-color: #66c2a5;
  color: white;
  border-radius: 10px;
  padding: 5px;
}
</style>