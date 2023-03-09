import { defineStore } from 'pinia'
import axios from "axios"
import { isEmpty } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin, GroupedBar } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

export const useDataStore = defineStore('dataStore', {
    state: () => ({
        points: [] as ScatterPoint[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
        bars: [] as GroupedBar[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
        clusters: [] as string[],
        size: { width: 0, height: 0 } as ComponentSize,
        margin: {left: 20, right: 20, top: 20, bottom: 40} as Margin,
}),
    getters: {
        resize: (state) => {
            return (!isEmpty(state.points) && state.size)
        }
    },
    actions: {
        async fetchData() { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            let resp = await axios.get(`${server}/fetchPolicyScatterplot`)
            this.points = resp.data.data; 
            this.clusters = resp.data.clusters;
            const data = {
                data: this.points,
                clusters: this.clusters
            };

            resp = await axios.post(`${server}/fetchGroupedBarChart`, data);
            this.bars = resp.data.data;
        }

    }
})