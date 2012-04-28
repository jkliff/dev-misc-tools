#!/usr/bin/env python
#
# plot-timeline.py - A simple program to plot timelines based on a Linux strace(1) log.
# Copyright (C) 2007 Federico Mena-Quintero, Johan Dahlin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Authors: Federico Mena-Quintero <federico@gnu.org>
#          Johan Dahlin <johan@gnome.org>
#
# Forked on April 26th, 2012.
# Since then this venerable tool by the great Federico Mena-Quintero has been
# disrespectfully butchered into a generic time line-base log visualizer.
# So is life.
#

import math
import optparse
import os
import re
import sys

import cairo

from datetime import datetime

### CUSTOMIZATION BEGINS HERE

FONT_NAME = "Bitstream Vera Sans"
FONT_SIZE = 10
PIXELS_PER_SECOND = 300
PIXELS_PER_LINE = 12
PLOT_WIDTH = 1400
TIME_SCALE_WIDTH = 20
SYSCALL_MARKER_WIDTH = 20
LOG_TEXT_XPOS = 300
LOG_MARKER_WIDTH = 20
BACKGROUND_COLOR = (80, 80, 80)

# list of strings to ignore in the plot
ignore_strings = [
#    "nautilus_directory_async_state_changed"
    ]

# list of pairs ("string", (r, g, b)) to give a special color to some strings
special_colors = [
#    ("nautilus_window_size_allocate", (1, 1, 1)),
#    ("STARTING MAIN LOOP", (1, 0, 0)),
    ]

### CUSTOMIZATION ENDS HERE

def get_special_color (string):
    for sc in special_colors:
        if string.find (sc[0]) >= 0:
            return sc[1]

    return None

def string_has_substrings (string, substrings):
    for i in substrings:
        if string.find (i) >= 0:
            return True

    return False


timestamp_mark = re.compile ('^(\d+\.\d+) (.*)$')
read_mark = re.compile ('^\d+\.\d+ read\(')
open_close_mark = re.compile ('^\d+\.\d+ (:?open|close)\(')


success_result = "0"

class BaseMark:
    colors = 0, 0, 0
    def __init__(self, timestamp, log):
        self.timestamp = timestamp
        self.log = log
        self.timestamp_ypos = 0
        self.log_ypos = 0

class AccessMark(BaseMark):
    pass

class LastMark(BaseMark):
    colors = 1.0, 0, 0

class FirstMark(BaseMark):
    colors = 1.0, 0, 0

class ExecMark(BaseMark):
#    colors = 0.75, 0.33, 0.33
    colors = (1.0, 0.0, 0.0)
    def __init__(self, timestamp, log, is_complete, is_resumed):
#        if is_complete:
	text = 'execve: '
#        elif is_resumed:
#            text = 'execve resumed: '
#        else:
#            text = 'execve started: '

        text = text + os.path.basename(log)
        BaseMark.__init__(self, timestamp, text)

class Metrics:
    def __init__(self):
        self.width = 0
        self.height = 0

# don't use black or red
palette = [
    (0.12, 0.29, 0.49),
    (0.36, 0.51, 0.71),
    (0.75, 0.31, 0.30),
    (0.62, 0.73, 0.38),
    (0.50, 0.40, 0.63),
    (0.29, 0.67, 0.78),
    (0.96, 0.62, 0.34),
    (1.0 - 0.12, 1.0 - 0.29, 1.0 - 0.49),
    (1.0 - 0.36, 1.0 - 0.51, 1.0 - 0.71),
    (1.0 - 0.75, 1.0 - 0.31, 1.0 - 0.30),
    (1.0 - 0.62, 1.0 - 0.73, 1.0 - 0.38),
    (1.0 - 0.50, 1.0 - 0.40, 1.0 - 0.63),
    (1.0 - 0.29, 1.0 - 0.67, 1.0 - 0.78),
    (1.0 - 0.96, 1.0 - 0.62, 1.0 - 0.34)
    ]

class SyscallParser:
    def __init__ (self):
        self.pending_execs = []
        self.syscalls = []

    def search_pending_execs (self, search_pid):
        n = len (self.pending_execs)
        for i in range (n):
            (pid, timestamp, command) = self.pending_execs[i]
            if pid == search_pid:
                return (i, timestamp, command)

        return (None, None, None)

    def add_line (self, str):
        """here we: 
- search for patterns to mark
- add then to self.syscalls with .append(asdf)
- appended data is AccessMark with a timestamp and text"""

        m = timestamp_mark.search (str)
        if m:
            #print m.group (1)
            timestamp = float (m.group (1))
            a = AccessMark (timestamp, m.group (2))
            color_idx = 0
            if read_mark.search (str):
                color_idx = 3
            elif open_close_mark.search (str):
                color_idx = 4
            a.colors = colors = palette [color_idx]
            self.syscalls.append (a)

        return

def parse_strace(filename):
    parser = SyscallParser ()

    for line in file(filename, "r"):
        if line == "":
            break

        parser.add_line (line)

    return parser.syscalls

def normalize_timestamps(syscalls):

    first_timestamp = syscalls[0].timestamp

    for syscall in syscalls:
        syscall.timestamp -= first_timestamp

def compute_syscall_metrics(syscalls):
    num_syscalls = len(syscalls)

    metrics = Metrics()
    metrics.width = PLOT_WIDTH

    last_timestamp = syscalls[num_syscalls - 1].timestamp
    num_seconds = int(math.ceil(last_timestamp))
    metrics.height = max(num_seconds * PIXELS_PER_SECOND,
                         num_syscalls * PIXELS_PER_LINE)

    text_ypos = 0
    duration = syscalls [-1].timestamp - syscalls[0].timestamp
    px_per_sec = metrics.height / duration

    for syscall in syscalls:
        syscall.timestamp_ypos = syscall.timestamp * px_per_sec #PIXELS_PER_SECOND
        syscall.log_ypos = text_ypos + FONT_SIZE

        text_ypos += PIXELS_PER_LINE

    return metrics

def plot_time_scale(surface, ctx, metrics):
    """TODO: fix this time scale to show the real timestamp at specific points"""
    print metrics.height, PIXELS_PER_SECOND, (metrics.height+ PIXELS_PER_SECOND - 1) /PIXELS_PER_SECOND
    num_seconds = (metrics.height + PIXELS_PER_SECOND - 1) / PIXELS_PER_SECOND

    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.set_line_width(1.0)
    print num_seconds
    for i in range(num_seconds):
        ypos = i * PIXELS_PER_SECOND

        ctx.move_to(0, ypos + 0.5)
        ctx.line_to(TIME_SCALE_WIDTH, ypos + 0.5)
        ctx.stroke()

        ctx.move_to(0, ypos + 2 + FONT_SIZE)
        ctx.show_text("%d s" % i)

def plot_syscall(surface, ctx, syscall):
    ctx.set_source_rgb(*syscall.colors)

    # Line
    print (TIME_SCALE_WIDTH, syscall.timestamp_ypos)
    print (TIME_SCALE_WIDTH + SYSCALL_MARKER_WIDTH, syscall.timestamp_ypos)
    print (LOG_TEXT_XPOS - LOG_MARKER_WIDTH, syscall.log_ypos - FONT_SIZE / 2 + 0.5)
    print (LOG_TEXT_XPOS, syscall.log_ypos - FONT_SIZE / 2 + 0.5)
    print '-'

    ctx.move_to(TIME_SCALE_WIDTH, syscall.timestamp_ypos)
    ctx.line_to(TIME_SCALE_WIDTH + SYSCALL_MARKER_WIDTH, syscall.timestamp_ypos)
    ctx.line_to(LOG_TEXT_XPOS - LOG_MARKER_WIDTH, syscall.log_ypos - FONT_SIZE / 2 + 0.5)
    ctx.line_to(LOG_TEXT_XPOS, syscall.log_ypos - FONT_SIZE / 2 + 0.5)
    ctx.stroke()

    # Log text

    ctx.move_to(LOG_TEXT_XPOS, syscall.log_ypos)
    ctx.show_text("%8.5f: %s" % (syscall.timestamp, syscall.log))

def plot_syscalls_to_surface(syscalls, metrics):
    num_syscalls = len(syscalls)

    surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
                                 metrics.width, metrics.height)

    ctx = cairo.Context(surface)
    ctx.select_font_face(FONT_NAME)
    ctx.set_font_size(FONT_SIZE)

    # Background

    ctx.set_source_rgb (*BACKGROUND_COLOR)
    ctx.rectangle(0, 0, metrics.width, metrics.height)
    ctx.fill()

    # Time scale

    plot_time_scale(surface, ctx, metrics)

    # Contents

    ctx.set_line_width(1.0)

    for syscall in syscalls:
        plot_syscall(surface, ctx, syscall)

    return surface

def main(args):
    option_parser = optparse.OptionParser(
        usage="usage: %prog -o output.png <strace.txt>")
    option_parser.add_option("-o",
                             "--output", dest="output",
                             metavar="FILE",
                             help="Name of output file (output is a PNG file)")

    options, args = option_parser.parse_args()

    if not options.output:
        print 'Please specify an output filename with "-o file.png" or "--output=file.png".'
        return 1

    if len(args) != 1:
        print 'Please specify only one input filename, which is an strace log taken with "strace -ttt -f"'
        return 1

    in_filename = args[0]
    out_filename = options.output

    syscalls = []
    for syscall in parse_strace(in_filename):
        syscalls.append(syscall)
        if isinstance(syscall, FirstMark):
            syscalls = []
        elif isinstance(syscall, LastMark):
            break

    if not syscalls:
        print 'No marks in %s, add access("MARK: ...", F_OK)' % in_filename
        return 1

    normalize_timestamps(syscalls)
    metrics = compute_syscall_metrics(syscalls)

    surface = plot_syscalls_to_surface(syscalls, metrics)
    surface.write_to_png(out_filename)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
