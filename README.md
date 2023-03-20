# ECS-273-Project
This repository contains the code, documentation, and methods used for the ECS 273 project.

The following is a view of the application dashboard.
![alt text](https://user-images.githubusercontent.com/91343348/226229799-0e4753b3-f3bb-4d9c-a4b5-6b6e203643d0.png)


## Functionality
The application was built on the same framework as the warm-up homework under the `./Assignment/Vue-Flask-Template` directory.


### Interactions
- **Cluster Selection** - On hover over scatterplot points or bars in the bar chart, all corresponding groups of elements in visualization views will be highlighted.

- **Dimensionality Reduction Selection** - Drop-down selection of multiple dimensionality reduction methods to update scatterplot spacing

- **Incident Type Selection** - Drop-down selection of incident types that update map encodings based on new heatmap scale. Legend also updates for new corresponding incidents.

- **Correlation Selection** - Drop-down selection of incidents to update calculations in the Policy-Incident Correlations and Clusters table.

- **Map Zoom & Pan** - Map is zoom/pan is enabled with typical browser zoom, and click to drag pan capabilities.

- **Table Scroll, Sort, and Search** - The Policy-Incident Correlations and Clusters table supports a scrollable unlimited amound of rows, sortable asc./desc. based on headers, and supports filtering of the data in rows via the search bar.

- **Window Size** - The layout supports mainly large full screen displays, but can be resized smaller after opening in full screen. Layout was created to restrict resizing to keep chart/map/plots in a size large enough to supports ease of analysis. Some scrolling is required if resized to smaller windows.

### Data Preparation and Pre-processing
- **Backend Server, APIs, & Data** - Data included under the directory `/src/server/data/clustering_data` and `/src/server/data/dimension_reduction_data` was preprocessed using the app.py and controller.py scripts. Data can be reprocessed by deleting `.pickle` files, and will recompute on page load of the application.

## Setting up Everything

### Step 1. Install Dependencies
The application was built on the same framework as the warm-up homework under the `./Assignment/Vue-Flask-Template` directory.

Install Python packages
```bash
cd Vue-Flask-Template
pip3 install -r requirements.txt
```
Install packages from package.json
```bash
cd dashboard 
npm install
```

### Step 1. Run the application
To start the application, under `./Assignment/Vue-Flask-Template/dashboard`, run
```bash
npm run start
```

*** Do to using different python virtual environments, if the npm start doesn't work, try the following command to run. The python 3 virtual environment uses the python command rather than python3 to start the server, therefore 2 separate npm commands were created depending on system environment. ***
```bash
npm run go
```
You can then visit `localhost:3000` in the browser to see the interface.