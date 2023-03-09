import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA

from sklearn.datasets import load_wine
# from resources.hd_processing_template import perform_PCA, perform_TSNE
#from resources.network_process_template import contsruct_networkx
#from resources.text_processing_template import preprocess
#from resources.time_processing_template import prepare_time_template_data, apply_arima, apply_sarima

# def processExample(method: str = 'PCA') -> tuple[list[dict], list[int]]:
    # data: dict = load_wine()
    # X: np.ndarray = data.data
    # y: np.ndarray = data.target
    # #feat_names: np.ndarray = data.feature_names
    # target_names: np.ndarray = data.target_names

    # if method == 'PCA':
    #     Z, _ = perform_PCA(X)
    # elif method == 't-SNE':
    #     Z = perform_TSNE(X, perplexity = 10)
    # else:
    #     raise ValueError("Requested a method that is not supported")
    # points = pd.DataFrame(Z, columns=['posX', 'posY'])
    # points['cluster'] = y
    # # How to JSON serialize pandas dataframes and numpy arrays
    # return points.to_dict(orient='records'), list(target_names)

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
    df["mass_shooting"] = mass_shooting
    df["gang"] = gang
    df["wounded"] = wounded
    df["dead"] = dead
    df["non_suicide"] = non_suicide
    df.to_pickle("../server/data/gunViolenceData.pickle")


def preprocessGunViolenceMetadata():
    gun_violence_data_filepath = '../server/data/gunViolenceData.pickle'
    population_data_filepath = '../server/data/populationData.xlsx'

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, gun_violence_data_filepath)
    if not os.path.exists(filename):
        preprocessGunViolenceData()
    
    # create gun violence metadata
    gun_violence_data = pd.read_pickle(gun_violence_data_filepath)
    all_incidents = gun_violence_data[['year', 'state']].groupby(['state', 'year']).size()
    all_incidents.name = 'all_incidents'
    gun_violence_metadata = gun_violence_data[['year', 'state', 'suicide', 'mass_shooting', 'gang', 'non_suicide']].groupby(['state', 'year']).sum().astype(int)
    gun_violence_metadata = gun_violence_metadata.join(all_incidents)

    # load and preprocess population data
    population_data = pd.read_excel(population_data_filepath, header=3, skiprows=[62, 63, 64, 65, 66, 67])
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
    metadata_df = metadata_df[metadata_df.year < 2019]

    metadata_df.to_pickle('../server/data/policyMetadata.pickle')  


def processMap(min_year: int = 2014, max_year: int = 2018):
    policy_data_filepath = "../server/data/policyDatabase.xlsx"
    gun_violence_metadata_filepath = '../server/data/gunViolenceMetadata.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, gun_violence_metadata_filepath)
    if not os.path.exists(filename):
        print("path doesn't exist")
        preprocessGunViolenceMetadata()
    gun_violence_metadata = pd.read_pickle(gun_violence_metadata_filepath)
    policy_data = pd.read_excel(policy_data_filepath).set_index(['year', 'state'])
    map_data = gun_violence_metadata.join(policy_data[['lawtotal']])
    map_data = map_data.reset_index()
    # filter by year range
    map_data = map_data[(map_data.year >= min_year) & (map_data.year <= max_year)].set_index(['state'])
    # get average within range
    map_data = map_data.groupby(by=['state']).mean()
    map_data =  map_data[['all_incidents', 'lawtotal']].reset_index()
    map_data.rename(columns={'lawtotal': 'policies_implemented', 'all_incidents':'incidents_per_capita'})

    return map_data.to_dict(orient='records')


def processPolicyScatterplot(num_clusters: int = 3, method: str = 'PCA'):
    cluster_names = []
    for i in range(num_clusters):
        cluster_names.append(f'cluster {i + 1}')

    # if we have calculated this already, it is much faster to save the result
    # and return it than recalculate it every time 
    output_filepath = f'../server/data/policyClusters_{num_clusters}_{method}.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, output_filepath)
    if os.path.exists(filename):
        df_embeddings = pd.read_pickle(output_filepath)
    else: 
        # load data
        data_filepath = "../server/data/policyDatabase.xlsx"
        df = pd.read_excel(data_filepath)
        df = df[(df.year > 2013) & (df.year < 2019)]
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
        df_embeddings['cluster'] = predictions
        df_embeddings['state'] = list(df['state'])
        df_embeddings['year'] = list(df['year'])
        df_embeddings["dimension1"] = data_embedded[:, 0]
        df_embeddings["dimension2"] = data_embedded[:, 1]

        df_embeddings.to_pickle(output_filepath)

    return df_embeddings.to_dict(orient='records'), list(cluster_names)


def processGroupedBarChart(policy_clusters: dict, cluster_names:list):
    """
    I'm expecting clusters to be the same data that is outputted 
    by processPolicyScatterplot
    NOTE: Might need to log scale the bar chart data because numbers are so small
    """
    gun_violence_metadata_filepath = '../server/data/gunViolenceMetadata.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, gun_violence_metadata_filepath)
    if not os.path.exists(filename):
        preprocessGunViolenceMetadata()
    gun_violence_metadata = pd.read_pickle(gun_violence_metadata_filepath)

    policy_clusters = pd.DataFrame(policy_clusters)
    policy_clusters.set_index(['state', 'year'], inplace=True)
    print(policy_clusters.index)
    all_data = gun_violence_metadata.join(policy_clusters)
    
    data = []
    for stat in gun_violence_metadata.columns:
        stat_data = {'group':stat}
        for cluster in range(len(cluster_names)):
            stat_data[cluster_names[cluster]] = all_data[all_data.cluster == cluster][stat].mean()
        data.append(stat_data)



    return data


def processPolicyClusterCategories(policy_clusters: dict, target_cluster: int):
    """
    I'm expecting clusters to be the same data that is outputted 
    by processPolicyScatterplot
    """
    policy_metadata_filepath = '../server/data/policyMetadata.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, policy_metadata_filepath)
    if not os.path.exists(filename):
        preprocessPolicyMetadata()
    
    policy_metadata = pd.read_pickle(policy_metadata_filepath)
    policy_metadata.set_index(['year', 'state'], inplace=True) # for grouping purposes
    policy_clusters = pd.DataFrame(policy_clusters)

    target_cluster_data = policy_clusters[policy_clusters.cluster == target_cluster]
    target_cluster_data.set_index(['year', 'state'], inplace=True) # for grouping purposes

    all_data = target_cluster_data.join(policy_metadata, on=['year', 'state'])
    all_data.reset_index(inplace=True)
    all_data = all_data[['sub_category', 'policies_implemented']]
    all_data = all_data.groupby('sub_category').mean()
    all_data.sort_values('policies_implemented', ascending=False, inplace=True)
    all_data.reset_index(inplace=True)

    return all_data.to_dict(orient='records')

    
if __name__ == "__main__":
    os.chdir('C:/Users/nammy/Desktop/ECS-273-Project/Vue-Flask-Template/dashboard/')
    print(processMap())
