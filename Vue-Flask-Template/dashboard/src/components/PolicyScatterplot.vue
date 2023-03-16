<script lang="ts">
import * as d3 from "d3";
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
        const { points } = storeToRefs(store);
        const { clusters } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);
        const { color } = storeToRefs(store);
        const { numClusters } = storeToRefs(store);

        return {
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            // resize,
            color,
            points,
            clusters,
            size,
            margin,
            numClusters
        }
    },
    computed: {
        ...mapState(useDataStore, []) // Traditional way to map the store state to the local state
    },
    created() {
        this.store.fetchData(this.numClusters);
        // this.store.initializeColorScale();
    },
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.scatterContainer as HTMLElement
            if (!target) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            // select the svg tag so that we can insert(render) elements, i.e., draw the chart, within it.
            console.log('this.numClusters: ', this.numClusters)
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
            svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height}`);


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
            let tooltip = d3
                .select('body')
                .append('div')
                .attr('class', 'd3-tooltip')
                .style('position', 'fixed')
                .style('z-index', '10')
                .style('padding', '1px')
                .style('background', 'rgba(0,0,0,0.6)')
                .style('border-radius', '4px')
                .style('color', '#fff')
                .text('a simple tooltip')
                .style('visibility', 'hidden');

            // We iterate through each <PolicyPoint> element in the array, create a circle for each and indicate the coordinates, the circle size, the color, and the opacity.
            const points = svg.selectAll('circle') // select all circles
                .data<ScatterPoint>(this.points) // bind data
                .join('circle') // join data with elements
                .attr("id", d => {
                    // console.log(`cluster${parseInt(d.cluster) + 1}`)
                    return `cluster${parseInt(d.cluster) + 1}`;
                })
                .attr('cx', (d: PolicyPoint) => xScale(d.dimension1))
                .attr('cy', (d: PolicyPoint) => yScale(d.dimension2))
                .attr('r', 5)
                .style('fill', (d: PolicyPoint) => {
                    return colorScale((d.cluster).toString())
                })
                .style('opacity', .5)
                .attr('transform', `translate(${this.margin.left - 20}, ${this.margin.top})`)
               

            // Add mouseover to highlight cluster of same color as point under mouse            
            points.on("mouseover", function (e, d) {
                const bars = d3.selectAll("rect")
                const color = d3.select(this).style("fill");
                bars.filter(function (d) {
                    return d3.select(this).style("fill") !== color;
                }).style("opacity", 0.5);
                points.filter(function (d) {
                    return d3.select(this).style("fill") === color;
                }).style("opacity", 1);
                points.filter(function (d) {
                    return d3.select(this).style("fill") !== color;
                }).style("opacity", 0.05);
                // tooltip appears
                tooltip.transition()
                    .duration(200)
                    .style('opacity', .9);
                tooltip.html(`${d.state}, ${d.year}`)
                    .style('left', (e.pageX) + 'px')
                    .style('top', (e.pageY - 28) + 'px')

                    .style('visibility', 'visible');

                d3.selectAll('#usstates').filter(function (d) {
                    return d3.select(this).style("fill") !== color;
                })
                    .style('opacity', '0.2')
                    // .style('filter', 'blur(3px)')
                    ;
                d3.selectAll(`.ministate:not(#cluster${d.cluster})`)
                    .style('opacity', '0.2')
                    // .style('filter', 'blur(3px)')
                    ;
            })
                .on("mouseout", function () {
                    points.style("opacity", 0.5);
                    d3.selectAll("rect").style("opacity", 1);
                    tooltip.style("opacity", 0)
                        .style('visibility', 'hidden')

                    d3.selectAll('#usstates')
                        .style("opacity", 0.6)
                        .style("stroke", '#ccc')
                        .style('stroke-width', '1px')
                        .style('filter', 'none');

                    d3.selectAll(`.ministate`)
                        .style('opacity', '1')
                        .style('filter', 'none');
                });
            
            // Add legend
            let legend = svg.append('g')
                .attr('id', 'legend')
                .attr('transform', `translate(${parentRect.width - this.margin.right}, ${this.margin.top + this.margin.bottom})`);

            // Add a circle and text element for each cluster in the legend
            legend.selectAll('circle')
                .data(this.clusters)
                .join('circle')
                .attr('cx', 0)
                .attr('cy', (d, i) => i * 25)
                .attr('r', 7)
                .style('fill', (d, i) => colorScale(i.toString()))
                .style('opacity', 0.7);
                
            legend.selectAll('text')
                .data(this.clusters)
                .join('text')
                .attr('x', 15)
                .attr('y', (d, i) => i * 25 + 5)
                .text(d => `${d}`)
                .style('font-size', '12px')

            const title = svg.append('g').append('text') // adding the text
                .attr('transform', `translate(${this.size.width / 2}, ${this.size.height + 10})`)
                .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '20px')
                .text('Clustering State Policies') // text content
        },
        rerender() {
            d3.select('.scatter-chart-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        }

    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.points': {
            handler(newPoints) { // when data changes
            if (!isEmpty(newPoints)) {
                
                console.log('rerendering policy scatter: ', this.numClusters)
                //Call and set the other api based on points, with POST method
                // set data for bar chart based on results from post
                this.rerender()
            }
        },
        deep: true
    },
        // 'store.numClusters': {
        //     handler(newNumClusters) { // when data changes
        //         if (!isEmpty(newNumClusters)) {
        //             console.log('rerendering policy scatter: ', this.numClusters)
        //             this.store.fetchData(newNumClusters);
        //             //Call and set the other api based on points, with POST method
        //             // set data for bar chart based on results from post
        //             this.rerender()
        //         }
        //     },
        //     deep: true
        // }
    },
    // The following are general setup for resize events.
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.$nextTick(() => {
            this.onResize()
        })
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