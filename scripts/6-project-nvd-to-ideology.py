"""
Description: This script takes the NVD data and projects it to the ideology space.
"""
import os
from typing import List

import numpy as np
import pandas as pd
from sklearn.manifold import TSNE
from tqdm import tqdm
from utils import read_json, save_json

node_attributes = pd.read_csv("data/nvd-node_attributes.csv")

politician_ids = node_attributes.columns[1:]
politician_matrix_id = {int(polit_id): i for i, polit_id in enumerate(politician_ids)}
distance_matrix = np.zeros((len(politician_ids), len(politician_ids)))
for polit_id in tqdm(politician_ids, desc="Building distance matrix"):
    specific_path = f"data/nvd/{polit_id}.csv"
    distances = pd.read_csv(specific_path, skiprows=1, names=["src", "dst", "distance"])

    # Setting all values
    for idx, row in distances.iterrows():
        src_matrix_id = int(politician_matrix_id[row["src"]])
        dst_matrix_id = int(politician_matrix_id[row["dst"]])
        dist = row["distance"]

        # set value in matrix
        distance_matrix[src_matrix_id, dst_matrix_id] = dist
        distance_matrix[dst_matrix_id, src_matrix_id] = dist

# save the distance matrix
np.save("data/nvd-distance-matrix.npy", distance_matrix)

# Create the t-SNE embeddings
X_embedded_2 = TSNE(n_components=2, metric="precomputed", init="random").fit_transform(
    distance_matrix
)

X_embedded_1 = TSNE(n_components=1, metric="precomputed", init="random").fit_transform(
    distance_matrix
)

# Scale the values to be between -1 and 1
X_embedded_2 = (X_embedded_2 - X_embedded_2.min()) / (
    X_embedded_2.max() - X_embedded_2.min()
)

X_embedded_2 = (X_embedded_2 * 2) - 1

X_embedded_1 = (X_embedded_1 - X_embedded_1.min()) / (
    X_embedded_1.max() - X_embedded_1.min()
)

X_embedded_1 = (X_embedded_1 * 2) - 1

# Save the embeddings
np.save("data/nvd-embeddings-2.npy", X_embedded_2)
np.save("data/nvd-embeddings-1.npy", X_embedded_1)

# Add the scores to the politician_117.json file
assert len(politician_ids) == len(X_embedded_2) == len(X_embedded_1)


politician_117 = read_json("data/politicians_117.json")
nvds: List[str] = [f_.split(".")[0] for f_ in os.listdir("data/nvd")]
updated_politician_117 = []
for idx, politician_id in enumerate(politician_ids):
    # constant confusion about ids...
    assert str(politician_id) in nvds, f"{politician_id} not in nvds"

    for info_idx, info in enumerate(politician_117):
        try:
            littlesis_match: bool = int(info["ids"]["littlesis"]) == int(politician_id)
        except KeyError:
            littlesis_match = False

        if littlesis_match:
            print("found", politician_id)
            info["embedding_2"] = X_embedded_2[idx].tolist()
            info["embedding_1"] = X_embedded_1[idx].tolist()

            politician_117[info_idx] = info

            break

save_json(path="data/politicians_117.json", data=politician_117)

# politicians and their embeddings
df = pd.DataFrame(
    {
        "politician_id": politician_ids,
        "embedding_2_0": X_embedded_2[:, 0],
        "embedding_2_1": X_embedded_2[:, 1],
        "embedding_1": X_embedded_1[:, 0],
    }
)

df.to_csv("data/nvd-politician-and-embeddings.csv", index=False)
