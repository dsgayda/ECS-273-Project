import { defineStore } from 'pinia'
import axios from "axios"
import { isEmpty } from 'lodash';
import { server } from '../helper';
import * as d3 from "d3";

import { PolicyPoint, ComponentSize, Margin, MapState, TopPolicies, GroupedBar, PolicyCategory, MapDatum} from '../types';

export const useDataStore = defineStore('dataStore', {
    state: () => ({
        points: [] as PolicyPoint[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
        states: [] as MapState[], 
        top_policies: [] as TopPolicies[],
        bars: [] as GroupedBar[], 
        clusters: [] as string[],
        categories: [] as PolicyCategory[],
        table: [] as any[],
        size: { width: 0, height: 0 } as ComponentSize,
        margin: {left: 70, right: 20, top: 20, bottom: 20} as Margin,
        color: d3.scaleOrdinal()
            .domain(['0', '1', '2', '3', '4', '5', '6'])
            .range(d3.schemeDark2),
        geoMapData: {},
}),
    getters: {
        resize: (state) => {
            console.log('resize in store')
            return (!isEmpty(state.points) && state.size)
        }
    },
    actions: {
        async fetchData(options?: {}) { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            let resp = await axios.get(`${server}/fetchPolicyScatterplot`)
            this.points = resp.data.data; 
            this.clusters = resp.data.clusters;
            
            const data = {
                data: this.points,
                clusters: this.clusters
            };

            resp = await axios.get(`${server}/fetchTopPoliciesPerPoint`);
            this.top_policies = resp.data.data;


            resp = await axios.post(`${server}/fetchGroupedBarChart`, data);
            this.bars = resp.data.data;

            resp = await axios.post(`${server}/fetchPolicyCorrelationTable`, data);
            this.table = resp.data.data;


            const getMap = { ...options };
            if (getMap) {
                resp = await axios.post(`${server}/fetchMap`, data);
                this.states = resp.data.data;

                resp = await axios.post(`${server}/fetchGeoMap`);
                this.geoMapData = resp.data;
            }
            

            // resp = await axios.post(`${server}/fetchPolicyClusterCategories`, data);
            // this.categories = resp.data.data;
        },
        // async fetchMap() { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
        //     axios.get(`${server}/fetchMap`)
        //         .then(resp => {
        //             this.mapData = resp.data.data;
        //             return true;
        //         })
        //         .catch(error => console.log(error));
        // },
        // async fetchGeoMap() { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            
        // }


    }
})