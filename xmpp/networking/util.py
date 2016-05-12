# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# (C) Copyright 2016 Gabriel Falcao <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import socket
import select
from collections import namedtuple

IP_REGEX = re.compile(r'^(\d{1,3}[.]){3}\d{1,3}$')

SocketStatePair = namedtuple('SocketStatePair', ['read', 'write'])


def create_tcp_socket(keep_alive_seconds=3, max_fails=5):
    result = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    set_keepalive(result, interval_sec=keep_alive_seconds, max_fails=max_fails)
    return result


def address_is_ip(address):
    return IP_REGEX.search(address) is not None


def set_keepalive(*args, **kw):
    if os.uname()[0].strip().lower() == 'darwin':
        set_keepalive_osx(*args, **kw)
    else:
        set_keepalive_linux(*args, **kw)


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


def set_keepalive_osx(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    sends a keepalive ping once every 3 seconds (interval_sec)
    """
    # scraped from /usr/include, not exported by python's socket module
    TCP_KEEPALIVE = 0x10
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True)
    sock.setsockopt(socket.IPPROTO_TCP, TCP_KEEPALIVE, interval_sec)


def socket_ready(socket, timeout, to_read=True, to_write=True):
    for_reads = to_read and [socket] or []
    for_writes = to_write and [socket] or []

    sockets = select.select(for_reads, for_writes, [], float(timeout) / 1000)
    reads, writes, exceptions = sockets
    read_socket = None
    write_socket = None

    if reads:
        read_socket = reads[0]
    if writes:
        write_socket = writes[0]

    return SocketStatePair(read_socket, write_socket)
