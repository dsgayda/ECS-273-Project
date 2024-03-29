<script lang="ts">
import * as d3 from "d3";
import { isEmpty, debounce } from 'lodash';

// Computed property: https://vuejs.org/guide/essentials/computed.html
// Lifecycle in vue.js: https://vuejs.org/guide/essentials/lifecycle.html#lifecycle-diagram
import { mapState, storeToRefs } from 'pinia'; 
import { useDataStore } from '../stores/dataStore';

export default {
    data() {
        return {
            margin: {left: 20, right: 40, top: 30, bottom: 40} as Margin,
        }
    },
    setup() { // Composition API syntax
        const store = useDataStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { bars } = storeToRefs(store);
        const { size } = storeToRefs(store);
        // const { margin } = storeToRefs(store);
        const { clusters } = storeToRefs(store);
        const { color }    = storeToRefs(store);
        return {
            // store, // Return store as the local state, but when you update the property value, the store is also updated.
            // resize,
            color,
            bars,
            size,
            // margin,
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
                .attr('width', '100%')
                .attr('height', '100%')
                // .style('display', 'block');

            const parentRect = gbc.getBoundingClientRect();

            svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${parentRect.width} ${parentRect.height }`);

            // append the svg object to the body of the page
            // List of groups = gun violence stats
            var groups = this.bars.map(d => d.group)
            // List of clusters
            var subgroups = this.clusters

            // ADD AXE
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

            
            var y = d3.scaleLinear()
                .domain([0, y_max])
                // .domain([40, 0])
                .range([ parentRect.height - this.margin.bottom, this.margin.top + 20]);
            
                
            // Another scale for subgroup position?
            var xSubgroup = d3.scaleBand()
                .domain(subgroups)
                .range([0, x.bandwidth()])
                .padding([0.05])
            // color palette = one color per subgroup
            var color = this.color;
            // Show the bars
            const bars = svg.selectAll("rect")
                // Enter in data = loop group per group
                .data(this.bars)
                .join("g") 
                
                .attr("transform", d => `translate(${x(d.group)}, ${0})`)
                .selectAll("rect")
                .data(function(d) { return subgroups.map(function(key) { return {key: key, value: d[key]}; }); })
                .join("rect")
                .attr("x", d => xSubgroup(d.key))
                .attr("y", d => {
                    return y(d.value)
                })
                .attr("width", xSubgroup.bandwidth())
                .attr("height", (d) => {return parentRect.height - y(d.value) - this.margin.bottom})
                .style("fill", d => {
                    return color((parseInt(d.key.substring(d.key.length - 1, d.key.length)) - 1).toString())
                })
                
                .attr("id", d => {
                    return d.key.replaceAll(' ', '');
                })
                .attr("transform", `translate(${this.margin.left + this.margin.right+ 20}, ${this.margin.bottom})`)
                .attr("class", "barchartrect")
                ;

            // Add mouseover to highlight same cluster as bar under mouse
            bars.on("mouseover", function(e, d) {
                    const points = d3.selectAll("circle");
                    const color = d3.select(this).style("fill");
                    bars.filter(function(d) {
                        return d3.select(this).style("fill") !== color;
                    }).style("opacity", 0.5);
                    points.filter(function(d) {
                        return d3.select(this).style("fill") === color;
                    }).style("opacity", 1);
                    points.filter(function(d) {
                        return d3.select(this).style("fill") !== color;
                    }).style("opacity", 0.05);
                    
                    d3.selectAll('#usstates').filter(function(d) {
                        return d3.select(this).style("fill") !== color;
                        })
                        .style('opacity', '0.2')
                        // .style('filter', 'blur(3px)')
                        ;
                    d3.selectAll(`.ministate:not(#cluster${(parseInt(d.key.substring(d.key.length - 1, d.key.length)) - 1).toString()})`)
                        .style('opacity', '0.2')
                        // .style('filter', 'blur(3px)')
                        ;
                    
                    
                })
                .on("mouseout", function() {
                    bars.style("opacity", 1);
                    d3.selectAll("circle").style("opacity", 1);
                    d3.selectAll('#usstates')
                        .style("opacity", 0.6)
                        .style('stroke-width', '1px')
                        .style('filter', 'none');
                    d3.selectAll(`.ministate`)
                        .style('opacity', '1')
                        .style('filter', 'none');
                });

            // Add X axis
            svg.append("g")
                .attr("transform", `translate(${this.margin.left + this.margin.right + 20}, ${parentRect.height})`)
                .call(d3.axisBottom(x).tickSize(0));
            
            // X axis label
            svg.append("text")
                .attr("class", "x label")
                .attr('transform', `translate(${parentRect.width / 2}, ${parentRect.height + 25})`)
                .attr("text-anchor", "middle")
                .style('font-size', '12px') 
                .text("Incident Type");

                        
            // Add Y axis
            svg.append("g")
                .attr('transform', `translate(${this.margin.left + this.margin.right + 20}, ${this.margin.bottom})`)
                .call(d3.axisLeft(y)
                .tickFormat(d3.format(".0%"))
                );
            
            // Add Y axis label
            svg.append('g')
                .attr('transform', `translate(${this.margin.right}, ${this.size.height / 2 + this.margin.bottom}) rotate(-90)`)
                .append('text')
                .attr("text-anchor", "middle")
                .style('font-size', '12px')
                .text('Percent of Total Incidents in All Clusters')   
                         
            // Add Title
            svg.append('g').append('text') // adding the text
                .attr('transform', `translate(${parentRect.width / 1.75}, ${this.margin.top + this.margin.bottom - 20})`)
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '20px') 
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
        this.initChart()
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