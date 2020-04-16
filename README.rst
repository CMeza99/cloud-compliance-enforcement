Cloud Policy Enforcement
========================

Manage and enforce cloud policies with `Cloud Custodian <https://cloudcustodian.io/>`_.
Documentation is available on `Gitlab Pages <http://digitalr00ts.pages.gitlab.disney.com/cloud-policy-enforcement>`_.

Requirements
------------

* Python 3.8
* `Tox <https://tox.readthedocs.io/>`_ >= 3.0
* `Pipenv <https://github.com/pypa/pipenv>`_ (for dev environment)


Basic Usage
-----------

Validate
^^^^^^^^^

.. code-block:: shell

  tox

or

.. code-block:: shell

  tox -e validate

Run Policies
^^^^^^^^^^^^

.. code-block:: shell

  tox -e run

Generate Documentation
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

  tox -e docs


Development Environment
-----------------------

.. code-block:: shell

  pipenv install --skip-lock --dev


Project Structure
-----------------

::

    .
    ├── cpe-cmd/ :: CPE Command
    ├── docs/ :: Documentation
    ├── modes/ :: Mode YAMLS to merge w/ policies
    ├── policies/ :: Policies (Can run locally w/ c7n)
    ├── Pipfile :: Development Environment
    ├── README.rst
    ├── package.json :: NPM Mermaid-CLI
    ├── policy-modes.yaml :: Couple modes to policies
    └── tox.ini :: Tox automation
