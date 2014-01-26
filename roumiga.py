#!/usr/bin/python

import os
import sys
sys.path.append('../ncclient')
sys.path.append('../py-junos-eznc/lib')

from jnpr.junos import Device
from getpass import getpass
from pprint import pprint

from roumiga.arp import ArpTable, ArpEntry
import roumiga

class NodeCapture:
    def __init__(self, snapshot, hostname, username, password):
        self.snapshot = snapshot
        self.hostname = hostname
        self.username = username
        self.password = password

        self.arp = []

    def snap(self):
        """ Snap a snapshot!
        """
        raise NotImplemented()


class NodeCaptureJnpr(NodeCapture):

    def snap(self):
        dev = Device(host=node, user=user, password=password)
        dev.open()
        import jnpr.junos.op.arp
        raw_arp = jnpr.junos.op.arp.ArpTable(dev)
        for a in raw_arp.get():
            arp_entry = ArpEntry.from_dict(node, a)
            roumiga.session.add(arp_entry)
            self.arp.append(arp_entry)

        dev.close()



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=
            "Assist in router migrations, upgrades, reboots and similar")
    parser.add_argument('--user', help="Username")
    parser.add_argument('--list-snapshots', action="store_true", help="List snapshots")
    parser.add_argument('--take-snapshot', action="store_true",
        help="Take snapshot of given nodes")
    parser.add_argument('--junos-node', nargs='+', help="List of JUNOS devices")
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

    if args.list_snapshots:
        for s in roumiga.Snapshot.list():
            print s.id

    if args.take_snapshot:
        snapshot = roumiga.Snapshot()
        for node in args.junos_node:
            ncj = NodeCaptureJnpr(snapshot, node, user, password)
            ncj.snap()
        roumiga.DeclarativeBase.metadata.create_all(roumiga.engine, checkfirst=True)
        roumiga.session.commit()

