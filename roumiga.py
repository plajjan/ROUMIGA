#!/usr/bin/python

import os
import sys
sys.path.append('../ncclient')
sys.path.append('../py-junos-eznc/lib')

from jnpr.junos import Device
from getpass import getpass
from pprint import pprint

from roumiga.arp import ArpEntry, ArpTable
from roumiga.bgp import BgpTable, BgpPeer
from roumiga.node import Node
import roumiga

class NodeCapture:
    def __init__(self, snapshot, hostname, username, password):
        self.snapshot = snapshot
        self.hostname = hostname
        self.username = username
        self.password = password

        self.arp = []
        self.bgp = []

    def snap(self):
        """ Snap a snapshot!
        """
        raise NotImplemented()


class NodeCaptureJnpr(NodeCapture):

    def snap(self):
        dev = Device(host=self.hostname, user=user, password=password)
        dev.open()

        # get basic Node facts
        node = Node(self.snapshot, self.hostname)
        node.fqdn = dev.facts['fqdn']
        node.hostname = dev.facts['hostname']
        node.model = dev.facts['model']
        node.personality = dev.facts['personality']
        node.serialnumber = dev.facts['serialnumber']
        node.switch_style = dev.facts['switch_style']
        node.version = dev.facts['version']
        node.uptime = dev.facts['RE0']['up_time']
        node.reboot_reason = dev.facts['RE0']['last_reboot_reason']
        roumiga.session.add(node)
        roumiga.session.flush()

        # do the ARP dance
        import jnpr.junos.op.arp
        raw_arp = jnpr.junos.op.arp.ArpTable(dev)
        for a in raw_arp.get():
            arp_entry = ArpEntry.from_dict(snapshot, node, a)
            roumiga.session.add(arp_entry)
            self.arp.append(arp_entry)

        # do the BGP dance
        import jnpr.junos.op.bgp
        raw_bgp = jnpr.junos.op.bgp.BgpPeerTable(dev)
        for b in raw_bgp.get():
            bgp_peer = BgpPeer.from_dict(snapshot, node, b)
            roumiga.session.add(bgp_peer)
            self.bgp.append(bgp_peer)

        dev.close()



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
            "Assist in router migrations, upgrades, reboots and similar")
    parser.add_argument('--create-tables', action="store_true", help="Create tables")
    parser.add_argument('--user', help="Username")
    parser.add_argument('--list-snapshots', action="store_true", help="List snapshots")
    parser.add_argument('--take-snapshot', action="store_true",
        help="Take snapshot of given nodes")
    parser.add_argument('--junos-node', nargs='+', help="List of JUNOS devices")
    parser.add_argument('--summary', help="Show summary of snapshot")
    parser.add_argument('--compare', type=int, nargs=2, help="Compare two snapshots")
    args = parser.parse_args()

    # get user from environment or as argument
    user = os.getenv('USER')
    if args.user:
        user = args.user
    # get password from environment or interactively
    if os.getenv('ROUMIGAPASS'):
        password = os.getenv('ROUMIGAPASS')
    else:
        password = getpass()

    if args.create_tables:
        roumiga.DeclarativeBase.metadata.create_all(roumiga.engine, checkfirst=True)

    if args.take_snapshot:
        snapshot = roumiga.Snapshot()
        roumiga.session.add(snapshot)
        roumiga.session.flush()
        for node in args.junos_node:
            ncj = NodeCaptureJnpr(snapshot, node, user, password)
            ncj.snap()
        roumiga.session.commit()

    if args.summary:
        s = roumiga.Snapshot.from_id(args.summary)
        print "Snapshot ID: %-5d  taken at: %s" % (s.id, str(s.time)[:19])
        for node in Node.from_snapshot(s):
            print "  ", node.hostname

    if args.list_snapshots:
        for s in roumiga.Snapshot.list():
            print "Snapshot ID: %-5d  taken at: %s" % (s.id, str(s.time)[:19])
            for node in Node.from_snapshot(s):
                print "  Node: ", node.hostname

    if args.compare:
        s1 = roumiga.Snapshot.from_id(args.compare[0])
        s2 = roumiga.Snapshot.from_id(args.compare[1])
        nodes1 = {}
        for n in Node.from_snapshot(s1):
            nodes1[n.fqdn] = n

        nodes2 = {}
        for n in Node.from_snapshot(s2):
            nodes2[n.fqdn] = n

        print "%-39s %-39s" % ("Snapshot %d" % (s1.id), "Snapshot %d" % (s2.id))
        for fqdn in set(nodes1).union(set(nodes2)):
            nt1, nt2 = ('N/A', 'N/A')
            if fqdn in set(nodes1):
                nt1 = nodes1[fqdn].hostname
            if fqdn in set(nodes2):
                nt2 = nodes2[fqdn].hostname
            print "%-39s %-39s" % (nt1, nt2)

        for fqdn in set(nodes1).intersection(nodes2):
            n1 = nodes1[fqdn]
            n2 = nodes2[fqdn]
            print "  Comparing %s" % (fqdn)
            at1 = ArpTable.from_snapshot(s1, n1)
            at2 = ArpTable.from_snapshot(s2, n2)
            print "    Following entries missing in Snapshot %d:" % s1.id
            for ae in at2.difference(at1):
                print "      ", ae
            print "    Following entries missing in Snapshot %d:" % s2.id
            for ae in at1.difference(at2):
                print "      ", ae
            diffd = at1.diff_data(at2)
            print "    Equality ratio: %.2f%% (total: %d  diff: %d)" % (diffd['ratio'], diffd['total'], diffd['total_diff'])



