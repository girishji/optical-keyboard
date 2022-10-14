# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place footprints
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

# https://deskthority.net/viewtopic.php?t=20144

import pcbnew
from pcbnew import wxPoint, wxPointMM
import itertools
import math


class Switch:
    _pos = {
        "S": (0, 0),
    }

    _radius = 1.5 * 1e6

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            "S": board.FindFootprintByReference("S" + str(num)),
        }
        self.orient()

    def orient(self):
        orientation = {"S": 0}
        for sym, fp in self.footprints.items():
            if fp:
                fp.SetOrientation(orientation[sym] * 10)

    def get_pad_center(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def add_tracks(self):
        end = self.get_pad_center("S", 1)
        end1 = wxPoint(sta.x, end.y - Switch._radius)
        add_track(sta, end1)
        end2 = add_arc_from(end1, 0, 1, 0, 0)
        add_track(end2, end)

    def place(self, offset):
        for fp in self._pos.keys():
            if self.footprints[fp]:
                p = wxPointMM(
                    Switch._pos[fp][0] + offset[0], Switch._pos[fp][1] + offset[1]
                )
                self.footprints[fp].SetPosition(p)

    def rotate(self, deg):
        p = self.footprints["S"].GetPosition()
        for _, fp in self.footprints.items():
            if fp:
                fp.Rotate(p, deg * 10)


class Keyboard(object):
    DIM = 19.00
    RADIUS = 3 * pcbnew.IU_PER_MM
    SW_COUNT = 72 + 1

    def __init__(self) -> None:
        self.switches = [Switch(None, None)]
        board = pcbnew.GetBoard()
        for i in range(1, Keyboard.SW_COUNT):
            self.switches.append(Switch(board, i))

    def place_footprints(self):
        dim = Keyboard.DIM
        board = pcbnew.GetBoard()

        # row 1
        # self.switches[1].place(((1 - 1 / 8) * dim, 0))
        self.switches[1].place((dim, 0))
        for i in range(2, 16):
            self.switches[i].place((i * dim, 0))
        self.switches[30].place((16 * dim - dim / 2, 0))

        # row 2
        offs = dim + dim / 4
        self.switches[16].place((offs, dim))
        for i in range(17, 29):
            self.switches[i].place((offs + dim / 4 + (i - 16) * dim, dim))
        self.switches[29].place((offs + dim / 4 + dim * 13 + dim / 4, dim))

        # row 3
        offs = (1 - 1 / 4) * dim
        self.switches[30].place((offs - dim * 1 / 8, 2 * dim))
        for i in range(31, 44):
            self.switches[i].place((offs + (i - 30) * dim, 2 * dim))
        self.switches[44].place((offs + (14 + 1 / 8) * dim, 2 * dim))

        # row 4
        offs = dim * (-1 / 2)
        self.switches[45].place((offs + dim, 3 * dim))
        offs += dim * (1 + 3 / 8)
        self.switches[46].place((offs + dim, 3 * dim))
        offs += (3 / 8) * dim
        for i in range(47, 57):
            self.switches[i].place((offs + (i - 45) * dim, 3 * dim))
        offs += dim * 12
        self.switches[57].place((offs + 1 / 8 * dim, 3 * dim))
        offs += dim * (1 + 1 / 4)
        self.switches[58].place((offs, 3 * dim))

        # row 5
        offs = (1 - 1 / 4) * dim
        self.switches[59].place((offs - dim / 8, 4 * dim))
        for i in range(60, 62):
            self.switches[i].place((offs + (i - 59) * dim, 4 * dim))
        offs = dim / 2 + dim * 3
        self.switches[62].place((offs + dim / 4 + 1, 4 * dim + 1))
        self.switches[62].rotate(-7)

        self.switches[63].place((offs + dim * 1.25 + dim / 8 + 1.4, 4 * dim + 5.5))
        self.switches[63].rotate(-16)
        offs += dim * 1.25 * 2
        # self.switches[65].place((offs - 1.5, 4.5 * dim + 4))
        self.switches[64].place((offs - 1.0, 4.5 * dim + 7))
        # self.switches[66].rotate(-15 + 90)
        self.switches[64].rotate(-20 + 90)

        offs += dim * 1.25
        self.switches[65].place((offs, 4 * dim))

        self.switches[66].place((offs + dim + dim / 4 + 1.0, 4.5 * dim + 7))
        self.switches[66].rotate(20 + 90)
        offs += dim * 1.25
        self.switches[67].place((offs + dim - 1.4, 4 * dim + 5))
        self.switches[67].rotate(16)
        self.switches[68].place((offs + 2 * dim - 1, 4 * dim + 1))
        self.switches[68].rotate(7)
        offs += 2 * dim
        self.switches[69].place((offs + dim, 4 * dim))

        for i in range(70, 73):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        pcbnew.Refresh()

    def remove_tracks(self):
        # delete tracks and vias
        board = pcbnew.GetBoard()
        for t in board.GetTracks():
            board.Delete(t)

    def add_via(self, loc):
        board = pcbnew.GetBoard()
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(loc)
        # via.SetDrill(int(0.3 * 1e6))
        # via.SetWidth(int(0.6 * 1e6))
        via.SetDrill(int(0.4 * 1e6))
        via.SetWidth(int(0.8 * 1e6))
        board.Add(via)

    def via_track(self, point, offset=-1.0, reverse=False, vertical=False):
        offset = -offset if reverse else offset
        end = (
            wxPoint(point.x + offset * 1e6, point.y)
            if not vertical
            else wxPoint(point.x, point.y + offset * 1e6)
        )
        add_track(point, end)
        self.add_via(end)
        return end

    def add_tracks(self):
        # add tracks
        for i in range(1, Keyboard.SW_COUNT):
            if i not in (64, 65, 67, 68):
                self.switches[i].add_tracks()

        # columns
        up, down = {}, {}
        for i in range(1, Keyboard.SW_COUNT):
            sta = self.switches[i].get_pad_center("S", 3)
            offset = -1 if i not in (73, 74, 66) else -1 - Switch._radius / 1e6
            sta1 = self.via_track(sta, offset=offset)
            if i in range(1, 16):
                sta2 = add_arc_from(sta1, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)
                down[i] = wxPoint(sta2.x, sta2.y + Switch._radius)
                add_track(sta2, down[i], layer=pcbnew.B_Cu)
            elif i in (64, 65, 67, 68):
                continue
            elif i >= 60:
                up[i] = add_arc_from(sta1, 0, 0, 1, 0, layer=pcbnew.B_Cu)
            else:
                end1 = add_arc_from(sta1, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
                up[i] = add_arc_from(end1, 0, 0, 1, 0, layer=pcbnew.B_Cu)
                end1 = add_arc_from(sta1, 0, 1, 0, 0, layer=pcbnew.B_Cu)
                down[i] = add_arc_from(end1, 0, 1, 1, 1, True, layer=pcbnew.B_Cu)

        exclude = (64, 65, 67, 68, -1)
        for i1, i2, i3, i4, i5 in list(
            zip(
                range(1, 15),
                range(16, 30),
                range(30, 44),
                range(45, 59),
                range(60, 74),
            )
        ) + [(-1, -1, 44, 59, 74)]:
            for st, en in [(i1, i2), (i2, i3), (i3, i4), (i4, i5)]:
                if st in exclude or en in exclude:
                    continue
                sta, end = down[st], up[en]
                sta1 = sta
                end1 = wxPoint(end.x, sta1.y + 2 * Switch._radius)
                add_track(end, end1, layer=pcbnew.B_Cu)
                if sta1.x < end1.x:
                    sta2 = add_arc_from(sta1, 1, 1, 1, 0, True, layer=pcbnew.B_Cu)
                    end2 = add_arc_from(end1, 0, 0, 0, 1, True, layer=pcbnew.B_Cu)
                    add_track(sta2, end2, layer=pcbnew.B_Cu)
                elif sta1.x > end1.x:
                    sta2 = add_arc_from(sta1, 0, 1, 0, 0, layer=pcbnew.B_Cu)
                    end2 = add_arc_from(end1, 1, 0, 1, 1, layer=pcbnew.B_Cu)
                    add_track(sta2, end2, layer=pcbnew.B_Cu)
                else:
                    add_track(sta1, end1, layer=pcbnew.B_Cu)

        # ground
        for i in range(1, Keyboard.SW_COUNT):
            if i not in (64, 65, 67, 68):
                self.via_track(self.switches[i].get_pad_center("S", 2), offset=1.0)
                self.via_track(self.switches[i].get_pad_center("S", 4), offset=-1.0)

        pcbnew.Refresh()


def add_holes():
    dim = Keyboard.DIM
    delta = 0.6
    border = 0
    board = pcbnew.GetBoard()
    holes = [board.FindFootprintByReference("Hs1")]  # dummy
    holes += [board.FindFootprintByReference("Hs" + str(num)) for num in range(1, 19)]

    def set_position(num, x, y):
        holes[num].SetPosition(pcbnew.wxPointMM(x, y))

    set_position(1, dim * 0.5, -dim * 0.5 - border + delta)
    set_position(2, dim * 5.5, -dim * 0.5 - border + delta)
    set_position(3, dim * 10.5, -dim * 0.5 - border + delta)
    set_position(4, dim * 15.5, -dim * 0.5 - border + delta)
    set_position(5, dim * (2 - 1 / 8), dim * 1.5 - 2)
    set_position(6, dim * 5, dim * 1.5 - delta)
    set_position(7, dim * 8, dim * 1.5 - delta)
    set_position(8, dim * 11, dim * 1.5 - delta)
    set_position(9, dim * (14 + 1 / 8), dim * 1.5 - 2)
    set_position(10, dim * 4.75, dim * 3.5 + delta)
    set_position(11, dim * 9.75, dim * 3.5 + delta)
    set_position(12, dim * (15 + 1 / 5 + 1 / 4), dim * 2.5 + border)
    set_position(13, dim * 0, dim * 4.5 + border - delta)
    set_position(14, dim * 3.25, dim * 4.5 + border - delta)
    set_position(15, dim * 6.25 - 1, dim * 5.5 + border + 0.5)
    set_position(16, dim * 8.25 + 1, dim * 5.5 + border + 0.5)
    set_position(17, dim * 12.0, dim * 4.5 + border - delta)
    set_position(18, dim * 15, dim * 4.5 + border - delta)

    pcbnew.Refresh()


def add_track(start, end, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc(start, end, mid, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_ARC(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetMid(mid)
    if track.GetAngle() < 0:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6))
    track.SetLayer(layer)
    board.Add(track)


def add_arc_from(
    point, ex, ey, mx, my, reverse=False, d=Switch._radius, layer=pcbnew.F_Cu
):
    end = wxPoint(point.x + (d if ex else -d), point.y + (d if ey else -d))
    mid = wxPoint(point.x + (d if mx else -d), point.y + (d if my else -d))
    if reverse:
        add_arc(end, point, mid, layer)
    else:
        add_arc(point, end, mid, layer)
    return end


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


kb = Keyboard()
kb.place_footprints()
# kb.remove_tracks()
# kb.add_tracks()
add_holes()
