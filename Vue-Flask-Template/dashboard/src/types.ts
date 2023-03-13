// Global types and interfaces are stored here.
export interface Margin {
    readonly left: number;
    readonly right: number;
    readonly top: number;
    readonly bottom: number;
}

export interface ComponentSize {
    width: number;
    height: number;
}

export interface Point {
    readonly posX: number;
    readonly posY: number;
}


export interface PolicyPoint {
    readonly dimension1: number;
    readonly dimension2: number;
    readonly cluster: string;
}

export interface GroupedBar {
    readonly group: string;
    readonly "cluster 1": number;
    readonly "cluster 2": number;
    readonly "cluster 3": number;
}

export interface PolicyCategory {
    readonly subgroup: string;
    readonly policies_implemented: number;
}

export interface MapState {
    readonly state: string;
    readonly incidents_per_capita: number;
    readonly policies_implemented: number;
    readonly cluster: number;
}

export interface TopPolicies {
    readonly state: string;
    readonly year: number;
    readonly top_policies: string[];
}


export interface MapDatum {
    readonly allIncidents: number;
    readonly lawTotal: number;
    readonly state: String;
}