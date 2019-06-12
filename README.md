# Clea

This project is an XML front matter metadata reader for documents
that *almost* follows the [SciELO Publishing Schema],
extracting and sanitizing the values regarding the affiliations.


## Installation

One can install Clea with either:

```
pip install scielo-clea          # Minimal
pip install scielo-clea[cli]     # Clea with CLI (recommended)
pip install scielo-clea[server]  # Clea with the testing/example server
pip install scielo-clea[all]     # Clea with both CLI and the server
```

Actually all these commands installs everything,
only the dependencies aren't the same.
The first is an installation with minimal requirements,
intended for use within Python, as an imported package.


## Running the command line interface

The CLI is a way to use Clea as an article XML to JSONL converter
(one JSON output line for each XML input):

```
clea -o output.jsonl article1.xml article2.xml article3.xml
```

The same can be done with ``python -m clea`` instead of ``clea``.
The output is the standard output stream.
See ``clea --help`` for more information.


## Running the testing server

You can run the development server using the flask CLI.
For example, for listening at 8080 from every host:

```
FLASK_APP=clea.server flask run -h 0.0.0.0 -p 8080
```

In a production server with 4 worker processes for handling requests,
you can, for example:

- Install gunicorn (it's not a dependency)
- Run `gunicorn -b 0.0.0.0:8080 -w 4 clea.server:app`


## Clea as a library

A simple example to see all the extracted data is:

```python
from clea import Article
from pprint import pprint

art = Article("some_file.xml")
pprint(art.data_full)
```

That's a dictionary of lists with all the "raw" extracted data.
The keys of that dictionary can be directly accessed,
so one can avoid extracting everything from the XML
by getting just the specific items/attributes
(e.g. `art["journal_meta"][0].data_full`
  or `art.journal_meta[0].data_full`
  instead of `art.data_full["journal_meta"][0]`).
These items/attributes are always lists, for example:

* `art["aff"]`: List of `clea.core.Branch` instances
* `art["sub_article"]`: List of `clea.core.SubArticle` instances
* `art["contrib"][0]["contrib_name"]`: List of strings

Where the `art["contrib"][0]` is a `Branch` instance,
and all such instances behave in the same way
(there's no nested branches).
That can be seen as another way to navigate in the former dictionary,
the last example should return the same list one would get with
`art.data_full["contrib"][0]["contrib_name"]`,
but without extracting everything else
that appears in the `art.data_full` dictionary.

More simple stuff that can be done:

```python
len(art.aff)              # Number of <aff> entries
len(art.sub_article)      # Number of <sub-article>
art.contrib[0].data_full  # Data from the first contributor as a dict

# Something like {"type": ["translation"], "lang": ["en"]},
# the content from <sub-article> attributes
art["sub_article"][0]["article"][0].data_full

# A string with the article title, accessing just the desired content
art["article_meta"][0]["article_title"][0]
```

All `SubArticle`, `Article` and `Branch` instances
have the `data_full` property and the `get` method,
the latter being internally used for item/attribute getting.
Their behavior is:

* `Branch.get` always returns a list of strings
* `Article.get("sub_article")` returns a list of `SubArticle`
* `Article.get(...)` returns a list of `Branch`
* `SubArticle` behaves like `Article`

The extracted information is not exhaustive!
Its result should not be seen as a replacement of the raw XML.

One of the goals of this library was
to help on creating a tabular data from a given XML
with as many rows as required
to have a pair of a matching `<aff>` and `<contrib>` in each row.
These are the `Article` methods/properties that does that matching:

* `art.aff_contrib_inner_gen()`
* `art.aff_contrib_full_gen()`
* `art.aff_contrib_inner`
* `art.aff_contrib_full`
* `art.aff_contrib_inner_indices`
* `art.aff_contrib_full_indices`

The most useful ones are probably the last ones,
which return a list of pairs (tuples) of indices (ints),
so one can use a `(ai, ci)` result
to access the `(art.aff[ai], art.contrib[ci])` pair,
unless the index is `-1` (not found).
The ones with the `_gen` suffix are generator functions
that yields a tuple with two `Branch` entries (or `None`),
the ones without a suffix return a list of merged dictionaries
in an almost tabular format (dictionary of lists of strings).
Each list regarding these elements for these specific elements
should usually have at most one string,
but that's not always the case even for these specific elements,
then one should be careful when using the `data` property.

The `inner` and `full` in the names
regards to `INNER JOIN` and `FULL OUTER JOIN` from SQL,
meaning the unmatched elements
(all `<aff>` and `<contrib>` unreferred nodes)
are discarded in the former strategy,
whereas they're forcefully matched with `None` in the latter.

To print all the extracted data from a XML
including the indices of matching `<aff>` and `<contrib>` pairs
performed in the `FULL OUTER JOIN` sense,
similar to the test server response:

```python
pprint({
    **article.data_full,
    "aff_contrib_pairs": article.aff_contrib_full_indices,
})
```


[SciELO Publishing Schema]: http://docs.scielo.org/projects/scielo-publishing-schema
