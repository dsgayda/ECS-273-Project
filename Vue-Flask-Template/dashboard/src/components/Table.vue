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
import * as labs from 'vuetify/labs/'

// Import Vuetify components
// import { VDataTable } from 'vuetify/lib';

export default {
    components: {
        VDataTable
    },
    data() {
        return {
            search: '',
            selectedValue: "All Incidents",
            headers6: [
                { title: 'category', align: 'start', sortable: true, key: 'category' },
                { title: 'correlation', align: 'end', key: 'correlation' },
                { title: 'cluster 1', align: 'end', key: 'cluster 0' },
                { title: 'cluster 2', align: 'end', key: 'cluster 1' },
                { title: 'cluster 3', align: 'end', key: 'cluster 2' },
                { title: 'cluster 4', align: 'end', key: 'cluster 3' },
                { title: 'cluster 5', align: 'end', key: 'cluster 4' },
                { title: 'cluster 6', align: 'end', key: 'cluster 5' },
            ],
            headers5: [
                { title: 'category', align: 'start', sortable: true, key: 'category' },
                { title: 'correlation', align: 'end', key: 'correlation' },
                { title: 'cluster 1', align: 'end', key: 'cluster 0' },
                { title: 'cluster 2', align: 'end', key: 'cluster 1' },
                { title: 'cluster 3', align: 'end', key: 'cluster 2' },
                { title: 'cluster 4', align: 'end', key: 'cluster 3' },
                { title: 'cluster 5', align: 'end', key: 'cluster 4' },
            ],
            headers4: [
                { title: 'category', align: 'start', sortable: true, key: 'category' },
                { title: 'correlation', align: 'end', key: 'correlation' },
                { title: 'cluster 1', align: 'end', key: 'cluster 0' },
                { title: 'cluster 2', align: 'end', key: 'cluster 1' },
                { title: 'cluster 3', align: 'end', key: 'cluster 2' },
                { title: 'cluster 4', align: 'end', key: 'cluster 3' },
            ],
            headers3: [
                { title: 'category', align: 'start', sortable: true, key: 'category' },
                { title: 'correlation', align: 'end', key: 'correlation' },
                { title: 'cluster 1', align: 'end', key: 'cluster 0' },
                { title: 'cluster 2', align: 'end', key: 'cluster 1' },
                { title: 'cluster 3', align: 'end', key: 'cluster 2' },
            ],
            headers2: [
                { title: 'category', align: 'start', sortable: true, key: 'category' },
                { title: 'correlation', align: 'end', key: 'correlation' },
                { title: 'cluster 1', align: 'end', key: 'cluster 0' },
                { title: 'cluster 2', align: 'end', key: 'cluster 1' },
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
                if (!isEmpty(newPoints)) {// when data changes
                    console.log('updating table based on new points')
                    // suicide  mass_shooting          gang  non_suicide
                    const data = {
                        data: this.store.points,
                        clusters: this.store.clusters,
                        incidentType: 'non_suicide'
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

                    this.tableItems = table;
                    //Call and set the other api based on points, with POST method
                    // set data for bar chart based on results from post
                    this.rerender()

                }
            },
            immediate: true,
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
                    'Non-Suicide': 'non_suicide'
                };

                const data = {
                        data: this.store.points,
                        clusters: this.store.clusters,
                        incidentType: incidentMap[newVal]
                    };
                        
                    let table = await this.store.fetchTableData(data);
                    this.tableItems = table;
                    //Call and set the other api based on points, with POST method
                    // set data for bar chart based on results from post
                    this.rerender()

                
                // this.store.selectedValue = newVal;
            },
            immediate: true
        }
    },
    // The following are general setup for resize events.
    async mounted() {
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
    <div v-if="isDataReady" style="max-height: 50% overflow-y: hidden" class="table-container d-flex"
        ref="tableContainer">
        <div v-if="sixHeaders">
            <v-card>
            <v-card-title>
                <v-row>
                    <v-col cols="8">
            Policy Correlations and Clusters
                </v-col>
                <v-col cols="4">
            <v-select
            :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide']"
            label="Correlation"
            density="compact"
            v-model="selectedValue"
            ></v-select>
            </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
            ></v-text-field>
            </v-card-title>
        </v-card>
            <v-data-table :headers="headers6" :items="tableItems" :search="search" density="compact" items-per-page="50"
                :footer-props="{ 'items-per-page-options': [5, 10, 25] }" class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-if="fiveHeaders">
            <v-card>
            <v-card-title>
                <v-row>
                    <v-col cols="8">
            Policy Correlations and Clusters
                </v-col>
                <v-col cols="4">
            <v-select
            :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide']"
            label="Correlation"
            density="compact"
            v-model="selectedValue"
            ></v-select>
            </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
            ></v-text-field>
            </v-card-title>
        </v-card>
            <v-data-table :headers="headers5" :items="tableItems" :search="search" density="compact" items-per-page="50"
                :footer-props="{ 'items-per-page-options': [5, 10, 25] }" class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="fourHeaders">
            <v-card>
            <v-card-title>
                <v-row>
                    <v-col cols="8">
            Policy Correlations and Clusters
                </v-col>
                <v-col cols="4">
            <v-select
            :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide']"
            label="Correlation"
            density="compact"
            v-model="selectedValue"
            ></v-select>
            </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
            ></v-text-field>
            </v-card-title>
        </v-card>
            <v-data-table :headers="headers4" :items="tableItems" :search="search" density="compact" items-per-page="50"
                :footer-props="{ 'items-per-page-options': [5, 10, 25] }" class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="threeHeaders">
            <v-card>
            <v-card-title>
                <v-row>
                    <v-col cols="8">
            Policy Correlations and Clusters
                </v-col>
                <v-col cols="4">
            <v-select
            :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide']"
            label="Correlation"
            density="compact"
            v-model="selectedValue"
            ></v-select>
            </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
            ></v-text-field>
            </v-card-title>
        </v-card>
            <v-data-table :headers="headers3" :items="tableItems" :search="search" density="compact" items-per-page="50"
                :footer-props="{ 'items-per-page-options': [5, 10, 25] }" class="elevation-1 my-data-table"></v-data-table>
        </div>
        <div v-else-if="twoHeaders">
            <v-card>
            <v-card-title>
                <v-row>
                    <v-col cols="8">
            Policy Correlations and Clusters
                </v-col>
                <v-col cols="4">
            <v-select
            :items="['All Incidents', 'Gang Related', 'Suicide', 'Non-Suicide']"
            label="Correlation"
            density="compact"
            v-model="selectedValue"
            ></v-select>
            </v-col>
            </v-row>
            <v-spacer></v-spacer>
            <v-text-field
                v-model="search"
                append-icon="mdi-magnify"
                label="Search"
                single-line
                hide-details
            ></v-text-field>
            </v-card-title>
        </v-card>
            <v-data-table :headers="headers2" :items="tableItems" :search="search" density="compact" items-per-page="50"
                :footer-props="{ 'items-per-page-options': [5, 10, 25] }" class="elevation-1 my-data-table"></v-data-table>
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
