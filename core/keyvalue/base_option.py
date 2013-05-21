from django.db import models
from django.core.exceptions import ValidationError

from mozdns.validation import validate_name
from core.keyvalue.models import KeyValue

import ipaddr


class DHCPKeyValue(KeyValue):
    is_option = models.BooleanField(default=False)
    is_statement = models.BooleanField(default=False)
    has_validator = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def _get_value(self):
        value = self.value.strip('\'" ')
        value = value.strip(';')
        value = value.strip()
        return value


class InerfaceMixin(object):
    # Make sure you mix this in with a class that inherits from DHCPKeyValue
    def _aa_host_name(self):
        """
        option host-name text;

            This option specifies the name of the client. The name may or may
            not be qualified with the local domain name (it is preferable to
            use the domain-name option to specify the domain name). See RFC
            1035 for character set restrictions. This option is only honored by
            dhclient-script(8) if the hostname for the client machine is not
            set.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        if (len(self.value) < 2 or not (
                self.value.startswith('"') and self.value.endswith('"'))):
            raise ValidationError(
                "Make sure the hostname has \" \" around it"
            )
        validate_name(self.value.strip('"'))

    def _aa_domain_name_servers(self):
        """
        DHCP option domain-name-servers
        """
        if not self.value:
            raise ValidationError("Domain Name Servers Required")

    def _aa_domain_name(self):
        """
        DHCP option domain-name
        """
        if not self.value:
            raise ValidationError("Domain Name Required")

    def _aa_filename(self):
        """
        DHCP option filename
        """
        if not self.value:
            raise ValidationError("Filename Required")

    def _aa_hostname(self):
        """DHCP option hostname
        """
        if not self.value:
            raise ValidationError("Hostname Required")


class CommonOption(DHCPKeyValue):
    class Meta:
        abstract = True

    def _aa_deny(self):
        """
        See allow.
        """
        choices = ["unknown-clients", "bootp", "booting", "duplicates",
                   "declines", "client-updates", "dynamic bootp clients"]
        self.is_statement = True
        self.is_option = False
        self.has_validator = True
        value = self._get_value()
        values = value.split(',')
        for value in values:
            if value in choices:
                continue
            else:
                raise ValidationError("Invalid option ({0}) parameter "
                                      "({1})'".format(self.key, self.value))

    def _aa_allow(self):
        """
        The following usages of allow and deny will work in any scope, although
        it is not recommended that they be used in pool declarations.

            allow unknown-clients;
            deny unknown-clients;
            ignore unknown-clients;

            allow bootp;
            deny bootp;
            ignore bootp;
            allow booting;
            deny booting;
            ignore booting;

            allow duplicates;
            deny duplicates;

            allow declines;
            deny declines;
            ignore declines;

            allow client-updates;
            deny client-updates;

            allow dynamic bootp clients;
            deny dynamic bootp clients;
        """

        choices = ["unknown-clients", "bootp", "booting", "duplicates",
                   "declines", "client-updates", "dynamic bootp clients"]
        self.is_statement = True
        self.is_option = False
        self.has_validator = True
        value = self._get_value()
        values = value.split(',')
        for value in values:
            if value.strip() in choices:
                continue
            else:
                raise ValidationError(
                    "Invalid parameter '{0}' for the option "
                    "'{1}'".format(self.value, self.key))

    def _routers(self, ip_type):
        """
        option routers ip-address [, ip-address... ];

            The routers option specifies a list of IP addresses for routers on
            the client's subnet. Routers should be listed in order of
            preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list(ip_type)

    def _ntp_servers(self, ip_type):
        """
        option ntp-servers ip-address [, ip-address... ];

            This option specifies a list of IP addresses indicating NTP (RFC
            1035) servers available to the client. Servers should be listed in
            order of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list(ip_type)

    def _aa_domain_name_servers(self):
        """
        option domain-name-servers ip-address [, ip-address... ];

            The domain-name-servers option specifies a list of Domain Name
            System (STD 13, RFC 1035) name servers available to the client.
            Servers should be listed in order of preference.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        self._ip_list(self.obj.ip_type)

    def _aa_domain_name(self):
        """
        option domain-name text;

            The 'text' should be a space seperated domain names. I.E.:
            phx.mozilla.com phx1.mozilla.com This option specifies the domain
            name that client should use when resolving hostnames via the Domain
            Name System.
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        if (len(self.value) < 2 or not (
                self.value.startswith('"') and self.value.endswith('"'))):
            raise ValidationError(
                "Make sure the domain(s) name have \" \" around them"
            )
        for name in self.value.strip('"').split(' '):
            validate_name(name)

    def _aa_domain_search(self):
        """
        The domain-search option specifies a 'search list' of Domain Names to
        be used by the client to locate not-fully-qualified domain names. The
        difference between this option and historic use of the domain-name
        option for the same ends is that this option is encoded in RFC1035
        compressed labels on the wire. For example:

            option domain-search "example.com", "sales.example.com";
        """
        self.is_option = True
        self.is_statement = False
        self.has_validator = True
        value = self.value.strip(';')
        value = value.strip(' ')
        for name in value.split(','):
            # Bug here. Ex: "asf, "'asdf"'
            name = name.strip(' ')
            if not name:
                raise ValidationError("Each name needs to be a non empty "
                                      "domain name surrounded by \"\"")

            if name[0] != '"' and name[len(name) - 1] != '"':
                raise ValidationError("Each name needs to be a non empty "
                                      "domain name surrounded by \"\"")
            validate_name(name.strip('"'))

    def _ip_list(self, ip_type):
        """
        Use this if the value is supposed to be a list of ip addresses.
        """
        self.ip_option = True
        self.has_validator = True
        ips = self._get_value()
        ips = ips.split(',')
        for router in ips:
            router = router.strip()
            try:
                if ip_type == '4':
                    ipaddr.IPv4Address(router)
                else:
                    raise NotImplemented()
            except ipaddr.AddressValueError:
                raise ValidationError("Invalid option ({0}) parameter "
                                      "({1})'".format(self.key, router))

    def _single_ip(self, ip_type):
        ip = self._get_value()
        try:
            if ip_type == '4':
                ipaddr.IPv4Address(ip)
            else:
                raise NotImplemented()
        except ipaddr.AddressValueError:
            raise ValidationError("Invalid option ({0}) parameter "
                                  "({1})'".format(self.key, ip))
