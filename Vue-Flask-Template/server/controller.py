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

    for i in range(len(df.incident_characteristics)):
        if pd.isna(df.incident_characteristics.iloc[i]) == False:
            if "mass shooting" in df.incident_characteristics[i].lower():
                mass_shooting[i] = True
            if "suicide" in df.incident_characteristics[i].lower():
                suicide[i] = True
            if "gang involvement" in df.incident_characteristics[i].lower():
                gang[i] = True
            if "dead" in df.incident_characteristics[i].lower():
                dead[i] = True
            if "wounded" in df.incident_characteristics[i].lower():
                wounded[i] = True
                
    df["suicide"] = suicide
    df["mass shooting"] = mass_shooting
    df["gang"] = gang
    df["wounded"] = wounded
    df["dead"] = dead

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
    if not os.path.exists(os.getcwd() +'../server/data/gunViolenceData.pickle'):
        preprocessGunViolenceData()
    

