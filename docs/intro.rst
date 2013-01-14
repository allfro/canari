
Introduction
============

Welcome to the official documentation for the `Canari Framework <http://canariproject.com>`_. The
`Canari Framework <http://canariproject.com>`_ is a rapid transform development framework that can be used to develop
**local and remote** transforms for `Maltego <http://paterva.com>`_ . Designed on the principles of convention over
configuration, developing transforms using Canari is extremely fast and easy. Canari takes care of XML serialization and
deserialization, argument or parameter parsing, as well as transform configuration and execution. Not only is Canari
great for Maltego transform development but it is also extremely easy to test, debug, and distribute your transforms.
Canari provides a powerful transform package specification that makes local transform distribution a cinch. Installing a
set of Maltego transforms, entities, and Maltego Scripts (or Machines) is as easy as typing one line in your terminal.
Even if you're not a Python developer, Canari has support for easily distributing transforms written in different
languages (i.e. PERL, Java, Ruby, etc.). The following subsections will provide an in-depth look of Canari's features,
libraries, and transform package specification.


Terminology
-----------

Before we get started with the documentation, it might be useful to introduce some of the terminology that will be used
throughout the documentation:

+-----------------------+----------------------------------------------------------------------------------------------+
| Term                  | Definition                                                                                   |
+=======================+==============================================================================================+
| **Entity**            | a piece of information on a Maltego graph represented as a node.                             |
+-----------------------+----------------------------------------------------------------------------------------------+
| **Input Entity**      | the entity that is being passed into the transform to use for data mining purposes.          |
+-----------------------+----------------------------------------------------------------------------------------------+
| **Output Entity**     | the entity that is being returned by the transform to be drawn on a Maltego graph.           |
+-----------------------+----------------------------------------------------------------------------------------------+
| **Transform**         | a function that takes one *input entity* as input and returns zero or more *output entities*.|
+-----------------------+----------------------------------------------------------------------------------------------+
| **Transform Module**  | a python module local transform code.                                                        |
+-----------------------+----------------------------------------------------------------------------------------------+
| **Transform Package** | a python package containing one or more transform modules, entities, and Maltego machines.   |
+-----------------------+----------------------------------------------------------------------------------------------+


Installing Canari
-----------------

Canari is officially supported on Python versions 2.6 and 2.7 with `setuptools <http://pypi.python.org/pypi/setuptools>`_
on Linux and Mac OS/X. Canari has not yet been tested on Windows but should be able to operate in this environment as
well. To install setuptools in your Python distribution, simply go to `<http://pypi.python.org/pypi/setuptools>`_ and
download the corresponding Python egg distribution for your operating system and follow the instructions for
installation. Once setuptools is installed, type the following command in your terminal::

    $ sudo easy_install canari

This will install of Canari's dependencies (argparse and pexpect) as well as Canari's transform development tool-suite.
If successful, you should be able to run Canari's commander by typing ``canari list-commands`` at the command-prompt::

    $ canari list-commands
    create-package - Creates a Canari transform package skeleton.
    create-transform - Creates a new transform in the specified directory and auto-updates __init__.py.
    csv2sheets - Convert mixed entity type CSVs to separated CSV sheets.
    debug-transform - Runs Canari local transforms in a terminal-friendly fashion.
    delete-transform - Deletes a transform in the specified directory and auto-updates __init__.py.
    generate-entities - Converts Maltego entity definition files to Canari python classes. Excludes Maltego built-in entities.
    install-package - Installs and configures canari transform packages in Maltego's UI
    list-commands - Lists all the available canari commands
    mtgx2csv - Convert Maltego graph files (*.mtgx) to comma-separated values (CSV) file.
    rename-transform - Renames a transform in the specified directory and auto-updates __init__.py.
    run-server - Runs a transform server for the given packages.
    run-transform - Runs Canari local transforms in a terminal-friendly fashion.
    shell - Creates a Canari debug shell for the specified transform package.
    uninstall-package - Uninstalls and unconfigures canari transform packages in Maltego's UI

If you were unable to run the Canari commander then please refer to :ref:`ref_troubleshoot` for information. Otherwise,
let's dive right into the :ref:`ref_canari_commander`.

.. _ref_troubleshoot:

Trouble-shooting Canari Installations
-------------------------------------

In some odd cases, the ``canari`` commander is inaccessible due to erroneous permission or system path definitions. To
troubleshoot this issue ensure the following two conditions are true:

* The path where ``canari`` is installed (i.e. ``/usr/local/bin``) has read and execute permissions for everyone.
* The system's ``PATH`` environment variable includes the path where ``canari`` has been installed.

The following subsections provide some pointers for trouble-shooting Canari installations on specific operating systems.


Linux and Mac OS/X
^^^^^^^^^^^^^^^^^^

To determine the location of your ``canari`` script, check the output of ``easy_install``::

    $ sudo easy_install canari
    ...
    Installing canari script to /usr/local/bin
    Installing dispatcher script to /usr/local/bin
    Installing pysudo script to /usr/local/bin
    ...

Once you've determined the location of the ``canari`` script (e.g. ``/usr/local/bin``), ensure that it is in
your system's ``PATH`` environment variable::

    $ echo $PATH
    /usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin

If the ``canari`` script's path is not included in your system's ``PATH`` environment variable, then check your
operating system's documentation on how to modify your ``PATH`` environment variable. Otherwise, if the path is in your
system's ``PATH`` environment variable and you are still unable to run ``canari`` then you'll want to ensure that the
``canari`` script's parent directory is accessible by everyone::

    $ ls -l /usr/local
    total 0
    drwxr-xr-x  58 root  wheel  1972  7 Jan 23:42 bin
    ...


Ensure that ``canari``'s parent directory (e.g. ``/usr/local/bin``) has ``755`` permissions. If not, use the following
command to correct the directory's permissions::

    $ sudo chmod 755 /usr/local/bin

If none of these steps have helped correct this issue please feel free to send an email to `<bugs@canariproject.com>`_
for additional help with the following details:

    * Operating system name and version.
    * Canari version.
    * ``easy_install`` output.

Windows
^^^^^^^

.. note::

    Canari has not been tested on Windows yet.
