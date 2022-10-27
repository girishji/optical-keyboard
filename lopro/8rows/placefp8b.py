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
    _sym_pos = {"S": (0, 0), "Ri": (8.0, 2.03), "D": (0, -4.8)}
    _radius = 1.5 * 1e6

    def __init__(self, board, num) -> None:
        if not board and not num:
            return  # dummy
        self.footprints = {
            sym: board.FindFootprintByReference(sym + str(num))
            for sym in self._sym_pos.keys()
        }
        self.orient()

    def orient(self):
        orientation = {"S": 0, "Ri": -90, "D": 0}
        for sym, fp in self.footprints.items():
            if fp:
                fp.SetOrientation(orientation[sym] * 10)

    def get_pad_center(self, fp, pad_num):
        return self.footprints[fp].FindPadByNumber(str(pad_num)).GetCenter()

    def add_tracks(self):
        sta = self.get_pad_center("Ri", 2)
        end = self.get_pad_center("S", 1)
        add_track(sta, end)

    def place(self, offset):
        for fp in self._sym_pos.keys():
            if self.footprints[fp]:
                p = wxPointMM(
                    Switch._sym_pos[fp][0] + offset[0],
                    Switch._sym_pos[fp][1] + offset[1],
                )
                self.footprints[fp].SetPosition(p)

    def placefp(self, fp, offset, orientation=0):
        p = self.footprints["S"].GetPosition()
        if orientation:
            fp.SetOrientation(orientation * 10)
        p = wxPoint(
            p.x + offset[0] * pcbnew.IU_PER_MM, p.y + offset[1] * pcbnew.IU_PER_MM
        )
        fp.SetPosition(p)

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
        self.board = pcbnew.GetBoard()
        for i in range(1, Keyboard.SW_COUNT):
            self.switches.append(Switch(self.board, i))

    def place_footprints(self):
        dim = Keyboard.DIM

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
        self.switches[57].place((offs + 3 / 8 * dim, 3 * dim))
        offs += dim * (1 + 3 / 4)
        self.switches[58].place((offs, 3 * dim))

        # row 5
        row5shift = 0

        offs = (1 - 1 / 4) * dim - row5shift
        self.switches[59].place((offs - dim / 8, 4 * dim))
        for i in range(60, 62):
            self.switches[i].place((offs + (i - 59) * dim, 4 * dim))
        offs = (3 + 1 / 2) * dim
        self.switches[62].place((offs + dim / 4 + 1, 4 * dim + 1))
        self.switches[62].rotate(-7)

        # self.switches[63].place((offs + dim * 1.25 + dim / 8 + 1.4, 4 * dim + 5.5))
        # self.switches[63].rotate(-16)
        offs += dim * (1 + 1 / 4 + 1 / 8)
        self.switches[63].place((offs + 1.4, 4 * dim + 5.2))
        self.switches[63].rotate(-16)
        offs += dim * (1 + 1 / 8)

        # self.switches[64].place((offs - 1.0, 4.5 * dim + 7))
        self.switches[64].place((offs - 0.6, 4.5 * dim + 7))
        # self.switches[66].rotate(-15 + 90)
        # self.switches[64].rotate(-20 + 90)
        self.switches[64].rotate(-28 + 90)

        offs += dim * 1.25
        self.switches[65].place((offs, 4 * dim))

        # self.switches[66].place((offs + dim + dim / 4 + 1.0, 4.5 * dim + 7))
        self.switches[66].place((offs + dim + dim / 4 + 0.6, 4.5 * dim + 7))
        self.switches[66].rotate(28 + 90)
        offs += dim * 1.25
        self.switches[67].place((offs + dim - 1.4, 4 * dim + 5.2))
        self.switches[67].rotate(16)
        self.switches[68].place((offs + 2 * dim - 1, 4 * dim + 1))
        self.switches[68].rotate(7)
        offs += (2 + 1 / 4) * dim
        self.switches[69].place((offs + dim, 4 * dim))

        for i in range(70, 73):
            self.switches[i].place((offs + (i - 68) * dim, 4 * dim))

        # Modules
        Mod = self.board.FindFootprintByReference("MOD1")
        Mod.SetPosition(wxPointMM(-7.0, -5.25))
        Mod = self.board.FindFootprintByReference("MOD2")
        Mod.SetPosition(wxPointMM(116.5, 74.50))

        # Connectors
        # J = [self.board.FindFootprintByReference("J" + str(num)) for num in range(1, 17)]
        # self.switches[2].placefp(J[0], [dim / 2 - 2.54, -dim / 2 + 1.15], 90)
        # self.switches[7].placefp(J[1], [dim / 2 - 2.54, -dim / 2 + 1.15], 90)
        # self.switches[13].placefp(J[2], [dim / 2 - 2.54, -dim / 2 + 1.15], -90)
        # self.switches[59].placefp(J[3], [-dim / 2 - 2.54, -0 / 2 + 1.15], -90)

        pcbnew.Refresh()

    def add_tracks(self):

        for sw in range(1, 73):
            self.switches[sw].add_tracks()

        # ground
        sw = self.switches[1].footprints["S"].GetPosition()
        pad = self.switches[1].get_pad_center("S", 4)
        sta = wxPoint(pad.x - sw.x, pad.y - sw.y)
        end = wxPoint(sta.x, sta.y - 1 * pcbnew.IU_PER_MM)
        for i in range(1, Keyboard.SW_COUNT):
            sw = self.switches[i].footprints["S"].GetPosition()
            deg = -self.switches[i].footprints["S"].GetOrientation() // 10
            add_track(transform(sta, sw, deg), transform(end, sw, deg))
            add_via(transform(end, sw, deg))

        # Rows
        ht = 3.5 * pcbnew.IU_PER_MM
        for st, en in [(1, 15), (16, 29), (30, 44), (45, 58), (59, 61), (69, 72)]:
            for i in range(st, en):
                sta = self.switches[i].get_pad_center("Ri", 1)
                end = self.switches[i + 1].get_pad_center("Ri", 1)
                pt1 = wxPoint(sta.x + ht, sta.y - ht)
                pt2 = wxPoint(end.x - ht, end.y - ht)
                add_track(sta, pt1, width=0.6)
                add_track(end, pt2, width=0.6)
                add_track(pt1, pt2, width=0.6)

        ht = 0.9 * pcbnew.IU_PER_MM
        for st, en in [
            (1, 9),
            (16, 24),
            (30, 38),
            (45, 53),
            (59, 61),
            (54, 57),
            (39, 44),
            (25, 27),
            (28, 29),
            (10, 15),
            (69, 72),
        ]:
            for i in range(st, en):
                sta = self.switches[i].get_pad_center("S", 2)
                end = self.switches[i + 1].get_pad_center("S", 2)
                pt1 = wxPoint(sta.x + ht, sta.y + ht)
                pt2 = wxPoint(end.x - ht, end.y + ht)
                add_track(sta, pt1, width=0.3)
                add_track(end, pt2, width=0.3)
                add_track(pt1, pt2, width=0.3)

        # columns
        viax = 1 * pcbnew.IU_PER_MM
        sw = self.switches[1].footprints["S"].GetPosition()
        pad = self.switches[1].get_pad_center("S", 3)
        sta = wxPoint(pad.x - sw.x, pad.y - sw.y)
        end = wxPoint(sta.x - viax, sta.y)
        for i in range(1, Keyboard.SW_COUNT):
            sw = self.switches[i].footprints["S"].GetPosition()
            deg = -self.switches[i].footprints["S"].GetOrientation() // 10
            add_track(transform(sta, sw, deg), transform(end, sw, deg))
            add_via(transform(end, sw, deg))

        for st, en in zip(range(1, 10), range(16, 25)):
            sta = self.switches[st].get_pad_center("S", 3)
            end = self.switches[en].get_pad_center("S", 3)
            xdiff = end.x - sta.x
            pt = wxPoint(end.x - viax - xdiff, end.y - xdiff)
            add_track(wxPoint(end.x - viax, end.y), pt, layer=pcbnew.B_Cu)
            add_track(pt, wxPoint(sta.x - viax, sta.y), layer=pcbnew.B_Cu)

        mm1 = 1 * pcbnew.IU_PER_MM
        for st, en in zip(range(16, 25), range(30, 39)):
            sta = self.switches[st].get_pad_center("S", 3)
            end = self.switches[en].get_pad_center("S", 3)
            sta = wxPoint(sta.x - viax, sta.y)
            end = wxPoint(end.x - viax, end.y)
            pt = wxPoint(end.x, end.y - 5.5 * mm1)
            add_track(end, pt, layer=pcbnew.B_Cu)
            pt2 = wxPoint(pt.x + 2 * mm1, pt.y - 2 * mm1)
            add_track(pt2, pt, layer=pcbnew.B_Cu)
            pt3 = wxPoint(pt2.x + 8 * mm1, pt2.y)
            add_track(pt2, pt3, layer=pcbnew.B_Cu)
            xdiff = sta.x - pt3.x
            pt4 = wxPoint(pt3.x + xdiff, pt3.y - xdiff)
            add_track(pt4, pt3, layer=pcbnew.B_Cu)
            add_track(pt4, sta, layer=pcbnew.B_Cu)

        pcbnew.Refresh()

    def add_led_tracks(self):

        # Rows
        ht = 1.5 * pcbnew.IU_PER_MM
        for st, en in [
            (1, 8),
            (9, 15),
            (16, 23),
            (24, 29),
            (30, 37),
            (38, 44),
            (45, 52),
            (53, 58),
            (59, 61),
            (69, 72),
        ]:
            for i in range(st, en):
                sta = self.switches[i].get_pad_center("D", 1)
                end = self.switches[i + 1].get_pad_center("D", 1)
                pt1 = wxPoint(sta.x + ht, sta.y + ht)
                pt2 = wxPoint(end.x - ht, end.y + ht)
                add_track(sta, pt1, width=0.4)
                add_track(end, pt2, width=0.4)
                add_track(pt1, pt2, width=0.4)

        # Vias
        viax = 3 * pcbnew.IU_PER_MM
        sw = self.switches[1].footprints["D"].GetPosition()
        pad = self.switches[1].get_pad_center("D", 2)
        sta = wxPoint(pad.x - sw.x, pad.y - sw.y)
        end = wxPoint(sta.x + viax, sta.y)
        for i in range(1, Keyboard.SW_COUNT):
            sw = self.switches[i].footprints["D"].GetPosition()
            deg = -self.switches[i].footprints["D"].GetOrientation() // 10
            add_track(transform(sta, sw, deg), transform(end, sw, deg))
            if i not in list(range(32, 43)):
                add_via(transform(end, sw, deg))

        # Cols
        for st, en in zip(range(2, 14), range(17, 29)):
            if st == 9:
                continue
            sta = self.switches[st].get_pad_center("D", 2)
            sta = wxPoint(sta.x + viax, sta.y)
            end = self.switches[en].get_pad_center("D", 2)
            end = wxPoint(end.x + viax, end.y)
            xdiff = end.x - sta.x
            pt = wxPoint(sta.x + xdiff, sta.y + xdiff)
            add_track(sta, pt, layer=pcbnew.B_Cu)
            add_track(end, pt, layer=pcbnew.B_Cu)

        via2x = 8 * pcbnew.IU_PER_MM
        for st, en in zip(range(18, 29), range(32, 43)):
            sta = self.switches[st].get_pad_center("D", 2)
            sta = wxPoint(sta.x + viax, sta.y)
            end = self.switches[en].get_pad_center("D", 2)
            end = wxPoint(end.x + viax, end.y)
            pt = wxPoint(end.x + via2x, end.y)
            add_track(end, pt)
            add_via(pt)
            if st == 25:
                continue
            end = pt
            xdiff = sta.x - end.x
            pt = wxPoint(end.x + xdiff, end.y - xdiff)
            add_track(sta, pt, layer=pcbnew.B_Cu)
            add_track(end, pt, layer=pcbnew.B_Cu)

        for st, en in zip(range(33, 42), range(48, 57)):
            if st == 40:
                continue
            sta = self.switches[st].get_pad_center("D", 2)
            sta = wxPoint(sta.x + viax + via2x, sta.y)
            end = self.switches[en].get_pad_center("D", 2)
            end = wxPoint(end.x + viax, end.y)
            xdiff = end.x - sta.x
            pt = wxPoint(sta.x + xdiff, sta.y + xdiff)
            add_track(sta, pt, layer=pcbnew.B_Cu)
            add_track(end, pt, layer=pcbnew.B_Cu)

        pcbnew.Refresh()

    # PT pullup resistors
    def pullup_resistors(self):
        R_PT = [self.board.FindFootprintByReference("R1")] + [
            self.board.FindFootprintByReference("R" + str(num)) for num in range(1, 19)
        ]
        # for r, sw in list(zip(range(1, 16), range(30, 45))) + list(
        #     zip(range(16, 18), range(25, 27))
        # ):
        #     self.switches[sw].placefp(R_PT[r], [-8, 2], -90)
        #     viax = 1 * pcbnew.IU_PER_MM
        #     sta = self.switches[sw].get_pad_center("S", 3)
        #     sta = wxPoint(sta.x - viax, sta.y)
        #     end = R_PT[r].FindPadByNumber("1").GetCenter()
        #     add_track(sta, end)

        # Tracks between them
        mm = pcbnew.IU_PER_MM
        for r in range(1, 18):
            sta = R_PT[r].FindPadByNumber("2").GetCenter()
            tmp = R_PT[r].FindPadByNumber("1").GetCenter()
            d1 = (sta.y - tmp.y) / 2.0
            end = wxPoint(sta.x - d1, sta.y - d1)
            sta = add_track(sta, end)
            if r == 15:
                continue
            if r == 17:
                sta1 = R_PT[18].FindPadByNumber("2").GetCenter()
                end1 = wxPoint(sta1.x - d1, sta1.y - d1)
                add_track(sta1, end1)
            d2 = 1.5 * mm
            end = wxPoint(sta.x, sta.y - d2)
            sta = add_track(sta, end)
            end = wxPoint(sta.x + d1, sta.y - d1)
            sta = add_track(sta, end)
            end = wxPoint(sta.x + 3.8 * mm, sta.y)
            sta = add_track(sta, end)
            d3 = 0.3 * mm
            end = wxPoint(sta.x + d1 + d2 + d3, sta.y + d1 + d2 + d3)
            sta = add_track(sta, end)
            end = wxPoint(sta.x + 2.5 * mm, sta.y)
            sta = add_track(sta, end)
            nxt = R_PT[r + 1].FindPadByNumber("2").GetCenter()
            nxt = wxPoint(nxt.x - d1, nxt.y - d1)
            d4 = sta.y - nxt.y
            end = wxPoint(sta.x + d4, sta.y - d4)
            sta = add_track(sta, end)
            sta = add_track(sta, nxt)


def add_holes_M1_6():
    dim = Keyboard.DIM
    delta = 0.6
    border = 1.8
    board = pcbnew.GetBoard()
    holes = [board.FindFootprintByReference("Hs1")]  # dummy
    holes += [board.FindFootprintByReference("Hs" + str(num)) for num in range(1, 19)]

    def set_position(num, x, y):
        holes[num].SetPosition(pcbnew.wxPointMM(x, y))

    set_position(1, dim * 1.5, -dim * 0.5 + border + delta)
    set_position(2, dim * 5.5, -dim * 0.5 + border + delta)
    set_position(3, dim * 10.5, -dim * 0.5 + border + delta)
    set_position(4, dim * 14.5, -dim * 0.5 + border + delta)
    set_position(5, dim * (2 - 1 / 8), dim * 1.5 - delta)
    set_position(6, dim * 5, dim * 1.5 - delta)
    set_position(7, dim * 7.25, dim * 2.5 - delta)
    set_position(8, dim * 9, dim * 1.5 - delta)
    set_position(9, dim * (14 + 1 / 8), dim * 1.5 - delta)
    set_position(10, dim * 2.5, dim * 2.5 + delta)
    set_position(11, dim * 9.75, dim * 3.5 + delta)
    set_position(12, dim * (15 + 1 / 5 + 1 / 4) - border, dim * 2.5)
    set_position(13, dim * 0 + border, dim * 4.5 - border - delta)
    set_position(14, dim * (4 + 1 / 4 + 1 / 8 - 1 / 16), dim * 4.6 - border - delta)
    set_position(15, dim * 7.85, dim * 4.5 - border)
    set_position(16, dim * 12.25, dim * 2.5 - delta)
    # set_position(16, dim * 8.25 + 1, dim * 5.5 + border + 0.5)
    set_position(17, dim * 11.10, dim * 4.5 - border - delta)
    set_position(18, dim * 15.20 + 3, dim * 4.5 - 3 * border)

    pcbnew.Refresh()


def add_holes_M2():
    dim = Keyboard.DIM
    delta = 0.6
    border = 0
    board = pcbnew.GetBoard()
    holes = [board.FindFootprintByReference("Hs1")]  # dummy
    holes += [board.FindFootprintByReference("Hs" + str(num)) for num in range(1, 19)]

    def set_position(num, x, y):
        holes[num].SetPosition(pcbnew.wxPointMM(x, y))

    set_position(1, dim * 1.5, -dim * 0.5 - border + delta)
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
    set_position(14, dim * (3 + 1 / 2 - 1 / 8 - 2 / 16), dim * 4.5 + border - delta)
    set_position(15, dim * 6.25 - 1, dim * 5.5 + border + 0.5)
    set_position(16, dim * 8.25 + 1, dim * 5.5 + border + 0.5)
    set_position(17, dim * 12.25, dim * 4.5 + border - delta)
    set_position(18, dim * 15.25 + 3, dim * 4.5 + border - 3 * delta)

    pcbnew.Refresh()


# Width = 0.2 (ICs), 0.25 (default), 0.4 (normal), 0.8 (power)
def add_track(start, end, layer=pcbnew.F_Cu, width=0.3):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_TRACK(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetWidth(int(width * 1e6))
    track.SetLayer(layer)
    board.Add(track)
    return end


def add_via(loc):
    board = pcbnew.GetBoard()
    via = pcbnew.PCB_VIA(board)
    via.SetPosition(loc)
    via.SetDrill(int(0.4 * 1e6))
    via.SetWidth(int(0.8 * 1e6))
    board.Add(via)


def add_arc(start, end, mid, power=False, layer=pcbnew.F_Cu):
    board = pcbnew.GetBoard()
    track = pcbnew.PCB_ARC(board)
    track.SetStart(start)
    track.SetEnd(end)
    track.SetMid(mid)
    if track.GetAngle() < 0:
        track = pcbnew.PCB_TRACK(board)
        track.SetStart(start)
        track.SetEnd(end)
    track.SetWidth(int(0.25 * 1e6) if not power else int(0.4 * 1e6))
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


def remove_tracks():
    # delete tracks and vias
    board = pcbnew.GetBoard()
    for t in board.GetTracks():
        board.Delete(t)


# remove_tracks()
kb = Keyboard()
kb.place_footprints()
# kb.add_tracks()
# kb.add_led_tracks()
# kb.pullup_resistors()
add_holes_M1_6()
