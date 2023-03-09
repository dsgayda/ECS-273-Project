import { defineStore } from 'pinia'
import axios from "axios"
import { isEmpty } from 'lodash';
import { server } from '../helper';

import { Point, ComponentSize, Margin, GroupedBar } from '../types';
interface ScatterPoint extends Point{
    cluster: string;
}

export const usePolicyScatterplot = defineStore('policyScatterplot', {
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
        async fetchPolicyScatterplot() { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            axios.get(`${server}/fetchPolicyScatterplot`)
                .then(resp => {
                    this.points = resp.data.data; 
                    this.clusters = resp.data.clusters;
                    return true;
                    })
                .catch(error => console.log(error));
        },
        async fetchGroupedBarChart() { // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
            
            if (this.points && this.clusters) {
            console.log('in fetch grouped bar chart!')
            const data = {
                points: this.points,
                cluster_names: this.clusters
            };
            axios.post(`${server}/fetchGroupedBarChart`, data,
            {
                withCredentials: true // include cookies with the request! Hooray!
            })
            .then(resp => { // check out the app.py in ./server/ to see the format
                this.bars = resp.data.data;
                this.clusters = resp.data.clusters;
                return true;
            })
            .catch(error => console.log(error));
                console.log('finished with fetch bar chart')
        }
        else {
            console.log('Did not run fetchGroupedBarChart()')
            return true;
        }
        },
    }
})