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
        ...mapState(useExampleStore, [])
    },
    created() {
        this.store.fetchData({ map: true });
        // this.store.fetchGeoMap();
    },
    methods: {
        onResize() {
            let target = this.$refs.mapContainer as HTMLElement
            if (target === undefined || target === null) return;
            this.size = { width: target.clientWidth, height: target.clientHeight }; // How you update the store
        },
        async initChart() {

            if (this.store.geoMapData?.objects?.states) {
                // const obData = csvParse(obDataCsv, ({ id, obesity2008, obesity2018 }) => [id, [+obesity2008, +obesity2018]]);

                const obDataCsv = `id,obesity2008,obesity2018
01,0.187,0.362
02,0.198,0.295
04,0.133,0.295
05,0.175,0.371
06,0.151,0.258
08,0.1,0.23
09,0.125,0.274
10,0.171,0.335
12,0.172,0.307
13,0.133,0.325
15,0.108,0.249
16,0.142,0.284
17,0.167,0.318
18,0.201,0.341
19,0.175,0.353
20,0.159,0.344
21,0.169,0.366
22,0.177,0.368
23,0.141,0.304
24,0.163,0.309
25,0.117,0.257
26,0.182,0.33
27,0.153,0.301
28,0.195,0.395
29,0.189,0.35
30,0.134,0.269
31,0.163,0.341
32,0.133,0.295
33,0.151,0.296
34,0.145,0.257
35,0.13,0.323
36,0.139,0.276
37,0.169,0.33
38,0.164,0.351
39,0.175,0.34
40,0.135,0.348
41,0.152,0.299
42,0.169,0.309
44,0.132,0.277
45,0.167,0.343
46,0.139,0.301
47,0.184,0.344
48,0.159,0.348
49,0.14,0.278
50,0.146,0.275
51,0.157,0.304
53,0.139,0.287
54,0.183,0.395
55,0.16,0.32
56,0.143,0.29
`

                const ob_data = new Map(csvParse(obDataCsv, ({ id, obesity2008, obesity2018 }) => [id, [+obesity2008, +obesity2018]]));
                

                const mappydata = new Map(Object.entries(this.states));
                // console.log('mappydata: ', mappydata)
// Do something with the obData Map
                
                let sc = this.$refs.mapContainer as HTMLElement;
                // let svg = d3.select(sc)
                //     .append('svg')
                //     .attr('id', 'map-svg')
                //     .attr('width', '100%')
                //     .attr('height', '100%')




                const parentRect = { width: sc.clientWidth, height: sc.clientHeight };

                // console.log('parentRect: ', parentRect)
                // console.log('this.size: ', this.size)
                const svg = d3.select(sc)

                    .attr("stroke-linejoin", "round")
                    .attr("stroke-linecap", "round")
                    .attr('fill', 'lightgray')
                    .append('svg')
                    .attr("viewBox", [0, 0, this.size.width, this.size.height])
                    .attr('width', '100%')
                    .attr('height', '100%')

                // svg.attr('viewBox', `${this.margin.left} ${this.margin.top} ${this.size.width} ${this.size.height}`);

                // const rect = svg.append('rect')
                //     .attr('width', '100%')
                //     .attr('height', '100%')
                //     .attr('fill', 'lightgray')
                //     .attr('opacity', 0.3)
                // .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`)

                // console.log('eh?: ', this.geoMapData)

                let data = this.store.geoMapData;
                let states = topojson.feature(data, data.objects.states);
                let path = d3.geoPath();
                let bounds = path.bounds(states);
                // get the bounds of the path data
                // calculate the scaling factor needed to fit the path inside the container
                const widthScale = this.size.width / (bounds[1][0] - bounds[0][0]);
                const heightScale = (this.size.height - (this.margin.bottom + this.margin.top) - 20) / (bounds[1][1] - bounds[0][1]);
                const scaleFactor = Math.min(widthScale, heightScale);

                // create a transform function that scales and translates the path
                const transformer = d3.geoTransform({
                    point: function (x, y) {
                        this.stream.point((x - bounds[0][0]) * scaleFactor, (y - bounds[0][1]) * scaleFactor);
                    }
                });

                // apply the transform function to the path generator
                path = d3.geoPath().projection(transformer);

                // svg.append("path")
                //     .datum(topojson.mesh(data, data.objects.states))
                //     .attr("stroke", "#ccc")
                //     .attr("d", path)
                //     .attr('transform', `translate(${this.margin.left}, 0)`)

                    svg.append("g")
                        .selectAll("path")
                        .data(states.features)
                        .enter().append("path")
                            .attr("fill", d => {
                                // console.log('not sure: ', this.states.filter(s => s.state === d.properties.name)[0]?.cluster)
                                if (!this.states.filter(s => s.state === d.properties.name)[0]?.cluster && this.states.filter(s => s.state === d.properties.name)[0]?.cluster !== 0) {

                                    // console.log('no cluster?: ', this.states.filter(s => s.state === d.properties.name)[0])
                                    return "white";
                                    // console.log('states.filter(s => s.state === d.properties.name)[0].cluster: ', this.states.filter(s => s.state === d.properties.name)[0].cluster)
                                
                                }
                                else {
                                    return this.color(this.states.filter(s => s.state === d.properties.name)[0].cluster.toString())
                                }
                               return "white";
                            }
                            )
                            .attr('id', 'usstates')
                            .attr("stroke", "#ccc")
                            .attr('opacity', '.6')
                            .attr("d", path)
                            .attr('transform', `translate(${this.margin.left}, 0)`);




                            // Find the minimum and maximum policies_implemented values
                        const policiesImplementedExtent = d3.extent(this.states, d => d.policies_implemented);

                        // Create a linear scale for circle size based on policies_implemented
                        const sizeScale = d3.scaleLinear()
                            .domain(policiesImplementedExtent)
                            .range([0.25, .9]);

                            // Use the size scale in the transform function
                    function transform(d, states) {
                        const [x, y] = path.centroid(d);
                        // console.log('hey: ', states.filter(s => s.state === d.properties.name)[0])
                        if (states.filter(s => s.state === d.properties.name)[0]?.policies_implemented) {
                            const policiesImplemented = states.filter(s => s.state === d.properties.name)[0].policies_implemented;
                        const size = sizeScale(policiesImplemented);
                        // console.log('policiesImplemented: ', policiesImplemented)

                        return `
                            translate(${x + 70},${y})
                            scale(${size})
                            translate(${-x},${-y})
                        `;
                        }

                        return `
                            translate(${x + 70},${y})
                            translate(${-x},${-y})
                        `;
                    }
                    // function transform(d, states) {
                    //     const [x, y] = path.centroid(d);

                    //     // console.log('mapper: ', states.filter(s => s.state === d.properties.name)[0].policies_implemented)

                    //     // scale(${Math.sqrt(ob_data.get(d.id)[year])})
                    //     return `
                    //         translate(${x + 70},${y})
                    //         scale(${Math.sqrt(states.filter(s => s.state === d.properties.name)[0].policies_implemented)/12})
                    //         translate(${-x},${-y})
                    //     `;
                    //     }

                        // Little States
                        // let redcolor = d3.scaleSequential(d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat()), d3.interpolateReds).nice()
                        let colorRange = ["green", "yellow", "red"];

                        // Define the domain of the quantize scale using the extent of the incidents_per_capita values
                        let colorDomain = d3.extent(Array.from(this.states.map(s => s.incidents_per_capita).values()).flat());

                        // Define the number of bins for the quantize scale
                        let numBins = colorRange.length;

                        // Create the quantize scale using d3.scaleQuantize()
                        let RYG_color = d3.scaleQuantize()
                            .domain(colorDomain)
                            .range(colorRange);

                        // console.log('mappy: ', this.states.map(s => s.incidents_per_capita))
                        const state = svg.append("g")
                            .attr("stroke", "#000")
                            .selectAll("path")
                            .data(topojson.feature(data, data.objects.states).features.filter(d => {
                                // console.log('ob_data.has(d.id): ', parseInt(d.id))
                                // console.log('d: ', d)

                                if (this.states.filter(s => s.state === d.properties.name) && this.states.filter(s => s.state === d.properties.name)[0]?.incidents_per_capita !== undefined) {
                                    // console.log('this.states.filter(s => s.state === d.properties.name): ', this.states.filter(s => s.state === d.properties.name))
                                    return true
                                }
                                else {
                                    // console.log('here: ', this.states.filter(s => s.state === d.properties.name))
                                    // console.log('after: ',  d.properties.name)
                                    return false;
                                }
                                
                                // return ob_data.has(d.id)
                            }))
                            .join("path")
                            .attr("vector-effect", "non-scaling-stroke")
                            .attr("d", path)
                            .attr("id", d => {
                                return `cluster${this.states.filter(s => s.state === d.properties.name)[0]?.cluster}`
                            })
                            .attr('class', 'ministate')
                            .attr("fill", d => {
                                // console.log('color: ', color(this.states.filter(s => s.state === d.properties.name).incidents_per_capita))
                                // console.log('d: ', d.properties.name)
                                // console.log('maybe: ', this.states.filter(s => s.state === d.properties.name)[0].incidents_per_capita)
                                return RYG_color(this.states.filter(s => s.state === d.properties.name)[0].incidents_per_capita)
                            })
                            .attr("transform", d => transform(d, this.states));




                //     console.log('data: ', data)
                //     let path = d3.geoPath().projection(d3.geoIdentity().reflectY(true) // flip the y-axis to match SVG convention
                //         .fitSize([parentRect.width, parentRect.height], data)); // fit the projection to the parentRect dimensions

                //     let scale = Math.min(this.size.height, this.size.width)


                //     svg.append("path")
                //         .attr('width', this.size.width)
                //         .attr('height', this.size.height)
                //         .datum(topojson.mesh(data, data.objects.states))
                //         .attr("fill", "none")
                //         .attr("stroke", "#000")
                //         .attr("d", path)
                //         .attr('transform', `translate(${parentRect.width / 2}, ${parentRect.height / 2}) scale(${scale})`);
                //         // .attr('transform', `scale(${.5}) translate(${parentRect.width/2},${parentRect.height/2})`)
                //         // .attr('transform', `translate(${parentRect.width/4}, ${parentRect.height/4})`)
                //     // .attr("transform", `scale(${scale/1000})`);

                //     console.log('parentHeight: ', parentRect.height)
            }

        },
        initLegend() {

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
            console.log('resize!')
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.mapData'(mapData) { // when data changes
            console.log('store.mapData!')
            if (!isEmpty(mapData)) {
                this.rerender()
            }
        },
        'store.geoMapData'(geoMapData) { // when data changes
            if (!isEmpty(geoMapData)) {
                this.rerender()
            }
        },
        'store.points'(newPoints) { // when data changes
            if (!isEmpty(newPoints)) {
                //Call and set the other api based on points, with POST method
                // set data for bar chart based on results from post
                this.rerender()
            }
        }
    },
    mounted() {
        window.addEventListener('resize', debounce(this.onResize, 100))
        this.onResize()
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
    height: 100%;
    width: 100%;
}
</style>