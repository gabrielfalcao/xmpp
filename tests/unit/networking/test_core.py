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
import socket
import Queue

from mock import patch, ANY, Mock
from xmpp.networking.core import XMPPConnection
from tests.unit.util import EventHandlerMock
from tests.unit.util import event_test


class StubAddress(object):
    def __init__(self, address):
        self.address = address


def test_empty_events():
    ('xmpp.networking.core.XMPPConnection should have clear event handlers in the beginning')

    conn = XMPPConnection('host', 5222)
    conn.on.hooks.should.be.empty


def test_debug_events():
    ('xmpp.networking.core.XMPPConnection should have clear event handlers in the beginning')

    conn = XMPPConnection('host', 5222, debug=True, auto_reconnect=True)
    conn.on.hooks.should.have.length_of(12)


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
def test_reconnect(context, create_tcp_socket):
    ('XMPPConnection.reconnect() should fire the tcp_restablished event if suitable')
    socket = create_tcp_socket.return_value

    conn = XMPPConnection('host', 5222)

    tcp_restablished = EventHandlerMock('on_tcp_restablished')
    tcp_failed = EventHandlerMock('on_tcp_failed')

    conn.on.tcp_restablished(tcp_restablished)
    conn.on.tcp_failed(tcp_failed)
    conn.reconnect()

    socket.connect.assert_called_once_with(('host', 5222))

    tcp_restablished.assert_called_once_with(ANY, 'host:5222')


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
def test_reconnect_failed(context, create_tcp_socket):
    ('XMPPConnection.reconnect() should fire the tcp_failed event if suitable')
    socket = create_tcp_socket.return_value
    error = RuntimeError('boom')
    socket.connect.side_effect = error
    conn = XMPPConnection('host', 5222)

    tcp_restablished = EventHandlerMock('on_tcp_restablished')
    tcp_failed = EventHandlerMock('on_tcp_failed')

    conn.on.tcp_restablished(tcp_restablished)
    conn.on.tcp_failed(tcp_failed)
    conn.reconnect()

    socket.connect.assert_called_once_with(('host', 5222))

    tcp_failed.assert_called_once_with(ANY, error)


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
@patch('xmpp.networking.core.dns')
def test_resolve_dns(context, dns, create_tcp_socket):
    ('xmpp.networking.core.XMPPConnection should have clear event handlers in the beginning')
    dns.resolver.query.return_value = [
        StubAddress('10.20.30.40'),
    ]
    socket = create_tcp_socket.return_value
    error = RuntimeError('boom')
    socket.connect.side_effect = error
    conn = XMPPConnection('host', 5222)

    conn.resolve_dns()
    conn.host.should.equal('10.20.30.40')


@event_test
def test_disconnect_failed(context):
    ('XMPPConnection.disconnect() should fire the tcp_failed event if suitable')

    conn = XMPPConnection('host', 5222)
    conn.socket = Mock(name='socket')
    conn.socket.shutdown.side_effect = socket.error('boom 1')
    conn.socket.close.side_effect = socket.error('boom 2')

    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')

    conn.on.tcp_disconnect(tcp_disconnect)
    conn.disconnect()

    tcp_disconnect.assert_called_once_with(ANY, "intentional")


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
@patch('xmpp.networking.core.dns.resolver')
def test_connect_failed_dns(context, resolver, create_tcp_socket):
    ('XMPPConnection.connect() should fire the tcp_failed event')
    resolver.NoAnswer = ValueError
    resolver.query.side_effect = resolver.NoAnswer('boom')

    conn = XMPPConnection('capulet.com', 5222)
    tcp_failed = EventHandlerMock('on_tcp_failed')
    conn.on.tcp_failed(tcp_failed)

    conn.connect()

    tcp_failed.assert_called_once_with(ANY, "failed to resolve: capulet.com")


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
@patch('xmpp.networking.core.dns.resolver')
def test_connect_ok(context, resolver, create_tcp_socket):
    ('XMPPConnection.connect() should fire the tcp_failed event')
    resolver.query.return_value = [
        StubAddress('10.20.30.40'),
    ]

    conn = XMPPConnection('capulet.com', 5222)
    tcp_established = EventHandlerMock('on_tcp_established')
    conn.on.tcp_established(tcp_established)

    conn.connect()

    tcp_established.assert_called_once_with(ANY, "10.20.30.40")
    conn.is_alive().should.be.true


@event_test
@patch('xmpp.networking.core.create_tcp_socket')
@patch('xmpp.networking.core.dns.resolver')
def test_connect_error(context, resolver, create_tcp_socket):
    ('XMPPConnection.connect() should fire the tcp_failed event')
    socket = create_tcp_socket.return_value
    socket.connect.side_effect = ValueError('boom')

    conn = XMPPConnection('capulet.com', 5222)
    tcp_failed = EventHandlerMock('on_tcp_failed')
    conn.on.tcp_failed(tcp_failed)

    conn.connect()

    tcp_failed.assert_called_once_with(ANY, "boom")


@event_test
@patch('xmpp.networking.core.socket_ready')
def test_send_whitespace_keepalive(context, socket_ready):
    ('XMPPConnection.send_whitespace_keepalive() should send')
    sockets = socket_ready.return_value

    conn = XMPPConnection('capulet.com', 5222)
    conn.socket = 'w00t'
    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')
    conn.on.tcp_disconnect(tcp_disconnect)

    conn.send_whitespace_keepalive()

    tcp_disconnect.called.should.be.false
    sockets.write.sendall.assert_called_once_with(b' ')

    socket_ready.assert_called_once_with('w00t', 3)


@event_test
@patch('xmpp.networking.core.socket_ready')
def test_send_whitespace_keepalive_failed(context, socket_ready):
    ('XMPPConnection.send_whitespace_keepalive() should send')
    sockets = socket_ready.return_value
    sockets.write.sendall.side_effect = socket.error('boom')

    conn = XMPPConnection('capulet.com', 5222)
    conn.socket = 'w00t'
    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')
    conn.on.tcp_disconnect(tcp_disconnect)

    conn.send_whitespace_keepalive()

    sockets.write.sendall.assert_called_once_with(b' ')

    socket_ready.assert_called_once_with('w00t', 3)
    tcp_disconnect.assert_called_once_with(ANY, 'boom')


@event_test
def test_perform_write_ok(context):
    ('XMPPConnection.perform_write() should consume the write queue')
    conn = XMPPConnection('capulet.com', 5222)
    conn.write_queue = Mock(name='write_queue')
    conn.write_queue.get.return_value = '<data />'

    write = EventHandlerMock('on_write')
    conn.on.write(write)

    socket = Mock(name='socket')
    conn.perform_write(socket)

    socket.sendall.assert_called_once_with('<data />')
    write.assert_called_once_with(ANY, '<data />')
    conn.write_queue.get.assert_called_once_with(block=False, timeout=3)


@event_test
def test_perform_write_empty_queue(context):
    ('XMPPConnection.perform_write() should do '
     'nothing when has an empty write queue')

    conn = XMPPConnection('capulet.com', 5222)
    conn.write_queue = Mock(name='write_queue')
    conn.write_queue.get.side_effect = Queue.Empty('dang!')

    write = EventHandlerMock('on_write')
    conn.on.write(write)

    socket = Mock(name='socket')
    conn.perform_write(socket)

    socket.sendall.called.should.be.false
    write.called.should.be.false


@event_test
@patch('xmpp.networking.core.logger')
def test_perform_write_socket_error(context, logger):
    ('XMPPConnection.perform_write() should '
     'fire tcp_disconnect on socket error')

    conn = XMPPConnection('capulet.com', 5222)
    conn.write_queue = Mock(name='write_queue')
    conn.write_queue.get.return_value = '<data />'

    write = EventHandlerMock('on_write')
    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')

    conn.on.write(write)
    conn.on.tcp_disconnect(tcp_disconnect)

    sock = Mock(name='socket')
    sock.sendall.side_effect = socket.error('boom')
    conn.perform_write(sock)

    sock.sendall.assert_called_once_with('<data />')
    write.called.should.be.false

    tcp_disconnect.assert_called_once_with(ANY, 'boom')

    logger.warning.assert_called_once_with(
        'failed to write data (%s): %s', 'boom', '<data />'
    )


@event_test
def test_perform_read_ok(context):
    ('XMPPConnection.perform_read() should consume the read queue')
    conn = XMPPConnection('capulet.com', 5222, recv_chunk_size=420)
    conn.read_queue = Mock(name='read_queue')

    read = EventHandlerMock('on_read')
    conn.on.read(read)

    socket = Mock(name='socket')
    socket.recv.return_value = '<data />'
    conn.perform_read(socket)

    socket.recv.assert_called_once_with(420)
    read.assert_called_once_with(ANY, '<data />')
    conn.read_queue.put.assert_called_once_with('<data />', block=False, timeout=3)


@event_test
@patch('xmpp.networking.core.logger')
def test_perform_read_socket_error(context, logger):
    ('XMPPConnection.perform_read() should '
     'fire tcp_disconnect on socket error')

    conn = XMPPConnection('capulet.com', 5222, recv_chunk_size=420)
    conn.read_queue = Mock(name='read_queue')
    conn.read_queue.get.return_value = '<data />'

    read = EventHandlerMock('on_read')
    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')

    conn.on.read(read)
    conn.on.tcp_disconnect(tcp_disconnect)

    sock = Mock(name='socket')
    sock.recv.side_effect = socket.error('boom')
    conn.perform_read(sock)

    sock.recv.assert_called_once_with(420)
    read.called.should.be.false

    tcp_disconnect.assert_called_once_with(ANY, 'boom')

    logger.warning.assert_called_once_with(
        'failed to read data of chunk size: %s', 420
    )


@event_test
@patch('xmpp.networking.core.logger')
def test_perform_read_socket_error(context, logger):
    ('XMPPConnection.perform_read() should '
     'fire tcp_disconnect on socket error')

    conn = XMPPConnection('capulet.com', 5222, recv_chunk_size=420)
    conn.read_queue = Mock(name='read_queue')
    conn.read_queue.get.return_value = '<data />'

    read = EventHandlerMock('on_read')
    tcp_disconnect = EventHandlerMock('on_tcp_disconnect')

    conn.on.read(read)
    conn.on.tcp_disconnect(tcp_disconnect)

    sock = Mock(name='socket')
    sock.recv.side_effect = socket.error('boom')
    conn.perform_read(sock)

    sock.recv.assert_called_once_with(420)
    read.called.should.be.false

    tcp_disconnect.assert_called_once_with(ANY, 'boom')

    logger.warning.assert_called_once_with(
        'failed to read data of chunk size: %s', 420
    )


@event_test
def test_perform_read_no_data(context):
    ('XMPPConnection.perform_read() should do nothing '
     'if no data was received')

    conn = XMPPConnection('capulet.com', 5222, recv_chunk_size=420)
    conn.read_queue = Mock(name='read_queue')

    read = EventHandlerMock('on_read')
    conn.on.read(read)

    socket = Mock(name='socket')
    socket.recv.return_value = ''
    conn.perform_read(socket)

    socket.recv.assert_called_once_with(420)
    read.called.should.be.false
    conn.read_queue.put.called.should.be.false


@event_test
def test_send(context):
    ('XMPPConnection.send() should adds data to a write queue')

    conn = XMPPConnection('capulet.com', 5222)
    conn.write_queue = Mock(name='write_queue')

    conn.send('foo')
    conn.write_queue.put.assert_called_once_with('foo', block=False, timeout=3)


@event_test
def test_receive(context):
    ('XMPPConnection.receive() should adds data to a read queue')

    conn = XMPPConnection('capulet.com', 5222)
    conn.read_queue = Mock(name='read_queue')

    conn.receive(30)

    conn.read_queue.get.assert_called_once_with(block=False, timeout=30)


@event_test
@patch('xmpp.networking.core.XMPPConnection.perform_read')
@patch('xmpp.networking.core.XMPPConnection.perform_write')
@patch('xmpp.networking.core.socket_ready')
def test_loop_once(context, socket_ready, perform_write, perform_read):
    ('XMPPConnection.loop_once() should perform write and read')
    socket = socket_ready.return_value

    conn = XMPPConnection('capulet.com', 5222)
    conn.socket = Mock(name='socket')
    conn.read_queue = Mock(name='read_queue')
    conn.write_queue = Mock(name='write_queue')

    conn.loop_once(2)

    conn.socket.setblocking.assert_called_once_with(False)

    perform_write.assert_called_once_with(socket.write)
    perform_read.assert_called_once_with(socket.read)
