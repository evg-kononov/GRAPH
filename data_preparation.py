import pandas as pd
import numpy as np
from tqdm import tqdm

if __name__ == "__main__":
    author_path = r"H:\data lake\entities\author.parquet"
    organization_path = r"H:\data lake\entities\organization.parquet"
    publication_path = r"H:\data lake\entities\publication.parquet"
    publication_author_path = r"H:\data lake\entities\publication_author.parquet"

    publication_author_data = pd.read_parquet(publication_author_path)
    authors = set(publication_author_data['author_id'].values.tolist())
    authors = sorted(authors)

    # TODO: две таблицы, одну group by publications и join с второй
    edges = []
    for source in tqdm(authors):
        l = publication_author_data[publication_author_data['author_id'] == source]['publication_id']
        targets = publication_author_data[publication_author_data['publication_id'].isin(l)].groupby('author_id',
                                                                                                     as_index=False).count()

        targets.rename(columns={'author_id': 'target', 'publication_id': 'weight'}, inplace=True)
        targets.drop(targets[targets['target'] <= source].index, inplace=True)
        if source % 5000000000 == 0:
            publication_author_data.drop(publication_author_data[publication_author_data['author_id'] <= source].index,
                                         inplace=True)
        targets["source"] = source
        edges.append(targets)

    edges = pd.concat(edges)
    edges["type"] = "Undirected"
    edges.to_csv("edges.csv", index=False)
