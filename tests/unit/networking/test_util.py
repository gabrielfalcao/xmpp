# <xmpp - stateless and concurrency-agnostic XMPP library for python>
#
# Copyright (C) <2016-2017> Gabriel Falcao <gabriel@nacaolivre.org>
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

from mock import patch, Mock, call
from xmpp.networking.util import create_tcp_socket
from xmpp.networking.util import address_is_ip
from xmpp.networking.util import socket_ready
from xmpp.networking.util import SocketStatePair
from xmpp.networking.util import set_keepalive
from xmpp.networking.util import set_keepalive_osx
from xmpp.networking.util import set_keepalive_linux


@patch('xmpp.networking.util.socket')
@patch('xmpp.networking.util.set_keepalive')
def test_create_tcp_socket(set_keepalive, socket):
    ('xmpp.networking.util.create_tcp_socket() should return a socket with keep_alive already set')

    result = create_tcp_socket(5, 10)

    result.should.equal(socket.socket.return_value)

    socket.socket.assert_called_once_with(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )
    set_keepalive.assert_called_once_with(
        result,
        interval_sec=5,
        max_fails=10
    )


@patch('xmpp.networking.util.os')
@patch('xmpp.networking.util.socket')
@patch('xmpp.networking.util.set_keepalive_osx')
def test_set_keepalive_on_mac(set_keepalive_osx, socket, os):
    ('xmpp.networking.util.set_keepalive() should call set_keepalive_osx on OSX')

    os.uname.return_value = ['Darwin']

    set_keepalive(foo='bar')

    set_keepalive_osx.assert_called_once_with(foo='bar')


@patch('xmpp.networking.util.os')
@patch('xmpp.networking.util.socket')
@patch('xmpp.networking.util.set_keepalive_linux')
def test_set_keepalive_on_linux(set_keepalive_linux, socket, os):
    ('xmpp.networking.util.set_keepalive() should call set_keepalive_linux on linux')

    os.uname.return_value = ['Linux']

    set_keepalive(foo='bar')

    set_keepalive_linux.assert_called_once_with(foo='bar')


@patch('xmpp.networking.util.socket')
def test_set_keepalive_osx(socket):
    ('xmpp.networking.util.set_keepalive_osx() should set socket options')

    sock = Mock(name='socket')
    set_keepalive_osx(sock, 42)

    sock.setsockopt.assert_has_calls([
        call(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True),
        call(socket.IPPROTO_TCP, 0x10, 42),
    ])


@patch('xmpp.networking.util.socket')
def test_set_keepalive_linux(socket):
    ('xmpp.networking.util.set_keepalive_linux() should set socket options')

    sock = Mock(name='socket')
    set_keepalive_linux(sock, 200, 100, 300)

    sock.setsockopt.assert_has_calls([
        call(socket.SOL_SOCKET, socket.SO_KEEPALIVE, True),
        call(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 100),
        call(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 200),
        call(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 300),
    ])


@patch('xmpp.networking.util.select')
def test_socket_ready(select):
    ('xmpp.networking.util.socket_ready() should a pair of sockets')

    select.select.return_value = [['reader1'], ['writer1'], ['exceptions1']]
    sock = Mock(name='socket')
    result = socket_ready(sock, 420)

    result.should.be.a(SocketStatePair)

    result.read.should.equal('reader1')
    result.write.should.equal('writer1')


def test_address_is_ip():
    ('xmpp.networking.util.address_is_ip() returns True for numbers')

    address_is_ip('10.10.10.10').should.be.true
    address_is_ip('hostname.com').should.be.false
