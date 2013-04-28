.. _bind:

## TODO REWRITE THIS ALL!

Building Bind Files
===================
While building zone and configuration files the DNS build script acquires and
yields a build mutex, uses a staging area for building new zone files, runs
integrity checks on new and existing zone and configuration files, handles
errors when they happen, and does sanity checking using the underlying VCS
(Version Control System).

Main
----
The build script starts in a :func:`main` function (currently in
``scripts/dnsbuilds/main.py``). In :func:`main`, command line arguments are
parsed and an :class:`DNSBuilder` instance is asked to do it's build routine
(:func:`build_dns`) inside of a ``try-except`` block.  Any error in the build
script will result in a failure email being sent.

.. note::
    To see information about configuration options pass the ``--help`` option
    to the build script.

locking
+++++++
Once :func:`build_dns` is called the build script attempts to obtain the
build mutex. The lock is implemented via the ``flock`` utility (see ``man 1 flock``).

.. note::
    The location of the lock file is specified by ``settings.dnsbuilds.LOCK_FILE``.
    If you change the location of the lock file make sure no instances of
    the script is already running.


staging
+++++++
Assuming :func:`build_dns` successfully gets the mutex, the script will attempt to
create a staging area. By default the build script will fail if a staging area
already exists, which would only happen when the script experiences an error mid
build or the ``--preserve-stage`` flag is passed to the build script. The staging
area is a good place to inspect zone files that fail sanity checks or are
rejected by BIND verification tools (like ``named-checkzone`` and
``named-checkconf``). If you are certain that the build script should overwrite a
stale staging area, pass the ``--clobber-stage`` flag to the build script.

.. note::
    The location of the staging area is specified by
    ``settings.dnsbuilds.STAGE_DIR``. The staging area is ephemeral and can live
    somewhere like `/tmp`.

Building zone and configuration files
+++++++++++++++++++++++++++++++++++++
.. note::
    This entire step can be skipped by passing the ``--no-build`` flag.

The build script uses the DNS data found in inventory's database to generate
BIND zone files which it then references in generated ``zone`` statements. To
create zone files the script begins by isolating a zone's :class:`SOA`
record. Using an SOA object along with the :class:`Domain` at the root of the
zone as arguments, the script calls a helper function :func:`build_zone_data`
that returns two pieces of data (strings): a string containing records that
are in the private :class:`View` of the zone and another string containing the
records in the zone's public :class:`View`. The serial in both the zone
files is left undetermined and is calculated later in the build process.

.. note::
    If no data is returned for a view, the zone file and ``zone`` statement
    corresponding to that view is not created.

Using the view specific zone data provided by :func:`build_zone_data` the build
script proceeds to write the zone files. This process happens in
:func:`build_view` and begins by calculating where the view's zone file should
be stored in the VCS (see :func:`calc_fname` and :func:`calc_target` for a more
in-depth explanation about how file locations are determined). Once the file
path of the view's zone file is known, the build script calls
:func:`verify_prev_build` to determine if the view's zone file is already
present. If the zone file is present, the file is parsed and the SOA inside has
it's serial number extracted. If the serial found in the existing zone file
doesn't match the serial of view's SOA, the zone is marked to be rebuilt; the
new serial number of the zone is set to be the higher of the two serial numbers
plus one. If the parsed serial matches the serial of the view's SOA, the zone
has not been changed. If it is found that the view's zone file doesn't exist,
the zone is marked to be rebuilt.

.. note::
    A zone will not be built if it's root domain (the domain referenced in the
    SOA record) does not have an NS record. See the :ref:`nameserver` docs for
    more info on this edge case.

.. note::
    If a zone has already been marked as needing to be rebuilt, the function
    :func:`verify_prev_build` will not change it to being 'Up To Date' even if
    the serial on the zone's SOA matches the one in the VCS.

.. note::
    If a view corresponding to a zone is flagged as needing to be rebuilt
    by :func:`verify_prev_build`, the build script will rebuild all views
    corresponding to that zone even if they don't necessarily need to be
    rebuilt.

At this point the build script has decided whether to rebuild the zone or to
leave the zone and it's zone files untouched in the VCS. If the zone is not
going to be rebuild, the file path to it's zone files is passed to
:func:`named_checkzone` and if that goes well the function :func:`build_zone`
is called to rebuild the zone. The zone is rebuilt by first writing the zone's
data to a file in the staging area. Then the newly created zone file is
passed to :func:`named_checkzone` and if that check passes the file is copied
over to the VCS (changes are *not* checked in yet).

Whether or not a zone is rebuilt, ``zone`` statements corresponding to the zone's
views are generated (see :func:`render_zone_stmt`) and stored in either the
list ``private_zone_stmts`` or ``public_zone_stmts``. Using these two lists the
build script generates configuration files that are intended to be used in an
``$INCLUDE`` statement inside of a BIND ``view`` statement. The configuration
files are written to a file in the staging area which is then passed to
:func:`named_checkconf` before being copied over into the VCS.

.. note::
    Currently, the zone statements have ``type master;`` in them and are put into
    the files ``master.private`` and ``master.public``.

The next step in the build process is sanity checking and updating the
underlying VCS.

SVN as the VCS
--------------
A mixin class is used to implement the function :func:`vcs_checkin` if the flag
``--ship-ip`` is provided to the build script. By default the build script will
not check files into the VCS.

The SVN mixin class calculates the total number of lines added and removed
during the build run. If it is found that the delta is too large the build
script will be forced to fail. If the delta is appropriate the function
:func:`svn_checkin` checks changes into SVN and includes the aggregate lines
added/removed in it's commit message.  If no lines have been added or removed,
no files are checked in and no commit happens.

Clean Up
--------
The last thing the build script does is remove it's staging area and yields the
build mutex. Passing ``--preserve-stage`` will cause the build script to not
remove the staging area after the build run is over even if the run is
successful. The build script will always yield the build mutex even if the
script encounters an error.

.. note::
    The lines added/removed delta is configured by the
    MAX_ALLOWED_LINES_CHANGED variable at settings.MAX_ALLOWED_LINES_CHANGED.

.. autoclass:: mozdns.mozbind.builder.BuildError
    :inherited-members:

.. autoclass:: mozdns.mozbind.builder.DNSBuilder
    :inherited-members:

.. automodule:: mozdns.mozbind.zone_builder
    :inherited-members: build_zone_data
