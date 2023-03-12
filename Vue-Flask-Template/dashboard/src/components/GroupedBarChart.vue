<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin, PolicyPoint, GroupedBar } from '../types';
// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
import { mapState, storeToRefs } from 'pinia'; 
import { useDataStore } from '../stores/dataStore';

export default {
    setup() { // Composition API syntax
        const store = useDataStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { bars } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);
        const { clusters } = storeToRefs(store);
        const { color }    = storeToRefs(store);
        return {
            // store, // Return store as the local state, but when you update the property value, the store is also updated.
            // resize,
            color,
            bars,
            size,
            margin,
            clusters
        }
    },
    computed: {
        ...mapState(useDataStore, []) // Traditional way to map the store state to the local state
    },
    created() {
        
        // this.store.fetchPolicyScatterplotAndBarChart();
    },
   
    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.groupedBarContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
        },
        initChart() {
            let gbc = this.$refs.groupedBarContainer as HTMLElement;
            let svg = d3.select(gbc)
                .append('svg')
                .attr('id', 'grouped-bar-svg')
                // .attr('width', '100%')
                // .attr('height', '100%')
                // .style('display', 'block');

            const parentRect = gbc.getBoundingClientRect();
            // svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height }`);

            svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height }`);


            // let chartContainer = svg;

            // append the svg object to the body of the page
            // List of groups = gun violence stats
            var groups = this.bars.map(d => d.group)
            // List of clusters
            var subgroups = this.clusters
            
            const x = d3.scaleBand()
                .domain(groups)
                .range([0, parentRect.width - (this.margin.right + this.margin.left)])
                .padding([0.2])
            
            let y_max = 0
            for(let elem of this.bars){
                for(let key of Object.keys(elem).filter(key => key !== "group")){
                    if(elem[key] > y_max){
                        y_max = elem[key]
                    }
                }
            }

            console.log('y max: ', y_max)
            
            var y = d3.scaleLinear()
                .domain([0, y_max])
                // .domain([40, 0])
                .range([ parentRect.height - this.margin.bottom, this.margin.top]);
            
                
            // Another scale for subgroup position?
            var xSubgroup = d3.scaleBand()
                .domain(subgroups)
                .range([0, x.bandwidth()])
                .padding([0.05])
            // color palette = one color per subgroup
            var color = this.color;
            // d3.scaleOrdinal()
            //     .domain(this.clusters)
            //     .range(d3.schemeSet1)
            // Show the bars
            svg
                .selectAll("rect")
                // Enter in data = loop group per group
                .data(this.bars)
                .join("g") 
                .attr("transform", d => `translate(${x(d.group)}, ${0})`)
                .selectAll("rect")
                .data(function(d) { return subgroups.map(function(key) { return {key: key, value: d[key]}; }); })
                .join("rect")
                .attr("x", d => xSubgroup(d.key))
                .attr("y", d => {
                    console.log('data: ', d.value)

                    console.log('y_max: ', y(y_max))
                    return y(d.value)
                })
                .attr("width", xSubgroup.bandwidth())
                .attr("height", (d) => {return parentRect.height - y(d.value) - this.margin.bottom})
                .attr("fill", d => {

                    console.log('color key: ', parseInt(d.key.substring(d.key.length - 1, d.key.length)) - 1)

                    console.log('color key: ', color(d.key))
                    return color((parseInt(d.key.substring(d.key.length - 1, d.key.length)) - 1).toString())
                })
                .attr("transform", `translate(${this.margin.left + this.margin.right+ 20}, 0)`)
                ;

            // Add X axis
            svg.append("g")
                .attr("transform", `translate(${this.margin.left + this.margin.right+ 20}, ${parentRect.height - this.margin.bottom})`)
                .call(d3.axisBottom(x).tickSize(0));
                
            // Add Y axis
            svg.append("g")
                .attr('transform', `translate(${this.margin.left + this.margin.right + 20}, 0)`)
                .call(d3.axisLeft(y)
                .tickFormat(d3.format(".0%"))
                );

            // Add Title
            svg.append('g').append('text') // adding the text
                .attr('transform', `translate(${parentRect.width / 1.75}, ${parentRect.height})`)
                .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '20px') // set the font size to 24 pixels
                .text('Average Incidents In Policy Clusters') // text content
        },
        rerender() {
            d3.selectAll('.chart-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        }
    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'bars'(newBars) { // when data changes
            if (!isEmpty(newBars)) {
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
    <div class="chart-container d-flex" ref="groupedBarContainer">
        
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>