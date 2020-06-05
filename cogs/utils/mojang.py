import json
import random
import struct

import datetime
import dns.resolver
import socket
from six import string_types


class Connection:
    def __init__(self):
        self.sent = bytearray()
        self.received = bytearray()

    def read(self, length):
        result = self.received[:length]
        self.received = self.received[length:]
        return result

    def write(self, data):
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        if isinstance(data, str):
            data = bytearray(data)
        self.sent.extend(data)

    def receive(self, data):
        if not isinstance(data, bytearray):
            data = bytearray(data)
        self.received.extend(data)

    def remaining(self):
        return len(self.received)

    def flush(self):
        result = self.sent
        self.sent = ""
        return result

    def _unpack(self, format, data):
        return struct.unpack(">" + format, bytes(data))[0]

    def _pack(self, format, data):
        return struct.pack(">" + format, data)

    def read_varint(self):
        result = 0
        for i in range(5):
            part = ord(self.read(1))
            result |= (part & 0x7F) << 7 * i
            if not part & 0x80:
                return result
        raise IOError("Server sent a varint that was too big!")

    def write_varint(self, value):
        remaining = value
        for i in range(5):
            if remaining & ~0x7F == 0:
                self.write(struct.pack("!B", remaining))
                return
            self.write(struct.pack("!B", remaining & 0x7F | 0x80))
            remaining >>= 7
        raise ValueError("The value %d is too big to send in a varint" % value)

    def read_utf(self):
        length = self.read_varint()
        return self.read(length).decode('utf8')

    def write_utf(self, value):
        self.write_varint(len(value))
        self.write(bytearray(value, 'utf8'))

    def read_ascii(self):
        result = bytearray()
        while len(result) == 0 or result[-1] != 0:
            result.extend(self.read(1))
        return result[:-1].decode("ISO-8859-1")

    def write_ascii(self, value):
        self.write(bytearray(value, 'ISO-8859-1'))
        self.write(bytearray.fromhex("00"))

    def read_short(self):
        return self._unpack("h", self.read(2))

    def write_short(self, value):
        self.write(self._pack("h", value))

    def read_ushort(self):
        return self._unpack("H", self.read(2))

    def write_ushort(self, value):
        self.write(self._pack("H", value))

    def read_int(self):
        return self._unpack("i", self.read(4))

    def write_int(self, value):
        self.write(self._pack("i", value))

    def read_uint(self):
        return self._unpack("I", self.read(4))

    def write_uint(self, value):
        self.write(self._pack("I", value))

    def read_long(self):
        return self._unpack("q", self.read(8))

    def write_long(self, value):
        self.write(self._pack("q", value))

    def read_ulong(self):
        return self._unpack("Q", self.read(8))

    def write_ulong(self, value):
        self.write(self._pack("Q", value))

    def read_buffer(self):
        length = self.read_varint()
        result = Connection()
        result.receive(self.read(length))
        return result

    def write_buffer(self, buffer):
        data = buffer.flush()
        self.write_varint(len(data))
        self.write(data)

class TCPSocketConnection(Connection):
    def __init__(self, addr, timeout=3):
        Connection.__init__(self)
        self.socket = socket.create_connection(addr, timeout=timeout)

    def flush(self):
        raise TypeError("TCPSocketConnection does not support flush()")

    def receive(self, data):
        raise TypeError("TCPSocketConnection does not support receive()")

    def remaining(self):
        raise TypeError("TCPSocketConnection does not support remaining()")

    def read(self, length):
        result = bytearray()
        while len(result) < length:
            new = self.socket.recv(length - len(result))
            if len(new) == 0:
                raise IOError("Server did not respond with any information!")
            result.extend(new)
        return result

    def write(self, data):
        self.socket.send(data)

    def __del__(self):
        try: self.socket.close()
        except: return

class UDPSocketConnection(Connection):
    def __init__(self, addr, timeout=3):
        Connection.__init__(self)
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)

    def flush(self):
        raise TypeError("UDPSocketConnection does not support flush()")

    def receive(self, data):
        raise TypeError("UDPSocketConnection does not support receive()")

    def remaining(self):
        return 65535

    def read(self, length):
        result = bytearray()
        while len(result) == 0:
            result.extend(self.socket.recvfrom(self.remaining())[0])
        return result

    def write(self, data):
        if isinstance(data, Connection):
            data = bytearray(data.flush())
        self.socket.sendto(data, self.addr)

    def __del__(self):
        try: self.socket.close()
        except AttributeError: pass

class ServerPinger:
    def __init__(self, connection, host="", port=0, version=47, ping_token=None):
        if ping_token is None:
            ping_token = random.randint(0, (1 << 63) - 1)
        self.version = version
        self.connection = connection
        self.host = host
        self.port = port
        self.ping_token = ping_token

    def handshake(self):
        packet = Connection()
        packet.write_varint(0)
        packet.write_varint(self.version)
        packet.write_utf(self.host)
        packet.write_ushort(self.port)
        packet.write_varint(1)  # Intention to query status

        self.connection.write_buffer(packet)

    def read_status(self):
        request = Connection()
        request.write_varint(0)  # Request status
        self.connection.write_buffer(request)

        response = self.connection.read_buffer()
        if response.read_varint() != 0:
            raise IOError("Received invalid status response packet.")
        try:
            raw = json.loads(response.read_utf())
        except ValueError:
            raise IOError("Received invalid JSON")
        try:
            return PingResponse(raw)
        except ValueError as e:
            raise IOError("Received invalid status response: %s" % e)

    def test_ping(self):
        request = Connection()
        request.write_varint(1)  # Test ping
        request.write_long(self.ping_token)
        sent = datetime.datetime.now()
        self.connection.write_buffer(request)

        response = self.connection.read_buffer()
        received = datetime.datetime.now()
        if response.read_varint() != 1:
            raise IOError("Received invalid ping response packet.")
        received_token = response.read_long()
        if received_token != self.ping_token:
            raise IOError("Received mangled ping response packet (expected token %d, received %d)" % (
                self.ping_token, received_token))

        delta = (received - sent)
        # We have no trivial way of getting a time delta :(
        return (delta.days * 24 * 60 * 60 + delta.seconds) * 1000 + delta.microseconds / 1000.0

class PingResponse:
    class Players:
        class Player:
            def __init__(self, raw):
                if type(raw) is not dict:
                    raise ValueError("Invalid player object (expected dict, found %s" % type(raw))

                if "name" not in raw:
                    raise ValueError("Invalid player object (no 'name' value)")
                if not isinstance(raw["name"], string_types):
                    raise ValueError("Invalid player object (expected 'name' to be str, was %s)" % type(raw["name"]))
                self.name = raw["name"]

                if "id" not in raw:
                    raise ValueError("Invalid player object (no 'id' value)")
                if not isinstance(raw["id"], string_types):
                    raise ValueError("Invalid player object (expected 'id' to be str, was %s)" % type(raw["id"]))
                self.id = raw["id"]

        def __init__(self, raw):
            if type(raw) is not dict:
                raise ValueError("Invalid players object (expected dict, found %s" % type(raw))

            if "online" not in raw:
                raise ValueError("Invalid players object (no 'online' value)")
            if type(raw["online"]) is not int:
                raise ValueError("Invalid players object (expected 'online' to be int, was %s)" % type(raw["online"]))
            self.online = raw["online"]

            if "max" not in raw:
                raise ValueError("Invalid players object (no 'max' value)")
            if type(raw["max"]) is not int:
                raise ValueError("Invalid players object (expected 'max' to be int, was %s)" % type(raw["max"]))
            self.max = raw["max"]

            if "sample" in raw:
                if type(raw["sample"]) is not list:
                    raise ValueError("Invalid players object (expected 'sample' to be list, was %s)" % type(raw["max"]))
                self.sample = [PingResponse.Players.Player(p) for p in raw["sample"]]
            else:
                self.sample = None

    class Version:
        def __init__(self, raw):
            if type(raw) is not dict:
                raise ValueError("Invalid version object (expected dict, found %s" % type(raw))

            if "name" not in raw:
                raise ValueError("Invalid version object (no 'name' value)")
            if not isinstance(raw["name"], string_types):
                raise ValueError("Invalid version object (expected 'name' to be str, was %s)" % type(raw["name"]))
            self.name = raw["name"]

            if "protocol" not in raw:
                raise ValueError("Invalid version object (no 'protocol' value)")
            if type(raw["protocol"]) is not int:
                raise ValueError("Invalid version object (expected 'protocol' to be int, was %s)" % type(raw["protocol"]))
            self.protocol = raw["protocol"]

    def __init__(self, raw):
        self.raw = raw

        if "players" not in raw:
            raise ValueError("Invalid status object (no 'players' value)")
        self.players = PingResponse.Players(raw["players"])

        if "version" not in raw:
            raise ValueError("Invalid status object (no 'version' value)")
        self.version = PingResponse.Version(raw["version"])

        if "description" not in raw:
            raise ValueError("Invalid status object (no 'description' value)")
        self.description = raw["description"]

        if "favicon" in raw:
            self.favicon = raw["favicon"]
        else:
            self.favicon = None

        self.latency = None

class ServerQuerier:
    MAGIC_PREFIX = bytearray.fromhex("FEFD")
    PACKET_TYPE_CHALLENGE = 9
    PACKET_TYPE_QUERY = 0

    def __init__(self, connection):
        self.connection = connection
        self.challenge = 0

    def _create_packet(self, id):
        packet = Connection()
        packet.write(self.MAGIC_PREFIX)
        packet.write(struct.pack("!B", id))
        packet.write_uint(0)
        packet.write_int(self.challenge)
        return packet

    def _read_packet(self):
        packet = Connection()
        packet.receive(self.connection.read(self.connection.remaining()))
        packet.read(1 + 4)
        return packet

    def handshake(self):
        self.connection.write(self._create_packet(self.PACKET_TYPE_CHALLENGE))

        packet = self._read_packet()
        self.challenge = int(packet.read_ascii())

    def read_query(self):
        request = self._create_packet(self.PACKET_TYPE_QUERY)
        request.write_uint(0)
        self.connection.write(request)

        response = self._read_packet()
        response.read(len("splitnum") + 1 + 1 + 1)
        data = {}
        players = []

        while True:
            key = response.read_ascii()
            if len(key) == 0:
                response.read(1)
                break
            value = response.read_ascii()
            data[key] = value

        response.read(len("player_") + 1 + 1)

        while True:
            name = response.read_ascii()
            if len(name) == 0:
                break
            players.append(name)

        return QueryResponse(data, players)

class QueryResponse:
    class Players:
        def __init__(self, online, max, names):
            self.online = int(online)
            self.max = int(max)
            self.names = names

    class Software:
        def __init__(self, version, plugins):
            self.version = version
            self.brand = "vanilla"
            self.plugins = []

            if plugins:
                parts = plugins.split(":", 1)
                self.brand = parts[0].strip()

                if len(parts) == 2:
                    self.plugins = [s.strip() for s in parts[1].split(";")]


    def __init__(self, raw, players):
        self.raw = raw
        self.motd = raw["hostname"]
        self.map = raw["map"]
        self.players = QueryResponse.Players(raw["numplayers"], raw["maxplayers"], players)
        self.software = QueryResponse.Software(raw["version"], raw["plugins"])

class MinecraftServer:
    def __init__(self, host, port=25565):
        self.host = host
        self.port = port

    @staticmethod
    def lookup(address):
        host = address
        port = None
        if ":" in address:
            parts = address.split(":")
            if len(parts) > 2:
                raise ValueError("Invalid address '%s'" % address)
            host = parts[0]
            port = int(parts[1])
        if port is None:
            port = 25565
            try:
                answers = dns.resolver.query("_minecraft._tcp." + host, "SRV")
                if len(answers):
                    answer = answers[0]
                    host = str(answer.target).rstrip(".")
                    port = int(answer.port)
            except Exception:
                pass

        return MinecraftServer(host, port)

    def ping(self, retries=3, **kwargs):
        connection = TCPSocketConnection((self.host, self.port))
        exception = None
        for attempt in range(retries):
            try:
                pinger = ServerPinger(connection, host=self.host, port=self.port, **kwargs)
                pinger.handshake()
                return pinger.test_ping()
            except Exception as e:
                exception = e
        else:
            raise exception

    def status(self, retries=3, **kwargs):
        connection = TCPSocketConnection((self.host, self.port))
        exception = None
        for attempt in range(retries):
            try:
                pinger = ServerPinger(connection, host=self.host, port=self.port, **kwargs)
                pinger.handshake()
                result = pinger.read_status()
                result.latency = pinger.test_ping()
                return result
            except Exception as e:
                exception = e
        else:
            raise exception

    def query(self, retries=3):
        exception = None
        host = self.host
        try:
            answers = dns.resolver.query(host, "A")
            if len(answers):
                answer = answers[0]
                host = str(answer).rstrip(".")
        except Exception as e:
            pass
        for attempt in range(retries):
            try:
                connection = UDPSocketConnection((host, self.port))
                querier = ServerQuerier(connection)
                querier.handshake()
                return querier.read_query()
            except Exception as e:
                exception = e
        else:
            raise exception

class Mojang:

    def __init__(self, session):
        self.Mojang_username = 'https://api.mojang.com/users/profiles/minecraft/{username}'
        self.Minecraft_username = 'https://api.mojang.com/user/profiles/{uuid}/names'
        self.session = session

    async def getUUID(self, user):
        response = {
            "code": None,
            "reason": None,
            "uuid": None,
            "name": None
        }
        request = await self.session.get(self.Mojang_username.format(username=user))
        response['code'] = str(request.status)
        response['reason'] = str(request.reason)
        if response['code'].startswith('2') and response['reason'] == 'OK':
            response['uuid'] = (await request.json())['id']
            response['name'] = (await request.json())['name']
        return response

    async def getUser(self, uuid):
        request = await self.session.get(self.Minecraft_username.format(uuid=uuid))
        if request.reason != 'OK': return False
        username = (await request.json())[-1]['name']
        return username
