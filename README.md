# Python Ping Program

This is a simple Python implementation of the `ping` command. It demonstrates the basic principles of ICMP packet creation, sending, and receiving to measure round-trip time (RTT) between a source and a destination. 

The program is designed to work similarly to the built-in `ping` command on most operating systems, but it allows for customization of parameters like TTL (time-to-live) and packet count.

## Features

- **Raw socket creation** to send and receive ICMP Echo requests and replies.
- **Customizable TTL** and number of ping requests to send.
- **Graceful exit** on receiving an interrupt signal (Ctrl+C).
- **Round-trip time calculation** for successful pings.
- **Basic error handling** for network failures.

## Usage

To use this program, you will need Python and administrative privileges (as it requires raw socket creation). 

### Requirements

- Python 3.x
- `dpkt` library (`pip install dpkt`)

### Running the Program

```bash
sudo python ping.py --dest <destination_ip> [--count <number_of_pings>] [--ttl <ttl_value>]
```

### Important Note

This program is a basic implementation of the `ping` command and should be used for educational purposes only. It is designed to demonstrate how ICMP packets work and is not intended for production use.
