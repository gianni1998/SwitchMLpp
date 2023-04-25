# Source https://itecnote.com/tecnote/python-open-sockets-in-multiple-network-namespaces-from-the-python-code/

import argparse
import os
import select
import socket
import subprocess

# Python doesn't expose the `setns()` function manually, so
# we'll use the `ctypes` module to make it available.
from ctypes import cdll
libc = cdll.LoadLibrary('libc.so.6')
setns = libc.setns


# This is just a convenience function that will return the path
# to an appropriate namespace descriptor, give either a path,
# a network namespace name, or a pid.
def get_ns_path(nspath=None, nsname=None, nspid=None):
    if nsname:
        nspath = '/var/run/netns/%s' % nsname
    elif nspid:
        nspath = '/proc/%d/ns/net' % nspid

    return nspath

# This is a context manager that on enter assigns the process to an
# alternate network namespace (specified by name, filesystem path, or pid)
# and then re-assigns the process to its original network namespace on
# exit.
class Namespace (object):
    def __init__(self, nsname=None, nspath=None, nspid=None):
        self.mypath = get_ns_path(nspid=os.getpid())
        self.targetpath = get_ns_path(nspath,
                                  nsname=nsname,
                                  nspid=nspid)

        if not self.targetpath:
            raise ValueError('invalid namespace')

    def __enter__(self):
        # before entering a new namespace, we open a file descriptor
        # in the current namespace that we will use to restore
        # our namespace on exit.
        self.myns = open(self.mypath)
        with open(self.targetpath) as fd:
            setns(fd.fileno(), 0)

    def __exit__(self, *args):
        setns(self.myns.fileno(), 0)
        self.myns.close()


# This is a wrapper for socket.socket() that creates the socket inside the
# specified network namespace.
def nssocket(ns, *args):
    with Namespace(nsname=ns):
        s = socket.socket(*args)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s