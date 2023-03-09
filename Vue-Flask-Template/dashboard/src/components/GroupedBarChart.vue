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

        return {
            // store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
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
            // append the svg object to the body of the page
            var svg = d3.select("#grouped-bar-svg")
            // List of groups = gun violence stats
            var groups = this.bars.map(d => d.group)
            // List of clusters
            var subgroups = JSON.parse(JSON.stringify(this.clusters))
            // Add X axis
            const x = d3.scaleBand()
                .domain(groups)
                .range([this.margin.left, this.size.width - this.margin.right])
                .padding([0.2])
            svg.append("g")
                .attr("transform", `translate(0, ${this.size.height - this.margin.bottom})`)
                .call(d3.axisBottom(x).tickSize(0));
            
            let y_max = 0
            for(let elem of this.bars){
                if(elem.group == "all_incidents"){
                    for(let key of Object.keys(elem).filter(key => key !== "group")){
                        if(elem[key] > y_max){
                            y_max = elem[key]
                        }
                    }
                }
            }
            // Add Y axis
            var y = d3.scaleLinear()
                .domain([y_max, 0])
                // .domain([40, 0])
                .range([ this.margin.bottom, this.size.height - this.margin.top ]);
            svg.append("g")
                .attr('transform', `translate(${this.margin.left}, ${0})`)
                .call(d3.axisLeft(y)
                .tickFormat(d3.format(".1e"))
                );
            // Another scale for subgroup position?
            var xSubgroup = d3.scaleBand()
                .domain(subgroups)
                .range([0, x.bandwidth()])
                .padding([0.05])
            // color palette = one color per subgroup
            var color = d3.scaleOrdinal()
                .domain(subgroups)
                .range(['#e41a1c','#377eb8','#4daf4a'])
            // Show the bars
            svg.append("g")
                .selectAll("g")
                // Enter in data = loop group per group
                .data(this.bars)
                .join("g")
                .attr("transform", d => `translate(${x(d.group)}, ${this.margin.bottom - 80})`)
                .selectAll("rect")
                .data(function(d) { return subgroups.map(function(key) { return {key: key, value: d[key]}; }); })
                .join("rect")
                .attr("x", d => xSubgroup(d.key))
                .attr("y", d => y(d.value))
                .attr("width", xSubgroup.bandwidth())
                .attr("height", (d) => {return this.size.height - y(d.value)})
                .attr("fill", d => color(d.key));
        },
        rerender() {
            d3.selectAll('#grouped-bar-svg').selectAll('*').remove() // Clean all the elements in the chart
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
        <svg id="grouped-bar-svg" width="100%" height="100%">
            <!-- all the visual elements we create in initChart() will be inserted here in DOM-->
        </svg>
    </div>
</template>

<style scoped>
.chart-container{
    height: 100%;
}
</style>