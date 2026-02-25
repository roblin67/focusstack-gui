#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 21:57:28 2026

@author: Robert Becht (roblin67@gmail.com)
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui import FocusStackGUI

app = QApplication(sys.argv)
window = FocusStackGUI()
window.resize(800, 700)
window.show()
sys.exit(app.exec())
