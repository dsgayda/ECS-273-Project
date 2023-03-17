import { defineStore } from "pinia";
import axios from "axios";
import { isEmpty } from "lodash";
import { server } from "../helper";
import * as d3 from "d3";

import {
  PolicyPoint,
  ComponentSize,
  Margin,
  MapState,
  TopPolicies,
  GroupedBar,
  PolicyCategory,
} from "../types";

export const useDataStore = defineStore("dataStore", {
  state: () => ({
    points: [] as PolicyPoint[], // "as <Type>" is a TypeScript expression to indicate what data structures this variable is supposed to store.
    methods: ['t-SNE', 'NMF', 'PCA'] as string[],
    states: [] as MapState[],
    top_policies: [] as TopPolicies[],
    bars: [] as GroupedBar[],
    clusters: [] as string[],
    categories: [] as PolicyCategory[],
    table: [] as any[],
    tableHeaders: [] as DataTableHeader[],
    tableItems: [] as TableItem[],
    numClusters: 3,
    size: { width: 0, height: 0 } as ComponentSize,
    margin: { left: 70, right: 20, top: 20, bottom: 20 } as Margin,
    color: d3
      .scaleOrdinal()
      .domain(["0", "1", "2", "3", "4"])
      .range(['#24a4d0', '#24d0a0', '#cdadf1', '#95bb88', '#343573', '#8e87da']),
    geoMapData: {},
  }),
  getters: {
    resize: (state) => {
      return !isEmpty(state.points) && state.size;
    },
  },
  actions: {
    async fetchData({numClusters = 3} = {}, {reductionType = "PCA"} = {}) {
      this.reductionType = reductionType;
      console.log('fetching data!: ', numClusters)
      // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
      let resp = await axios.post(`${server}/fetchPolicyScatterplot`,
      {
        numClusters: numClusters,
        reductionType: reductionType
      },
      {
        headers: {
          "Content-Type": "application/json",
        },
        
      });
      this.points = resp.data.data;
      this.clusters = resp.data.clusters;

      const data = {
        data: resp.data.data,
        clusters: resp.data.clusters,
      };

      resp = await axios.get(`${server}/fetchTopPoliciesPerPoint`);
      this.top_policies = resp.data.data;

      resp = await axios.post(`${server}/fetchGroupedBarChart`, data);
      this.bars = resp.data.data;

      // resp = await axios.post(`${server}/fetchPolicyClusterCategories`, data);
      // this.categories = resp.data.data;
    },
    async fetchGeoMap(data) {
      // same API request but in slightly different syntax when it's declared as a method in a component or an action in the store.
      try {
        const geoMapResponse = await axios.post(`${server}/fetchGeoMap`, {
          headers: {
            "Content-Type": "application/json",
          },
        });
        this.geoMapData = geoMapResponse.data;

        const geoMapData = geoMapResponse.data;
        const mapResponse = await axios.post(`${server}/fetchMap`, data);
        this.states = mapResponse.data.data;
        let states = mapResponse.data.data;

        return { geoMapData, states };
      } catch (error) {
        console.log("Error fetching geo map data:", error);
      }
      return;
    },
    async fetchTableData(data, retries = 3, delay = 2000) {
      try {
        const resp = await axios.post(`${server}/fetchPolicyCorrelationTable`, data);
        const table = resp.data.data;
        return table;
      } catch (error) {
        console.log("Error fetching table data:", error);
    
        if (retries > 0) {
          console.log(`Retrying in ${delay / 1000} seconds...`);
          await new Promise(resolve => setTimeout(resolve, delay));
          return this.fetchTableData(data, retries - 1, delay);
        } else {
          console.log("No more retries left.");
        }
      }
      return;
    },
  },
});
