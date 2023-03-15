<script lang="ts">
import * as d3 from "d3";
import {sliderVertical} from 'd3-simple-slider';
import { isEmpty, debounce } from 'lodash';

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
// For importing a store. See how it's set up in ./dashboard/stores/ and ./dashboard/main.ts
import { mapState, storeToRefs } from 'pinia';
import { useDataStore } from '../stores/dataStore';

export default {
    setup() { // Composition API syntax
        const store = useDataStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);

        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            // resize,
            size,
            margin
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
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let sc = this.$refs.scatterToolsContainer as HTMLElement;
            let svg = d3.select(sc)
                .append('svg')
                .attr('id', 'scatter-tools-svg')
                .attr('width', '100%')
                .attr('height', '100%')

            // get the size of the parent container
            const parentRect = { width: sc.clientWidth, height: sc.clientHeight };
        
            // update the viewBox attribute based on the size of the parent container
            svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height }`);

            // trying to copy https://github.com/johnwalley/d3-simple-slider
            var slider = sliderVertical()
                .min(2)
                .max(6)
                .attr('width', this.size.width/20)
                ;
            
            const sliderContainer = d3.select(sc)
                .append('svg')
                .attr('width', this.size.width)
                .attr('height', this.size.height)
                .append('g')
                .attr('transform', `translate(${30}, ${30})`)
            
            sliderContainer.call(slider)
        },
        rerender() {
            d3.selectAll('.scatter-chart-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        }

    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
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
    <div class="scatter-tools-container d-flex" ref="scatterToolsContainer">
    </div>
</template>

<style scoped>
.scatter-tools-container {
    height: calc(100%);
}
</style>