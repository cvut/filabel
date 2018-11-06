filabel
=======

|license| |pypi|

Tool for labeling PRs at GitHub by globs

Installation
------------

You can install this app in a standard way using ``setup.py``:

::

    $ python setup.py install
    $ pip install -e .

Or from PyPI:

::

    $ pip install filabel_cvut


Usage
-----

Run the CLI application simply with command and get to know it via help:

::

    $ filabel --help


Or run the web service

::

    $ export FILABEL_CONFIG=/path/to/my_labels.cfg:/path/to/my_auth.cfg
    $ export FLASK_APP=filabel
    $ flask run


For more info about configuration files, take a look at the content of
``config`` directory.


License
-------

This project is licensed under the MIT License - see the `LICENSE`_ file for more details.

.. _LICENSE: LICENSE


.. |license| image:: https://img.shields.io/github/license/cvut/filabel.svg
    :alt: License
    :target: LICENSE
.. |pypi| image:: https://badge.fury.io/py/filabel_cvut.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/filabel_cvut
