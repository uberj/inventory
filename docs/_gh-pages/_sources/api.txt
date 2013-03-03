Inventory DNS API
=================


A high level view of how the API works::

    +------+
    | User |
    +------+
        |
    +------------------------+
    | Command Line Interface |   <----------- See page on CLI for this
    +------------------------+
        |
    +---------------+
    | HTTP POST/GET |   <----------- This document defines what is happening here.
    +---------------+
        |
    +----------+
    | Iventory |
    +----------+
        |
    +----------+
    | Database |
    +----------+

.. include:: api.man.rst
