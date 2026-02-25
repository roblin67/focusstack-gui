#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 21:57:02 2026

@author: Robert Becht (roblin67@gmail.com)
"""

import os
import re
#from PyQt6.QtWidgets import QFileDialog
from datetime import datetime
#import sys
#from PyQt6.QtWidgets import QProgressBar

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QTextEdit, QTabWidget, QFormLayout, QCheckBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QLabel,
    QProgressBar, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

from worker import FocusStackWorker
from runner import build_command, run_process


class FocusStackGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Focus-Stack Pro GUI")

        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.images = []

        self._build_files_tab()
        self._build_align_tab()
        self._build_merge_tab()
        self._build_depth_tab()
        self._build_performance_tab()
        self._build_help_tab()

        self.layout.addWidget(self.tabs)

        self.run_btn = QPushButton("Run Focus Stack")
        self.run_btn.clicked.connect(self.run_stack)
        self.layout.addWidget(self.run_btn)
        
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_stack)
        self.cancel_btn.setEnabled(False)
        self.layout.addWidget(self.cancel_btn)

        self.console = QTextEdit()
        self.layout.addWidget(self.console)

        self.setLayout(self.layout)

    # ---------- FILES ----------
    def _build_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Select images
        btn = QPushButton("Select Images")
        btn.clicked.connect(self.select_images)
        layout.addWidget(btn)
       
        # Mode galerie
        self.image_list = QListWidget()
        self.image_list.setToolTip(
            "Selected images for stacking\n"
            "You can select multiple items and remove them"
        )
        self.image_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.image_list.setIconSize(QSize(120, 120))
        self.image_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.image_list.setMovement(QListWidget.Movement.Static)
        self.image_list.setSpacing(10)
        
        self.image_list.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        
        layout.addWidget(QLabel("Selected images:"))
        layout.addWidget(self.image_list)
        
        # # Image list widget
        # self.image_list = QListWidget()
        # self.image_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        # self.image_list.setIconSize(QSize(80, 80))
        # layout.addWidget(QLabel("Selected images:"))
        # layout.addWidget(self.image_list)
        
        # Remove button
        remove_btn = QPushButton("Remove selected images")
        remove_btn.clicked.connect(self.remove_selected_images)
        layout.addWidget(remove_btn)

        # Output directory selector
        self.output_dir = QLineEdit(os.getcwd())
        choose_dir_btn = QPushButton("Choose Output Folder")
        choose_dir_btn.clicked.connect(self.select_output_folder)

        layout.addWidget(QLabel("Output folder:"))
        layout.addWidget(self.output_dir)
        layout.addWidget(choose_dir_btn)

        # Auto-folder option
        self.auto_subfolder = QCheckBox("Create dated subfolder automatically")
        self.auto_subfolder.setToolTip(
            "If enabled, a folder named stack_YYYYMMDD_HHMMSS\n"
            "will be created inside the selected output directory."
        )
        self.auto_subfolder.setChecked(True)
        layout.addWidget(self.auto_subfolder)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Files")
        
    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Output Folder", self.output_dir.text()
        )
        if folder:
            self.output_dir.setText(folder)

    # ---------- ALIGN ----------
    def _build_align_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.global_align = QCheckBox()
        self.global_align.setToolTip(
            "Align each image directly against the reference image\n"
            "Default: align with neighbour image"
        )
        self.full_res_align = QCheckBox()
        self.full_res_align.setToolTip(
            "Use full resolution images during alignment\n"
            "Default: alignment limited to 2048px"
        )
        self.no_align = QCheckBox()
        self.no_align.setToolTip(
            "Skip alignment completely\n"
            "Overrides all other alignment options"
        )
        self.align_only = QCheckBox()
        self.align_only.setToolTip(
            "Only perform alignment and exit\n"
            "No merging will be done"
        )
        self.no_whitebalance = QCheckBox()
        self.no_whitebalance.setToolTip(
            "Disable automatic white balance correction"
        )
        self.no_contrast = QCheckBox()
        self.no_contrast.setToolTip(
            "Disable automatic contrast and exposure correction"
        )
        self.no_transform = QCheckBox()
        self.no_transform.setToolTip(
            "Disable geometric alignment correction"
        )

        layout.addRow("Global align", self.global_align)
        layout.addRow("Full resolution align", self.full_res_align)
        layout.addRow("No align", self.no_align)
        layout.addRow("Align only", self.align_only)
        layout.addRow("No white balance", self.no_whitebalance)
        layout.addRow("No contrast", self.no_contrast)
        layout.addRow("No transform", self.no_transform)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Align")

    # ---------- MERGE ----------
    def _build_merge_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.consistency = QSpinBox()
        self.consistency.setRange(0, 2)
        self.consistency.setValue(2)
        self.consistency.setToolTip(
            "Neighbour pixel consistency filter\n"
            "Range: 0 (off) to 2 (strong)\n"
            "Default: 2"
        )

        self.denoise = QDoubleSpinBox()
        self.denoise.setRange(0, 10)
        self.denoise.setValue(1.0)
        self.denoise.setToolTip(
            "Merged image denoise level\n"
            "Default: 1.0"
        )

        layout.addRow("Consistency", self.consistency)
        layout.addRow("Denoise", self.denoise)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Merge")

    # ---------- DEPTH ----------
    def _build_depth_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.depthmap_enable = QCheckBox()
        self.depthmap_enable.setToolTip(
            "Generate a depth map image"
        )
        self.depthmap_file = QLineEdit("depthmap.png")

        self.depth_threshold = QSpinBox()
        self.depth_threshold.setToolTip(
            "Threshold to accept depth points\n"
            "Range: 0–255\n"
            "Default: 10"
        )
        self.depth_threshold.setRange(0, 255)
        self.depth_threshold.setValue(10)

        self.depth_smooth_xy = QSpinBox()
        self.depth_smooth_xy.setToolTip(
            "Depthmap smoothing in X and Y directions\n"
            "Default: 20"
        )
        self.depth_smooth_xy.setValue(20)

        self.depth_smooth_z = QSpinBox()
        self.depth_smooth_z.setToolTip(
            "Depthmap smoothing in Z direction\n"
            "Default: 40"
        )
        self.depth_smooth_z.setValue(40)

        layout.addRow("Enable depthmap", self.depthmap_enable)
        layout.addRow("Depthmap file", self.depthmap_file)
        layout.addRow("Threshold", self.depth_threshold)
        layout.addRow("Smooth XY", self.depth_smooth_xy)
        layout.addRow("Smooth Z", self.depth_smooth_z)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Depthmap")

    # ---------- PERFORMANCE ----------
    def _build_performance_tab(self):
        tab = QWidget()
        layout = QFormLayout()

        self.threads = QSpinBox()
        self.threads.setToolTip(
            "Number of CPU threads\n"
            "Default: number of CPUs + 1"
        )

        self.threads.setValue(4)

        self.batchsize = QSpinBox()
        self.batchsize.setToolTip(
            "Images per merge batch\n"
            "Default: 8"
        )
        self.batchsize.setValue(8)

        self.no_opencl = QCheckBox()
        self.no_opencl.setToolTip(
            "Disable OpenCL GPU acceleration\n"
            "Default: GPU enabled"
        )
        self.verbose = QCheckBox()
        self.verbose.setToolTip(
            "Enable verbose processing output"
        )

        layout.addRow("Threads", self.threads)
        layout.addRow("Batch size", self.batchsize)
        layout.addRow("Disable OpenCL", self.no_opencl)
        layout.addRow("Verbose", self.verbose)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Performance")
        
    def _build_help_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
    
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setFontFamily("Courier")
        
        help_text.setPlainText("""
    Usage: focus-stack [options] file1.jpg file2.jpg ...
    
    ==============================
    OUTPUT FILE OPTIONS
    ==============================
    --output=output.jpg
        Set output filename
    
    --depthmap=depthmap.png
        Write a depth map image (default disabled)
    
    --3dview=3dview.png
        Write a 3D preview image (default disabled)
    
    --save-steps
        Save intermediate images from processing steps
    
    --jpgquality=95
        Quality for saving in JPG format (0-100, default 95)
    
    --nocrop
        Save full image including extrapolated border data
    
    
    ==============================
    IMAGE ALIGNMENT OPTIONS
    ==============================
    --reference=0
        Set index of image used as alignment reference
        (default: middle one)
    
    --global-align
        Align directly against reference
    
    --full-resolution-align
        Use full resolution images in alignment
        (default max 2048px)
    
    --no-whitebalance
        Disable white balance correction
    
    --no-contrast
        Disable contrast and exposure correction
    
    --no-transform
        Disable image position correction
    
    --align-only
        Only align images and exit
    
    --align-keep-size
        Keep original image size (no crop)
    
    --no-align
        Skip alignment completely
    
    
    ==============================
    IMAGE MERGE OPTIONS
    ==============================
    --consistency=2
        Neighbour pixel consistency filter level 0..2
        (default 2)
    
    --denoise=1.0
        Merged image denoise level (default 1.0)
    
    
    ==============================
    DEPTH MAP OPTIONS
    ==============================
    --depthmap-threshold=10
        Threshold to accept depth points (0–255)
    
    --depthmap-smooth-xy=20
        Smoothing in X and Y directions
    
    --depthmap-smooth-z=40
        Smoothing in Z direction
    
    --remove-bg=0
        Positive removes black background,
        negative removes white
    
    --halo-radius=20
        Radius of halo removal
    
    --3dviewpoint=x:y:z:zscale
        Viewpoint for 3D preview (default 1:1:1:2)
    
    
    ==============================
    PERFORMANCE OPTIONS
    ==============================
    --threads=2
        Number of threads (default CPUs + 1)
    
    --batchsize=8
        Images per merge batch (default 8)
    
    --no-opencl
        Disable OpenCL GPU acceleration
    
    --wait-images=0.0
        Wait for image files to appear
    
    
    ==============================
    INFORMATION OPTIONS
    ==============================
    --verbose
        Verbose processing output
    
    --version
        Show application version
    
    --opencv-version
        Show OpenCV library version
    """)
    
        layout.addWidget(help_text)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Help")

    # ---------- ACTIONS ----------
    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.jpg *.jpeg *.png *.tif *.tiff)"
        )
        
        if files:
            self.images = files
            self.image_list.clear()
    
            for file in files:
                icon = QIcon(file)
                item = QListWidgetItem(icon, os.path.basename(file))
                item.setToolTip(file)  # affiche le chemin complet au survol
                self.image_list.addItem(item)
    
            self.console.append(f"{len(files)} images selected.")
            
    def remove_selected_images(self):
        selected_items = self.image_list.selectedItems()
    
        if not selected_items:
            return
    
        for item in selected_items:
            self.images.remove(item.text())
            self.image_list.takeItem(self.image_list.row(item))
    
        self.console.append("Selected images removed.")

    def run_stack(self):
        if not self.images:
            self.console.append("No images selected.")
            return
        
        # Build output path
        base_dir = self.output_dir.text()

        if self.auto_subfolder.isChecked():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_dir = os.path.join(base_dir, f"stack_{timestamp}")
            os.makedirs(base_dir, exist_ok=True)

        # ---- Auto filename based on first image ----
        first_image = os.path.basename(self.images[0])
        name_without_ext = os.path.splitext(first_image)[0]
        name_without_ext = re.sub(r"[^\w\-]", "_", name_without_ext)
        image_count = len(self.images)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_filename = f"{name_without_ext}_stack_{image_count}img_{timestamp}.jpg"
        
        output_path = os.path.join(base_dir, output_filename)

        options = {
            "output": output_path,
            "global_align": self.global_align.isChecked(),
            "full_res_align": self.full_res_align.isChecked(),
            "no_align": self.no_align.isChecked(),
            "align_only": self.align_only.isChecked(),
            "no_whitebalance": self.no_whitebalance.isChecked(),
            "no_contrast": self.no_contrast.isChecked(),
            "no_transform": self.no_transform.isChecked(),
            "consistency": self.consistency.value(),
            "denoise": self.denoise.value(),
            "depthmap": self.depthmap_enable.isChecked(),
            "depthmap_file": self.depthmap_file.text(),
            "depth_threshold": self.depth_threshold.value(),
            "depth_smooth_xy": self.depth_smooth_xy.value(),
            "depth_smooth_z": self.depth_smooth_z.value(),
            "threads": self.threads.value(),
            "batchsize": self.batchsize.value(),
            "no_opencl": self.no_opencl.isChecked(),
            "verbose": self.verbose.isChecked(),
        }

        self.progress.setValue(0)
        self.console.append("Starting Focus-stack...\n")
        self.console.append(f"Working directory: {os.getcwd()}")
        
        self.worker = FocusStackWorker(self.images, options)

        self.worker.output_signal.connect(self.console.append)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self.on_finished)

        self.cancel_btn.setEnabled(True)
        self.run_btn.setEnabled(False)

        self.worker.start()
    
    def cancel_stack(self):
        if hasattr(self, "worker"):
            self.worker.stop()
            self.console.append("Process cancelled.")
            
    def on_finished(self):
        self.progress.setValue(100)
        self.console.append("\nProcess finished.")
        self.cancel_btn.setEnabled(False)
        self.run_btn.setEnabled(True)
