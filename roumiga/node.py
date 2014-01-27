"""
"""

from roumiga import DeclarativeBase, DBSession

from sqlalchemy import  Column, ForeignKey
from sqlalchemy.types import Date, Float, Integer, String, Text, Interval

class Node(DeclarativeBase):
    """ Represents a single Node
    """
    __tablename__ = "node"

    id = Column(Integer, primary_key = True)
    snapshot = Column(Integer)
    fqdn = Column(Text)
    hostname = Column(Text)
    model = Column(Text)
    personality = Column(Text)
    serialnumber = Column(Text)
    switch_style = Column(Text)
    version = Column(Text)
    uptime = Interval(Text)


    def __init__(self, snapshot, hostname):
        self.snapshot = snapshot.id
        self.hostname = hostname


    def __str__(self):
        return "I'm an ArpEntry: %s  %s  %s" % (self.mac_address, self.ip_address, self.interface)

    @classmethod
    def from_dict(self, data):
        a = ArpEntry()
        a.mac_address = data['mac_address']
        a.ip_address = data['ip_address']
        a.hostname = data['hostname']
        a.interface = data['interface']

        return a


    @classmethod
    def from_node(cls, input_node):
        return DBSession.query(ArpEntry).filter(ArpEntry.node==input_node).all()


    @classmethod
    def from_snapshot(cls, snapshot):
        return DBSession.query(Node).filter(Node.snapshot==snapshot.id).all()


if __name__ == '__main__':
    import argparse
    print "hejsan"
