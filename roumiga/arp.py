"""
"""

from roumiga import DeclarativeBase, DBSession

from sqlalchemy import  Column, ForeignKey
from sqlalchemy.types import Date, Float, Integer, String, Text


class ArpTable:
    def __init__(self):
        self.entries = {}

    def append(self, new_entry):
        self.entries[new_entry.mac_address] = new_entry


    @classmethod
    def from_eznc(self, entries):
        table = ArpTable()

        for entry in entries:
            ae = ArpEntry.from_dict(entry)
            #table.entries[

        return table

class ArpEntry(DeclarativeBase):
    """ Represents a single ARP entry
    """
    __tablename__ = "arp"

    id = Column(Integer, primary_key = True)
    node = Column(Text)
    mac_address = Column(Text)
    ip_address = Column(Text)
    interface = Column(Text)


    def __init__(self, node, mac_address, ip_address, interface):
        self.node = node
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.interface = interface


    def __str__(self):
        return "I'm an ArpEntry: %s  %s  %s" % (self.mac_address, self.ip_address, self.interface)

    @classmethod
    def from_dict(self, node, data):
        a = ArpEntry(node, data['mac_address'], data['ip_address'],
                data['interface'])

        return a


    @classmethod
    def get_from_node(cls, input_node):
        return DBSession.query(ArpEntry).filter(ArpEntry.node==input_node).all()


if __name__ == '__main__':
    print "hejsan"
