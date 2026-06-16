import socket
import sys

def test_udp_handshake(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    try:
        sock.connect((host, port))
        sock.send(b'\x00')  # SYN-like packet
        data, addr = sock.recvfrom(1024)
        print(f"✅ UDP handshake successful to {host}:{port}")
    except socket.timeout:
        print(f"❌ UDP handshake TIMEOUT to {host}:{port} (Oracle is dropping it)")
    except Exception as e:
        print(f"❌ UDP handshake FAILED: {e}")
    finally:
        sock.close()



test_udp_handshake("media.discordapp.net", 50000)
test_udp_handshake("c-sea08-cd431db3.discord.media", 50000)
