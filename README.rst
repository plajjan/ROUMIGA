ROUMIGA - ROUter MIgrations Assistant
=====================================
When upgrading a router it is often useful comparing its state before the
upgrade to a state after the upgrade. ROUMIGA helps you with this.

The idea is to snap a state over the ARP table, BGP peers, LDP peers, ISIS
neighbors, LLDP neighbors and so forth at different points in time and then
aiding you in comparing these.

One could easily do a "fuzzy" comparison where it's okay to have +-10% of
received prefixes from a BGP neighbor and the states still being considered
"equal" while for things like ISIS neighbors an exact match is required.

A snapshot in ROUMIGA can contain multiple devices. By taking a snapshot of a
portion of your network, one can assure that no crucial links are down before
performing an upgrade.

Usage
-----
Take a snapshot;

    roumiga --take-snapshot --junos-device 1.3.3.7

Restart your box or do something funny to it and take another snapshot. List
snapshots;

    roumiga --list-snapshots

Now compare two snapshots, like snapshot 1 and snapshot 2;

    roumiga --compare 1 2
