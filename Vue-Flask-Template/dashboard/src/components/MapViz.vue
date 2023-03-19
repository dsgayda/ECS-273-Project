<script lang="ts">
import * as d3 from "d3";
import { debounce, isEmpty } from 'lodash';
import { MapDatum } from '../types';
import * as topojson from 'topojson';
// import obDataCsv from '../obesity-2008-2018.csv';
import { csvParse } from 'd3';
import * as ss from 'simple-statistics';
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
        const { reductionType } = storeToRefs(store);

        const { numClusters } = storeToRefs(store);

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
            update,
            numClusters,
            reductionType
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
            
            // this.store.fetchData({numClusters: this.store.numClusters}, {reductionType: this.store.reductionType});
            let target = this.$refs.mapContainer as HTMLElement
            if (!target) return;
            this.size = { width: target.clientWidth, height: target.clientHeight }; // How you update the store
        },
        async initChart() {

            if (this.store.geoMapData?.objects?.states && Array.from(this.states.map(s => s.incidents_per_capita).values()).flat().length > 0) {

            let multiplier = 50000;
            if (this.selectedValue === "Mass Shooting") {
                multiplier = 10000000
            }
            else if (this.selectedValue === "Gang Related" || this.selectedValue === "Suicide") {
                multiplier = 1000000
            }


                const mappydata = new Map(Object.entries(this.states));


                let sc = this.$refs.mapContainer as HTMLElement;


                const parentRect = { width: sc.clientWidth, height: sc.clientHeight };

                const svg = d3.select(sc)

                    .attr("stroke-linejoin", "round")
                    .attr("stroke-linecap", "round")
                    .attr('fill', 'lightgray')
                    .append('svg')
                    // .attr("viewBox", [sc.clientWidth / 3 - sc.clientWidth / 2, 0, sc.clientWidth, sc.clientHeight])
                    .attr('width', '100%')
                .attr('height', '100%')


                const mapTitle1 = svg.append('g')
                    .attr('class', 'title')
                    .attr('transform', `translate(${0}, ${10})`);

                    mapTitle1.append('rect')
                        .attr('x', '-2.5em')
                        .attr('y', '-1.5em')
                        .attr('width', '200%')
                        .attr('height', '2.5em')
                        .style('fill', '#fff')
                        .attr('transform', `translate(${0}, 0)`);

                const mapTitle = svg.append('g')
                    .attr('class', 'title')
                    .attr('transform', `translate(${this.size.width/2}, ${10})`);
                    // Add the text element to the group
                    mapTitle.append('text')
                    .text('Policy & Incident Map')
                    .attr('dy', '0.5rem')
                    .style('text-anchor', 'middle')
                    .style('font-weight', 'bold')
                    .style('font-size', '20px');


                 // Create a rectangular background element
                //  const bgRect = svg.insert('rect', ':first-child')
                //     .attr('x', 0)
                //     .attr('y', 0)
                //     .attr('width', sc.clientWidth)
                //     .attr('height', sc.clientHeight)
                //     .attr('transform', `translate(${-this.margin.left - this.margin.right}, 0)`)
                //     .style('fill', '#EFEFEF');

                let data = this.store.geoMapData;
                let states = topojson.feature(data, data.objects.states);
                let path = d3.geoPath();
                let bounds = path.bounds(states);
                // get the bounds of the path data
                // calculate the scaling factor needed to fit the path inside the container
                const widthScale = this.size.width / (bounds[1][0] - bounds[0][0]);
                const heightScale = (this.size.height - (this.margin.bottom + this.margin.top) - sc.clientHeight / 10) / (bounds[1][1] - bounds[0][1]);
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
                    .attr('transform', `translate(${65}, ${30})`)
                    .on('mousemove', (e, d) => {
                        console.log('mouse over state: ', this.states.filter(s => s.state === d.properties.name)[0])
                        let stateInfo = this.states.filter(s => s.state === d.properties.name)[0];
                        d3.select('.d3-tooltip').transition()
                            .duration(200)
                            .style('opacity', .9);
                        d3.select('.d3-tooltip')
                            .html(`State: ${stateInfo.state}<br>
                            Cluster: ${stateInfo.cluster + 1}<br>
                            Incidents: ${(stateInfo.incidents_per_capita * multiplier).toFixed(1)}<br>
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
                            translate(${x + 65},${y + 30})
                            scale(${size})
                            translate(${-x},${-y})
                        `;
                    }

                    return `
                            translate(${x + 65},${y + 30})
                            translate(${-x},${-y})
                        `;
                }

                // Little States
                // let redcolor = d3.scaleSequential(d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat()), d3.interpolateReds).nice()
                // let colorrr = d3.scaleSequential(d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat()), d3.interpolateYlOrRd).nice()

                // Color gradient green -> yellow -> red
                let colorRange = ["white", "yellow", "orange", "red"];

                // Define the domain of the linear scale using the extent of the incidents_per_capita values
                let colorDomain = d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());

                let datas = Array.from(this.states.map(s => s.incidents_per_capita).values()).flat();
                // console.log('datas:', datas)
                // let datas = [1, 2, 3, 4, 5, 6, 7];
                

                // Define the domain of the linear scale using the min, 1st quartile, median, 3rd quartile, and max values
                // let domain = [colorDomain[0], colorDomain[1]];

                    let quartiles = ss.quantile(datas, [0.25, 0.5, 0.75]);
                    console.log('quartiles: ', quartiles);
                    let q1 = quartiles[0];
                    let q2 = quartiles[1];
                    let q3 = quartiles[2];
                    const domain = [colorDomain[0], q1, q2, q3, colorDomain[1]];
                    let colorrr = d3.scaleSequential(d3.extent(domain), d3.interpolateYlOrRd)
                
                // Create the linear scale using d3.scaleLinear() and interpolate between the colors
                let RYG_color = d3.scaleLinear()
                    .domain(domain)
                    .interpolate(d3.interpolateYlOrRd)
                    .range(colorRange)
                    .clamp(true);

                // Calculate the median value
                // let medianValue = d3.median(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());

                // Create the linear scale using d3.scaleLinear() and interpolate between the colors
                // min -> 1st quartile -> median -> 3rd quartile -> max
                // let RYG_color = d3.scaleLinear()
                //     .domain([colorDomain[0], medianValue, colorDomain[1]])
                    
                //     .interpolate(d3.interpolateRgb)
                //     .range([colorRange[0], colorRange[1], colorRange[2]])
                //     .clamp(true);

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
                        return colorrr(this.states.filter(s => s.state === d.properties.name)[0].incidents_per_capita)
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
                            Incidents: ${(stateInfo.incidents_per_capita * multiplier).toFixed(1)}<br>
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
                    .attr('width', legendContainer.clientWidth)
                    .attr('height', legendContainer.clientHeight)
                    // .attr('height', '100%')
                    // .attr("viewBox", [-10, 0, legendContainer.clientWidth, legendContainer.clientHeight])
                    .attr('id', 'legend')
                // .attr('transform', `translate(${0}, ${legendContainer.clientHeight})`);

                // // Add a circle and text element for each cluster in the legend
                legend.selectAll('circle')
                    .data(this.clusters)
                    .join('circle')
                    .attr('cx', 0)
                    .attr('cy', (d, i) => i * 25)
                    .attr('r', 7)
                    .style('fill', (d, i) => this.color(i.toString()))
                .attr('transform', `translate(${legendContainer.clientWidth/8}, ${legendContainer.clientHeight/25 + 8})`);

                legend.selectAll('text')
                    .data(this.clusters)
                    .join('text')
                    .attr('x', 15)
                    .attr('y', (d, i) => i * 25 + 5)
                    .text(d => `${d}`)
                    .style('font-size', '12px')
                    .attr('transform', `translate(${legendContainer.clientWidth/8}, ${legendContainer.clientHeight/25 + 8})`);

                this.createLegend(svg, colorrr, domain, multiplier, datas , sc)
                    ;
            }

        },
        initLegend() {

        },
        createLegend(svg, colorScale, colorDomain, multiplier, datas, sc) {
            console.log('colorDomain: ', colorDomain)
            const legendWidth = 250;
            const legendHeight = 5;
            const legendMargin = { top: 10, right: 10, bottom: 10, left: 10 };

            const legend = svg.append("g")
                .attr("transform", `translate(${this.margin.left - 50}, ${(this.size.height - this.size.height / 10 )+ 10})`);

            const gradient = legend.append("defs")
                .append("linearGradient")
                .attr("id", "gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "0%")
                .attr("spreadMethod", "pad");

            let colorData = [
                { offset: "0%", color: colorScale(colorDomain[0]) },
                { offset: "25%", color: colorScale(colorDomain[1])},
                { offset: "50%", color: colorScale(colorDomain[2]) },
                // { offset: "50%", color: colorScale(colorDomain[2])  },
                { offset: "75%", color: colorScale(colorDomain[3])  },
                { offset: "100%", color: colorScale(colorDomain[4])  }
                // { offset: "100%", color: colorScale(colorDomain[5]) }
            ];

            // let colorData = [];
            // datas.sort((a, b) => a - b);
            // for (let i = 0; i < datas.length; i++) {
            // const offset = (i / (datas.length - 1)) * 100;
            // const color = colorScale(datas[i]);
            // colorData.push({ offset: `${offset}%`, color });
            // }

            
            console.log('colorData: ', colorData)

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
            const legendScale = d3.scaleLinear()
                .domain([colorDomain[0] * multiplier, colorDomain[4] * multiplier])
                .range([0, legendWidth]);

            const tickValues = legendScale.ticks(10);
            console.log('tickvals: ', tickValues)
            const legendAxis = d3.axisBottom(legendScale)
                .tickValues(tickValues)
                .tickFormat(d3.format("d"));


            legend.append("g")
                // .attr("transform", `translate(0, ${legendHeight})`)
                .call(legendAxis);

            const title = legend.append('g').append('text') // adding the text
                // .attr('transform', `translate(${this.size.width / 2}, ${this.size.height + 10})`)
                // .attr('dy', '0.5rem') // relative distance from the indicated coordinates.
                .style('text-anchor', 'middle')
                .style('font-weight', 'bold')
                .style('font-size', '8px')
                .attr('transform', `translate(${legendWidth / 2}, -5)`)
                .text('Gun Incidents Per 50k People') // text content


                //  const bgRect = svg.append('g').append('rect', ':first-child')
                //     .attr('x', 0)
                //     .attr('y', 0)
                //     .attr('width', sc.clientWidth)
                //     .attr('height', 20)
                //     .attr('transform', `translate(${-this.margin.left - this.margin.right}, 0)`)
                //     .style('fill', '#FFFFFF');

            
        },

        rerender() {
            d3.selectAll('.map-container').selectAll('*').remove() // Clean all the elements in the chart
            d3.selectAll('.legend-container').selectAll('*').remove()
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
            console.log('resize STORE:::::::::::')

            // this.store.fetchData({numClusters: this.store.numClusters}, {reductionType: this.store.reductionType});
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
    <v-row style="height: 100%" >
        <v-col cols="10" >

            <div class="map-container d-flex justify-center" ref="mapContainer" style=" height: 100%; background-color: #EFEFEF; ">

            </div>
        </v-col>
        <v-col cols="2" >
            <v-row style="height: 20%; padding: 10px">
                <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']" label="Incident" density="compact" v-model="selectedValue"></v-select>

            </v-row>
            <v-row style="height: 80%; padding: 10px">
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