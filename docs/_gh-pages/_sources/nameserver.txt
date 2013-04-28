.. _nameserver:

Nameservers
===========

Docs on how ``NS`` records are stored.

Glue Records
------------

    "If the name server does lie within the domain it should have a
    corresponding A record"

    -- `zytrax.com <http://www.zytrax.com/books/dns/ch8/ns.html>`_.

The the previous RFC citation, the corresponding A record is called a *glue
record*. The :class:`Nameserver` model will enforce the existence of glue
records where they are needed. If you create an ``NS`` record and that ``NS``
record is in within the domain it was created for, you will be forced to create
a glue record first.

For example: Let's say you you are authoritative for the ``foo.com`` domain,
child domains of ``foo.com``, and all records in those domains and everything
is in the ``foo.com`` zone. Now, you go to create an ``NS`` entry for your
nameserver ``ns1.foo.com``.  You want the record::

    foo.com     ``NS``      ns1.foo.com


Because ``ns1.foo.com`` is in the ``foo.com`` domain, you need to create a glue
record for ``ns1.foo.com``. The glue record is just an ``A`` or ``AAAA`` record.
The :class:`Nameserver` class will not allow the creation of the ``NS`` entry
before the glue record exists.

If you create an ``NS`` record that points to a name that exists outside of the
domain you are making the ``NS`` record for, you don't need to create the glue
record.

For example: Let's say you are authoritative for the ``foo.com`` zone in the
exact same way you were for the previous example. You go to create an ``NS``
record for the ``foo.com`` domain and you choose the name server
``ns1.bar.com``.  You want the record::

        foo.com     ``NS``      ns1.bar.com

Since ``ns1.bar.com`` is not the in the ``foo.com`` domain, you do not need to
create a glue record.

Nameservers and SOA Records
---------------------------
Bind requires that at least one ``NS`` record exist at the same level as an SOA
record. This state would be ensured by handling the following three cases:

    * An ``NS`` record doesn't exist for a zone's root domain, an attempt is made
      to create a non ``NS`` record in the zone (CNAME, A, TXT, etc.).
    * Non-``NS`` records exist in a zone along with one ``NS`` record at the
      root domain, an attempt is made to delete the ``NS`` record.
    * A record exists outside of a zone and then the record's domain (or one of
      it's master domains) is pointed toward a valid SOA, thus creating a new zone.
      If no ``NS`` record exist at the root domain of the SOA the database
      would be in an invalid state.

Currently, the invalid state is allowed in the database and the case where a
zone's root domain has no ``NS`` record is handled at zone file compilation time.
That is, if a zone is found to be in an invalid state it's zone file is not
created and it's zone is not included in the ``named.conf`` configuration file.

General approach to preventing this state:

Case 1::

    if new_record.domain.soa:
        # The case of new_record.reverse_domain would be covered similarly
        root_domain = new_record.domain.soa.root_domain
        if root_domain and not root_domain.nameserver_set.exists():
            raise ValidationError("Case 1")

Case 2::

    class Nameserver(Model):
        ...
        ...
        def delete(self):
            ...
            ...
            if (self.domain.soa.root_domain == self.domain and
                self.domain.nameserver_set.count() == 1 and  # We are it!
                self.domain.recursive_has_record_set()):
                raise ValidationError("Case 2")
            ...
            ...

Case 3::

    class Domain(Model):
        ...
        ...
        def save(self):
            ...
            ...
            if self.pk:
                ...
                ...
                db_self = Domain.objects.get(pk=self.pk)
                if (db_self.soa != self.soa and  # Our SOA has changed
                    not self.soa.root_domain and  # We are about to be the root
                    not self.nameserver_set.exists() and
                    self.recursive_has_record_set()):
                    raise ValidationError("Case 3")
                ...
                ...



Nameserver
----------
.. automodule:: mozdns.nameserver.models
    :inherited-members:
