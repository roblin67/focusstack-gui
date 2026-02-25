#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 09:40:24 2026

@author: Robert Becht (roblin67@gmail.com)
"""

from PyQt6.QtCore import QThread, pyqtSignal
from runner import build_command, run_process
import re


class FocusStackWorker(QThread):
    output_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def __init__(self, images, options):
        super().__init__()
        self.images = images
        self.options = options
        self._running = True

    def run(self):
        cmd = build_command(self.images, self.options)
        process = run_process(cmd)

        for line in process.stdout:
            if not self._running:
                process.kill()
                break

            line = line.strip()
            self.output_signal.emit(line)
            self._update_progress(line)

        self.finished_signal.emit()

    def stop(self):
        self._running = False

    def _update_progress(self, line):
        """
        Progress estimation based on Focus-stack output text.
        """

        if "Align" in line:
            self.progress_signal.emit(20)

        elif "Laplacian" in line or "pyramid" in line:
            self.progress_signal.emit(40)

        elif "Merge" in line:
            self.progress_signal.emit(70)

        elif "Depth" in line:
            self.progress_signal.emit(85)

        elif "Saving" in line or "Write" in line:
            self.progress_signal.emit(95)

        elif "Done" in line:
            self.progress_signal.emit(100)
