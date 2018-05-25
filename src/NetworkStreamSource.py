'''
Copyright (c) 2018, UChicago Argonne, LLC. All rights reserved.

Copyright 2018. UChicago Argonne, LLC. This software was produced
under U.S. Government contract DE-AC02-06CH11357 for Argonne National
Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
U.S. Department of Energy. The U.S. Government has rights to use,
reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should
be clearly marked, so as not to confuse it with the version available
from ANL.

Additionally, redistribution and use in source and binary forms, with
or without modification, are permitted provided that the following
conditions are met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in
      the documentation and/or other materials provided with the
      distribution.

    * Neither the name of UChicago Argonne, LLC, Argonne National
      Laboratory, ANL, the U.S. Government, nor the names of its
      contributors may be used to endorse or promote products derived
      from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
'''

# Initial Author <2018>: Arthur Glowacki

from PyQt5.QtCore import QThread, pyqtSignal
import pyxrfmaps.pyxrfmaps
import zmq

class NetStreamSource(QThread):
    new_xrf_packet_trigger = pyqtSignal(pyxrfmaps.StreamBlock)

    def __init__(self, str_ip, port=43434):
        QThread.__init__(self)
        self.conn_str = 'tcp://' + str(str_ip) + ':' + str(port)
        self._running = False

    def run(self):
        self._running = True
        print ('Connecting to ' + self.conn_str)
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect(self.conn_str)
        socket.setsockopt(zmq.SUBSCRIBE, b"XRF-Counts")
        #socket.setsockopt(zmq.RCVTIMEO, 1000)  # set timeout to 1000ms
        serializer = pyxrfmaps.io.net.BasicSerializer()
        while self._running:
            token = socket.recv()
            if(token == b"XRF-Counts"):
                message = socket.recv()
                new_packet = serializer.decode_counts(message, len(message))
                self.new_xrf_packet_trigger.emit(new_packet)
        self.socket.close()


    def stop(self):
        self._running = False