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
