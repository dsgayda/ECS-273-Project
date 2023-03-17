import pandas as pd
import numpy as np
import os
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from sklearn.decomposition import NMF
from pprint import pprint
import warnings
from pandas.errors import PerformanceWarning

warnings.filterwarnings("ignore", category=PerformanceWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from sklearn.datasets import load_wine

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

    metadata = {'year':[], 'state':[], 'category':[], 'sub_category':[], 'policies_implemented':[], 'percent_policies_implemented':[]}
    for i in range(len(policies)):
        for j, (sub_category, variables) in enumerate(sub_categories.items()):
            metadata['year'].append(policies.year[i])
            metadata['state'].append(policies.state[i])
            metadata['category'].append(codebook[codebook['Sub-Category'] == sub_category].Category.iloc[0])
            metadata['sub_category'].append(sub_category)
            policies_implemented = 0
            for variable in variables:
                policies_implemented += policies[variable][i]
            policies_implemented = policies_implemented
            percent_policies_implemented = policies_implemented / len(variables)
            metadata['policies_implemented'].append(policies_implemented)
            metadata['percent_policies_implemented'].append(percent_policies_implemented)


    metadata_df = pd.DataFrame(metadata)
    metadata_df.sort_values(['year', 'state', 'category'], inplace=True)
    metadata_df = metadata_df[metadata_df.year > 2013]
    metadata_df = metadata_df[metadata_df.year < 2019]

    metadata_df.to_pickle('../server/data/policyMetadata.pickle')  


def processMap(cluster_data: dict, min_year: int = 2014, max_year: int = 2018):
    """
    output columns: state, incidents_per_capita, policies_implemented, cluster
    """
    policy_data_filepath = "../server/data/policyDatabase.xlsx"
    gun_violence_metadata_filepath = '../server/data/gunViolenceMetadata.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, gun_violence_metadata_filepath)
    if not os.path.exists(filename):
        print("path doesn't exist")
        preprocessGunViolenceMetadata()

    # load data and join
    gun_violence_metadata = pd.read_pickle(gun_violence_metadata_filepath)
    policy_data = pd.read_excel(policy_data_filepath).set_index(['year', 'state'])
    map_data = gun_violence_metadata.join(policy_data[['lawtotal']])
    map_data = map_data.reset_index()
    # filter by year range
    map_data = map_data[(map_data.year >= min_year) & (map_data.year <= max_year)].set_index(['state'])
    # get average num incidents and policies within range
    map_data = map_data.groupby(by=['state']).mean()
    map_data =  map_data[['all_incidents', 'lawtotal']].reset_index()
    map_data.rename(columns={'lawtotal': 'policies_implemented', 'all_incidents':'incidents_per_capita'}, inplace=True)
    # now get cluster data
    cluster_data = pd.DataFrame(cluster_data)
    # get the state, cluster, and number of instances of the state within that cluster
    values = cluster_data[['state', 'cluster']].groupby(['state', 'cluster']).size().reset_index()
    values.rename(columns={0:'values'}, inplace=True)
    # group by state and find index of row with max value in each cluster
    # (i.e. find the cluster that the state is in the most)
    max_idx = values.groupby('state')['values'].idxmax()
    # select rows corresponding to max value in each group, and retrieve cluster value
    clusters = values.loc[max_idx, 'cluster']
    values = values.iloc[clusters.index]
    # add clusters to map data
    map_data = map_data.set_index(['state']).join(values.set_index(['state']))
    map_data.drop(columns=['values'], inplace=True)
    map_data.reset_index(inplace=True)
    return map_data.to_dict(orient='records')


def processTopPoliciesPerState(n_policies: int = 3):
    """
    output columns: state, year, top_policies
    """
    # load in policy metadata
    policy_metadata_filepath = '../server/data/policyMetadata.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, policy_metadata_filepath)
    if not os.path.exists(filename):
        preprocessPolicyMetadata()
    policy_metadata = pd.read_pickle(policy_metadata_filepath)

    # get top three policies for each state in each year
    policy_metadata.sort_values(['year', 'state','percent_policies_implemented', 'policies_implemented'], 
                                ascending=False, inplace=True)
    policy_metadata = policy_metadata.groupby(['year', 'state']).head(n_policies)
    policy_metadata.drop(columns=['category', 'policies_implemented', 'percent_policies_implemented'], inplace=True)
    policy_metadata.set_index(['year', 'state'], inplace=True)

    # return a list of top policies for each state in each year
    output_data = []
    for (year, state) in set(policy_metadata.index):
        top_policies = list(policy_metadata['sub_category'].loc[(year, state)])
        output_data.append({'year': year, 'state': state, 'top_policies': top_policies})
    
    return output_data


def processPolicyScatterplot(input_num_clusters: int = 3, input_method: str = 't-SNE'):
    # filter out the UserWarning
    warnings.filterwarnings("ignore", category=UserWarning)

    # create cluster labels
    cluster_names = [f'cluster {i + 1}' for i in range(input_num_clusters)]

    # check if we already have data:
    cluster_filepath = f'../server/data/clustering_data/{input_num_clusters}.pickle'
    dim_red_filepath = f'../server/data/dimension_reduction_data/{input_method}.pickle'
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, cluster_filepath)
    if os.path.exists(filename): # have all clustering options been precalculated?
        df_preds = pd.read_pickle(cluster_filepath)
        df_dim = pd.read_pickle(dim_red_filepath)
        df_embeddings = df_dim.set_index(['state', 'year']).join(df_preds.set_index(['state', 'year'])).reset_index()
        return df_embeddings.to_dict(orient='records'), cluster_names
        

    # if we don't have data already, calculate all data and then rerun function
    # load data
    policy_data_filepath = "../server/data/policyDatabase.xlsx"
    policy_df = pd.read_excel(policy_data_filepath)
    policy_df = policy_df[(policy_df.year > 2013) & (policy_df.year < 2019)]
    # create input data for clustering
    agg_df = policy_df.drop(columns=['year', 'lawtotal']).groupby('state').apply(
                lambda x: np.concatenate([x[col].values for col in x.columns if col != 'state'])
                ).reset_index()
    X = agg_df[0].to_numpy()
    X = np.stack(X)


    # cluster data
    for num_clusters in range(2, 7):
        output_filepath = f'../server/data/clustering_data/{num_clusters}.pickle'
        clusterer = KMeans(n_clusters=num_clusters, init='k-means++')
        predictions = clusterer.fit_predict(X)
        predictions = pd.DataFrame({'cluster': predictions})
        predictions['state'] = agg_df.state
        predictions = policy_df.set_index('state')[['year']].join(predictions.set_index('state')).reset_index()
        predictions.to_pickle(output_filepath)
        
    # dimension reduction
    for method in ['t-SNE', 'NMF', 'PCA']:
        output_filepath = f'../server/data/dimension_reduction_data/{method}.pickle'
        if method == 'PCA':
            reducer = PCA(n_components=2)
        elif method == 't-SNE':
            reducer = TSNE(n_components=2)
        elif method == 'NMF':
            reducer = NMF(n_components=2)
        data_embedded = reducer.fit_transform(X)
        # create output data frame
        df_embeddings = pd.DataFrame()
        df_embeddings["dimension1"] = data_embedded[:, 0]
        df_embeddings["dimension2"] = data_embedded[:, 1]
        df_embeddings['state'] = agg_df.state
        df_embeddings = policy_df.set_index('state')[['year']].join(df_embeddings.set_index('state')).reset_index()
        df_embeddings.to_pickle(output_filepath)
    # now that all data has been generated, rerun function
    processPolicyScatterplot(input_num_clusters, input_method)


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
    # rename columns to give cleaner names for chart
    gun_violence_metadata.rename(columns={'mass_shooting': 'mass shooting', 'non_suicide': 'non-suicide'}, inplace=True)

    policy_clusters = pd.DataFrame(policy_clusters)
    policy_clusters.set_index(['state', 'year'], inplace=True)
    all_data = gun_violence_metadata.join(policy_clusters)
    
    data = []
    for stat in gun_violence_metadata.columns:
        stat_data = {'group':stat}
        for cluster in range(len(cluster_names)):
            stat_data[cluster_names[cluster]] = all_data[all_data.cluster == cluster][stat].mean()
        data.append(stat_data)

    data = pd.DataFrame(data)
    data = data[data.group != 'all_incidents'] # not interesting
    data.set_index(['group'], inplace=True)
    data = data.div(data.sum(axis=1), axis=0) # divide each row by the sum of the row
    data.reset_index(inplace=True)

    return data.to_dict(orient='records')


def processPolicyCorrelations(policy_clusters:dict, incidence_type='all_incidents'):
    """
    output columns:
    policy category, correlation, cluster 1, cluster 2, ....
    """
    # load in data
    policy_metadata_filepath = '../server/data/policyMetadata.pickle'
    gun_violence_metadata_filepath = '../server/data/gunViolenceMetadata.pickle'

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, policy_metadata_filepath)
    if not os.path.exists(filename):
        preprocessPolicyMetadata()
    
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, gun_violence_metadata_filepath)
    if not os.path.exists(filename):
        preprocessGunViolenceMetadata()
    
    policy_metadata = pd.read_pickle(policy_metadata_filepath)
    gun_violence_metadata = pd.read_pickle(gun_violence_metadata_filepath)
    policy_clusters = pd.DataFrame(policy_clusters)

    # join policy and incident data to calculate correlations
    policy_metadata = policy_metadata[['year', 'state', 'sub_category', 'percent_policies_implemented']]
    policy_metadata = policy_metadata.set_index(['year', 'state']).join(gun_violence_metadata)

    # calculate correlation for each policy subcategory
    subcategory_corrs = []
    for subcategory in set(policy_metadata.sub_category):
        subcategory_data = policy_metadata[policy_metadata.sub_category == subcategory]
        subcategory_corr = subcategory_data.corr().iloc[0, 1:].reset_index()
        subcategory_corr['category'] = subcategory
        subcategory_corrs.append(subcategory_corr)
    correlation_df = pd.concat(subcategory_corrs)
    correlation_df.rename(columns={'index': 'incidence_type', 'percent_policies_implemented': 'correlation'}, 
                          inplace=True)
    correlation_df = correlation_df[correlation_df.incidence_type == incidence_type]
    correlation_df.drop(columns=['incidence_type'], inplace=True)

    # join with cluster policy data
        
    policy_clusters.set_index(['state', 'year'], inplace=True)
    cluster_data = policy_metadata.join(policy_clusters)
    cluster_data = cluster_data[['sub_category', 'percent_policies_implemented', 'cluster']]

    # rename the clusters to strings for readability
    mapping = {}
    for cluster in set(cluster_data.cluster):
        mapping[cluster] = f"cluster {cluster}"
    cluster_data['cluster'] = cluster_data['cluster'].apply(lambda x: mapping.get(x, x))
    cluster_data.rename(columns={'sub_category': 'category'}, inplace=True)
    cluster_data = cluster_data.groupby(['category', 'cluster']).mean()
    cluster_data.reset_index(inplace=True)
    cluster_data = cluster_data.pivot(index='category', columns='cluster', 
                                      values='percent_policies_implemented')
    
    table_data = cluster_data.join(correlation_df.set_index(['category'])[['correlation']])
    # sort table and round values
    table_data = table_data.sort_values(by=['correlation']).reset_index().round(3)
    return table_data.to_dict(orient='records')

    
if __name__ == "__main__":
    os.chdir('C:/Users/nammy/Desktop/ECS-273-Project/Vue-Flask-Template/dashboard/')
    cluster_data, clusters = processPolicyScatterplot(5, 't-SNE')
