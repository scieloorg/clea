from contextlib import contextmanager
import html

from lxml import etree
from unidecode import unidecode
import numpy as np
import regex

from .cache import CachedMethod, CachedProperty
from . import join
from .misc import get_lev
from .regexes import TAG_PATH_REGEXES, SUB_ARTICLE_NAME, get_branch_dicts


_PARSER = etree.XMLParser(recover=True)
_DOCTYPE = '<!DOCTYPE article PUBLIC "" "http://">\n'  # Force Entity objects


class InvalidInput(Exception):
    pass


def etree_tag_path_gen(root, start=""):
    """Extract the tag path."""
    start += "/" + root.tag
    yield start, root
    for node in root.iterchildren(tag=etree.Element):
        yield from etree_tag_path_gen(node, start)


def etree_path_gen(branch, path=""):
    """Extract the branch path."""
    path += "/" + branch.tag
    for k, v in sorted(branch.items()):
        path += f"@{xml_attr_cleanup(k)}={xml_attr_cleanup(v)}"
    yield path, branch
    for node in branch.iterchildren(tag=etree.Element):
        yield from etree_path_gen(node, path)


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
    full_text = etree.tostring(node,
        encoding=str,
        method="text",
        with_tail=False,
    )
    return regex.sub(r"\s+", " ", full_text).strip()


@contextmanager
def open_or_bypass(fileobj_or_filename, mode="r"):
    if isinstance(fileobj_or_filename, str):
        with open(fileobj_or_filename, mode) as result:
            yield result
    else:
        yield fileobj_or_filename


def replace_html_entity_by_text(entity):
    value = html.unescape(entity.text) + (entity.tail or "")
    previous = entity.getprevious()
    parent = entity.getparent()
    parent.remove(entity)
    if previous is not None:
        if previous.tail is None:
            previous.tail = value
        else:
            previous.tail += value
    else:
        if parent.text is None:
            parent.text = value
        else:
            parent.text += value


class Article(object):
    """Article abstraction from its XML file."""

    def __init__(self, xml_file, raise_on_invalid=True):
        with open_or_bypass(xml_file) as fobj:
            raw_data = fobj.read()
            if isinstance(raw_data, bytes):
                raw_data = raw_data.decode("utf-8")
        try:  # Remove <?xml> and <!DOCTYPE> headers
            document = regex.search("<[^?!](?:.|\n)*$", raw_data,
                                    flags=regex.MULTILINE).group()
        except AttributeError:
            document = raw_data
        self.root = etree.fromstring(_DOCTYPE + document, parser=_PARSER)
        if self.root is None:
            if raise_on_invalid:
                raise InvalidInput("Not an XML file")
            self.root = etree.Element("article")

        # There should be no entity at all,
        # but if there's any (legacy), they are the HTML5 ones
        for entity in self.root.iterdescendants(tag=etree.Entity):
            replace_html_entity_by_text(entity)

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

    aff_contrib_inner_gen = join.aff_contrib_inner_gen
    aff_contrib_full_gen = join.aff_contrib_full_gen
    aff_contrib_inner = CachedProperty(join.aff_contrib_inner)
    aff_contrib_full = CachedProperty(join.aff_contrib_full)
    aff_contrib_inner_indices = CachedProperty(join.aff_contrib_inner_indices)
    aff_contrib_full_indices = CachedProperty(join.aff_contrib_full_indices)


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
