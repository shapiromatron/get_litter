# History

## 0.3.0 (2020-03-26)

* Standardize author name cleanup across all import types
* Rename `authors_list` to `authors`; all return a list of authors
* Pubmed and HERO import fetch requests expect a list of integer values, not strings
* Pubmed and HERO ids returned in content are now integer instead of strings
* For HERO and RIS, don't save json field as string, but instead as JSON-compatible dictionary
* Python 3.6 or higher is required

## 0.2.6 (2020-01-30)

* Make Pubmed API key optional

## 0.2.5 (2020-01-30)

* Use new HERO URL
* Use Pubmed API keys
* Code style enforcement with black
* Simplify tooling dependencies (no more travis, readthedocs, etc)

## 0.2.4 (2018-06-05)

* Fix bug in capturing title text with child elements


## 0.2.3 (2018-04-25)

* Fix bug in capturing abstract text with child elements


## 0.2.2 (2018-04-10)

* Bump RISparser version
* Prevent error if fetch called before count (@breisfeld)


## 0.2.1 (2017-05-30)

* Return unicode XML instead of bytes in dict


## 0.2.0 (2017-05-29)

* Upgraded to Python 3 only


## 0.1.2 (2017-04-07)

* Try to return an int for ID unless it fails; then keep string


## 0.1.1 (2016-09-27)

* Added documentation.


## 0.1.0 (2016-09-26)

* Initial release.
