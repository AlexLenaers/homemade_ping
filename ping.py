import argparse
import socket
import struct
import time
import dpkt
import signal

TTL_DEFAULT = 128
pinging = True


def make_icmp_socket(ttl=64, timeout=1):
    """Creates a raw socket for ICMP protocol with specified TTL and timeout values."""
    try:
        icmp_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, struct.pack('I', ttl))
        icmp_socket.settimeout(timeout)
        return icmp_socket
    except PermissionError:
        print("You need administrative privileges to run this program.")
        quit()
    except socket.error as e:
        print(f"Socket error: {e}")
        quit()


def send_icmp_echo(socket_obj, payload, id, seq, destination):
    """Crafts and sends an ICMP Echo packet."""
    echo = dpkt.icmp.ICMP.Echo(id=id, seq=seq, data=bytes(payload, 'utf-8'))
    icmp = dpkt.icmp.ICMP(type=dpkt.icmp.ICMP_ECHO, data=echo)
    packet = bytes(icmp)

    try:
        socket_obj.sendto(packet, (destination, 0))
    except socket.gaierror:
        print("Destination not found: exiting...")
        quit()


def recv_icmp_response(icmp_socket):
    """Receives an ICMP response packet."""
    packet, addr = icmp_socket.recvfrom(1024)
    return packet


def parse_icmp_response(recv_packet):
    """Parses the header of the received ICMP packet."""
    header = recv_packet[20:28]
    type, code, checksum, id, seq = struct.unpack("bbHHh", header)
    return type, code, checksum, id, seq


def signal_handler(sig, frame):
    """Handles interrupt signal (Ctrl+C) to exit gracefully."""
    global pinging
    pinging = False


def main():
    global pinging

    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simple implementation of the ping program.')
    parser.add_argument('-d', '--dest', metavar='', required=True, help='Destination IP address')
    parser.add_argument('-c', '--count', metavar='', type=int, required=False, help='Number of packets to send',
                        default=-1)
    parser.add_argument('-m', '--ttl', metavar='', type=int, required=False, help='Time to live (TTL) value',
                        default=TTL_DEFAULT)
    args = parser.parse_args()

    # TTL validation
    if args.ttl < 1 or args.ttl > 255:
        print("TTL must be between 1 and 255")
        quit()

    total_rtt = 0  # Total round-trip time
    successful_pings = 0  # Count of successful pings
    seq = 0  # Sequence number for ICMP requests

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    # Use a context manager to ensure socket is closed properly
    with make_icmp_socket(args.ttl, 1) as icmp_socket:
        while pinging and (args.count == -1 or seq < args.count):
            # Send ICMP echo packet
            send_icmp_echo(icmp_socket, "ping", seq, seq, args.dest)
            send_time = time.time()

            try:
                # Receive ICMP response
                recv_packet = recv_icmp_response(icmp_socket)
                na, na, na, packet_id, packet_seq = parse_icmp_response(recv_packet)
                receive_time = time.time()
                rtt = (receive_time - send_time) * 1000  # in milliseconds
                total_rtt += rtt
                successful_pings += 1

                print(f"destination = {args.dest}; icmp_seq = {int(packet_seq / 256)}; "
                      f"icmp_id = {int(packet_id / 256)}; ttl = {args.ttl}; rtt = {rtt:.1f} ms")
            except socket.timeout:
                print(f"destination = {args.dest}; icmp_seq = {seq}; icmp_id = {seq}; "
                      f"ttl = {args.ttl}; Request timed out")
            seq += 1

    # Calculate and print statistics after exiting loop
    avg_rtt = total_rtt / successful_pings if successful_pings > 0 else 0
    print(f"\nAverage rtt: {avg_rtt:.1f} ms; {successful_pings}/{seq} ({100*successful_pings/seq:.2f}%) successful pings.")


if __name__ == '__main__':
    main()
