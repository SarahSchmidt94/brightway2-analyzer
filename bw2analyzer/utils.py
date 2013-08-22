from __future__ import division
from time import time
from bw2calc import LCA
from bw2data import Database, methods, databases, mapping
import numpy as np
import progressbar


def contribution_for_all_datasets_one_method(database, method, progress=True):
    """Calculate contribution analysis (for technosphere processes) for all inventory datasets in one database for one LCIA method.

    Args:
        *database* (str): Name of database
        *method* (tuple): Method tuple

    Returns:
        NumPy array of relative contributions. Each column sums to one.
        Lookup dictionary, dataset keys to row/column indices
        Total elapsed time in seconds

    """
    def get_normalized_scores(lca):
        scores = np.abs(np.array(
            lca.characterized_inventory.sum(axis=0)
        ).ravel())
        summed = scores.sum()
        if summed == 0:
            return np.zeros(scores.shape)
        else:
            return scores / summed

    start = time()
    assert database in databases, "Can't find database %s" % database
    assert method in methods, "Can't find method %s" % method
    keys = Database(database).load().keys()
    assert keys, "Database %s appears to have no datasets" % database

    # Array to store results
    results = np.zeros((len(keys), len(keys)), dtype=np.float32)

    # Instantiate LCA object
    lca = LCA({keys[0]: 1}, method=method)
    lca.lci()
    lca.decompose_technosphere()
    lca.lcia()

    if progress:
        widgets = [
            'Datasets: ',
            progressbar.Percentage(),
            ' ',
            progressbar.Bar(marker=progressbar.RotatingMarker()),
            ' ',
            progressbar.ETA()
        ]
        pbar = progressbar.ProgressBar(
            widgets=widgets,
            maxval=len(keys)
        ).start()

    # Actual calculations
    for index, key in enumerate(keys):
        lca.redo_lcia({key: 1})
        col = lca.technosphere_dict[mapping[key]]
        try:
            results[:, col] = get_normalized_scores(lca)
        except:
            # LCA score is zero
            pass
        if progress:
            pbar.update(index)

    if progress:
        pbar.finish()

    lca.fix_dictionaries()
    return results, lca.technosphere_dict, time() - start