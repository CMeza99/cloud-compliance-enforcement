Cloud Policy Enforcement Script
===============================

Requirements
--------------

* Python 3.8


Features
--------

* Compiles policies, so policy files can be DRY
* Validates compiled policies
* Executes Cloud Custodian with sane defaults and in parallel


Usage
-----

.. code-block:: console

  usage: cpe [-h] [-v] [-x {run}]

  Cloud Policy Enforcement Script: A workflow manager wrapping Cloud Custodian.

  optional arguments:
    -h, --help            show this help message and exit
    -v, --version         show program's version number and exit
    -x {run}, --c7n-cmd {run}
                          Cloud Custodian command to execute

  Policies are always validated, even when no c7n command is specified.


Example
-------

.. code-block:: console

   AWS_PROFILE=twds-se-test CPE_LOGLEVEL=debug CPE_DRYRUN=0 cpe -x run
