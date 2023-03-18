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
import { ComponentSize } from '../types';
export default {
    setup() { // Composition API syntax
        const store = useDataStore();
        const exampleStore = useExampleStore();

        // Alternative expression from computed
        const { geoMapData, margin, states, color, clusters, update } = storeToRefs(store);
        const { resize } = storeToRefs(exampleStore);

        const size = { width: 0, height: 0 } as ComponentSize;
        return {
            exampleStore,
            store, // Return store as the local state, but when you update the property value, the store is also updated.
            resize,
            states,
            geoMapData,
            size,
            margin,
            color,
            clusters,
            update
        }
    },
    data() {
        return {
            selectedValue: 'All Incidents',
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
            // this.store.resize();
            let target = this.$refs.mapContainer as HTMLElement
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
                    .attr("viewBox", [this.size.width / 4 - this.size.width / 2, 0, this.size.width, this.size.height])
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
                    .attr("stroke", "#555")
                    .attr('opacity', '.6')
                    .attr("d", path)
                    // .attr('transform', `translate(${0}, 0)`)
                    .on('mousemove', (e, d) => {
                        console.log('mouse over state: ', this.states.filter(s => s.state === d.properties.name)[0])
                        let stateInfo = this.states.filter(s => s.state === d.properties.name)[0];
                        d3.select('.d3-tooltip').transition()
                            .duration(200)
                            .style('opacity', .9);
                        d3.select('.d3-tooltip')
                            .html(`State: ${stateInfo.state}<br>
                            Cluster: ${stateInfo.cluster + 1}<br>
                            Incidents: ${(stateInfo.incidents_per_capita * 50000).toFixed(1)}<br>
                            Avg. # Policies: ${stateInfo.policies_implemented}`)

                            .style('left', (e.pageX + 10) + 'px')
                            .style('top', (e.pageY) + 'px')

                            .style('visibility', 'visible');
                        // cluster: 2, incidents_per_capita: 0.00008333123749441487, policies_implemented: 104.2, state: 'California'
                    })
                    .on('mouseout', (e, d) => {
                        d3.select('.d3-tooltip').transition()
                            // .duration(500)
                            // .style('opacity', 0)
                            .style('visibility', 'hidden');

                    });

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
                let colorRange = ["white", "yellow", "red"];

                // Define the domain of the linear scale using the extent of the incidents_per_capita values
                let colorDomain = d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());

                // Calculate the median value
                let medianValue = d3.median(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());

                // Create the linear scale using d3.scaleLinear() and interpolate between the colors
                let RYG_color = d3.scaleLinear()
                    .domain([colorDomain[0], medianValue, colorDomain[1]])
                    .range(colorRange)
                    .interpolate(d3.interpolateRgb)
                    .range([colorRange[0], colorRange[1], colorRange[2]])
                    .clamp(true);

                const state = svg.append("g")
                    .attr("stroke", "#666")
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
                    .attr("transform", d => transform(d, this.states))
                    .on('mousemove', (e, d) => {
                        console.log('mouse over state: ', this.states.filter(s => s.state === d.properties.name)[0])
                        let stateInfo = this.states.filter(s => s.state === d.properties.name)[0];
                        d3.select('.d3-tooltip').transition()
                            .duration(200)
                            .style('opacity', .9);
                        d3.select('.d3-tooltip')
                            .html(`State: ${stateInfo.state}<br>
                            Cluster: ${stateInfo.cluster + 1}<br>
                            Incidents: ${(stateInfo.incidents_per_capita * 50000).toFixed(1)}<br>
                            Avg. # Policies: ${stateInfo.policies_implemented}`)
                            .style('left', (e.pageX + 10) + 'px')
                            .style('top', (e.pageY) + 'px')

                            .style('visibility', 'visible');
                        // cluster: 2, incidents_per_capita: 0.00008333123749441487, policies_implemented: 104.2, state: 'California'
                    })
                    .on('mouseout', (e, d) => {
                        d3.select('.d3-tooltip').transition()
                            // .duration(500)
                            // .style('opacity', 0)
                            .style('visibility', 'hidden');

                    })



                let legendContainer = this.$refs.legendContainer as HTMLElement;


                const legendSize = { width: legendContainer.clientWidth, height: legendContainer.clientHeight };


                // const svg = d3.select(sc)

                //     .attr("stroke-linejoin", "round")
                //     .attr("stroke-linecap", "round")
                //     .attr('fill', 'lightgray')
                //     .append('svg')
                //     .attr("viewBox", [this.size.width/4 - this.size.width/3, 0, this.size.width, this.size.height])
                //     .attr('width', parentRect.width)
                //     .attr('height', parentRect.height)
                let legend = d3.select(legendContainer).append('svg')
                    .attr('width', legendSize.width)
                    .attr('height', legendSize.height)
                    // .attr('height', '100%')
                    // .attr("viewBox", [-10, 0, legendSize.width, legendSize.height])
                    .attr('id', 'legend')
                // .attr('transform', `translate(${0}, ${legendSize.height})`);

                // // Add a circle and text element for each cluster in the legend
                legend.selectAll('circle')
                    .data(this.clusters)
                    .join('circle')
                    .attr('cx', 0)
                    .attr('cy', (d, i) => i * 25)
                    .attr('r', 7)
                    .style('fill', (d, i) => this.color(i.toString()))
                .attr('transform', `translate(${legendSize.width/8}, ${8})`);

                legend.selectAll('text')
                    .data(this.clusters)
                    .join('text')
                    .attr('x', 15)
                    .attr('y', (d, i) => i * 25 + 5)
                    .text(d => `${d}`)
                    .style('font-size', '12px')
                    .attr('transform', `translate(${legendSize.width/8}, ${8})`);

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
                .attr("transform", `translate(${this.margin.left - 50}, ${this.size.height - this.size.height / 10})`);

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

            if (this.selectedValue === 'Non-Suicide' || this.selectedValue === 'All Incidents') {
                
            const legendScale = d3.scaleLinear()
                .domain([colorDomain[0] * 50000, colorDomain[1] * 50000])
                .range([0, legendWidth]);

            const tickValues = legendScale.ticks(10);
            if (tickValues[0] > colorDomain[0] * 50000) {
                tickValues.unshift(colorDomain[0] * 50000);
            }
            if (tickValues[tickValues.length - 1] < colorDomain[1] * 50000) {
                tickValues.push(colorDomain[1] * 50000);
            }

            // Check if the top tick is very close to the top value
            const topValue = tickValues[tickValues.length - 1];
            if (Math.abs(topValue - colorDomain[1] * 50000) < 0.0001) {
                // Remove the tick value just below the top value
                tickValues.pop();
            }
            // Check if the bottom tick is very close to the bottom value
            const bottomValue = tickValues[0];
            if (Math.abs(bottomValue - colorDomain[0] * 50000) < 0.0001) {
                // Remove the tick value just below the top value
                tickValues.shift();
            }

            const legendAxis = d3.axisBottom(legendScale)
                .tickValues(tickValues)
                .tickFormat(d3.format("d"));


            // const legendAxis = d3.axisBottom(legendScale)
            //     .ticks(10)
            //     .tickFormat(d3.format("d"));

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

            }
            else if (this.selectedValue === "Mass Shooting") {

                const legendScale = d3.scaleLinear()
                    .domain([colorDomain[0] * 10000000, colorDomain[1] * 10000000])
                    .range([0, legendWidth]);
    
                const tickValues = legendScale.ticks(10);
                if (tickValues[0] > colorDomain[0] * 10000000) {
                    tickValues.unshift(colorDomain[0] * 10000000);
                }
                if (tickValues[tickValues.length - 1] < colorDomain[1] * 10000000) {
                    tickValues.push(colorDomain[1] * 10000000);
                }
    
                // Check if the top tick is very close to the top value
                const topValue = tickValues[tickValues.length - 1];
                if (Math.abs(topValue - colorDomain[1] * 10000000) < 0.0001) {
                    // Remove the tick value just below the top value
                    tickValues.pop();
                }
                // Check if the bottom tick is very close to the bottom value
                const bottomValue = tickValues[0];
                if (Math.abs(bottomValue - colorDomain[0] * 10000000) < 0.0001) {
                    // Remove the tick value just below the top value
                    tickValues.shift();
                }
    
                const legendAxis = d3.axisBottom(legendScale)
                    .tickValues(tickValues)
                    .tickFormat(d3.format("d"));
    
    
                // const legendAxis = d3.axisBottom(legendScale)
                //     .ticks(10)
                //     .tickFormat(d3.format("d"));
    
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
                    .text('Gun Incidents Per 10M People') // text content
    
                
            }
            else {
                
                const legendScale = d3.scaleLinear()
                    .domain([colorDomain[0] * 1000000, colorDomain[1] * 1000000])
                    .range([0, legendWidth]);
    
                const tickValues = legendScale.ticks(10);
                if (tickValues[0] > colorDomain[0] * 1000000) {
                    tickValues.unshift(colorDomain[0] * 1000000);
                }
                if (tickValues[tickValues.length - 1] < colorDomain[1] * 1000000) {
                    tickValues.push(colorDomain[1] * 1000000);
                }
    
                // Check if the top tick is very close to the top value
                const topValue = tickValues[tickValues.length - 1];
                if (Math.abs(topValue - colorDomain[1] * 1000000) < 0.0001) {
                    // Remove the tick value just below the top value
                    tickValues.pop();
                }
                // Check if the bottom tick is very close to the bottom value
                const bottomValue = tickValues[0];
                if (Math.abs(bottomValue - colorDomain[0] * 1000000) < 0.0001) {
                    // Remove the tick value just below the top value
                    tickValues.shift();
                }
    
                const legendAxis = d3.axisBottom(legendScale)
                    .tickValues(tickValues)
                    .tickFormat(d3.format("d"));
    
    
                // const legendAxis = d3.axisBottom(legendScale)
                //     .ticks(10)
                //     .tickFormat(d3.format("d"));
    
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
                    .text('Gun Incidents Per 1M People') // text content
    
                }

        },

        rerender() {
            d3.selectAll('.map-container').selectAll('*').remove() // Clean all the elements in the chart
            d3.selectAll('.legend-container').selectAll('svg').remove()
            this.initChart()
            // d3.selectAll('#map-svg').selectAll('*').remove() // Clean all the elements in the chart
            // d3.selectAll('#map-legend-svg').selectAll('*').remove()
            // this.initChart()
            // this.initLegend()
        }
    },
    watch: {
        'store.update'() {
            this.rerender();
        },
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

                    const incidentMap = {
                    'All Incidents': 'all_incidents',
                    'Gang Related': 'gang',
                    Suicide: 'suicide',
                    'Non-Suicide': 'non_suicide',
                    'Mass Shooting': 'mass_shooting'
                };

                    const data = {
                        data: this.store.points,
                        clusters: this.store.clusters,
                        incidentType: incidentMap[this.selectedValue]
                    };

                    let resp = await this.store.fetchGeoMap(data);
                    this.store.geoMapData = resp?.geoMapData;
                    this.store.mapData = resp?.mapData;
                    //Call and set the other api based on points, with POST method
                    // set data for bar chart based on results from post
                    this.rerender()
                }
            },
            // immediate: true,
        },
        selectedValue: {
            async handler(newVal) {
                // for when the user chooses a different incidence type

                
                const incidentMap = {
                    'All Incidents': 'all_incidents',
                    'Gang Related': 'gang',
                    Suicide: 'suicide',
                    'Non-Suicide': 'non_suicide',
                    'Mass Shooting': 'mass_shooting'
                };

                    const data = {
                        data: this.store.points,
                        clusters: this.store.clusters,
                        incidentType: incidentMap[this.selectedValue]
                    };

                let resp = await this.store.fetchGeoMap(data);
                this.store.geoMapData = resp?.geoMapData;
                this.store.mapData = resp?.mapData;
                //Call and set the other api based on points, with POST method
                // set data for bar chart based on results from post
                this.rerender()


                // this.store.selectedValue = newVal;
            },
        }
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
    <v-row style="height: 100%">
        <v-col cols="9" >

            <div class="map-container d-flex justify-end" ref="mapContainer">

            </div>
        </v-col>
        <v-col cols="3" >
            <v-row style="height: 20%">
                <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']" label="Incident" density="compact" v-model="selectedValue"></v-select>

            </v-row>
            <v-row style="height: 80%">
                <div style="height: 100%; width: 100%;" class="legend-container d-flex justify-end" ref="legendContainer"></div>
            </v-row>
        </v-col>
    </v-row>



    <!-- <v-select :items="['t-SNE', 'NMF', 'PCA']"
                                    label="Reduction" density="compact" v-model="yes"></v-select> -->
</template>

<style scoped>
.map-container {
    height: 95%;
    width: 100%;
}
</style>