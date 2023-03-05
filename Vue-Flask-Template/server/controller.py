import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA


def processPolicyScatterPlot(num_clusters: int = 3, method: str = 'PCA'):
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

    return df_embeddings.to_dict(orient='records')



