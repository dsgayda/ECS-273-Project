<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin, PolicyPoint } from '../types';
// A "extends" B means A inherits the properties and methods from B.
interface ScatterPoint extends PolicyPoint { 
    cluster: string;
}

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
// For importing a store. See how it's set up in ./dashboard/stores/ and ./dashboard/main.ts
import { mapState, storeToRefs } from 'pinia'; 
import { usePolicyScatterplot } from '../stores/policyClusterStore';

export default {
    setup() { // Composition API syntax
        const store = usePolicyScatterplot()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { points } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);

        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
            points,
            size,
            margin
        }
    },
    computed: {
        ...mapState(usePolicyScatterplot, []) // Traditional way to map the store state to the local state
    },
    created() {
        this.store.fetchPolicyScatterplot();
        this.store.fetchGroupedBarChart();
        console.log('after fetch data: ', this.store.points);
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            let chartContainer = d3.select('#scatter-svg')

            // we need compute the [min, max] from the data values of the attributes that will be used to represent x- and y-axis.
            let xExtents = d3.extent(this.points.map((d: ScatterPoint) => d.dimension1 as number)) as [number, number]
            let yExtents = d3.extent(this.points.map((d: ScatterPoint) => d.dimension2 as number)) as [number, number]

            // We need a way to map our data to where it should be rendered within the svg (in pixels) based on the data value, 
            //      so the extents above help us define the limits.
            // Scales are just like mapping functions y = f(x), where x refers to domain, y refers to range in this case.
            // We have the margin here just to leave some space
            // In viewport (our screen), the leftmost side always refer to 0 in the horizontal coordinates in pixels (x). 
            let xScale = d3.scaleLinear()
                .range([this.margin.left, this.size.width - this.margin.right]) // left side to the right side on the screen
                .domain(xExtents)

            // In viewport (our screen), the topmost side always refer to 0 in the vertical coordinates in pixels (y). 
            let yScale = d3.scaleLinear()
                .range([this.size.height - this.margin.bottom, this.margin.top]) //bottom side to the top side on the screen
                .domain(yExtents)
            // There are other scales such as scaleOrdinal and scaleBand, 
                // whichever is appropriate depends on the data types and the kind of visualizations you're creating.

            /*
            // This following part visualizes the axes. We did not do it because the x- and y- axis in DR projections usually mean nothing for interpretation.
            // Check out https://observablehq.com/@d3/margin-convention?collection=@d3/d3-axis
            // Note that for axis labels, this is just a demostration, their positions are not perfect.
            const xAxis = chartContainer.append('g')
                .attr('transform', `translate(0, ${this.size.height - this.margin.bottom})`)
                .call(d3.axisBottom(xScale))

            const yAxis = chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, 0)`)
                .call(d3.axisLeft(yScale))

            const yLabel = chartContainer.append('g')
                .attr('transform', `translate(${this.margin.left}, ${this.size.height / 2 + this.margin.top}) rotate(-90)`)
                .append('text')
                .text('PC2')

            const xLabel = chartContainer.append('g')
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height - this.margin.top})`)
                .append('text')
                .text('PC1')
            */

            // Similar to above but now we are creating the color scale with scaleOrdinal.
            // let clusters: string[] = this.clusters.map((cluster: string, idx: number) => String(idx))
            // let clusters: string[] = this.clusters.map(())
            let colorScale = d3.scaleOrdinal().domain(["cluster1", "cluster2", "cluster3"]).range(d3.schemeTableau10) // d3.schemeTableau10: string[]

            // "g" is group element that does nothing but helps avoid DOM looking like a mess
            // We iterate through each <ScatterPoint> element in the array, create a circle for each and indicate the coordinates, the circle size, the color, and the opacity.
            const points = chartContainer.append('g')
                .selectAll('circle') //adding circles
                .data<ScatterPoint>(this.points) // TypeScript expression
                .join('circle')
                .attr('cx', (d: ScatterPoint) => xScale(d.dimension1))
                .attr('cy', (d: ScatterPoint) => yScale(d.dimension2))
                .attr('r', 5)
                .style('fill', (d: ScatterPoint) => colorScale(String(d.cluster)) as string)
                .style('opacity', .7)

            // For transform, check out https://www.tutorialspoint.com/d3js/d3js_svg_transformation.htm, but essentially we are adjusting the positions of the selected elements.
            const title = chartContainer.append('g')
                .append('text') // adding the text
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height - this.margin.top})`)
                .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text('Policy PCA Projection') // text content
        },
        rerender() {
            d3.selectAll('#scatter-svg').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        }

    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.points'(newPoints) { // when data changes
            if (!isEmpty(newPoints)) {
                console.log('newpoints found: ', newPoints)

                 
                //Call and set the other api based on points, with POST method
                // set data for bar chart based on results from post
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
    <div class="chart-container d-flex" ref="scatterContainer">
        <svg id="scatter-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>