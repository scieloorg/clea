from functools import partial

import Levenshtein as lev


def clean_empty(data):
    """Remove empty entries in a nested list/dictionary of items,
    deep removing nested empty entries.
    """
    if isinstance(data, dict):
        cleaned = {k: clean_empty(v) for k, v in data.items()}
        return {k: v for k, v in cleaned.items() if v}
    if isinstance(data, list):
        return [v for v in map(clean_empty, data) if v]
    return data


def get_lev(dict_or_node, key):
    """Fuzzy item getter for dictionary-like and Element-like objects.
    This can be seen as a ``__getitem__`` alternative
    that gets from the nearest key available in the given object,
    minimizing the Levenshtein distance for such.
    """
    keys = dict_or_node.keys()
    if not keys:
        return ""
    return dict_or_node.get(min(keys, key=partial(lev.distance, key)))
