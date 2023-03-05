import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from sklearn.datasets import load_wine
from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima

def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:
    data: dict = load_wine()
    X: np.ndarray = data.data
    y: np.ndarray = data.target
    #feat_names: np.ndarray = data.feature_names
    target_names: np.ndarray = data.target_names

    if method == 'PCA':
        Z, _ = perform_PCA(X)
    elif method == 't-SNE':
        Z = perform_TSNE(X, perplexity = 10)
    else:
        raise ValueError("Requested a method that is not supported")
    points = pd.DataFrame(Z, columns=['posX', 'posY'])
    points['cluster'] = y
    # How to JSON serialize pandas dataframes and numpy arrays
    return points.to_dict(orient='records'), list(target_names)


def preprocessGunViolenceData():
    gun_violence_data_filepath = "../server/data/gunViolenceData.csv"

    df = pd.read_csv(gun_violence_data_filepath)
    df['year'] = pd.DatetimeIndex(df['date']).year
    df = df[df.state != 'District of Columbia']
    df = df[df.year > 2013]
    df.reset_index(inplace=True)

    # parsing data for keywords

    suicide = [False] * len(df)
    mass_shooting = [False] * len(df)
    gang = [False] * len(df)
    wounded = [False] * len(df)
    dead = [False] * len(df)
    non_suicide = [False] * len(df)

    for i in range(len(df.incident_characteristics)):
        if pd.isna(df.incident_characteristics.iloc[i]) == False:
            if "mass shooting" in df.incident_characteristics[i].lower():
                mass_shooting[i] = True
            if "Suicide" in df.incident_characteristics[i]:
                suicide[i] = True
            if "gang involvement" in df.incident_characteristics[i].lower():
                gang[i] = True
            if "Dead" in df.incident_characteristics[i]:
                dead[i] = True
            if "Wounded" in df.incident_characteristics[i]:
                wounded[i] = True
            if "Suicide^" not in df.incident_characteristics[i] and "Suicide - Attempt" not in df.incident_characteristics[i]:
                non_suicide[i] = True
                
                
    df["suicide"] = suicide
    df["mass shooting"] = mass_shooting
    df["gang"] = gang
    df["wounded"] = wounded
    df["dead"] = dead
    df["non-suicide"] = non_suicide
    df.to_pickle("../server/data/gunViolenceData.pickle")


def preprocessPolicyMetadata():
    policy_data_filepath = "../server/data/policyDatabase.xlsx"
    policy_codebook_filepath = "../server/data/policyCodebook.xlsx"

    policies = pd.read_excel(policy_data_filepath)
    codebook = pd.read_excel(policy_codebook_filepath)

    sub_categories = {}
    for category in set(codebook['Sub-Category']):
        sub_categories[category] = list(codebook[codebook['Sub-Category'] == category]['Variable Name'])

    metadata = {'year':[], 'state':[], 'category':[], 'sub_category':[], 'policies_implemented':[]}
    for i in range(len(policies)):
        for j, (sub_category, variables) in enumerate(sub_categories.items()):
            metadata['year'].append(policies.year[i])
            metadata['state'].append(policies.state[i])
            metadata['category'].append(codebook[codebook['Sub-Category'] == sub_category].Category.iloc[0])
            metadata['sub_category'].append(sub_category)
            policies_implemented = 0
            for variable in variables:
                policies_implemented += policies[variable][i]
            metadata['policies_implemented'].append(policies_implemented)

    metadata_df = pd.DataFrame(metadata)
    metadata_df.sort_values(['year', 'state', 'category'], inplace=True)
    metadata_df = metadata_df[metadata_df.year > 2013]
    metadata_df = metadata_df[metadata_df.year < 2021]

    metadata_df.to_pickle('../server/data/policyMetadata.pickle', index=False)

def preprocessGunViolenceMetadata():
    gun_violence_data_filepath = '../server/data/gunViolenceData.pickle'
    population_data_filepath = '../server/data/populationData.xlsx'

    if not os.path.exists(os.getcwd() + gun_violence_data_filepath):
        preprocessGunViolenceData()
    
    # create gun violence metadata
    gun_violence_data = pd.read_pickle(gun_violence_data_filepath)
    all_incidents = gun_violence_data[['year', 'state']].groupby(['state', 'year']).size()
    all_incidents.name = 'all incidents'
    gun_violence_metadata = gun_violence_data[['year', 'state', 'suicide', 'mass shooting', 'gang', 'non-suicide']].groupby(['state', 'year']).sum().astype(int)
    gun_violence_metadata = gun_violence_metadata.join(all_incidents)

    # load and preprocess population data
    population_data = pd.read_excel(population_data_filepath)
    population_data.rename(columns={'July 1': 2020}, inplace=True)
    population_data.dropna(inplace=True)
    population_data['state'] = population_data['Unnamed: 0'].str.replace('[^\w\s]','')
    population_data = pd.melt(population_data, id_vars=['state'], value_vars=[2014, 2015, 2016, 2017, 2018, 2019, 2020])
    population_data.rename(columns={'variable': 'year', 'value':'population'}, inplace=True)

    # get metadata per capita instead of total counts
    gun_violence_metadata['population'] = list(gun_violence_metadata.merge(population_data, on=['year', 'state'], how='left')['population'])
    gun_violence_metadata = gun_violence_metadata.div(gun_violence_metadata['population'], axis=0).drop(columns=['population'])

    # store data
    gun_violence_metadata.to_pickle('../server/data/gunViolenceMetadata.pickle')   


def processPolicyScatterplot(num_clusters: int = 3, method: str = 'PCA'):
    # load data
    data_filepath = "../server/data/policyDatabase.xlsx"
    df = pd.read_excel(data_filepath)
    X = df.drop(columns=['state', 'year', 'lawtotal'])

    # cluster data
    clusterer = KMeans(n_clusters=num_clusters, init='k-means++')
    predictions = clusterer.fit_predict(X)

    if method == 'PCA':
        pca = PCA(n_components=2)
        data_embedded = pca.fit_transform(X)

    elif method == 't-SNE':
        tsne = TSNE(n_components=2, verbose=1)
        data_embedded = tsne.fit_transform(X)
    else:
        raise ValueError("Requested a method that is not supported")
    
    df_embeddings = pd.DataFrame()
    df_embeddings["cluster"] = predictions
    df_embeddings['state'] = list(df['state'])
    df_embeddings['year'] = list(df['year'])
    df_embeddings["dimension1"] = data_embedded[:, 0]
    df_embeddings["dimension2"] = data_embedded[:, 1]

    cluster_names = []
    for i in range(num_clusters):
        cluster_names.append(f'cluster {i + 1}')

    return df_embeddings.to_dict(orient='records'), list(cluster_names)


def processGroupedBarChart(cluster_labels: list):
    if not os.path.exists(os.getcwd() +'../server/data/gunViolenceMetadata.pickle'):
        preprocessGunViolenceMetadata()
    

