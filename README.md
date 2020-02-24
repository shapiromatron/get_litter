# Literature Getter (litter_getter)

![PyPI](https://img.shields.io/pypi/v/litter_getter)

Retrieve literature from biomedical reference libraries such as PubMed, EPA's HERO, and imports from Endnote RIS exports.

* Search and reference parsing using [PubMed](http://www.ncbi.nlm.nih.gov/pubmed)
* Search and reference parsing using [US EPA HERO](https://hero.epa.gov/hero/)
* Endnote/Reference Manager RIS file-export parsing

## Installation

Install with pip:

```bash
pip install litter_getter
```

To grab a developer build:

```bash
git clone git@github.com:shapiromatron/litter_getter.git
cd litter_getter/
python -m venv venv
source venv/bin/activate
pip install -e .[dev,test]
```

Tests require use of an API key; see below. I generally add one to my virtual environment:

```bash
echo "export \"PUBMED_API_KEY=this-is-my-key\"" >> venv/bin/activate
tail venv/bin/activate
source venv/bin/activate

make test
```

## Usage

The data are currently extracted as list of dicts, using a preset, opinionated,
dictionary format. This could probably be revised for increased flexibility; if
you have a need, feel free to submit an issue.

### PubMed

The PubMed API generally uses an API key for best [performance](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/), in `litter_getter` this is optional but can be added, you'll only need to do this one time for a session.

```python
from litter_getter import pubmed

pubmed.connect('my-special-api-key')
```

If you're not using a key and a server returns 429 errors, you may want to try adding a key. A query can be submitted; the number of references returned and the IDs for the references can be extracted:

```python
from litter_getter import pubmed

search_term = """science[journal] AND breast cancer AND 2008[pdat]"""
search = pubmed.PubMedSearch(term=search_term)

search.get_ids_count()
search.id_count
>>> 123

search.get_ids()
>>> ['19008416', '18927361', '18787170', '18487186', '18239126', '18239125']
```

After obtaining a list of references, details on each reference can be downloaded and parsed:

```python
ids = [19008416, 18927361]
fetch = pubmed.PubMedFetch(id_list=ids)
refs = fetch.get_content()

refs[0].keys()
>>> ['xml', 'doi', 'title', 'abstract', 'citation', 'authors_short', 'year', 'PMID', 'authors']
```

The complete XML returned from Pubmed is captured in the `xml` field.

### HERO

If reference IDs are known, references can be collected and parsed from the EPA HERO database:

```python
from litter_getter import hero

ids = [1221, 1223]
fetch = hero.HEROFetch(id_list=ids)
results = fetch.get_content()

results.keys()
>>> ['failure', 'success']

results.failures()
>>> [12413113]

>>> results['success'][0].keys()
>>> ['source', 'json', 'title', 'authors_short', 'HEROID', 'abstract', 'year', 'PMID', 'authors']
```

The complete JSON returned from HERo is captured in the `json` field.

### RIS

RIS exports from common reference management software such as [Endnote]()http://endnote.com/) or [Reference Manager](http://referencemanager.com/) can be parsed via:

```python
from litter_getter import ris
import os

fn = os.path.expanduser("~/Desktop/sample_ris.txt")
importer = ris.RisImporter(fn)
refs = importer.references

refs[0].keys()
>>> ['doi', 'title', 'reference_type', 'abstract', 'citation', 'accession_number',
        'json', 'authors_short', 'year', 'accession_db', 'PMID', 'id']
```
