# Clea

This project is an XML front matter metadata reader for documents
that *almost* follows the [SciELO Publishing Schema],
extracting and sanitizing the values regarding the affiliations.


## Installation

Installation with minimal requirements,
intended for use within Python, as an imported package:

```
pip install scielo-clea
```

Installation for use as a server (mainly for testing):

```
pip install scielo-clea[server]
```


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
from clea.core import Article
from pprint import pprint

art = Article("some_file.xml")
pprint(art.data_full)
```

That's a dictionary of lists with all the "raw" extracted data.
Using `art.data` instead of `art.data_full` should get the first item
of the lists, or an empty string if it's empty
(the same applies to branches and sub-articles).

More simple stuff that can be done:

```python
len(art.aff)              # Number of <aff> entries
len(art.sub_article)      # Number of <sub-article>
art.contrib[0].data_full  # Data from the first contributor as a dict

# Something like {"type": "translation", "lang": "en"},
# the content from <sub-article> attributes
art.sub_article[0].article[0].data
```

The extracted information is not exhaustive!
Its result should not be seen as a replacement of the raw XML.

One of the goals of this library was
to help on creating a tabular data from a given XML
with as many rows as required
to have a pair of a matching `<aff>` and `<contrib>` in each row.
These are the functions that does that matching:

* `clea.join.aff_contrib_inner_gen(article)`
* `clea.join.aff_contrib_full_gen(article)`
* `clea.join.aff_contrib_inner(article)`
* `clea.join.aff_contrib_full(article)`

The ones with the `_gen` suffix are generator functions
that yields a tuple with two `Branch` entries (or `None`),
the other ones return a list of merged dictionaries
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
including both the `INNER JOIN` and `FULL OUTER JOIN`
of matching `<aff>` and `<contrib>` pairs,
similar to the test server response:

```python
from clea.join import aff_contrib_inner, aff_contrib_full

pprint({**article.data_full,
    "aff_contrib_full": aff_contrib_full(article),
    "aff_contrib_inner": aff_contrib_inner(article),
})
```


[SciELO Publishing Schema]: http://docs.scielo.org/projects/scielo-publishing-schema
