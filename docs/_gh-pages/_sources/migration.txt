.. _migration:
.. |project| replace:: INV2

Migration
=========
So you want to use Inventory2.0. Here are some considerations:

To use the interface auto-generation, both the reverse and forward entries (A/PTR) that
|project| generates need to be under control of |project|. This means that |project| must
be in control of the DNS zones the and A/PTR are in.

Within each datacenter there are 5 points |project| needs to worry about:

    1) DNS records in the forward private file (dnsconfig/zones/mozilla.com/zones/scl3/private)
    2) DNS records in the forward public file (dnsconfig/zones/mozilla.com/zones/scl3/public)
    3) DNS records in variose private reverse files (dnsconfig/zones/in-addr/10*)
    4) DNS records in variose public reverse files (dnsconfig/external/db.*)
    5) DHCP ``host`` statements

I propose we put 1, 2, and 5 into |project| and leave 3 and 4 out for now. This will allow us to
use auto-host-generation where it would be the most useful (in private IP space) while minimizing
the initial amount of data we put into the system.

Proposed Migration Steps
>>>>>>>>>>>>>>>>>>>>>>>>
Step 1 Private Reverse (Point 3)
--------------------------------
As a first step, I propose that we get as much private reverse domains into |project| as we can.
*Any change to a reverse record under in a subdomain of 10.in-addr.arpa happen in inventory* [1].

Step 2 Forward DNS (Point 1 and 2)
----------------------------------
Once private reverse is managed by inventory we can move a Datacenter's forward records into the DNS
subsystem. At this point *``zones/<DC>/private`` and ``zones/<DC>/public`` will be in |project| and
|project| is where any change to a DC's forward DNS should happend.*




Migrating A Datacenter's Forward Zone (Step 1)
----------------------------------------------
Moving a datacenter's

[1] We might need to exclude services from this.

The consequences not including public reverse

    1) Decide which zones should initially be put into the new system::

        0.0.10.in-addr.arpa
        22.0.10.in-addr.arpa
        250.0.10.in-addr.arpa
        0.10.10.in-addr.arpa
        1.10.10.in-addr.arpa
        10.10.10.in-addr.arpa
        11.10.10.in-addr.arpa
        12.10.10.in-addr.arpa
        14.10.10.in-addr.arpa
        16.10.10.in-addr.arpa
        17.10.10.in-addr.arpa
        2.10.10.in-addr.arpa
        3.10.10.in-addr.arpa
        1.110.10.in-addr.arpa
        2.110.10.in-addr.arpa
        3.110.10.in-addr.arpa
        4.110.10.in-addr.arpa
        5.110.10.in-addr.arpa
        6.110.10.in-addr.arpa
        7.110.10.in-addr.arpa
        8.110.10.in-addr.arpa
        12.10.in-addr.arpa
        0.12.10.in-addr.arpa
        17.12.10.in-addr.arpa
        20.12.10.in-addr.arpa
        40.12.10.in-addr.arpa
        41.12.10.in-addr.arpa
        47.12.10.in-addr.arpa
        48.12.10.in-addr.arpa
        49.12.10.in-addr.arpa
        50.12.10.in-addr.arpa
        51.12.10.in-addr.arpa
        52.12.10.in-addr.arpa
        53.12.10.in-addr.arpa
        54.12.10.in-addr.arpa
        55.12.10.in-addr.arpa
        69.12.10.in-addr.arpa
        75.12.10.in-addr.arpa
        14.10.in-addr.arpa
        0.14.10.in-addr.arpa
        1.14.10.in-addr.arpa
        10.14.10.in-addr.arpa
        101.14.10.in-addr.arpa
        102.14.10.in-addr.arpa
        103.14.10.in-addr.arpa
        104.14.10.in-addr.arpa
        105.14.10.in-addr.arpa
        106.14.10.in-addr.arpa
        107.14.10.in-addr.arpa
        108.14.10.in-addr.arpa
        109.14.10.in-addr.arpa
        11.14.10.in-addr.arpa
        110.14.10.in-addr.arpa
        12.14.10.in-addr.arpa
        14.14.10.in-addr.arpa
        2.14.10.in-addr.arpa
        20.14.10.in-addr.arpa
        200.14.10.in-addr.arpa
        201.14.10.in-addr.arpa
        202.14.10.in-addr.arpa
        203.14.10.in-addr.arpa
        205.14.10.in-addr.arpa
        210.14.10.in-addr.arpa
        211.14.10.in-addr.arpa
        212.14.10.in-addr.arpa
        214.14.10.in-addr.arpa
        216.14.10.in-addr.arpa
        220.14.10.in-addr.arpa
        225.14.10.in-addr.arpa
        230.14.10.in-addr.arpa
        231.14.10.in-addr.arpa
        232.14.10.in-addr.arpa
        234.14.10.in-addr.arpa
        236.14.10.in-addr.arpa
        3.14.10.in-addr.arpa
        16.16/10.10.in-addr.arpa
        18.18/10.10.in-addr.arpa
        0.20.10.in-addr.arpa
        1.20.10.in-addr.arpa
        2.20.10.in-addr.arpa
        3.20.10.in-addr.arpa
        60.20.10.in-addr.arpa
        70.20.10.in-addr.arpa
        74.20.10.in-addr.arpa
        75.20.10.in-addr.arpa
        77.20.10.in-addr.arpa
        81.20.10.in-addr.arpa
        0.2.10.in-addr.arpa
        10.2.10.in-addr.arpa
        11.2.10.in-addr.arpa
        110.2.10.in-addr.arpa
        171.2.10.in-addr.arpa
        20.2.10.in-addr.arpa
        70.2.10.in-addr.arpa
        71.2.10.in-addr.arpa
        72.2.10.in-addr.arpa
        73.2.10.in-addr.arpa
        74.2.10.in-addr.arpa
        75.2.10.in-addr.arpa
        76.2.10.in-addr.arpa
        77.2.10.in-addr.arpa
        8.2.10.in-addr.arpa
        80.2.10.in-addr.arpa
        81.2.10.in-addr.arpa
        82.2.10.in-addr.arpa
        83.2.10.in-addr.arpa
        84.2.10.in-addr.arpa
        9.2.10.in-addr.arpa
        90.2.10.in-addr.arpa
        91.2.10.in-addr.arpa
        0.22.10.in-addr.arpa
        1.22.10.in-addr.arpa
        110.22.10.in-addr.arpa
        111.22.10.in-addr.arpa
        112.22.10.in-addr.arpa
        113.22.10.in-addr.arpa
        114.22.10.in-addr.arpa
        115.22.10.in-addr.arpa
        2.22.10.in-addr.arpa
        24.22.10.in-addr.arpa
        25.22.10.in-addr.arpa
        26.22.10.in-addr.arpa
        27.22.10.in-addr.arpa
        28.22.10.in-addr.arpa
        29.22.10.in-addr.arpa
        3.22.10.in-addr.arpa
        30.22.10.in-addr.arpa
        31.22.10.in-addr.arpa
        32.22.10.in-addr.arpa
        33.22.10.in-addr.arpa
        4.22.10.in-addr.arpa
        60.22.10.in-addr.arpa
        62.22.10.in-addr.arpa
        69.22.10.in-addr.arpa
        70.22.10.in-addr.arpa
        72.22.10.in-addr.arpa
        74.22.10.in-addr.arpa
        75.22.10.in-addr.arpa
        8.22.10.in-addr.arpa
        80.22.10.in-addr.arpa
        81.22.10.in-addr.arpa
        83.22.10.in-addr.arpa
        84.22.10.in-addr.arpa
        85.22.10.in-addr.arpa
        0.24.10.in-addr.arpa
        1.24.10.in-addr.arpa
        2.24.10.in-addr.arpa
        70.24.10.in-addr.arpa
        74.24.10.in-addr.arpa
        75.24.10.in-addr.arpa
        77.24.10.in-addr.arpa
        8.24.10.in-addr.arpa
        80.24.10.in-addr.arpa
        0.242.10.in-addr.arpa
        17.242.10.in-addr.arpa
        24.242.10.in-addr.arpa
        32.242.10.in-addr.arpa
        40.242.10.in-addr.arpa
        75.242.10.in-addr.arpa
        0.243.10.in-addr.arpa
        17.243.10.in-addr.arpa
        24.243.10.in-addr.arpa
        32.243.10.in-addr.arpa
        40.243.10.in-addr.arpa
        72.243.10.in-addr.arpa
        75.243.10.in-addr.arpa
        0.244.10.in-addr.arpa
        17.244.10.in-addr.arpa
        24.244.10.in-addr.arpa
        32.244.10.in-addr.arpa
        40.244.10.in-addr.arpa
        75.244.10.in-addr.arpa
        0.245.10.in-addr.arpa
        17.245.10.in-addr.arpa
        24.245.10.in-addr.arpa
        32.245.10.in-addr.arpa
        40.245.10.in-addr.arpa
        75.245.10.in-addr.arpa
        0.246.10.in-addr.arpa
        17.246.10.in-addr.arpa
        24.246.10.in-addr.arpa
        32.246.10.in-addr.arpa
        40.246.10.in-addr.arpa
        75.246.10.in-addr.arpa
        0.247.10.in-addr.arpa
        17.247.10.in-addr.arpa
        24.247.10.in-addr.arpa
        32.247.10.in-addr.arpa
        40.247.10.in-addr.arpa
        75.247.10.in-addr.arpa
        0.248.10.in-addr.arpa
        17.248.10.in-addr.arpa
        24.248.10.in-addr.arpa
        32.248.10.in-addr.arpa
        40.248.10.in-addr.arpa
        72.248.10.in-addr.arpa
        75.248.10.in-addr.arpa
        0.250.10.in-addr.arpa
        1.250.10.in-addr.arpa
        10.250.10.in-addr.arpa
        120.250.10.in-addr.arpa
        128.250.10.in-addr.arpa
        16.250.10.in-addr.arpa
        17.250.10.in-addr.arpa
        18.250.10.in-addr.arpa
        19.250.10.in-addr.arpa
        2.250.10.in-addr.arpa
        20.250.10.in-addr.arpa
        21.250.10.in-addr.arpa
        22.250.10.in-addr.arpa
        23.250.10.in-addr.arpa
        3.250.10.in-addr.arpa
        32.250.10.in-addr.arpa
        33.250.10.in-addr.arpa
        34.250.10.in-addr.arpa
        35.250.10.in-addr.arpa
        36.250.10.in-addr.arpa
        37.250.10.in-addr.arpa
        38.250.10.in-addr.arpa
        39.250.10.in-addr.arpa
        4.250.10.in-addr.arpa
        48.250.10.in-addr.arpa
        49.250.10.in-addr.arpa
        5.250.10.in-addr.arpa
        50.250.10.in-addr.arpa
        51.250.10.in-addr.arpa
        6.250.10.in-addr.arpa
        64.250.10.in-addr.arpa
        65.250.10.in-addr.arpa
        7.250.10.in-addr.arpa
        73.250.10.in-addr.arpa
        75.250.10.in-addr.arpa
        0.251.10.in-addr.arpa
        17.251.10.in-addr.arpa
        24.251.10.in-addr.arpa
        32.251.10.in-addr.arpa
        40.251.10.in-addr.arpa
        75.251.10.in-addr.arpa
        0.253.10.in-addr.arpa
        1.253.10.in-addr.arpa
        10.26.10.in-addr.arpa
        11.26.10.in-addr.arpa
        12.26.10.in-addr.arpa
        13.26.10.in-addr.arpa
        14.26.10.in-addr.arpa
        15.26.10.in-addr.arpa
        36.26.10.in-addr.arpa
        37.26.10.in-addr.arpa
        38.26.10.in-addr.arpa
        39.26.10.in-addr.arpa
        40.26.10.in-addr.arpa
        41.26.10.in-addr.arpa
        42.26.10.in-addr.arpa
        43.26.10.in-addr.arpa
        44.26.10.in-addr.arpa
        45.26.10.in-addr.arpa
        46.26.10.in-addr.arpa
        47.26.10.in-addr.arpa
        48.26.10.in-addr.arpa
        49.26.10.in-addr.arpa
        50.26.10.in-addr.arpa
        51.26.10.in-addr.arpa
        52.26.10.in-addr.arpa
        53.26.10.in-addr.arpa
        54.26.10.in-addr.arpa
        55.26.10.in-addr.arpa
        56.26.10.in-addr.arpa
        57.26.10.in-addr.arpa
        58.26.10.in-addr.arpa
        59.26.10.in-addr.arpa
        60.26.10.in-addr.arpa
        61.26.10.in-addr.arpa
        62.26.10.in-addr.arpa
        63.26.10.in-addr.arpa
        64.26.10.in-addr.arpa
        65.26.10.in-addr.arpa
        66.26.10.in-addr.arpa
        67.26.10.in-addr.arpa
        74.26.10.in-addr.arpa
        75.26.10.in-addr.arpa
        8.26.10.in-addr.arpa
        9.26.10.in-addr.arpa
        10.4.10.in-addr.arpa
        11.4.10.in-addr.arpa
        20.4.10.in-addr.arpa
        60.4.10.in-addr.arpa
        70.4.10.in-addr.arpa
        71.4.10.in-addr.arpa
        72.4.10.in-addr.arpa
        73.4.10.in-addr.arpa
        74.4.10.in-addr.arpa
        75.4.10.in-addr.arpa
        80.4.10.in-addr.arpa
        81.4.10.in-addr.arpa
        10.6.10.in-addr.arpa
        20.6.10.in-addr.arpa
        72.6.10.in-addr.arpa
        74.6.10.in-addr.arpa
        80.6.10.in-addr.arpa
        0.8.10.in-addr.arpa
        1.8.10.in-addr.arpa
        10.8.10.in-addr.arpa
        100.8.10.in-addr.arpa
        101.8.10.in-addr.arpa
        11.8.10.in-addr.arpa
        110.8.10.in-addr.arpa
        120.8.10.in-addr.arpa
        121.8.10.in-addr.arpa
        2.8.10.in-addr.arpa
        3.8.10.in-addr.arpa
        32.8.10.in-addr.arpa
        33.8.10.in-addr.arpa
        60.8.10.in-addr.arpa
        62.8.10.in-addr.arpa
        69.8.10.in-addr.arpa
        70.8.10.in-addr.arpa
        72.8.10.in-addr.arpa
        73.8.10.in-addr.arpa
        74.8.10.in-addr.arpa
        75.8.10.in-addr.arpa
        76.8.10.in-addr.arpa
        80.8.10.in-addr.arpa
        81.8.10.in-addr.arpa
        82.8.10.in-addr.arpa
        83.8.10.in-addr.arpa
        84.8.10.in-addr.arpa
        85.8.10.in-addr.arpa

    This is a list of all reverse zones found in sysadmins/dnsconfig/zones/in-addr/.
