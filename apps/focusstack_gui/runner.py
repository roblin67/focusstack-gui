#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 21:56:09 2026

@author: Robert Becht (roblin67@gmail.com)
"""

import subprocess
from config import FOCUS_STACK_BIN

def build_command(images, options):
    cmd = [FOCUS_STACK_BIN]
    cmd += images

    # Output
    cmd.append(f"--output={options['output']}")

    # Align
    if options["global_align"]:
        cmd.append("--global-align")
    if options["full_res_align"]:
        cmd.append("--full-resolution-align")
    if options["no_align"]:
        cmd.append("--no-align")
    if options["align_only"]:
        cmd.append("--align-only")
    if options["no_whitebalance"]:
        cmd.append("--no-whitebalance")
    if options["no_contrast"]:
        cmd.append("--no-contrast")
    if options["no_transform"]:
        cmd.append("--no-transform")

    # Merge
    cmd.append(f"--consistency={options['consistency']}")
    cmd.append(f"--denoise={options['denoise']}")

    # Depthmap
    if options["depthmap"]:
        cmd.append(f"--depthmap={options['depthmap_file']}")
        cmd.append(f"--depthmap-threshold={options['depth_threshold']}")
        cmd.append(f"--depthmap-smooth-xy={options['depth_smooth_xy']}")
        cmd.append(f"--depthmap-smooth-z={options['depth_smooth_z']}")

    # Performance
    cmd.append(f"--threads={options['threads']}")
    cmd.append(f"--batchsize={options['batchsize']}")
    if options["no_opencl"]:
        cmd.append("--no-opencl")
    if options["verbose"]:
        cmd.append("--verbose")

    return cmd


def run_process(cmd):
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
        errors="ignore"
    )
