<script lang="ts">
import * as d3 from "d3";
import axios from 'axios';
import { isEmpty, debounce } from 'lodash';
import { server } from '../helper';
import { watch, ref, toRefs, computed } from 'vue';

import { DataTableHeader, TableItem } from '../types';

import { mapState, storeToRefs } from 'pinia';
import { useDataStore } from '../stores/dataStore';
import { createVuetify } from 'vuetify'
import { VDataTable } from 'vuetify/labs/VDataTable'

import { VDataTableVirtual } from 'vuetify/labs/VDataTable'

// Import Vuetify components
// import { VDataTable } from 'vuetify/lib';

export default {
    components: {
        VDataTable,
        // VDataTableVirtual
    },
    data() {
        return {
            tableHeight: '250',
            tableWidth: '100',
            search: '',
            selectedValue: "All Incidents",
            itemsPerPage: 50,
            headers6: [
                { title: 'Category', align: 'start', sortable: true, key: 'category' },
                { title: 'Indicator', align: 'end', sortable: true, key: 'correlation' },
                { title: 'Cluster 1 (%)', align: 'end', sortable: true, key: 'cluster 0' },
                { title: 'Cluster 2 (%)', align: 'end', sortable: true, key: 'cluster 1' },
                { title: 'Cluster 3 (%)', align: 'end', sortable: true, key: 'cluster 2' },
                { title: 'Cluster 4 (%)', align: 'end', sortable: true, key: 'cluster 3' },
                { title: 'Cluster 5 (%)', align: 'end', sortable: true, key: 'cluster 4' },
                { title: 'Cluster 6 (%)', align: 'end', sortable: true, key: 'cluster 5' },
            ],
            headers5: [
                { title: 'Category', align: 'start', sortable: true, key: 'category' },
                { title: 'Indicator', align: 'end', sortable: true, key: 'correlation' },
                { title: 'Cluster 1 (%)', align: 'end', sortable: true, key: 'cluster 0' },
                { title: 'Cluster 2 (%)', align: 'end', sortable: true, key: 'cluster 1' },
                { title: 'Cluster 3 (%)', align: 'end', sortable: true, key: 'cluster 2' },
                { title: 'Cluster 4 (%)', align: 'end', sortable: true, key: 'cluster 3' },
                { title: 'Cluster 5 (%)', align: 'end', sortable: true, key: 'cluster 4' },
            ],
            headers4: [
                { title: 'Category', align: 'start', sortable: true, key: 'category' },
                { title: 'Indicator', align: 'end', sortable: true, key: 'correlation' },
                { title: 'Cluster 1 (%)', align: 'end', sortable: true, key: 'cluster 0' },
                { title: 'Cluster 2 (%)', align: 'end', sortable: true, key: 'cluster 1' },
                { title: 'Cluster 3 (%)', align: 'end', sortable: true, key: 'cluster 2' },
                { title: 'Cluster 4 (%)', align: 'end', sortable: true, key: 'cluster 3' },
            ],
            headers3: [
                { title: 'Category', align: 'start', sortable: true, key: 'category' },
                { title: 'Indicator', align: 'end', sortable: true, key: 'correlation' },
                { title: 'Cluster 1 (%)', align: 'end', sortable: true, key: 'cluster 0' },
                { title: 'Cluster 2 (%)', align: 'end', sortable: true, key: 'cluster 1' },
                { title: 'Cluster 3 (%)', align: 'end', sortable: true, key: 'cluster 2' },
            ],
            headers2: [
                { title: 'Category', align: 'start', sortable: true, key: 'category' },
                { title: 'Indicator', align: 'end', sortable: true, key: 'correlation' },
                { title: 'Cluster 1 (%)', align: 'end', sortable: true, key: 'cluster 0' },
                { title: 'Cluster 2 (%)', align: 'end', sortable: true, key: 'cluster 1' },
            ]
        }
    },
    setup() {
        const store = useDataStore()
        // Alternative expression from computed
        const { resize } = storeToRefs(store);
        const { points } = storeToRefs(store);
        const { clusters } = storeToRefs(store);
        const { size } = storeToRefs(store);
        const { margin } = storeToRefs(store);
        const { color } = storeToRefs(store);
        const { table } = storeToRefs(store);

        const tableHeaders = ref<DataTableHeader[]>([]);
        const tableItems = ref<TableItem[]>([]);
        const showDataTable = 5;

        const isDataReady = computed(() => {
            return tableItems?.value?.length > 0 && tableHeaders?.value?.length > 0;
        });

        const sixHeaders = computed(() => {

            if (tableHeaders.value.length === 8) {
                return true;
            }
            return false;
        });

        const fiveHeaders = computed(() => {

            if (tableHeaders.value.length === 7) {
                return true;
            }
            return false;
        });
        const fourHeaders = computed(() => {
            if (tableHeaders.value.length === 6) {
                return true;
            }
            return false;
        });
        const threeHeaders = computed(() => {
            if (tableHeaders.value.length === 5) {
                return true;
            }
            return false;
        });
        const twoHeaders = computed(() => {
            if (tableHeaders.value.length === 4) {
                return true;
            }
            return false;
        });



        let isDataLoaded = false;
        return {
            isDataReady,
            sixHeaders,
            fiveHeaders,
            fourHeaders,
            threeHeaders,
            twoHeaders,
            store,
            table,
            tableHeaders,
            tableItems,
            showDataTable,
            isDataLoaded
        }
    },
    created() {

    },

    methods: {
        onResize() {  // record the updated size of the target element
            let target = this.$refs.tableContainer as HTMLElement
            if (target === undefined) return;
            this.size = { width: target.clientWidth, height: target.clientHeight };
            
            this.tableHeight = target.clientHeight.toString();
            // this.tableWidth = target.clientWidth.toString();
            const box = document.querySelector('.v-data-table-footer')
                if (box) {
                box.remove()
                }
        },
        initChart() {
            // let tabbb = d3.selectAll('td')
            // .style('font-size', '.8rem')


        },
        rerender() {
            // d3.selectAll('.table-container').selectAll('*').remove() // Clean all the elements in the chart
            this.initChart()
        },

    },
    watch: {
        resize(newSize) { // when window resizes
            if ((newSize.width !== 0) && (newSize.height !== 0)) {
                this.rerender()
            }
        },
        'store.points': {
            async handler(newPoints) {
                if (!isEmpty(newPoints) ) {// when data changes
                    console.log('updating table based on new points')


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

                    let table = await this.store.fetchTableData(data);

                    this.tableHeaders = [];
                    for (let i = 0; i < Object.keys(table[0]).length; i++) {
                        if (i === 0) {
                            this.tableHeaders.push({
                                text: Object.keys(table[0])[i],
                                align: "start",
                                sortable: true,
                                key: Object.keys(table[0])[i],
                            });
                        } else {
                            this.tableHeaders.push({
                                text: Object.keys(table[0])[i],
                                align: "end",
                                sortable: false,
                                key: Object.keys(table[0])[i],
                            });
                        }
                    }

                    for (let i in table) {
                        for (let key in table[i]) {
                            if (key !== 'category' && key !== 'correlation') {

                                let percentageString = (table[i][key] * 100).toFixed(2) + '%';
                                const percentage = parseFloat(percentageString);

                                if (percentage.toFixed(2).slice(-2) === '00') {
                                    percentageString = percentage.toFixed(0) + '%';
                                } else {
                                    percentageString = percentage.toFixed(2) + '%';
                                }
                                table[i][key] = parseFloat((table[i][key] * 100).toFixed(2))
                                // table[i][key] = percentageString;
                            }
                        }
                    }

                    this.tableItems = table;

                    //Call and set the other api based on points, with POST method
                    // set data for bar chart based on results from post
                    this.rerender()

                }
            },
        },
        'store.tableHeaders'(newHeaders) {
            this.rerender();
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
                    incidentType: incidentMap[newVal]
                };

                let table = await this.store.fetchTableData(data);
                this.tableItems = table;
                //Call and set the other api based on points, with POST method
                // set data for bar chart based on results from post
                this.rerender()


                // this.store.selectedValue = newVal;
            },
        }
    },
    // The following are general setup for resize events.
    async mounted() {
        let target = this.$refs.tableContainer as HTMLElement
        this.tableHeight = target.clientHeight.toString()
        window.addEventListener('resize', debounce(this.onResize, 100));
        this.onResize();
    },

    beforeDestroy() {
        window.removeEventListener('resize', this.onResize)
    }
    //... rest of the code
}
</script>

<template>
    <div v-if="isDataReady" style="max-height: 100% overflow-y: hidden" class="table-container" ref="tableContainer">
        <div v-if="sixHeaders">
            <v-card>
                <v-card-title>
                    <v-row>
                        <v-col cols="12">
                            Policy-Incident Correlations and Clusters
                        </v-col>
                    </v-row>
                    <v-spacer></v-spacer>
                    <v-row>
                        <v-col cols="4">
                            <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']"
                                label="Correlation" density="compact" v-model="selectedValue"></v-select>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                                hide-details></v-text-field>

                        </v-col>
                    </v-row>

                </v-card-title>
            </v-card>
            <v-data-table
    v-model:items-per-page="itemsPerPage" :headers="headers6" :items="tableItems" :search="search" density="compact"
                :height="tableHeight" :hide-default-footer="true"
                class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-if="fiveHeaders">
            <v-card>
                <v-card-title>
                    <v-row>
                        <v-col cols="12">
                            Policy-Incident Correlations and Clusters
                        </v-col>
                    </v-row>
                    <v-spacer></v-spacer>
                    <v-row>
                        <v-col cols="4">
                            <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']"
                                label="Correlation" density="compact" v-model="selectedValue"></v-select>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                                hide-details></v-text-field>

                        </v-col>
                    </v-row>

                </v-card-title>
            </v-card>
            <v-data-table
    v-model:items-per-page="itemsPerPage" :headers="headers5" :items="tableItems" :search="search" density="compact"
                :height="tableHeight" :hide-default-footer="true"
                class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="fourHeaders">
            <v-card>
                <v-card-title>
                    <v-row>
                        <v-col cols="12">
                            Policy-Incident Correlations and Clusters
                        </v-col>
                    </v-row>
                    <v-spacer></v-spacer>
                    <v-row>
                        <v-col cols="4">
                            <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']"
                                label="Correlation" density="compact" v-model="selectedValue"></v-select>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                                hide-details></v-text-field>

                        </v-col>
                    </v-row>

                </v-card-title>
            </v-card>
            <v-data-table
    v-model:items-per-page="itemsPerPage" :headers="headers4" :items="tableItems" :search="search" density="compact"
                :height="tableHeight" :hide-default-footer="true"
                class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="threeHeaders">
            <v-card>
                <v-card-title>
                    <v-row>
                        <v-col cols="12">
                            Policy-Incident Correlations and Clusters
                        </v-col>
                    </v-row>
                    <v-spacer></v-spacer>
                    <v-row>
                        <v-col cols="4">
                            <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']"
                                label="Correlation" density="compact" v-model="selectedValue"></v-select>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                                hide-details></v-text-field>

                        </v-col>
                    </v-row>

                </v-card-title>
            </v-card>

            <v-data-table
    v-model:items-per-page="itemsPerPage" :headers="headers3" :items="tableItems" :search="search" density="compact"
                :height="tableHeight" :hide-default-footer="true"
                class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="twoHeaders">
            <v-card>
                <v-card-title>
                    <v-row>
                        <v-col cols="12">
                            Policy-Incident Correlations and Clusters
                        </v-col>
                    </v-row>
                    <v-spacer></v-spacer>
                    <v-row>
                        <v-col cols="4">
                            <v-select :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide', 'Mass Shooting']"
                                label="Correlation" density="compact" v-model="selectedValue"></v-select>
                        </v-col>
                        <v-col cols="8">
                            <v-text-field v-model="search" append-icon="mdi-magnify" label="Search" single-line
                                hide-details></v-text-field>

                        </v-col>
                    </v-row>

                </v-card-title>
            </v-card>
            <v-data-table
    v-model:items-per-page="itemsPerPage" :headers="headers2" :items="tableItems" :search="search" density="compact"
                :height="tableHeight" :hide-default-footer="true"
                class="elevation-1 my-data-table"></v-data-table>
        </div>
    </div>
    <div v-else class="vdiv">
        <h3>Loading...</h3>
    </div>
</template>



<style>
.vdiv {
    overflow-y: auto;
}

.elevation-1 {
    max-height: 100px;
}

.my-data-table {
    width: 100%;
}

.table-container {
    height: calc(50%);
}
</style>
