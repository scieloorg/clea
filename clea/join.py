from .misc import get_lev


def aff_contrib_inner_gen(article):
    """Generator of matching <aff> and <contrib> of an article
    as pairs of Branch instances,
    using a strategy based on SQL's INNER JOIN."""
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
    """Generator of matching <aff> and <contrib> of an article
    as pairs of Branch instances,
    using a strategy based on SQL's FULL OUTER JOIN."""
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


def aff_contrib_inner_indices(article):
    """List of ``(ia, ic)`` tuples of indices for all matching
    ``(article["aff"][ia], article["contrib"][ic])`` pairs,
    using a strategy based on SQL's INNER JOIN.
    """
    affs = [None] + article["aff"]
    contribs = [None] + article["contrib"]
    return [(affs.index(aff) - 1, contribs.index(contrib) - 1)
             for aff, contrib in aff_contrib_inner_gen(article)]


def aff_contrib_full_indices(article):
    """List of ``(ia, ic)`` tuples of indices for all matching
    ``(article["aff"][ia], article["contrib"][ic])`` pairs,
    using a strategy based on SQL's FULL OUTER JOIN.
    """
    affs = [None] + article["aff"]
    contribs = [None] + article["contrib"]
    return [(affs.index(aff) - 1, contribs.index(contrib) - 1)
             for aff, contrib in aff_contrib_full_gen(article)]
