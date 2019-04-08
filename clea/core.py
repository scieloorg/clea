from functools import partial
from lxml import etree
from unidecode import unidecode
import Levenshtein as lev
import numpy as np
import regex

from .regexes import TAG_PATH_REGEXES, SUB_ARTICLE_NAME, BRANCH_REGEXES


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
        self.root = etree.parse(xml_file,
            parser=etree.XMLParser(recover=True)
        ).getroot()

    @property
    def tag_paths_pairs(self):
        return list(etree_tag_path_gen(self.root))

    def get(self, tag_name):
        tag_regex = TAG_PATH_REGEXES[tag_name]
        if tag_name == SUB_ARTICLE_NAME:
            return [SubArticle(parent=self, root=el, tag_name=tag_name)
                    for path, el in self.tag_paths_pairs
                    if tag_regex.search(path)]
        return [Branch(article=self, node=el, tag_name=tag_name)
                for path, el in self.tag_paths_pairs
                if tag_regex.search(path)]

    @property
    def data(self):
        return {tag_name: [branch.data for branch in self.get(tag_name)]
                for tag_name in TAG_PATH_REGEXES}

    @property
    def data_full(self):
        return {tag_name: [branch.data_full for branch in self.get(tag_name)]
                for tag_name in TAG_PATH_REGEXES}

    def __getattr__(self, attr_name):
        return self.get(attr_name.replace("_", "-"))


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
        self.branch_regexes = BRANCH_REGEXES[tag_name]
        self.field_regexes = {key: r
                              for key, attr, r in self.branch_regexes}

    @property
    def paths_pairs(self):
        return list(etree_path_gen(self.node))

    @property
    def data(self):
        paths, nodes = zip(*self.paths_pairs)
        paths_str = "\n".join(paths)
        ends = np.cumsum([len(p) + 1 for p in paths]) # Add \n
        keys, attrs, regexes = zip(*self.branch_regexes)
        matches_gen = (r.search(paths_str) for r in regexes)
        nodes_gen = (match and nodes[np.where(ends > match.start())[0][0]]
                     for match in matches_gen)
        return {key: node_getattr(node, attr)
                for key, attr, node in zip(keys, attrs, nodes_gen)}

    @property
    def _paths_nodes_pair(self):
        return tuple(zip(*self.paths_pairs))

    @property
    def paths(self):
        return self._paths_nodes_pair[0]

    @property
    def nodes(self):
        return self._paths_nodes_pair[1]

    @property
    def paths_str(self):
        return "\n".join(self.paths)

    @property
    def ends(self):
        return np.cumsum([len(p) + 1 for p in self.paths]) # Add \n

    @property
    def data_full(self):
        keys, attrs, regexes = zip(*self.branch_regexes)
        matches_iter_gen = (r.finditer(self.paths_str) for r in regexes)
        nodes_iter_gen = ([match and self.nodes[np.where(self.ends >
                                                         match.start())[0][0]]
                           for match in matches]
                          for matches in matches_iter_gen)
        return {key: [node_getattr(node, attr) for node in nodes_gen]
                for key, attr, nodes_gen in zip(keys, attrs, nodes_iter_gen)}

    def get_field_nodes(self, field):
        field_regex = self.field_regexes[field]
        matches = field_regex.finditer(self.paths_str)
        return [self.nodes[np.where(self.ends > m.start())[0][0]]
                for m in matches if m]
