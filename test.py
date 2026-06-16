import socket
import sys

def test_udp(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(b'', (host, port))
        print(f"✅ UDP connectivity to {host}:{port} is OPEN")
        sock.close()
    except socket.timeout:
        print(f"❌ UDP to {host}:{port} is BLOCKED/TIMEOUT")
    except Exception as e:
        print(f"❌ UDP to {host}:{port} ERROR: {e}")

# Test Discord's media servers (Seattle region from your logs)
test_udp("c-sea08-cd431db3.discord.media", 2053)
test_udp("media.discordapp.net", 2053)
