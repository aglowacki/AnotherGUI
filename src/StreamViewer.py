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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QProgressBar, QTextEdit
from NetworkStreamSource import NetStreamSource
from XrfCountsWidget import XrfCountsWidget


class StreamViewer(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.net_stream = None
        self.qline_ip_addr = QLineEdit("127.0.0.1")
        self.btn_update = QPushButton("Update")
        self.base_layout = QVBoxLayout()
        self.createBaseLayout()

    def createBaseLayout(self):
        hlayout = QHBoxLayout()
        hlayout.addWidget(self.qline_ip_addr)
        hlayout.addWidget(self.btn_update)
        self.base_layout.addLayout(hlayout)
        self.setLayout(self.base_layout)


class XrfStreamViewer(StreamViewer):
    def __init__(self):
        StreamViewer.__init__(self)
        self.xrfWidget = XrfCountsWidget()
        self.status_textbox = QTextEdit()
        self.progressBar = QProgressBar()
        self.last_row = -1
        self.createLayout()


    def createLayout(self):
        self.btn_update.released.connect(self.update_ip)
        #_textEdit = QTextEdit()
        #_textEdit->resize(1024, 800)
        #_textEdit->scrollBarWidgets(Qt::AlignRight)
        self.base_layout.addWidget(self.xrfWidget)
        self.base_layout.addWidget(self.progressBar)
        self.setWindowTitle("XRF Stream Viewer")

    def new_stream_block(self, stream_block):
        if stream_block.row() == 0 and stream_block.col() == 0:
            self.xrfWidget.initialize_from_stream_block(stream_block)
            ##self.mapsElementsWidget.setModel(self.currentModel)
            self.progressBar.setRange(0, stream_block.height() - 1)

        self.xrfWidget.update_from_stream_block(stream_block)
        if self.last_row != stream_block.row():
            status_str = ">" + str(stream_block.row()) + " " + str(stream_block.col()) + " : " + str(stream_block.height()) + " " + str(stream_block.width())
            print(status_str)
            self.xrfWidget.redrawCounts()
            self.progressBar.setValue(stream_block.row())
            # _textEdit.clear()
            self.progressBar.update()
        self.last_row = stream_block.row()

    def update_ip(self):
        if self.net_stream is not None:
            self.net_stream.stop()
        self.net_stream = NetStreamSource(self.qline_ip_addr.text())
        self.net_stream.new_xrf_packet_trigger.connect(self.new_stream_block)
        self.net_stream.start()

