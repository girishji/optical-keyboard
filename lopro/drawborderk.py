# Copyright (C) 2022 Girish Palya <girishji@gmail.com>
# License: https://opensource.org/licenses/MIT
#
# Console script to place mouting holes
#
# To run as script in python console,
#   place or symplink this script to ~/Documents/KiCad/6.0/scripting/plugins
#   Run from python console using 'import filename'
#   To reapply:
#     import importlib
#     importlib.reload(filename)
#  OR
#    exec(open("path-to-script-file").read())

import pcbnew
from pcbnew import wxPoint
import math


DIM = 19.05 * pcbnew.IU_PER_MM
# RADIUS = 3.0 * pcbnew.IU_PER_MM
RADIUS = 5.0 * pcbnew.IU_PER_MM
RADIUS2 = 8.0 * pcbnew.IU_PER_MM
BORDER = 3.0 * pcbnew.IU_PER_MM

WR = {
    "offset": 64 * pcbnew.IU_PER_MM,
    # "depth": 87 * pcbnew.IU_PER_MM,
    "standoff": 28 * pcbnew.IU_PER_MM,
    "width": 90 * pcbnew.IU_PER_MM,
    "height": 65 * pcbnew.IU_PER_MM,
}

SWITCHES = [pcbnew.GetBoard().FindFootprintByReference("S1")]  # dummy
for i in range(1, 75):
    SWITCHES.append(pcbnew.GetBoard().FindFootprintByReference("S" + str(i)))


def pcb_type():
    if pcbnew.GetBoard().FindFootprintByReference("Hs" + str(22)):
        return "pcb"
    if pcbnew.GetBoard().FindFootprintByReference("Hs" + str(12)):
        return "sw_plate"
    return "wr_plate"


def add_line(start, end, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(layer)
    # ls.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
    board.Add(ls)


def add_line_arc(start, center, reverse=False, angle=-90, layer=pcbnew.Edge_Cuts):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetStart(start)
    arc.SetCenter(center)
    arc.SetArcAngleAndEnd(-angle * 10, reverse)
    arc.SetLayer(layer)
    # arc.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
    board.Add(arc)


def centerpt(start, quadrant, d=RADIUS):
    ctr = {
        1: wxPoint(start.x + d, start.y),
        2: wxPoint(start.x, start.y + d),
        3: wxPoint(start.x - d, start.y),
        4: wxPoint(start.x, start.y - d),
    }
    return ctr[quadrant]


def endpt(start, quadrant, d=RADIUS):
    end = {
        1: wxPoint(start.x + d, start.y + d),
        2: wxPoint(start.x - d, start.y + d),
        3: wxPoint(start.x - d, start.y - d),
        4: wxPoint(start.x + d, start.y - d),
    }
    return end[quadrant]


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )


def remove_drawings():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        board.Delete(t)


def draw_border_tilted_keys():
    dim = DIM
    brd = BORDER
    rad = RADIUS
    board = pcbnew.GetBoard()
    switches = SWITCHES
    clearance = 2 * pcbnew.IU_PER_MM

    sw = switches[62].GetPosition()
    degl = -switches[62].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 + 2 * clearance, dim / 2 + brd)
    lend = wxPoint(dim / 2 - clearance, dim / 2 + brd)
    sta = transform(lsta, sw, degl)
    end = transform(lend, sw, degl)
    add_line(sta, end)

    sw = switches[63].GetPosition()
    degl = -switches[63].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 - dim / 8 + 2 * clearance, dim / 2 + brd)
    lend = wxPoint(dim / 2 - brd - rad + clearance, dim / 2 + brd)
    sta = transform(lsta, sw, degl)
    add_line(sta, end)
    end = transform(lend, sw, degl)
    add_line(sta, end)
    ctr = transform(wxPoint(lend.x, lend.y + rad), sw, degl)
    add_line_arc(end, ctr, angle=-65)

    sw = switches[64].GetPosition()
    deg = 90 - switches[64].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lend = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, sw, deg)
    end = transform(lend, sw, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), sw, deg)
    add_line_arc(sta, ctr, angle=-65)
    ctr = transform(wxPoint(lend.x, lend.y - rad), sw, deg)
    add_line_arc(end, ctr, reverse=True, angle=90)
    lend1 = wxPoint(lend.x + rad, lend.y - rad)
    end1 = transform(lend1, sw, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + rad - clearance)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x + rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=False, angle=-90 + deg)

    sw = switches[68].GetPosition()
    degl = -switches[68].GetOrientation() // 10
    lsta = wxPoint(-dim / 2 + clearance, dim / 2 + brd)
    lend = wxPoint(dim / 2 - clearance, dim / 2 + brd)
    sta1 = transform(lsta, sw, degl)
    end = transform(lend, sw, degl)
    add_line(sta1, end)

    sw = switches[67].GetPosition()
    degr = -switches[67].GetOrientation() // 10
    lsta = wxPoint(dim / 2 - clearance, dim / 2 + brd)
    lend = wxPoint(-dim / 2 + rad + brd + 0.5 * clearance, dim / 2 + brd)
    sta = transform(lend, sw, degr)
    end = transform(lsta, sw, degr)
    add_line(sta, end)
    add_line(sta1, end)
    end = transform(lend, sw, degr)
    add_line(sta, end)
    ctr = transform(wxPoint(lend.x, lend.y + rad), sw, degr)
    add_line_arc(end, ctr, reverse=True, angle=65)

    sw = switches[66].GetPosition()
    deg = 90 - switches[66].GetOrientation() // 10
    lend = wxPoint(-dim / 2 - brd + rad, dim / 2 + dim / 8 + brd)
    lsta = wxPoint(dim / 2 + brd - rad, dim / 2 + dim / 8 + brd)
    sta = transform(lsta, sw, deg)
    end = transform(lend, sw, deg)
    add_line(sta, end)
    ctr = transform(wxPoint(lsta.x, lsta.y - rad), sw, deg)
    add_line_arc(sta, ctr, reverse=True, angle=65)
    ctr = transform(wxPoint(lend.x, lend.y - rad), sw, deg)
    add_line_arc(end, ctr, reverse=False, angle=-90)
    lend1 = wxPoint(lend.x - rad, lend.y - rad)
    end1 = transform(lend1, sw, deg)
    lend2 = wxPoint(lend1.x, lend1.y - dim + rad - clearance)
    end2 = transform(lend2, sw, deg)
    add_line(end1, end2)
    ctr = transform(wxPoint(lend2.x - rad, lend2.y), sw, deg)
    add_line_arc(end2, ctr, reverse=True, angle=90 + deg)


def draw_wrist_support():
    rad = RADIUS2
    hole_offset = -rad + (4.5 + 1.0) * pcbnew.IU_PER_MM
    dim = DIM
    brd = BORDER
    switches = SWITCHES

    def place_hole(num, loc):
        if pcb_type() == "sw_plate":
            return
        hole = pcbnew.GetBoard().FindFootprintByReference("Hs" + str(num))
        hole.SetPosition(loc)

    def support_lines(ctr, holenum):
        sta = wxPoint(ctr.x - WR["offset"], ctr.y + dim / 2 + WR["standoff"] + rad)
        begin = wxPoint(sta.x - rad, sta.y - rad)
        add_line_arc(sta, centerpt(sta, 3, rad), reverse=True, angle=90)
        place_hole(holenum, wxPoint(sta.x - rad - hole_offset, sta.y + hole_offset))
        end = wxPoint(sta.x, sta.y + WR["height"] - 2 * rad)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 3, rad), reverse=False, angle=-90)
        holenum += 1
        place_hole(holenum, wxPoint(end.x - rad - hole_offset, end.y - hole_offset))
        sta = wxPoint(end.x - rad, end.y + rad)
        end = wxPoint(sta.x - WR["width"] + 2 * rad, sta.y)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 4, rad), reverse=False, angle=-90)
        holenum += 1
        place_hole(holenum, wxPoint(end.x + hole_offset, end.y - rad - hole_offset))
        sta = wxPoint(end.x - rad, end.y - rad)
        end = wxPoint(sta.x, sta.y - WR["height"] + 2 * rad)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 1, rad), reverse=False, angle=-90)
        holenum += 1
        place_hole(holenum, wxPoint(end.x + rad + hole_offset, end.y + hole_offset))
        end = wxPoint(end.x + rad, end.y - rad)
        add_line(begin, end, layer=pcbnew.Dwgs_User)

    def support_offset(ctr, side="left"):
        extend = 2 * pcbnew.IU_PER_MM
        if pcb_type() != "pcb":
            return
        sta = wxPoint(ctr.x - WR["offset"] - rad, ctr.y + dim / 2 + WR["standoff"])
        end = wxPoint(sta.x - extend, sta.y)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 4, rad), reverse=False, angle=-90)
        sta = wxPoint(end.x - rad, end.y - rad)
        end = wxPoint(sta.x, ctr.y + dim / 2 + brd + rad)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 1, rad), reverse=False, angle=-90)

        sta = wxPoint(
            ctr.x - WR["offset"] - WR["width"] + rad, ctr.y + dim / 2 + WR["standoff"]
        )
        end = wxPoint(sta.x + extend, sta.y)
        add_line(sta, end)
        add_line_arc(end, centerpt(end, 4, rad), reverse=True, angle=90)
        sta = wxPoint(end.x + rad, end.y - rad)
        end = wxPoint(sta.x, ctr.y + dim / 2 + brd + rad)
        add_line(sta, end)
        add_line_arc(
            end, centerpt(end, 3, rad), reverse=True, angle=60 if side == "left" else 90
        )

    holenum = 1 if pcb_type() == "wr_plate" else 1 + 18
    ctr = switches[65].GetPosition()
    support_lines(ctr, holenum)
    support_offset(ctr)
    ctr = wxPoint(ctr.x + 2 * WR["offset"] + WR["width"], ctr.y)
    support_lines(ctr, holenum + 4)
    support_offset(ctr, side="right")


def draw_border():
    dim = DIM
    brd = BORDER
    switches = SWITCHES
    clearance = 0.7 * pcbnew.IU_PER_MM
    rad1 = 3 * pcbnew.IU_PER_MM
    left_offset = 5 * pcbnew.IU_PER_MM

    if pcb_type() == "wr_plate":
        draw_wrist_support()
        return

    swl = switches[45].GetPosition()
    swr = switches[15].GetPosition()
    tl = wxPoint(swl.x - dim / 2 - brd + RADIUS2 - left_offset, swr.y - dim / 2 - brd)
    tr = wxPoint(swr.x + dim / 2 + brd - rad1 + clearance, tl.y)
    add_line(tl, tr)
    add_line_arc(tl, centerpt(tl, 2, RADIUS2), reverse=True, angle=90)
    add_line_arc(tr, centerpt(tr, 2, rad1), reverse=False, angle=-90)
    sta = endpt(tl, 2, RADIUS2)
    end = wxPoint(tl.x - RADIUS2, swl.y + 1.5 * dim - RADIUS2 + brd)
    add_line(endpt(tl, 2, RADIUS2), end)
    if pcb_type() == "pcb":
        add_line_arc(end, centerpt(end, 1, RADIUS2), reverse=True, angle=45)
    else:
        add_line_arc(end, centerpt(end, 1, RADIUS2), reverse=True, angle=90)
        sta = wxPoint(end.x + RADIUS2, end.y + RADIUS2)
        end = wxPoint(sta.x + 3 * dim, sta.y)
        add_line(sta, end)

    sta = wxPoint(tr.x + rad1, tr.y + rad1)
    sw = switches[72].GetPosition()
    end = wxPoint(tr.x + rad1, sw.y + dim / 2 + brd - RADIUS2)
    add_line(sta, end)
    add_line_arc(end, centerpt(end, 3, RADIUS2), reverse=False, angle=-90)
    if pcb_type() != "pcb":
        sta = wxPoint(end.x - RADIUS2, end.y + RADIUS2)
        end = wxPoint(sta.x - 4 * dim, sta.y)
        add_line(sta, end)

    draw_border_tilted_keys()
    if pcb_type() == "pcb":
        draw_wrist_support()

    pcbnew.Refresh()


remove_drawings()
draw_border()
