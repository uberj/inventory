.. |project| replace:: mozinv

Welcome to |project|'s documentation!
=====================================

    "It is highly recommended that you use some software which automates this checking, or generate your
    DNS data from a database which automatically creates consistent data."

    -- `RFC 1912 <http://tools.ietf.org/html/rfc1912>`_



Vocabulary (DNS Jargon)
=======================
* Name and Label: "Each node in the DNS tree has a name consisting of zero or more labels"  `RFC4343 <http://tools.ietf.org/html/rfc4343>`_ . The name ``x.y.z`` consists of the labels ``x``, ``y``, and ``z``. When talking about a name that corresponds to an actual system, the last label is sometimes referred to as the 'hostname'.

* Forward: Used to reference the part of DNS that maps names to Ip addresses.

* Reverse: Used to reverence the part of DNS that maps Ip addresses to names.

Quick Read
==========
*Read these pages for a TL;DR*

*   :ref:`core`

*   :ref:`domain`

Q: Who are these docs for?

A: People who have to read the source code of this project.

Core
====

.. toctree::
   :maxdepth: 2

   staticinterface
   core
   site
   vlan
   network
   range
   flows

DNS
===

The following dns records are supported: A, AAAA, PTR, CNAME, MX, NS, SRV, TXT, SSHFP and SOA

.. toctree::
   :maxdepth: 2

   domain
   label_domain
   dns_views
   soa
   nameserver
   mx
   ip
   common_record
   address_record
   ptr
   cname
   srv
   txt
   sshfp
   validation

DHCP
====
.. toctree::
   :maxdepth: 2

   DHCP

Lib
===

.. toctree::
   :maxdepth: 2

   coding_standard
   lib
   api

Migration
---------
.. toctree::

    migration


Random
------
In prod::

    mysql> SELECT * FROM information_schema.session_variables WHERE variable_name = 'tx_isolation';
    +---------------+-----------------+
    | VARIABLE_NAME | VARIABLE_VALUE  |
    +---------------+-----------------+
    | TX_ISOLATION  | REPEATABLE-READ |
    +---------------+-----------------+
    1 row in set (0.00 sec)






Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
