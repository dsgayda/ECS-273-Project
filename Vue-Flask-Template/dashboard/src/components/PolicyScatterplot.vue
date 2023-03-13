<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin, PolicyPoint } from '../types';
// A "extends" B means A inherits the properties and methods from B.

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
        const { points } = storeToRefs(store);
        const { clusters } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);
        const { color }    = storeToRefs(store);

        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            // resize,
            color,
            points,
            clusters,
            size,
            margin
        }
    },
    computed: {
        ...mapState(useDataStore, []) // Traditional way to map the store state to the local state
    },
    created() {
        this.store.fetchData();
        // this.store.initializeColorScale();
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            console.log('this.size: ', this.size);
            let sc = this.$refs.scatterContainer as HTMLElement;
            let svg = d3.select(sc)
                .append('svg')
                .attr('id', 'scatter-svg')
                .attr('width', '100%')
                .attr('height', '100%')
                // .style('display', 'block');
            // // get the size of the parent container
            // const parentRect = sc.getBoundingClientRect();
            const parentRect = { width: sc.clientWidth, height: sc.clientHeight };
        
            // update the viewBox attribute based on the size of the parent container
            svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height }`);


            let chartContainer = svg;

            chartContainer.append('rect')
                .attr('width', parentRect.width)
                .attr('height', parentRect.height)
                .attr('fill', 'lightgray')
                .attr('opacity', 0.3)
            .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)


            // we need compute the [min, max] from the data values of the attributes that will be used to represent x- and y-axis.
            let xExtents = d3.extent(this.points.map((d: PolicyPoint) => d.dimension1 as number)) as [number, number]
            let yExtents = d3.extent(this.points.map((d: PolicyPoint) => d.dimension2 as number)) as [number, number]

            // We need a way to map our data to where it should be rendered within the svg (in pixels) based on the data value, 
            //      so the extents above help us define the limits.
            // Scales are just like mapping functions y = f(x), where x refers to domain, y refers to range in this case.
            // We have the margin here just to leave some space
            // In viewport (our screen), the leftmost side always refer to 0 in the horizontal coordinates in pixels (x). 
            let xScale = d3.scaleLinear()
                .range([this.margin.left, parentRect.width - (this.margin.right + this.margin.left)]) // left side to the right side on the screen
                .domain(xExtents)

            // In viewport (our screen), the topmost side always refer to 0 in the vertical coordinates in pixels (y). 
            let yScale = d3.scaleLinear()
                .range([parentRect.height - (this.margin.bottom + this.margin.top), this.margin.top]) //bottom side to the top side on the screen
                .domain(yExtents)
           
            let colorScale = this.color; 

            // Add a tooltip
            const tooltip = d3.select("svg").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);
           
            // We iterate through each <PolicyPoint> element in the array, create a circle for each and indicate the coordinates, the circle size, the color, and the opacity.
            const points = svg.selectAll('circle') // select all circles
                .data<ScatterPoint>(this.points) // bind data
                .join('circle') // join data with elements
                .attr('cx', (d: PolicyPoint) => xScale(d.dimension1))
                .attr('cy', (d: PolicyPoint) => yScale(d.dimension2))
                .attr('r', 5)
                .style('fill', (d: PolicyPoint) => {
                    return colorScale((d.cluster).toString())
                })
                .style('opacity', .25)
                .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)
                .on('mouseover', (event, d) => {
                    console.log('mouseover event', event, d);
                    tooltip.transition()
                        .duration(200)
                        .style('opacity', .9);
                    tooltip.html(`Details: ${d.state}, ${d.year}`)
                        .style('left', (event.pageX) + 'px')
                        .style('top', (event.pageY - 28) + 'px');
                })
                .on('mouseout', (d) => {
                    tooltip.transition()
                        .duration(500)
                        .style('opacity', 0);
                });

            
            // Add mouseover to highlight bars of same color as bar under mouse
            // TODO: Do this for each visualization
            points.on("mouseover", function(d) {
                    const color = d3.select(this).style("fill");
                    points.filter(function(d) {
                        return d3.select(this).style("fill") === color;
                    }).style("opacity", 1);
                })
                .on("mouseout", function() {
                    points.style("opacity", 0.25);
                });

            const title = chartContainer.append('g').append('text') // adding the text
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height})`)
                .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .text('Clustering State Policies') // text content
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
        'store.points'(newPoints) { // when data changes
            if (!isEmpty(newPoints)) {
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
    <div class="scatter-chart-container d-flex" ref="scatterContainer">
    </div>
</template>

<style scoped>
.scatter-chart-container {
    height: calc(100%);
}
</style>