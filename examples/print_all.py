#!/usr/bin/env python

import sys
from optparse import OptionParser
from datetime import *
from mrtparse import *

indt = 0

def prline(line):
    global indt
    print('    ' * indt + line)

def print_mrt(m):
    global indt
    indt = 0
    prline('---------------------------------------------------------------')
    prline('MRT Header')

    indt += 1
    prline('Timestamp: %d(%s)' % (m.ts, datetime.fromtimestamp(m.ts)))
    prline('Type: %d(%s)' % (m.type, val_dict(MSG_T, m.type)))
    prline('Subtype: %d(%s)' %
        (m.subtype, val_dict(MSG_ST, m.type, m.subtype)))
    prline('Length: %d' % m.len)

    if (   m.type == MSG_T['BGP4MP_ET']
        or m.type == MSG_T['ISIS_ET']
        or m.type == MSG_T['OSPFv3_ET']):
        prline('Microsecond Timestamp: %d' % m.micro_ts)

def print_td_v2(m):
    global indt
    indt = 0
    prline('%s' % TD_V2_ST[m.subtype])

    indt += 1
    if m.subtype == TD_V2_ST['PEER_INDEX_TABLE']:
        prline('Collector: %s' % m.peer.collector)
        prline('View Name Length: %d' % m.peer.view_len)
        prline('View Name: %s' % m.peer.view)
        prline('Peer Count: %d' % m.peer.count)

        for entry in m.peer.entry:
            prline('Peer Type: 0x%02x' % entry.type)
            prline('Peer BGP ID: %s' % entry.bgp_id)
            prline('Peer IP Address: %s' % entry.ip)
            prline('Peer AS: %s' % entry.asn)

    elif ( m.subtype == TD_V2_ST['RIB_IPV4_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV4_MULTICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_UNICAST']
        or m.subtype == TD_V2_ST['RIB_IPV6_MULTICAST']):
        prline('Sequence Number: %d' % m.rib.seq)
        prline('Prefix Length: %d' % m.rib.plen)
        prline('Prefix: %s' % m.rib.prefix)
        prline('Entry Count: %d' % m.rib.count)

        for entry in m.rib.entry:
            prline('Peer Index: %d' % entry.peer_index)
            prline('Originated Time: %d(%s)' %
                (entry.org_time, datetime.fromtimestamp(entry.org_time)))
            prline('Attribute Length: %d' % entry.attr_len)
            for attr in entry.attr:
                print_bgp_attr(attr)

def print_bgp4mp(m):
    global indt
    indt = 0
    prline('%s' % BGP4MP_ST[m.subtype])

    indt += 1
    prline('Peer AS Number: %s' % m.bgp.peer_as)
    prline('Local AS Number: %s' % m.bgp.local_as)
    prline('Interface Index: %d' % m.bgp.ifindex)
    prline('Address Family: %d(%s)' %
        (m.bgp.af, val_dict(AFI_T, m.bgp.af)))
    prline('Peer IP Address: %s' % m.bgp.peer_ip)
    prline('Local IP Address: %s' % m.bgp.local_ip)

    if (   m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE']
        or m.subtype == BGP4MP_ST['BGP4MP_STATE_CHANGE_AS4']):
        prline('Old State: %d(%s)' %
            (m.bgp.old_state, val_dict(BGP_FSM, m.bgp.old_state)))
        prline('New State: %d(%s)' %
            (m.bgp.new_state, val_dict(BGP_FSM, m.bgp.new_state)))

    elif ( m.subtype == BGP4MP_ST['BGP4MP_MESSAGE']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_LOCAL']
        or m.subtype == BGP4MP_ST['BGP4MP_MESSAGE_AS4_LOCAL']):
        print_bgp_msg(m)

def print_bgp_msg(m):
    global indt
    indt = 0
    prline('BGP Message')

    indt += 1
    prline('Marker: -- ignored --')
    prline('Length: %d' % m.bgp.msg.len)
    prline('Type: %d(%s)' %
        (m.bgp.msg.type, val_dict(BGP_MSG_T, m.bgp.msg.type)))

    if m.bgp.msg.type == BGP_MSG_T['OPEN']:
        prline('Version: %d' % (m.bgp.msg.ver))
        prline('My AS: %d' % (m.bgp.msg.my_as))
        prline('Hold Time: %d' % (m.bgp.msg.holdtime))
        prline('BGP Identifier: %s' % (m.bgp.msg.bgp_id))
        prline('Optional Parameter Length: %d' % (m.bgp.msg.opt_len))

        for opt in m.bgp.opt_params:
            print_bgp_opt_params(opt)

    elif m.bgp.msg.type == BGP_MSG_T['UPDATE']:
        prline('Withdrawn Routes Length: %d' % (m.bgp.msg.wd_len))
        for withdrawn in m.bgp.msg.withdrawn:
            prline('Withdrawn Route: %s/%d' %
                (withdrawn.prefix, withdrawn.plen))

        prline('Total Path Attribute Length: %d' % (m.bgp.msg.attr_len))
        for attr in m.bgp.msg.attr:
            print_bgp_attr(attr)

        for nlri in m.bgp.msg.nlri:
            prline('NLRI: %s/%d' % (nlri.prefix, nlri.plen))

    elif m.bgp.msg.type == BGP_MSG_T['NOTIFICATION']:
        prline('Error Code: %d(%s)' % 
            (m.bgp.msg.err_code, val_dict(BGP_ERR_C, m.bgp.msg.err_code)))
        prline('Error Subcode: %d(%s)' % 
            (m.bgp.msg.err_subcode,
            val_dict(BGP_ERR_SC, m.bgp.msg.err_code, m.bgp.msg.err_subcode)))

def print_bgp_opt_params(opt_params):
    global indt
    indt = 1
    prline('Parameter Type/Length: %d/%d' % (opt.type, opt.len))

    indt += 1
    prline('%s' % val_dict(BGP_OPT_PARAMS_T, opt.type))

    if opt.type != BGP_OPT_PARAMS_T['Capabilities']:
        return

    indt += 1
    prline('Capability Code: %d(%s)' %
        (opt.cap_type, val_dict(CAP_CODE_T, opt.cap_type)))
    prline('Capability Length: %d' % opt.cap_len)

    if opt.cap_type == CAP_CODE_T['Multiprotocol Extensions for BGP-4']:
        prline('AFI: %d(%s)' %
            (opt.multi_ext['afi'],
             val_dict(AFI_T, opt.multi_ext['afi'])))
        prline('Reserved: %d' % opt.multi_ext['reserved'])
        prline('SAFI: %d(%s)' %
            (opt.multi_ext['safi'],
             val_dict(SAFI_T, opt.multi_ext['safi'])))

    elif opt.cap_type == CAP_CODE_T['Outbound Route Filtering Capability']:
        prline('AFI: %d(%s)' %
            (opt.orf['afi'], val_dict(AFI_T, opt.orf['afi'])))
        prline('Reserved: %d' % opt.orf['rsvd'])
        prline('SAFI: %d(%s)' %
            (opt.orf['safi'], val_dict(SAFI_T, opt.orf['safi'])))
        prline('Number: %d' % opt.orf['number'])

        for entry in opt.orf['entry']:
            prline('Type: %d' % entry['type'])
            prline('Send Receive: %d' % entry['send_recv'])

    elif opt.cap_type == CAP_CODE_T['Support for 4-octet AS number capability']:
        prline('AS Number: %d' % opt.support_for_as['as_number'])

    elif opt.cap_type == CAP_CODE_T['Route Refresh Capability for BGP-4']:
        pass

    elif opt.cap_type == CAP_CODE_T['Graceful Restart Capability']:
        prline('Restart Timers: %d' % opt.graceful_restart['timer'])
        if opt.cap_len > 2:
            prline('AFI: %d(%s)' %
                (opt.graceful_restart['afi'],
                 val_dict(AFI_T, opt.graceful_restart['afi'])))
            prline('SAFI: %d(%s)' %
                (opt.graceful_restart['safi'],
                 val_dict(SAFI_T, opt.graceful_restart['safi'])))
            prline('Flag: %d' % opt.graceful_restart['flags_for_afi'])

    elif opt.cap_type == CAP_CODE_T['Multiple routes to a destination capability']:
        while opt.cap_len > 3:
            prline('Prefix: %d' % self.multi_routes_dest['prefix'])
            opt.cap_len -= 1

    elif opt.cap_type == CAP_CODE_T['Extended Next Hop Encoding']:
        while opt.cap_len > 5:
            prline('NLRI AFI: %d' % (self.self.ext_next_hop['nlri_afi'] ))
            prline('NLRI SAFI: %d' % (self.self.ext_next_hop['nlri_safi'] ))
            prline('Nexthop AFI: %d' % (self.self.ext_next_hop['nexthop_afi'] ))
            opt.cap_len -= 6

def print_bgp_attr(attr):
    global indt
    indt = 1
    prline('Path Attribute Flag/Type/Length: 0x%02x/%d/%d' %
        (attr.flag, attr.type, attr.len))

    indt += 1
    line = '%s: ' % val_dict(BGP_ATTR_T, attr.type)
    if attr.type == BGP_ATTR_T['ORIGIN']:
        line += '%d(%s)' % (attr.origin, val_dict(ORIGIN_T, attr.origin))
    elif attr.type == BGP_ATTR_T['NEXT_HOP']:
        line += '%s' % attr.next_hop
    elif attr.type == BGP_ATTR_T['MULTI_EXIT_DISC']:
        line += '%d' % attr.med
    elif attr.type == BGP_ATTR_T['LOCAL_PREF']:
        line += '%d' % attr.local_pref
    elif attr.type == BGP_ATTR_T['ATOMIC_AGGREGATE']:
        pass
    elif attr.type == BGP_ATTR_T['AGGREGATOR']:
        line += '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
    elif attr.type == BGP_ATTR_T['COMMUNITY']:
        line += '%s' % ' '.join(attr.comm)
    elif attr.type == BGP_ATTR_T['ORIGINATOR_ID']:
        line += '%s' % attr.org_id
    elif attr.type == BGP_ATTR_T['CLUSTER_LIST']:
        line += '%s' % attr.cl_list
    elif attr.type == BGP_ATTR_T['EXTENDED_COMMUNITIES']:
        ext_comm_list = []
        for ext_comm in attr.ext_comm:
            ext_comm_list.append('0x%016x' % ext_comm)
        line += '%s' % ' '.join(ext_comm_list)
    elif attr.type == BGP_ATTR_T['AS4_AGGREGATOR']:
        line += '%s %s' % (attr.aggr['asn'], attr.aggr['id'])
    prline(line)

    indt += 1
    if(    attr.type == BGP_ATTR_T['AS_PATH']
        or attr.type == BGP_ATTR_T['AS4_PATH']):
        for path_seg in attr.as_path:
            prline('Path Segment Type: %d(%s)' %
                (path_seg['type'],
                 val_dict(AS_PATH_SEG_T, path_seg['type'])))
            prline('Path Segment Length: %d' % path_seg['len'])
            prline('Path Segment Value: %s' % path_seg['val'])

    elif attr.type == BGP_ATTR_T['MP_REACH_NLRI']:
        prline('AFI: %d(%s), SAFI: %d(%s)' %
            (attr.mp_reach['afi'],
             val_dict(AFI_T, attr.mp_reach['afi']),
             attr.mp_reach['safi'],
             val_dict(SAFI_T, attr.mp_reach['safi'])))
        prline('Length: %d, Next-Hop: %s' %
            (attr.mp_reach['nlen'], attr.mp_reach['next_hop']))

        for nlri in attr.mp_reach['nlri']:
            prline('NLRI: %s/%d' % (nlri.prefix, nlri.plen))

    elif attr.type == BGP_ATTR_T['MP_UNREACH_NLRI']:
        prline('AFI: %d(%s), SAFI: %d(%s)' %
            (attr.mp_unreach['afi'],
             val_dict(AFI_T, attr.mp_unreach['afi']),
             attr.mp_unreach['safi'],
             val_dict(SAFI_T, attr.mp_unreach['safi'])))

        for withdrawn in attr.mp_unreach['withdrawn']:
            prline('Withdrawn Route: %s/%d' %
                (withdrawn.prefix, withdrawn.plen))

def main():
    if len(sys.argv) != 2:
        print('Usage: %s FILENAME' % sys.argv[0])
        exit(1)

    d = Reader(sys.argv[1])
    for m in d:
        print_mrt(m)
        if (   m.type == MSG_T['BGP4MP']
            or m.type == MSG_T['BGP4MP_ET']):
            print_bgp4mp(m)
        elif m.type == MSG_T['TABLE_DUMP_V2']:
            print_td_v2(m)

if __name__ == '__main__':
    main()
