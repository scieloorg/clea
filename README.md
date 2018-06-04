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

Installation for use as a server:

```
pip install scielo-clea[server]
```

## Running

You can run the development server using the flask CLI.
For example, for listening at 8080 from every host:

```
FLASK_APP=clea.server flask run -h 0.0.0.0 -p 8080
```

In a production server with 4 worker processes for handling requests,
you can, for example:

- Install gunicorn (it's not a dependency)
- Run `gunicorn -b 0.0.0.0:8080 clea.server:app`


[SciELO Publishing Schema]: http://docs.scielo.org/projects/scielo-publishing-schema
