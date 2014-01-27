"""
"""

from roumiga import DeclarativeBase, DBSession

from sqlalchemy import Column, ForeignKey, and_
from sqlalchemy.types import Date, Float, Integer, String, Text

class BgpTable:
    def __init__(self):
        self.entries = []
        self.by_ip = {}

    @classmethod
    def from_snapshot(cls, snapshot, node):
        bgpt = BgpTable()
        for bp in BgpPeer.from_snapshot(snapshot, node):
            bgpt.append(bp)

        return bgpt

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




class BgpPeer(DeclarativeBase):
    """ Represents a single BGP peer
    """
    __tablename__ = "bgp"

    id = Column(Integer, primary_key = True)
    snapshot = Column(Integer)
    node = Column(Integer)
    peer_address = Column(Text)


    def __init__(self, snapshot, node, peer_address):
        self.snapshot = snapshot.id
        self.node = node.id
        self.peer_address = peer_address


    def __hash__(self):
        return hash("%s" % (self.peer_address))


    def __str__(self):
        return "BGP peer: %s" % (self.peer_address)


    @classmethod
    def from_dict(self, snapshot, node, data):
        a = BgpPeer(snapshot, node, data['peer_address'])

        return a


    @classmethod
    def from_snapshot(cls, snapshot, node):
        return DBSession.query(BgpTable).filter(and_(BgpTable.snapshot==snapshot.id, BgpTable.node==node.id)).all()




if __name__ == '__main__':
    print "hejsan"
