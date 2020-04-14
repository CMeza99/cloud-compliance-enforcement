Cloud Policy Enforcement
========================

Manage and enforce cloud policies with `Cloud Custodian`_.

Requirements
------------

* Python 3.8
* Tox >= 3.0
* Pipenv (for dev environment)


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
