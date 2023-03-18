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
        const { clusters } = storeToRefs(store);
        const { color } = storeToRefs(store);
        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
            size,
            margin,
            methods,
            numClusters,
            clusters,
            color

        }
    },
    data() {
        return {
            selectedDimensionReduction: 3,
            reductionType: 't-SNE',
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
            

            const centerX = (parentRect.width / 2) - this.margin.right;
                const centerY = parentRect.height / 2;
            let colorScale = this.color;
             // Add legend
             let legend = svg.append('g')
                .attr('id', 'legend')



            // Add a circle and text element for each cluster in the legend
            legend.selectAll('circle')
                .data(this.clusters)
                .join('circle')
                .attr('cx', 0)
                .attr('cy', (d, i) => i * 25)
                .attr('r', 7)
                .attr('transform', `translate(
                ${centerX - 10}, ${centerY - 150})`)
                .style('fill', (d, i) => colorScale(i.toString()));
                
            legend.selectAll('text')
                .data(this.clusters)
                .join('text')
                .attr('x', 15)
                .attr('y', (d, i) => i * 25 + 5)
                .text(d => `${d}`)
                .attr('transform', `translate(
                ${centerX - 10}, ${ centerY - 150})`)
                .style('font-size', '12px')
                .style('font-weight', '500');



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


                const sliderGroup = svg
                    .append('g')
                    .attr('transform', `translate(${centerX}, ${centerY - 10})`)
                    .call(slider);

            svg.append('g').append('text') // adding the text
                .attr('transform', `translate(${centerX - 10}, ${centerY - this.margin.top - 10})`)
                .style('text-anchor', 'right')
                .style('font-weight', 'bold')
                .style('font-size', '12px') 
                .text('Clusters') // text content
            
            // const reductionType = this.reductionType;
            // MAKE BUTTON
            d3.select("#dimensionButton")
                .selectAll('myOptions')
                .data(this.methods)
                .enter()
                .append('option')
                .text(function (d) { return d; }) // text showed in the menu
                .attr("value", function (d) { 
                    // this.reductionType = d.valueOf();
                    // d3.select('.dimension-button').attr('v-model', this.reductionType)
                    
                    return d; 
                }) // corresponding value returned by the button
                .attr('selected', function(d) {
                    console.log('selected')
                    if (d.valueOf() === this.reductionType) {
                        return d.valueOf()
                    }
                })
                .on("change", function (d) {
                    console.log('d change: ', d.valueOf())
                    // if (d.valueOf() === this.reductionType) {
                    //     return d.valueOf()
                    // }
                    // console.log('reductionType: ', d.valueOf());
                    // this.reductionType = d.valueOf();
                    // d3.select('.dimension-button').attr('v-model', d.valueOf())
                })

        },
        rerender() {
            d3.selectAll('.scatter-tools-container').selectAll('*').remove() // Clean all the elements in the chart
            d3.select('.dimension-button').selectAll('*').remove()
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
            console.log('storenum: ', this.reductionType)
            // Trying to update by fetching new data but it's not working yet...
            this.store.fetchData({numClusters: newNumClusters},{reductionType: this.reductionType});
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
        },
        reductionType: {
            async handler(newreductionType) {
                console.log('reductionType here: ', newreductionType);
                // for when the user chooses a new num clusters
                // data to pass into backend
                // const data = {
                //     clusters: this.numClusters,
                //     reductionType: newreductionType,
                // }
                // this.reductionType = newreductionType;
                this.store.fetchData({numClusters: this.numClusters}, {reductionType: newreductionType});
                this.rerender();
                // now what??
            },
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
    <!-- <select id="dimensionButton" 
            label="DimensionReduction"
            
            class="dimension-button">
    </select> -->
    <v-select :items="['t-SNE', 'NMF', 'PCA']"
                                label="Reduction" density="compact" v-model="reductionType"></v-select>
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