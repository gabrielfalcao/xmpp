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

import sys
import ssl
import socket
import logging
import Queue
import dns.resolver
import couleur
from speakers import Speaker as Events
from xmpp import security
from xmpp.networking.util import create_tcp_socket
from xmpp.networking.util import address_is_ip
from xmpp.networking.util import socket_ready

logger = logging.getLogger('xmpp.networking')
stderr = couleur.Shell(sys.stderr, linebreak=True)

DEFAULT_CIPHERS = "HIGH+kEDH:HIGH+kEECDH:HIGH:!PSK:!SRP:!3DES:!aNULL"


class TLSContext(object):
    def __init__(self, ssl_version, certfile=None, keyfile=None, ca_certs=None, ciphers=None):
        self._DER_CERT = None
        self._socket = None
        if ca_certs is None:
            cert_policy = ssl.CERT_NONE
        else:
            cert_policy = ssl.CERT_REQUIRED

        self.__client_args = {
            'certfile'.encode('utf-8'): certfile,
            'keyfile'.encode('utf-8'): keyfile,
            'ca_certs'.encode('utf-8'): ca_certs,
            'cert_reqs'.encode('utf-8'): cert_policy,
            'do_handshake_on_connect'.encode('utf-8'): False,
            "ssl_version".encode('utf-8'): ssl_version,
        }
        if sys.version_info >= (2, 7):
            self.__client_args['ciphers'] = ciphers

    def get_peer_pem_cert(self):
        if not self._DER_CERT:
            return

        PEM = ssl.DER_cert_to_PEM_cert(self._DER_CERT)
        return PEM

    def get_client_args(self):
        return self.__client_args.copy()

    def set_der_cert(self, cert):
        self._DER_CERT = cert

    def wrap_socket(self, S):
        S.setblocking(True)
        ssl_socket = ssl.wrap_socket(S, **self.get_client_args())
        try:
            ssl_socket.do_handshake()
            S.setblocking(False)
        except (socket.error, ssl.SSLError) as e:
            raise TLSUpgradeError(e, self)

        return ssl_socket

    def verify_peer_cert(self, domain, socket):
        DER_CERT = socket.getpeercert(binary_form=True)
        self.set_der_cert(DER_CERT)

        try:
            security.verify_certificate(domain, DER_CERT)
        except security.CertificateError as e:
            raise TLSUpgradeError(e, self.tls_context)

    def upgrade_and_verify(self, domain, socket):
        ssl_socket = self.wrap_socket(socket)
        self.verify_peer_cert(domain, ssl_socket)
        return ssl_socket


class XMPPConnection(object):
    def __init__(self, host, port, debug=False, auto_reconnect=False,
                 queue_class=Queue.Queue, hwm_in=256, hwm_out=256, recv_chunk_size=65536):
        self.socket = None
        self.tls_context = None
        self.host = bytes(host)
        self.port = int(port)
        self.read_queue = queue_class(hwm_in)
        self.write_queue = queue_class(hwm_out)
        self.recv_chunk_size = int(recv_chunk_size)
        self.__alive = False
        self.on = Events('connection', [
            'tcp_established',    # the TCP connection was established
            'tcp_restablished',   # the TCP connection was lost and restablished
            'tcp_downgraded',     # the TLS connection was downgraded to TCP
            'tcp_disconnect',     # the TCP connection was lost
            'tcp_failed',         # the TCP connection failed to be established

            'ssl_established',    # the TLS connection was established
            'ssl_invalid_chain',  # the TLS handshake failed for invalid chain
            'ssl_invalid_cert',   # the TLS handshake failed for invalid server cert
            'ssl_failed',         # failed to establish a TLS connection
            'ssl_start',          # started SSL negotiation

            'write',              # the TCP/TLS connection is ready to send data
            'read',               # the TCP/TLS connection is ready to receive data
            'ready_to_write',     # the TCP/TLS connection is ready to send data
            'ready_to_read',      # the TCP/TLS connection is ready to receive data
        ])

        if debug:
            self.on.tcp_established(lambda event, data: stderr.bold_green("TCP ESTABLISHED: {0}".format(data)))
            self.on.tcp_restablished(lambda event, data: stderr.bold_blue("TCP RESTABLISHED: {0}".format(data)))
            self.on.tcp_downgraded(lambda event, data: stderr.bold_cyan("TCP DOWNGRADED: {0}".format(data)))
            self.on.tcp_disconnect(lambda event, data: stderr.bold_red("TCP DISCONNECT: {0}".format(data)))
            self.on.tcp_failed(lambda event, data: stderr.red("TCP FAILED: {0}".format(data)))

            self.on.ssl_established(lambda event, pem_cert: stderr.green("SSL ESTABLISHED: {0}".format(pem_cert)))
            self.on.ssl_failed(lambda event, error: stderr.red("SSL FAILED: {0}".format(error)))
            self.on.ssl_invalid_chain(lambda event, error: stderr.red("SSL INVALID CHAIN: {0}".format(error)))
            self.on.ssl_invalid_cert(lambda event, error: stderr.red("SSL INVALID CERT: {0}".format(error)))
            self.on.ssl_start(lambda event, tls: stderr.bold_magenta("SSL NEGOTIATION STARTED: {0}".format(tls)))

            self.on.read(lambda event, data: stderr.yellow("XMPP RECV: {0}".format(data)))
            self.on.write(lambda event, data: stderr.blue("XMPP SEND: {0}".format(data)))

        if auto_reconnect:
            self.on.tcp_disconnect(lambda event, data: self.reconnect())

    def reconnect(self, timeout_in_seconds=3):
        self.socket = create_tcp_socket(keep_alive_seconds=3, max_fails=5)
        try:
            self.socket.connect((self.host, self.port))
            self.on.tcp_restablished.shout(self.host)
            self.__alive = True
        except Exception as e:
            self.__alive = False
            logger.exception("Failed to connect to %s:%s", self.host, self.port)
            self.on.tcp_failed.shout(e)

        self.connect(timeout_in_seconds)

    def resolve_dns(self):
        answers = dns.resolver.query(self.host, 'A')
        for a in answers:
            self.host = a.address

    def disconnect(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            logger.debug('connection closed')

        try:
            self.socket.close()
        except:
            logger.exception("failed to close")

        self.__alive = False
        self.socket = None
        self.on.tcp_disconnect.shout("intentional")

    def connect(self, timeout_in_seconds=3):
        # test this without an internet connection to handle edge
        # cases
        if self.socket:
            # TODO: report already connected
            return

        if not address_is_ip(self.host):
            try:
                self.resolve_dns()
            except dns.resolver.NoAnswer as e:
                self.on.tcp_failed.shout(dns.resolver.NoAnswer('failed to resolve {0}'.format(self.host)))
                return

        self.socket = create_tcp_socket(keep_alive_seconds=3, max_fails=5)
        try:
            self.socket.connect((self.host, self.port))
            self.on.tcp_established.shout(self.host)
            self.__alive = True
        except Exception as e:
            self.__alive = False
            logger.exception("Failed to connect to %s:%s", self.host, self.port)
            self.on.tcp_failed.shout(e)

    def send_whitespace_keepalive(self):
        connection = socket_ready(self.socket, 0.1)
        if connection.write:
            try:
                connection.write.sendall(b' ')
            except socket.error as e:
                if e.errno == 32:  # broken pipe
                    logger.warning(e)
                else:
                    self.on.tcp_disconnect.shout(e)

            return True

        return False

    def is_alive(self):
        return self.__alive

    def downgrade_to_tcp(self, reconnect_timeout_in_seconds=3):
        if not self.tls_context:
            logger.warning("already downgraded to TCP")
            return

        self.tls_context = None
        try:
            self.socket = self.socket.unwrap()
        except (AttributeError, socket.error):
            self.socket = None
            self.reconnect(reconnect_timeout_in_seconds)
        else:
            self.on.tcp_downgraded.shout({
                'socket': self.socket.fileno(),
                'host': self.host,
            })

    def upgrade_to_tls(self, domain, ssl_version, **kw):
        if self.tls_context:
            raise RuntimeError('already upgraded!')

        self.tls_context = TLSContext(ssl_version, **kw)

        try:
            ssl_socket = self.tls_context.upgrade_and_verify(domain, self.socket)
        except TLSUpgradeError as e:
            return self.on.ssl_failed.shout(e)

        if hasattr(self.socket, 'socket'):
            # We are using a testing socket, so preserve the top
            # layer of wrapping.
            self.socket.socket = ssl_socket
        else:
            self.socket = ssl_socket

        self.on.ssl_established.shout(self)

    def perform_write(self, connection):
        self.on.ready_to_write.shout(self)
        try:
            data = self.write_queue.get(block=False, timeout=3)
        except Queue.Empty:
            return

        try:
            connection.sendall(data)
            self.on.write.shout(data)
        except socket.error as e:
            self.write_queue.put(data, block=False)
            self.on.tcp_disconnect.shout(e)
            logger.exception('failed to write data: %s', data)

    def perform_read(self, connection):
        data = None
        try:
            data = connection.recv(self.recv_chunk_size)
        except socket.error as e:
            if self.tls_context:
                self.on.ssl_failed.shout(e)
            else:
                self.on.tcp_disconnect.shout(e)

            logger.exception('failed to read data of chunk size: %s', self.recv_chunk_size)

        if data:
            self.on.read.shout(data)
        else:
            return

        self.read_queue.put(data, block=False, timeout=3)
        self.on.ready_to_read.shout(self)

    def send(self, data):
        self.write_queue.put(data, block=False, timeout=3)

    def receive(self):
        return self.read_queue.get(block=False, timeout=3)

    def poll(self, timeout=3):
        self.socket.setblocking(False)
        socket = socket_ready(self.socket, timeout)
        if socket.read:
            self.perform_read(socket.read)

        if socket.write:
            self.perform_write(socket.write)


class ConnectionInterrupted(Exception):
    pass


class TLSUpgradeError(Exception):
    def __init__(self, error, context):
        self.error = error
        self.context = context
        message = '{0}'.format(error)
        super(TLSUpgradeError, self).__init__(message)
