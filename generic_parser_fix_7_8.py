#!/usr/bin/env python
"""
Use DPKT to read in a pcap file and create one directional sessions of packets sizes (ip total length) and ts.
"""
import dpkt
import os
import socket
import argparse
import csv
import time

FLAGS = None
# INPUT = "../dataset/iscxNTVPN2016/CompletePCAPs"#"../dataset/CICNTTor2017/Pcaps/tor" #"../dataset/iscxNTVPN2016/CompletePCAPs"#"./test_pacaps"#"../dataset/iscxNTVPN2016/CompletePCAPs" # ""
INPUT = './test_pcaps/my_chat'
FILTER_LIST = None # [(["audio", "voip"], True), (["vpn", "tor"], False)]

PROTO_DICT = {dpkt.tcp.TCP: "TCP", dpkt.udp.UDP: "UDP"}


def inet_to_str(inet):
    """Convert inet object to a string
        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    # First try ipv4 and then ipv6
    try:
        return socket.inet_ntop(socket.AF_INET6, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET, inet)


def get_transport_layer(ip):
    """Resolve the TCP/UDP layer for a dpkt IP/IP6 packet, walking through
    any IPv6 extension headers (hop-by-hop options, routing, fragment, etc.)
    that may sit between the IP6 header and the real transport layer.

    Args:
        ip: dpkt.ip.IP or dpkt.ip6.IP6 instance
    Returns:
        dpkt.tcp.TCP or dpkt.udp.UDP instance, or None if it couldn't be resolved
        (e.g. encrypted ESP payload, or an unsupported/truncated extension chain).
    """
    data = ip.data

    # Extension header objects (and IP/IP6 itself) expose the remaining
    # payload via `.data`, so keep drilling down until we hit TCP/UDP,
    # raw bytes, or something with no further `.data` to follow.
    seen = set()
    while not isinstance(data, (dpkt.tcp.TCP, dpkt.udp.UDP)):
        if isinstance(data, (bytes, bytearray, str)) or not hasattr(data, "data"):
            break
        if id(data) in seen:  # guard against any accidental cycles
            break
        seen.add(id(data))
        data = data.data

    if isinstance(data, (dpkt.tcp.TCP, dpkt.udp.UDP)):
        return data

    # Fallback: dpkt left the payload as raw, un-dissected bytes (this can
    # happen when it doesn't recognize part of the extension-header chain).
    # `ip.nxt` (IPv6) / `ip.p` (IPv4) reflects the final upper-layer protocol
    # number after extension headers are skipped, so use it to manually
    # parse the remaining bytes as TCP/UDP.
    proto_num = getattr(ip, "nxt", getattr(ip, "p", None))
    raw = bytes(data) if isinstance(data, (bytes, bytearray)) else None
    if raw:
        try:
            if proto_num == dpkt.ip.IP_PROTO_TCP:
                return dpkt.tcp.TCP(raw)
            elif proto_num == dpkt.ip.IP_PROTO_UDP:
                return dpkt.udp.UDP(raw)
        except (dpkt.UnpackError, dpkt.NeedData):
            return None

    return None


def is_fragment(ip):
    """Return True if this is an IPv4 fragment (MF flag set or nonzero
    offset) or an IPv6 packet whose extension-header chain contains a
    Fragment Header.

    Args:
        ip: dpkt.ip.IP or dpkt.ip6.IP6 instance
    Returns:
        bool
    """
    if isinstance(ip, dpkt.ip.IP):
        # Newer dpkt versions split the combined `.off` field into separate
        # `.mf` (more-fragments flag) and `.offset` (fragment offset)
        # attributes and deprecated `.off`. Prefer those when present to
        # avoid the deprecation warning; fall back to `.off` on older dpkt.
        if hasattr(ip, "mf") and hasattr(ip, "offset"):
            return bool(ip.mf) or ip.offset != 0
        return bool(ip.off & dpkt.ip.IP_MF) or (ip.off & dpkt.ip.IP_OFFMASK) != 0

    if isinstance(ip, dpkt.ip6.IP6):
        frag_hdr_cls = getattr(dpkt.ip6, "IP6FragmentHeader", None)
        if frag_hdr_cls is None:
            return False
        data = ip.data
        seen = set()
        while hasattr(data, "data") and not isinstance(data, (dpkt.tcp.TCP, dpkt.udp.UDP)):
            if isinstance(data, frag_hdr_cls):
                return True
            if id(data) in seen:
                break
            seen.add(id(data))
            data = data.data
        return False

    return False


def get_pcaps_list(dir_path, filter_list=None):
    def filter_list_func(fn):
        if filter_list is not None:
            for filter_str_list, type in filter_list:
                result = any([filter_str in fn.lower() for filter_str in filter_str_list])
                if result is not type:
                    return False
        return True
    return [(os.path.join(dir_path, fn), fn) for fn in next(os.walk(dir_path))[2] if (".pcap" in os.path.splitext(fn)[-1] and filter_list_func(fn))]


def parse_pcap(pcap, pcap_path, file_name):
    """Print out information about each packet in a pcap
       Args:
           pcap: dpkt pcap reader object (dpkt.pcap.Reader)
    """
    counter = 0
    frag_counter = 0
    pcap_dict = {}

    # For each packet in the pcap process the contents
    for ts, packet in pcap:

        # Unpack the Ethernet frame
        try:
            eth = dpkt.ethernet.Ethernet(packet)
        except dpkt.dpkt.NeedData:
            print("dpkt.dpkt.NeedData")

        # Make sure the Ethernet data contains an IP packet
        if isinstance(eth.data, dpkt.ip.IP):
            ip = eth.data
        elif isinstance(eth.data, dpkt.ip6.IP6):  # ADD THIS
            ip = eth.data
        elif isinstance(eth.data, str):
            try:
                ip = dpkt.ip.IP(packet)
            except dpkt.UnpackError:
                continue
        else:
            continue

        # Now unpack the data within the Ethernet frame (the IP packet)
        # Pulling out src_ip, dst_ip, protocol (tcp/udp), dst/src port, length

        if is_fragment(ip):
            frag_counter += 1

        # Resolve the transport layer. For IPv6 this walks through any
        # extension headers instead of assuming ip.data is already TCP/UDP.
        transport = get_transport_layer(ip)

        # Print out the info
        if transport is not None and type(transport) in PROTO_DICT:
            session_tuple_key = (inet_to_str(ip.src), transport.sport, inet_to_str(ip.dst), transport.dport, PROTO_DICT[type(transport)])
            pcap_dict.setdefault(session_tuple_key, (ts, [], []))
            d = pcap_dict[session_tuple_key]
            size = len(ip) #ip.len
            d[1].append(round(ts - d[0], 6)), d[2].append(size)
            counter += 1

    print("Total Number of Parsed Packets in " + pcap_path + ": " + str(counter))
    print("Total Number of Fragments in " + pcap_path + ": " + str(frag_counter))

    csv_file_path = os.path.splitext(pcap_path)[0] + ".csv"
    with open(csv_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file)
        for key, value in pcap_dict.items():
            writer.writerow([file_name.split(".")[0]] + list(key) + [value[0], len(value[1])] + value[1] + [None] + value[2])

    for k,v in pcap_dict.items():
        if len(v[1]) > 2000:
            print(k, v[0], len(v[1]))


def generic_parser(file_list):
    """Open up a pcap file and create a output file containing all one-directional parsed sessions"""
    for pcap_path, file_name in file_list:
        try:
            with open(pcap_path, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)
                parse_pcap(pcap, pcap_path, file_name)

        except ValueError:
            new_pcap_file = os.path.splitext(pcap_path)[0] + "_new.pcap"
            os.system("editcap -F libpcap -T ether " + pcap_path + " " + new_pcap_file)

            with open(new_pcap_file, 'rb') as f:
                pcap = dpkt.pcap.Reader(f)
                parse_pcap(pcap, pcap_path, file_name)

            os.remove(new_pcap_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default=INPUT, help='Path to pcap')

    FLAGS = parser.parse_args()
    file_list = get_pcaps_list(FLAGS.input, FILTER_LIST)
    start_time = time.time()
    generic_parser(file_list)
    total_time = time.time() - start_time
    print("--- %s seconds ---" % total_time)