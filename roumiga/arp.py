"""
"""

from roumiga import DeclarativeBase, DBSession

from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.types import Date, Float, Integer, String, Text

class ArpTable:
    def __init__(self):
        self.entries = []
        self.by_mac = {}
        self.by_ip = {}

    @classmethod
    def from_snapshot(cls, snapshot, node):
        at = ArpTable()
        for ae in ArpEntry.from_snapshot(snapshot, node):
            at.append(ae)

        return at

    def append(self, new_entry):
        self.entries.append(new_entry)
        self.by_mac[new_entry.mac_address] = new_entry
        self.by_ip[new_entry.ip_address] = new_entry

    def diff_data(self, other):
        """ Return various data about difference between us and other seen from
            our perspective
        """
        total = len(set(self.entries).union(set(other.entries)))
        total_diff = len(self.difference(other)) + len(other.difference(self))
        ratio = (float(total-total_diff)/total)*100
        return {
                'total': total,
                'total_diff': total_diff,
                'ratio': ratio
                }


    def difference(self, other):
        """ Return entries in self but not in other
        """
        return set(self.entries).difference(set(other.entries))

    def difference_both(self, other):
        """ Return our and other sidesis missing missing entries from this and other
        """
        return self.difference(other), other.difference(self)




class ArpEntry(DeclarativeBase):
    """ Represents a single ARP entry
    """
    __tablename__ = "arp"

    id = Column(Integer, primary_key = True)
    snapshot = Column(Integer)
    node = Column(Integer)
    mac_address = Column(Text)
    ip_address = Column(Text)
    interface = Column(Text)


    def __init__(self, snapshot, node, mac_address, ip_address, interface):
        self.snapshot = snapshot.id
        self.node = node.id
        self.mac_address = mac_address
        self.ip_address = ip_address
        self.interface = interface


    def __eq__(self, other):
        if (self.mac_address == other.mac_address and
            self.ip_address == other.ip_address and
            self.interface == other.interface):
                return True
        return False


    def __hash__(self):
        return hash("%s%s%s" % (self.mac_address, self.ip_address, self.interface))


    def __str__(self):
        return "MAC: %s  IP:%s  Intf: %s" % (self.mac_address, self.ip_address, self.interface)


    @classmethod
    def from_dict(self, snapshot, node, data):
        a = ArpEntry(snapshot, node, data['mac_address'], data['ip_address'],
                data['interface_name'])

        return a


    @classmethod
    def from_snapshot(cls, snapshot, node):
        return DBSession.query(ArpEntry).filter(and_(ArpEntry.snapshot==snapshot.id, ArpEntry.node==node.id)).all()




if __name__ == '__main__':
    print "hejsan"
