<script lang="ts">
import * as d3 from "d3";
import { debounce, isEmpty } from 'lodash';
import { MapDatum } from '../types';
import * as topojson from 'topojson';
// import obDataCsv from '../obesity-2008-2018.csv';
import { csvParse } from 'd3';
/* The new major things from ExampleWithLegend.vue
1) Add a dropdown menu to switch between different DR techniques, the changes are mostly in the template
2) Using a store from './dashboard/stores/exampleStore'
3) Composition API rather than Option API (just used a little bit)
*/

// For importing a store. See how it's set up in ./dashboard/stores/ and ./dashboard/main.ts
import { mapState, storeToRefs } from 'pinia';
import { useDataStore } from '../stores/dataStore';
import { useExampleStore } from "../stores/exampleStore";
export default {
    setup() { // Composition API syntax
        const store = useDataStore();
        const exampleStore = useExampleStore();

        // Alternative expression from computed
        const { geoMapData, size, margin, states, color } = storeToRefs(store);
        const { resize } = storeToRefs(exampleStore);

        return {
            exampleStore,
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
            states,
            geoMapData,
            size,
            margin,
            color
        }
    },
    computed: {
        ...mapState(useDataStore, []), // Traditional way to map the store state to the local state
        ...mapState(useExampleStore, []),

    },
    created() {
    },
    methods: {
        onResize() {

            let target = this.$refs.mapContainer as HTMLElement
            console.log('target: ', target)
            if (!target) return;
            this.size = { width: target.clientWidth, height: target.clientHeight }; // How you update the store
        },
        async initChart() {

            if (this.store.geoMapData?.objects?.states) {
                const mappydata = new Map(Object.entries(this.states));


                let sc = this.$refs.mapContainer as HTMLElement;


                const parentRect = { width: sc.clientWidth, height: sc.clientHeight };

                const svg = d3.select(sc)

                    .attr("stroke-linejoin", "round")
                    .attr("stroke-linecap", "round")
                    .attr('fill', 'lightgray')
                    .append('svg')
                    .attr("viewBox", [0, 0, this.size.width, this.size.height])
                    .attr('width', parentRect.width)
                    .attr('height', parentRect.height)

                let data = this.store.geoMapData;
                let states = topojson.feature(data, data.objects.states);
                let path = d3.geoPath();
                let bounds = path.bounds(states);
                // get the bounds of the path data
                // calculate the scaling factor needed to fit the path inside the container
                const widthScale = this.size.width / (bounds[1][0] - bounds[0][0]);
                const heightScale = (this.size.height - (this.margin.bottom + this.margin.top) - parentRect.height / 10) / (bounds[1][1] - bounds[0][1]);
                const scaleFactor = Math.min(widthScale, heightScale);

                // create a transform function that scales and translates the path
                const transformer = d3.geoTransform({
                    point: function (x, y) {
                        this.stream.point((x - bounds[0][0]) * scaleFactor, (y - bounds[0][1]) * scaleFactor);
                    }
                });

                // apply the transform function to the path generator
                path = d3.geoPath().projection(transformer);
                svg.append("g")
                    .selectAll("path")
                    .data(states.features)
                    .enter().append("path")
                    .attr("fill", d => {
                        // console.log('not sure: ', this.states.filter(s => s.state === d.properties.name)[0]?.cluster)
                        if (!this.states.filter(s => s.state === d.properties.name)[0]?.cluster && this.states.filter(s => s.state === d.properties.name)[0]?.cluster !== 0) {
                            return "white";
                        }
                        else {
                            return this.color(this.states.filter(s => s.state === d.properties.name)[0].cluster.toString())
                        }
                    }
                    )
                    .attr('id', 'usstates')
                    .attr("stroke", "#ccc")
                    .attr('opacity', '.6')
                    .attr("d", path)
                    .attr('transform', `translate(${0}, 0)`);

                // Find the minimum and maximum policies_implemented values
                const policiesImplementedExtent = d3.extent(this.states, d => d.policies_implemented);

                // Create a linear scale for circle size based on policies_implemented
                const sizeScale = d3.scaleLinear()
                    .domain(policiesImplementedExtent)
                    .range([0.25, .9]);

                // Use the size scale in the transform function
                function transform(d, states) {
                    const [x, y] = path.centroid(d);
                    if (states.filter(s => s.state === d.properties.name)[0]?.policies_implemented) {
                        const policiesImplemented = states.filter(s => s.state === d.properties.name)[0].policies_implemented;
                        const size = sizeScale(policiesImplemented);

                        return `
                            translate(${x},${y})
                            scale(${size})
                            translate(${-x},${-y})
                        `;
                    }

                    return `
                            translate(${x},${y})
                            translate(${-x},${-y})
                        `;
                }

                // Little States
                // let redcolor = d3.scaleSequential(d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat()), d3.interpolateReds).nice()

                // Color gradient green -> yellow -> red
                let colorRange = ["green", "yellow", "red"];

                // Define the domain of the linear scale using the extent of the incidents_per_capita values
                let colorDomain = d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());
                console.log('colorDomain', colorDomain)
                // Create the linear scale using d3.scaleLinear() and interpolate between the colors
                let RYG_color = d3.scaleLinear()
                    .domain([colorDomain[0], (colorDomain[0] + colorDomain[1]) / 2, colorDomain[1]])
                    .range(colorRange)
                    .interpolate(d3.interpolateRgb);

                const state = svg.append("g")
                    .attr("stroke", "#000")
                    .selectAll("path")
                    .data(topojson.feature(data, data.objects.states).features.filter(d => {

                        if (this.states.filter(s => s.state === d.properties.name) && this.states.filter(s => s.state === d.properties.name)[0]?.incidents_per_capita !== undefined) {
                            return true
                        }
                        else {
                            return false;
                        }

                    }))
                    .join("path")
                    .attr("vector-effect", "non-scaling-stroke")
                    .attr("d", path)
                    .attr("id", d => {
                        return `cluster${this.states.filter(s => s.state === d.properties.name)[0]?.cluster}`
                    })
                    .attr('class', 'ministate')
                    .attr("fill", d => {
                        return RYG_color(this.states.filter(s => s.state === d.properties.name)[0].incidents_per_capita)
                    })
                    .attr("transform", d => transform(d, this.states));

                this.createLegend(svg, RYG_color, colorDomain)
                    ;
            }

        },
        initLegend() {

        },
        createLegend(svg, colorScale, colorDomain) {
            const legendWidth = 250;
            const legendHeight = 5;
            const legendMargin = { top: 10, right: 10, bottom: 10, left: 10 };

            const legend = svg.append("g")
                .attr("transform", `translate(${this.margin.left - 50}, ${this.size.height - this.size.height/10})`);

            const gradient = legend.append("defs")
                .append("linearGradient")
                .attr("id", "gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "0%")
                .attr("spreadMethod", "pad");

            const colorData = [
                { offset: "0%", color: colorScale(colorDomain[0]) },
                { offset: "50%", color: colorScale((colorDomain[0] + colorDomain[1]) / 2) },
                { offset: "100%", color: colorScale(colorDomain[1]) }
            ];

            gradient.selectAll("stop")
                .data(colorData)
                .enter()
                .append("stop")
                .attr("offset", d => d.offset)
                .attr("stop-color", d => d.color)
                .attr("stop-opacity", 1);

            legend.append("rect")
                .attr("width", legendWidth)
                .attr("height", legendHeight)
                .style("fill", "url(#gradient)");

            console.log('colorDomain: ', colorDomain)
            const legendScale = d3.scaleLinear()
                .domain([colorDomain[0] * 50000, colorDomain[1] * 50000])
                .range([0, legendWidth]);

            const legendAxis = d3.axisBottom(legendScale)
                .ticks(5)
                .tickFormat(d3.format("d"));

            legend.append("g")
                .attr("transform", `translate(0, ${legendHeight})`)
                .call(legendAxis);

            const title = legend.append('g').append('text') // adding the text
                // .attr('transform', `translate(${this.size.width / 2}, ${this.size.height + 10})`)
                // .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '8px') 
                .attr('transform', `translate(${legendWidth / 2}, -5)`)
                .text('Gun Incidents Per 50k People') // text content
            
    //             legend.append('g').append('rect')
    // .attr('width', 250)
    // .attr('height', 100)
    // .attr('fill', 'white') // Add the fill color for the box
    // .attr('stroke', 'black')
    // .attr('stroke-width', 1)
    // .attr('transform', `translate(${this.size.width - this.size.width/3}, ${-this.size.height + this.size.height/8})`); // Fix the typo in the attribute name


        },

        rerender() {
            d3.selectAll('.map-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
            // d3.selectAll('#map-svg').selectAll('*').remove() // Clean all the elements in the chart
            // d3.selectAll('#map-legend-svg').selectAll('*').remove()
            // this.initChart()
            // this.initLegend()
        }
    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.mapData'(mapData) { // when data changes
            if (!isEmpty(mapData)) {
                this.rerender()
            }
        },
        'store.geoMapData'(geoMapData) { // when data changes
            if (!isEmpty(geoMapData)) {
                this.rerender()
            }
        },
        'store.points': {
            async handler(newPoints) {
                if (!isEmpty(newPoints)) {
                    const data = {
                        data: this.store.points,
                        clusters: this.store.clusters,
                    };
                    let resp = await this.store.fetchGeoMap(data);
                    this.store.geoMapData = resp?.geoMapData;
                    this.store.mapData = resp?.mapData;
                    //Call and set the other api based on points, with POST method
                    // set data for bar chart based on results from post
                    this.rerender()
                }
            },
            immediate: true,
        },
    },
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

<!-- We only use vanilla widgets here, you can use the equivalent components from the UI library -->
<!-- Helpful References: https://vuejs.org/guide/essentials/class-and-style.html#binding-html-classes -->
<template>
    <div class="map-container d-flex justify-end" ref="mapContainer">

    </div>
</template>

<style scoped>
.map-container {
    height: 95%;
    width: 100%;
}
</style>