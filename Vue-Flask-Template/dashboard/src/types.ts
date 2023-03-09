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