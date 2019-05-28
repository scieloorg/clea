from functools import lru_cache, partial

from lxml import etree
from unidecode import unidecode
import Levenshtein as lev
import numpy as np
import regex

from .regexes import TAG_PATH_REGEXES, SUB_ARTICLE_NAME, get_branch_dicts


_PARSER = etree.XMLParser(recover=True, remove_comments=True)


class AbstractDescriptorCacheDecorator:

    def __init__(self, func):
        self.func = func
        self.names = []

    def __set_name__(self, owner, name):
        self.names.append(name)

    def store_result(self, instance, result):
        for name in self.names:
            setattr(instance, name, result)


class CachedProperty(AbstractDescriptorCacheDecorator):
    """Descriptor and also a method decorator, like ``property``,
    where the decorated function gets called only once
    and its result is stored in the instance dictionary afterwards.
    """
    def __get__(self, instance, owner):
        result = self.func(instance)
        self.store_result(instance, result)
        return result


class CachedMethod(AbstractDescriptorCacheDecorator):
    """Cache decorator like ``functools.lru_cache``,
    but applied on each bound method (i.e., in the instance)
    in order to avoid memory leak issues relating to
    caching an unbound method directly from the owner class.
    """
    def __get__(self, instance, owner):
        result = lru_cache(None)(partial(self.func, instance))
        self.store_result(instance, result)
        return result


def etree_tag_path_gen(root, start=""):
    """Extract the tag path."""
    start += "/" + root.tag
    yield start, root
    for node in root.iterchildren():
        yield from etree_tag_path_gen(node, start)


def etree_path_gen(branch, path=""):
    """Extract the branch path."""
    path += "/" + branch.tag
    for k, v in sorted(branch.items()):
        path += f"@{xml_attr_cleanup(k)}={xml_attr_cleanup(v)}"
    yield path, branch
    for node in branch:
        if not isinstance(node, str):
            yield from etree_path_gen(node, path)


def get_lev(dict_or_node, key):
    """Fuzzy item getter for dictionary-like and Element-like objects.
    This can be seen as a ``__getitem__`` alternative
    that gets from the nearest key available in the given object,
    minimizing the Levenshtein distance for such.
    """
    return dict_or_node.get(min(dict_or_node.keys(),
                                key=partial(lev.distance, key)))


def xml_attr_cleanup(name):
    """Clean the given XML attribute name/value.
    This just removes what's required in order to build a branch path.
    """
    return regex.sub("[/@]", "%", unidecode(name))


def node_getattr(node, attr=""):
    """Item getter from an Element node of an ElementTree.
    Returns the decoded inner text string form the node,
    unless an attribute name is given.
    """
    if node is None:
        return ""
    if attr:
        return get_lev(node, attr)
    full_text = etree.tounicode(node, method="text", with_tail=False)
    return regex.sub(r"\s+", " ", full_text).strip()


class Article(object):
    """Article abstraction from its XML file."""

    def __init__(self, xml_file):
        et = etree.parse(xml_file, parser=_PARSER)
        # Workaround due to an lxml bug regarding entities
        # https://bugs.launchpad.net/lxml/+bug/1830661
        if et.docinfo.doctype:
            et_no_doctype = etree.tostring(et, doctype="")
            self.root = etree.fromstring(et_no_doctype, parser=_PARSER)
        else:
            self.root = et.getroot()

    @CachedProperty
    def tag_paths_pairs(self):
        return list(etree_tag_path_gen(self.root))

    @CachedMethod
    def get(self, tag_name):
        tag_regex = TAG_PATH_REGEXES[tag_name]
        if tag_name == SUB_ARTICLE_NAME:
            return [SubArticle(parent=self, root=el, tag_name=tag_name)
                    for path, el in self.tag_paths_pairs
                    if tag_regex.search(path)]
        return [Branch(article=self, node=el, tag_name=tag_name)
                for path, el in self.tag_paths_pairs
                if tag_regex.search(path)]

    @CachedProperty
    def data_full(self):
        return {tag_name: [branch.data_full for branch in self.get(tag_name)]
                for tag_name in TAG_PATH_REGEXES}

    __getitem__ = __getattr__ = lambda self, name: self.get(name)


class SubArticle(Article):
    def __init__(self, parent, root, tag_name):
        self.parent = parent # Should be the <article> (main XML root)
        self.root = root # The <sub-article> element
        self.tag_name = tag_name


class Branch(object):

    def __init__(self, article, node, tag_name):
        self.article = article
        self.node = node # Branch "root" element
        self.tag_name = tag_name
        self.field_regexes, self.field_attrs = get_branch_dicts(tag_name)

    @CachedProperty
    def paths_pairs(self):
        return list(etree_path_gen(self.node))

    @CachedProperty
    def _paths_nodes_pair(self):
        return tuple(zip(*self.paths_pairs))

    @CachedProperty
    def paths(self):
        return self._paths_nodes_pair[0]

    @CachedProperty
    def nodes(self):
        return self._paths_nodes_pair[1]

    @CachedProperty
    def paths_str(self):
        return "\n".join(self.paths)

    @CachedProperty
    def ends(self):
        return np.cumsum([len(p) + 1 for p in self.paths]) # Add \n

    @CachedProperty
    def data_full(self):
        return {key: self.get(key) for key in self.field_regexes}

    @CachedMethod
    def get_field_nodes(self, field):
        field_regex = self.field_regexes[field]
        matches = field_regex.finditer(self.paths_str)
        return [self.nodes[np.where(self.ends > m.start())[0][0]]
                for m in matches]

    @CachedMethod
    def get(self, field):
        attr = self.field_attrs[field]
        nodes = self.get_field_nodes(field)
        return [node_getattr(node, attr) for node in nodes]

    __getitem__ = __getattr__ = lambda self, name: self.get(name)
