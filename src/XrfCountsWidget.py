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

import PyQt5
from PyQt5.QtWidgets import QWidget, QTabWidget, QHBoxLayout, QVBoxLayout, QComboBox, QSplitter, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

class XrfCountsWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.analysis_enum_to_str = { 1: 'ROI', 2:'Gauss Tails', 4:'Matrix', 8:'SVD', 16:'NNLS'}
        self.analyzed_counts = {}
        self.tab_widget = QTabWidget()
        self.cb_analysis = QComboBox()
        self.cb_element = QComboBox()
        self.scene = QGraphicsScene()
        self.graphicsView = QGraphicsView()
        self.pixmap = QPixmap()
        self.createLayout()

    def createLayout(self):

        #self.spectra_widget = FitSpectraWidget()
        self.cb_analysis.currentIndexChanged.connect(self.onAnalysisSelect)
        self.cb_element.currentIndexChanged.connect(self.onElementSelect)

        self.scene.addPixmap(self.pixmap)
        self.graphicsView.setScene(self.scene)

        hbox = QHBoxLayout()
        counts_layout = QVBoxLayout()
        #layout = QVBoxLayout()

        #splitter = QSplitter()
        #splitter.setOrientation(PyQt5.QtWidgets.Horizontal)
        #splitter.addWidget(self.graphicsView)
        #splitter.setStretchFactor(0, 1)
        #splitter.addWidget(m_tabWidget)
        #createToolBar(m_imageViewWidget)
        #counts_layout.addWidget(m_toolbar)
        #counts_layout.addWidget(splitter)

        hbox.addWidget(self.cb_analysis)
        hbox.addWidget(self.cb_element)

        counts_layout.addWidget(self.graphicsView)
        counts_layout.addItem(hbox)

        #window = QWidget()
        #window.setLayout(counts_layout)

        #self.tab_widget.addTab(window, "Counts")
        #self.tab_widget.addTab(_spectra_widget, "Integrated Spectra")

        #layout.addWidget(self.tab_widget)

        self.setLayout(counts_layout)

    def onAnalysisSelect(self, name):
        elementName = self.cb_element.currentText()
        found_element = False

        try:
            analysis_type = self.analyzed_counts[name]
            self.cb_element.clear()
            lastName = ''
            for el_name, el_counts in analysis_type:
                self.cb_element.addItem(el_name)
                if elementName == el_name:
                    found_element = True
                lastName = el_name

            if found_element:
                self.cb_element.setCurrentText(elementName)
                self.displayCounts(name, elementName)
            else:
                self.displayCounts(name, lastName)
        except:
            return

    def onElementSelect(self, name):
        if type(name) == int:
            return
        analysisName = self.cb_analysis.currentText()
        if len(analysisName) > 0 and len(name) > 0:
            self.displayCounts(analysisName, name)

    def initialize_from_stream_block(self, block):
        self.analyzed_counts = {}
        self.cb_analysis.clear()
        self.cb_element.clear()
        cnt = 0
        for name in block.fitting_blocks.keys():
            self.cb_analysis.addItem(self.analysis_enum_to_str[name])
            group_name = self.analysis_enum_to_str[name]
            self.analyzed_counts[group_name] = {}
            for el_name in block.fitting_blocks[name].fit_counts.keys():
                self.analyzed_counts[group_name][el_name] = np.zeros(shape=(block.height(), block.width()), dtype=np.float32)
                if cnt < 1:
                    self.cb_element.addItem(el_name)
            cnt += 1

    def update_from_stream_block(self, block):
        if len(self.analyzed_counts.keys()) < 1:
            self.initialize_from_stream_block(block)
        for name in block.fitting_blocks.keys():
            try:
                xrf_counts = self.analyzed_counts[self.analysis_enum_to_str[name]]
                for el_name in xrf_counts.keys():
                    xrf_counts[el_name][block.row(), block.col()] = block.fitting_blocks[name].fit_counts[el_name]
            except:
                pass

    def redrawCounts(self):
        self.displayCounts(self.cb_analysis.currentText(), self.cb_element.currentText())

    def displayCounts(self, analysis_type, element):
        if len(self.analyzed_counts.keys()) < 1 or len(element) < 1:
            return
        fit_counts = {}
        try:
            fit_counts = self.analyzed_counts[analysis_type]
        except:
            return
        if len(fit_counts.keys()) > 0:
            data = fit_counts[element].astype(np.uint8)
            h, w = data.shape
            COLORTABLE = [~((i + (i << 8) + (i << 16))) for i in range(255, -1, -1)]
            '''
            height = data.shape[0]
            width = data.shape[1]
            length = data.size
            
            counts_max = fit_counts[element].max()
            counts_min = fit_counts[element].min()
            max_min = counts_max - counts_min
            i = 0
            for row in range(height):
                for col in range(width):
                    data[i] = (((fit_counts.at(element)(row, col) - counts_min) / max_min) * 255)
                    i+=1
            grayscale = []

            for j in range(255):
                grayscale.append(qRgb(i, i, i))

            image = QImage(data.constData(), width, height, width, QImage.Format_Indexed8)
            image.setColorTable(grayscale)
            '''
            image = QImage(data.data, data.shape[1], data.shape[0], QImage.Format_Indexed8)
            image.setColorTable(COLORTABLE)
            image.ndarray = data
            #self.graphicsView.scene().setPixmap(QPixmap.fromImage(image.convertToFormat(QImage.Format_RGB32)))
            self.pixmap = QPixmap.fromImage(image)
            self.graphicsView.setScene(self.scene)
            #self.graphicsView.scene.setPixmap(QPixmap.fromImage(image.convertToFormat(QImage.Format_RGB32)))

