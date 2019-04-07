from collections import ChainMap
from itertools import chain

from .core import get_lev


def aff_contrib_full_outer_join_dframe(article):
    import pandas as pd
    return pd.merge(pd.DataFrame(article.data["aff"]),
                    pd.DataFrame(article.data["contrib"]),
                    left_on="aff_id", right_on="xref_aff",
                    how="outer")


def aff_contrib_inner_gen(article):
    affs_ids = [get_lev(aff.node, "id") for aff in article.aff]
    contrib_rids = [[get_lev(xref, "rid")
                     for xref in contrib.get_field_nodes("xref_aff")]
                    for contrib in article.contrib]
    for aff_id, aff in zip(affs_ids, article.aff):
        for rid_list, contrib in zip(contrib_rids, article.contrib):
            for rid in rid_list:
                if rid == aff_id:
                    yield aff, contrib


def aff_contrib_full_gen(article):
    affs_ids = [get_lev(aff.node, "id") for aff in article.aff]
    contrib_rids = [[get_lev(xref, "rid")
                     for xref in contrib.get_field_nodes("xref_aff")]
                    for contrib in article.contrib]
    contrib_missing = set(range(len(article.contrib)))
    for aff_id, aff in zip(affs_ids, article.aff):
        amiss = True
        for cidx, (rid_list, contrib) in enumerate(zip(contrib_rids,
                                                       article.contrib)):
            for rid in rid_list:
                if rid == aff_id:
                    yield aff, contrib
                    amiss = False
                    contrib_missing.discard(cidx)
        if amiss:
            yield aff, None
    for cidx in sorted(contrib_missing):
        yield None, article.contrib[cidx]


def aff_contrib_inner(article):
    """Inner join list of matching <aff> and <contrib> entries."""
    return [{**aff.data_full, **contrib.data_full}
            for aff, contrib in aff_contrib_inner_gen(article)]


def aff_contrib_full(article):
    """Full outer join list of matching <aff> and <contrib> entries."""
    return [{**(aff.data_full if aff else {}),
             **(contrib.data_full if contrib else {}),
            } for aff, contrib in aff_contrib_full_gen(article)]


def aff_contrib_inner_join(article):
    """Legacy inner join, returning items in tabular format as strings,
    including the first matching entries from both article-meta
    and journal-meta items.
    """
    dicts = dict(ChainMap(*chain.from_iterable(
        [branch.data for branch in article.get(tag_name)]
        for tag_name in ["article-meta", "journal-meta"]
    )))
    return [{**dicts,
             **{k: "; ".join(v) for k, v in aff_contrib},
            } for aff_contrib in aff_contrib_inner(article)]


# TODO: Remove this deprecated name
aff_contrib_pairs_generator = aff_contrib_inner_gen
