.. _ref_canari_commander:

Canari Commander
================

The Canari commander (``canari``) script provides all of the functionality to create, debug, execute, distribute, and
install transforms. The ``canari`` commander provides the following set of commands:

+--------------------------+-------------------------------------------------------------------------------------------+
| Canari Command           | Description                                                                               |
+==========================+===========================================================================================+
| :ref:`create-package`    | Creates a Canari transform package skeleton.                                              |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`create-transform`  | Creates a new transform in the specified directory and auto-updates ``__init__.py``.      |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`csv2sheets`        | Convert mixed entity type CSVs to separated CSV sheets.                                   |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`debug-transform`   | Runs Canari local transforms in a terminal-friendly fashion.                              |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`delete-transform`  | Deletes a transform in the specified directory and auto-updates ``__init__.py``.          |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`generate-entities` | Converts Maltego entity definition files to Canari python classes. Excludes Maltego       |
|                          | built-in entities.                                                                        |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`help`              | Provides detailed help on a specific command (alias for ``-h`` option in all commands).   |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`install-package`   | Installs and configures Canari transform packages in Maltego's UI                         |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`list-commands`     | Lists all the available Canari commands                                                   |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`mtgx2csv`          | Convert Maltego graph files (``*.mtgx``) to comma-separated values (CSV) file.            |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`rename-transform`  | Renames a transform in the specified directory and auto-updates ``__init__.py``.          |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`run-server`        | Runs a transform server for the given packages.                                           |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`run-transform`     | Runs Canari local transforms in a terminal-friendly fashion.                              |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`shell`             | Creates a Canari debug shell for the specified transform package.                         |
+--------------------------+-------------------------------------------------------------------------------------------+
| :ref:`uninstall-package` | Uninstalls and unconfigures canari transform packages in Maltego's UI                     |
+--------------------------+-------------------------------------------------------------------------------------------+


Canari Commands
---------------

The following subsections provide detailed information on each of the ``canari`` commands. Each of these commands accept
an additional ``-h`` argument that is an alias to the ``help`` command.


.. _list-commands:

``list-commands``
^^^^^^^^^^^^^^^^^

The ``list-commands`` command accepts lists all of the available ``canari`` commands along with a brief description. It
accepts no parameters::

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
    ...

.. _help:

``help``
^^^^^^^^

The ``help`` command displays detailed help on a specific ``canari`` command. It accepts the following parameters:

* ``<command name>`` (**required**): the name of the ``canari`` command you're seeking help for.

The following example illustrates the use of the ``canari help`` command to display detailed help for the
``run-transform`` command::

    $ canari help run-transform
    usage: canari run-transform <transform> [param1 ... paramN] <value> [field1=value1...#fieldN=valueN]

    Runs Canari local transforms in a terminal-friendly fashion.

    positional arguments:
      <transform>           The name of the transform you wish to run (e.g.
                            sploitego.transforms.nmapfastscan).
      <value>               The value of the input entity being passed into the
                            local transform.
      [param1 ... paramN]   Any extra parameters that can be sent to the local
                            transform.
      [field1=value1...#fieldN=valueN]
                            The fields of the input entity being passed into the
                            local transform.

    optional arguments:
      -h, --help            show this help message and exit

.. _run-transform:

``run-transform``
^^^^^^^^^^^^^^^^^

The ``run-transform`` command loads and executes the specified local transform module, returning transform results to
the Maltego UI. It accepts the following parameters:

* ``<transform module>`` (**required**): the name of the python module that contains the local transform data mining
  logic (e.g. :py:mod:`sploitego.transforms.whatismyip`)
* ``[param1 ... paramN]`` (**optional**): any extra local transform parameters that can be parsed using
  :py:mod:`argparse` (e.g. ``-p 80``)
* ``<value>`` (**required**): the value of the entity being passed into the local transform (e.g. ``google.com``)
* ``[field1=value1...#fieldN=valueN]`` (**optional**): optionally, any entity field values delimited by # (e.g.
  ``url=http://www.google.ca#public=true``)

The following example illustrates the use of ``canari run-transform`` to execute the :py:mod:`sploitego.transforms.whatismyip`
transform module that comes bundled with the `Sploitego <https://github.com/allfro/sploitego>`_ transform package::

    $ canari run-transform sploitego.transforms.whatismyip -
    <MaltegoMessage><MaltegoTransformResponseMessage><Entities><Entity Type="maltego.IPv4Address"><Value>192.168.0.200</Value>
    <Weight>1</Weight><AdditionalFields><Field DisplayName="Internal" MatchingRule="strict" Name="ipaddress.internal">true</Field>
    <Field DisplayName="Hardware Address" MatchingRule="strict" Name="ethernet.hwaddr">de:ad:be:ef:fe:ed</Field></AdditionalFields>
    </Entity></Entities></MaltegoTransformResponseMessage></MaltegoMessage>

.. _debug-transform:

``debug-transform``
^^^^^^^^^^^^^^^^^^^

The ``debug-transform`` command operates in the same fashion as the :ref:`run-transform` command but outputs the result
in a terminal friendly manner. The following example illustrates the use of ``canari debug-transform`` to execute the
:py:mod:`sploitego.transforms.nmapfastscan` transform module on ``www.google.ca``::

    $ canari run-transform sploitego.transforms.nmapfastscan www.google.com
      `- MaltegoTransformResponseMessage:
        `- Entities:
          `- Entity:  {'Type': 'sploitego.Port'}
            `- Value: 80
            `- Weight: 1
            `- AdditionalFields:
              `- Field: TCP {'DisplayName': 'Protocol', 'Name': 'protocol', 'MatchingRule': 'strict'}
              `- Field: Open {'DisplayName': 'Port Status', 'Name': 'port.status', 'MatchingRule': 'strict'}
              `- Field: 173.194.75.147 {'DisplayName': 'Destination IP', 'Name': 'ip.destination', 'MatchingRule': 'strict'}
              `- Field: syn-ack {'DisplayName': 'Port Response', 'Name': 'port.response', 'MatchingRule': 'strict'}
            `- IconURL: file:///Library/Python/2.6/site-packages/canari-1.0-py2.6.egg/canari/resources/images/networking/openport.gif
            `- DisplayInformation:
              `- Label: http {'Type': 'text/text', 'Name': 'Service Name'}
              `- Label: table {'Type': 'text/text', 'Name': 'Method'}
    ...


.. _run-server:

``run-server``
^^^^^^^^^^^^^^

The ``run-server`` command loads one or more transform packages and handles remote transform requests brokered by a
`Transform Distribution Server (TDS) <http://paterva.com>`_ via port 80 or 443 (if SSL enabled). ``run-server``
provides similar functionality to the `Paterva Transform Application Server <http://paterva.com>`_. It accepts the
following parameters:

* ``<package>`` (**required**): The name of the transform packages you wish to host (e.g. :py:mod:`mypkg.transforms`).
* ``--port <port>`` (**optional**): The port the server will run on (default: 443; or 80 if SSL is disabled).
* ``--disable-ssl`` (**optional**): Any extra parameters that can be sent to the local transform.
* ``--enable-privileged`` (**optional**): permit TAS to run packages that require elevated privileges.
* ``--listen-on <address>`` (**optional**): The address of the interface to listen on.
* ``--cert <certificate>`` (**optional**): The name of the certificate file used for the server in PEM format.
* ``--hostname <hostname>`` (**optional**): The hostname of this transform server.
* ``--daemon`` (**optional**): Daemonize server (fork to background).

The following example illustrates the use of ``canari run-server`` to operate a transform application server to serve
transform requests for transforms belonging to the :py:mod:`sploitego` transform package::

    $ canari run-server sploitego --disable-ssl
    You must run this server as root to continue...
    Loading transform packages...
    Loading transform package sploitego.transforms
    WARNING: No route found for IPv6 destination :: (no default route?)
    Loading sploitego.transforms.bcsitereview at /sploitego.transforms.bcsitereview...
    Loading sploitego.transforms.sitereputation at /sploitego.transforms.sitereputation...
    Starting web server on :80...
    Really? Over regular HTTP? What a shame...


.. note::

    ``run-server`` will automatically ask for ``root`` credentials if the server is listening on ports in the reserved
    range (0-1024) or if any of the transform modules within the specified transform package is decorated with the
    :py:func:`@superuser` decorator and ``--enable-privileged`` is set.

.. _install-package:

``install-package``
^^^^^^^^^^^^^^^^^^^

The ``install-package`` command installs and configures a transform package (transforms, entities, Maltego machines) in
the Maltego UI. It accepts the following parameters:

* ``<package>`` (**required**): name of the transform package that contains transform modules (i.e. ``canari``).
* ``-s [dir]``, ``--settings-dir=[dir]`` (**optional**): the name of the directory that contains Maltego's settings.

.. note::

    The Maltego settings directory is typically located in the following locations:

    * **Linux**: ``~/.maltego/<version>`` (i.e. ``~/.maltego/3.2.0``)
    * **Mac OS/X**: ``~/Library/Application\ Support/maltego/<version>`` (i.e. ``~/Library/Application\ Support/maltego/3.2.0``)

* ``-w [dir]``, ``--working-dir=[dir]`` (**optional, default: current working directory**): the default working
  directory for the Maltego transforms.

The following example illustrates the use of ``canari install-package`` command to install transforms from the
:py:mod:`sploitego` transform package::

    $ canari install-package sploitego
    Installing transform sploitego.v2.NmapReportToBanner_Amap from sploitego.transforms.amap...
    Installing transform sploitego.v2.WebsiteToSiteCategory_BlueCoat from sploitego.transforms.bcsitereview...
    Installing transform sploitego.v2.DomainToDNSName_Bing from sploitego.transforms.bingsubdomains...
    Installing transform sploitego.v2.DNSNameToIPv4Address_DNS from sploitego.transforms.dnsalookup...
    Installing transform sploitego.v2.IPv4AddressToDNSName_CacheSnoop from sploitego.transforms.dnscachesnoop...
    Installing transform sploitego.v2.NSRecordToDNSName_CacheSnoop from sploitego.transforms.dnscachesnoop...
    ...

.. warning::

    You must have initialized Maltego for the first time before attempting to install a transform package using
    ``install-package``. Otherwise, the installation will fail.

.. warning::

    **DO NOT** run ``canari install-package`` as ``root`` unless you intend to run Maltego as ``root`` at all times.

.. _uninstall-package:

``uninstall-package``
^^^^^^^^^^^^^^^^^^^^^

The ``uninstall-package`` command uninstalls and un-configures all the local transform modules within the specified
transform package in the Maltego UI. It accepts the following parameters:

* ``<package>`` (**required**): name of the transform package that contains transform modules. (i.e. :py:mod:`sploitego`)
* ``-s [dir]``, ``--settings-dir=[dir]`` (**optional**): the name of the directory that contains Maltego's settings
  (i.e. ``~/.maltego/<version>`` in Linux, ``~/Library/Application\ Support/maltego/<version>`` in Mac OS X)

The following example illustrates the use of ``canari uninstall-package`` to uninstall transforms from the
:py:mod:`sploitego` transform package::

    $ canari uninstall-package sploitego
    Multiple versions of Maltego detected:
    [0] Maltego v3.1.1
    [1] Maltego v3.1.1CE
    Please select which version you wish to install the transforms in [0]: 1
    Uninstalling transform sploitego.v2.NmapReportToBanner_Amap from sploitego.transforms.amap...
    Uninstalling transform sploitego.v2.WebsiteToSiteCategory_BlueCoat from sploitego.transforms.bcsitereview...
    Uninstalling transform sploitego.v2.DomainToDNSName_Bing from sploitego.transforms.bingsubdomains...
    Uninstalling transform sploitego.v2.DNSNameToIPv4Address_DNS from sploitego.transforms.dnsalookup...
    Uninstalling transform sploitego.v2.IPv4AddressToDNSName_CacheSnoop from sploitego.transforms.dnscachesnoop...
    Uninstalling transform sploitego.v2.NSRecordToDNSName_CacheSnoop from sploitego.transforms.dnscachesnoop...

.. _shell:

``shell``
^^^^^^^^^

The canari shell script offers an interactive shell for running transforms (work in progress). It accepts the following
parameters:

* ``<transform package>`` (**required**): the name of the transform package to load.

The following example illustrates the use of canari shell to run transforms from the sploitego transform package::

    $ canari shell sploitego
    Welcome to Canari.
    mtg> whatismyip('4.2.2.1')
    `- MaltegoTransformResponseMessage:
      `- Entities:
        `- Entity:  {'Type': 'maltego.IPv4Address'}
          `- Value: 10.0.1.22
          `- Weight: 1
          `- AdditionalFields:
            `- Field: true {'DisplayName': 'Internal', 'Name': 'ipaddress.internal', 'MatchingRule': 'strict'}
            `- Field: 68:a8:6d:4e:0f:72 {'DisplayName': 'Hardware Address', 'Name': 'ethernet.hwaddr', 'MatchingRule': 'strict'}
    mtg>

.. _create-package:

``create-package``
^^^^^^^^^^^^^^^^^^

The ``create-package`` command generates a transform package skeleton for eager transform developers. It accepts the
following parameters:

* ``<package name>`` (**required**): the desired name of the transform package you wish to develop.

The following example illustrates the use of ``canari create-package`` to create a transform package named
:py:mod:`foobar`::

    $ canari create-package foobar
    creating skeleton in foobar
    creating directory foobar
    creating directory foobar/src
    creating directory foobar/maltego
    creating directory foobar/src/foobar
    creating directory foobar/src/foobar/transforms
    creating directory foobar/src/foobar/transforms/common
    creating directory foobar/src/foobar/resources
    creating directory foobar/src/foobar/resources/etc
    creating directory foobar/src/foobar/resources/images
    creating file foobar/setup.py...
    creating file foobar/README.md...
    creating file foobar/src/foobar/__init__.py...
    creating file foobar/src/foobar/resources/__init__.py...
    creating file foobar/src/foobar/resources/etc/__init__.py...
    creating file foobar/src/foobar/resources/images/__init__.py...
    creating file foobar/src/foobar/resources/etc/foobar.conf...
    creating file foobar/src/foobar/transforms/__init__.py...
    creating file foobar/src/foobar/transforms/helloworld.py...
    creating file foobar/src/foobar/transforms/common/__init__.py...
    creating file foobar/src/foobar/transforms/common/entities.py...
    done!


.. _create-transform:

``create-transform``
^^^^^^^^^^^^^^^^^^^^

The ``create-transform`` command generates a transform module and automatically adds it to the ``__init__.py`` file in a
transform package. It accepts the following parameters:

* ``<transform name>`` (**required**): the desired name of the transform module to create.

The following example illustrates the use of ``canari create-transform`` to create a transform module named
:py:mod:`cooltransform`::

    $ cd foobar/src/foobar/transforms/
    $ canari create-transform cooltransform
    creating file ./cooltransform.py...
    updating __init__.py
    done!

.. _rename-transform:

``rename-transform``
^^^^^^^^^^^^^^^^^^^^

The ``rename-transform`` command renames a transform module and automatically updates the corresponding ``__init__.py``
file entry in a transform package. It accepts the following parameters:

* ``<old transform name>`` (**required**): the name of the transform module to rename.
* ``<new transform name>`` (**required**): the new desired name of the transform module.

The following example illustrates the use of ``canari rename-transform`` to rename a transform module named
:py:mod:`cooltransform` to :py:mod:`mytransform`::

    $ cd foobar/src/foobar/transforms/
    $ canari rename-transform cooltransform mytransform
    renaming transform '/home/foo/foobar/src/foobar/transforms/cooltransform.py' to '/home/foo/foobar/src/foobar/transforms/mytransform.py'...
    updating /home/foo/foobar/src/foobar/transforms/__init__.py
    done!


.. _delete-transform:

``delete-transform``
^^^^^^^^^^^^^^^^^^^^

The ``delete-transform`` command deletes a transform module and automatically removes the corresponding ``__init__.py``
file entry in a transform package. It accepts the following parameters:

* ``<transform name>`` (**required**): the name of the transform module to delete.

The following example illustrates the use of ``canari delete-transform`` to delete a transform module named
:py:mod:`mytransform`::

    $ cd foobar/src/foobar/transforms/
    $ canari delete-transform mytransform
    deleting transform '/home/foo/foobar/src/foobar/transforms/poop.py'...
    updating /home/foo/foobar/src/foobar/transforms/__init__.py
    done!


.. _generate-entities:

``generate-entities``
^^^^^^^^^^^^^^^^^^^^^

The ``generate-entities`` command generates the Python/Canari definitions of the entities contained within Maltego or a
Maltego entity export file (``*.mtz``) and writes the result to a file. The entities within the ``maltego`` namespace
(or builtin entities) are automatically excluded and only custom entity definitions are generated. It accepts the
following parameters:

* ``<outfile>`` (**optional**): Which file to write the output to (default: ``entities.py``).
* ``--mtz-file <mtzfile>``, ``-m <mtzfile>`` (**optional**): A ``*.mtz`` file containing an export of Maltego entities.
* ``--exclude-namespace <namespace>``, ``-e <namespace>`` (**optional**): Name of Maltego entity namespace to ignore.
  Can be defined multiple times.
* ``--namespace <namespace>``, ``-n <namespace>`` (**optional**): Name of Maltego entity namespace to generate entity
  classes for. Can be defined multiple times.
* ``--append``, ``-a`` (**optional**): Whether or not to append to the existing ``entities.py`` file.
* ``--entity <entity>``, ``-E <entity>`` (**optional**): Name of Maltego entity to generate Canari python class for.

If no arguments are passed, the ``generate-entities`` command will load the entity definition files from Maltego's
setting directory and automatically generate an ``entities.py`` file in the current working directory.

.. warning::

    The ``generate-entities`` command will overwrite the current ``entities.py`` file if executed with no arguments in
    the ``src/<package>/transforms/common`` directory.


.. _mtgx2csv:

``mtgx2csv``
^^^^^^^^^^^^

The ``mtgx2csv`` command generates a comma-separated report (CSV) of a Maltego-generated graph. It accepts the
following parameters:

* ``<graph>`` (**required**): the name of the Maltego graph file.

The following example illustrates the use of ``canari mtgx2csv`` to create a CSV report of a Maltego graph file named
``Graph1.mtgx``::

    $ canari mtgx2csv ``Graph1.mtgx``
    $ ls *.csv
    Graph1.csv

.. _csv2sheets:

``csv2sheets``
^^^^^^^^^^^^^^

The ``csv2sheets`` command separates the CSV report file into multiple CSV files containing entities of the same type.
It accepts the following parameters:

* ``<csv report>`` (**required**): the name of the CSV report generated by ``canari mtgx2csv``
* ``<prefix>`` (**required**): a prefix to prepend to the generated CSV files.

The following example illustrates the use of ``canari csv2sheets`` to create a CSV files containing entities of the same
type from the CSV report Graph1.csv::

    $ csv2sheets Graph1.csv IRS
    $ ls *.csv
    Graph1.csv IRS_0.csv IRS_1.csv ...