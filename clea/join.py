from collections import ChainMap
from itertools import chain

from .core import get_lev
from .regexes import FRONT_TAG_PATH_REGEXES


def aff_contrib_full_outer_join_dframe(article):
    import pandas as pd
    return pd.merge(pd.DataFrame(article.data["aff"]),
                    pd.DataFrame(article.data["contrib"]),
                    left_on="aff_id", right_on="xref_aff",
                    how="outer")


def aff_contrib_pairs_generator(article):
    affs_ids = [get_lev(aff.node, "id") for aff in article.aff]
    contrib_rids = [[get_lev(xref, "rid")
                     for xref in contrib.get_field_nodes("xref_aff")]
                    for contrib in article.contrib]
    for aff_id, aff in zip(affs_ids, article.aff):
        for rid_list, contrib in zip(contrib_rids, article.contrib):
            for rid in rid_list:
                if rid == aff_id:
                    yield aff, contrib


def aff_contrib_inner_join(article):
    dicts = dict(ChainMap(*chain.from_iterable(
        [branch.data for branch in article.get(tag_name)]
        for tag_name in FRONT_TAG_PATH_REGEXES
    )))
    return [{**dicts,
             **{k: "; ".join(v) for k, v in aff.data_full.items()},
             **{k: "; ".join(v) for k, v in contrib.data_full.items()},
            } for aff, contrib in aff_contrib_pairs_generator(article)]
