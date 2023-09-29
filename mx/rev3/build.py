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

from collections import namedtuple
import itertools
import math
import pcbnew
from pcbnew import VECTOR2I, wxPoint, wxPointMM

dim = 19.00
COUNT = 72
board =pcbnew.GetBoard()

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]

def place_switches():

    place = lambda fp, offset: fp.SetPosition(VECTOR2I(wxPointMM(*offset)))
    orient = lambda fp, deg: fp.SetOrientationDegrees(deg)

    for i in range(1, COUNT + 1):
        orient(switches[i], 0)

    # row 1
    place(switches[1], (dim, 0))
    for i in range(2, 16):
        place(switches[i], (i * dim, 0))

    # row 2
    offs = dim + dim / 4
    place(switches[16], (offs, dim))
    for i in range(17, 29):
        place(switches[i], (offs + dim / 4 + (i - 16) * dim, dim))
    place(switches[29], (offs + dim / 4 + dim * 13 + dim / 4, dim))

    # row 3
    offs = (1 - 1 / 4) * dim
    place(switches[30], (offs - dim * 1 / 8, 2 * dim))
    for i in range(31, 44):
        place(switches[i], (offs + (i - 30) * dim, 2 * dim))
    # place(switches[44], (offs + (14 + 1 / 8) * dim, 2 * dim))
    place(switches[44], (offs + 14 * dim, 2 * dim))

    # row 4
    offs = dim * (-1 / 2)
    place(switches[45], (offs + dim, 3 * dim))
    offs += dim * (1 + 3 / 8)
    place(switches[46], (offs + dim, 3 * dim))
    offs += (3 / 8) * dim
    for i in range(47, 57):
        place(switches[i], (offs + (i - 45) * dim, 3 * dim))
    offs += dim * 12
    place(switches[57], (offs + 3 / 8 * dim, 3 * dim))
    # place(switches[57], (offs + 1 / 4 * dim, 3 * dim)) # 1.5u shift
    offs += dim * (1 + 3 / 4)
    # offs += dim * (1 + 3 / 4 - 1 / 4) # 1.5u shift
    place(switches[58], (offs, 3 * dim))

    # row 5
    row5shift = 0

    offs = (1 - 1 / 4) * dim - row5shift
    place(switches[59], (offs - dim / 8, 4 * dim))
    for i in range(60, 62):
        place(switches[i], (offs + (i - 59) * dim, 4 * dim))
    offs = (3 + 1 / 2) * dim
    place(switches[62], (offs + dim / 4 + 1, 4 * dim + 1))
    orient(switches[62], -7)

    offs += dim * (1 + 1 / 4 + 1 / 8)
    place(switches[63], (offs + 1.4, 4 * dim + 5.2))
    orient(switches[63], -16)
    offs += dim * (1 + 1 / 8)

    place(switches[64], (offs - 0.6, 4.5 * dim + 7))
    orient(switches[64], -28 + 90)

    offs += dim * 1.25
    place(switches[65], (offs, 4 * dim))

    # place(switches[66], (offs + dim + dim / 4 + 1.0, 4.5 * dim + 7))
    place(switches[66], (offs + dim + dim / 4 + 0.6, 4.5 * dim + 7))
    orient(switches[66], 28 + 90 + 180)
    offs += dim * 1.25
    place(switches[67], (offs + dim - 1.4, 4 * dim + 5.2))
    orient(switches[67], 16)
    place(switches[68], (offs + 2 * dim - 1, 4 * dim + 1))
    orient(switches[68], 7)
    # offs += (2 + 1 / 4) * dim
    offs += 2 * dim
    place(switches[69], (offs + dim, 4 * dim))

    for i in range(70, 73):
        place(switches[i], (offs + (i - 68) * dim, 4 * dim))


def transform(pt, around, theta):
    matrix = [
        [math.cos(math.radians(theta)), -math.sin(math.radians(theta))],
        [math.sin(math.radians(theta)), math.cos(math.radians(theta))],
    ]
    return wxPoint(
        around.x + pt.x * matrix[0][0] + pt.y * matrix[0][1],
        around.y + pt.x * matrix[1][0] + pt.y * matrix[1][1],
    )

def place_leds():
    leds = [board.FindFootprintByReference('D' + str(num)) for num in range(1, COUNT + 1)]
    offset = wxPointMM(0, -dim * 0.268)
    for led, sw in zip(leds, switches[1:]):
        deg = sw.GetOrientationDegrees()
        led.SetOrientationDegrees(deg)
        swpos = sw.GetPosition().getWxPoint()
        led.SetPosition(VECTOR2I(transform(offset, swpos, -deg)))

def place_ir_resistors():
    rIR = [board.FindFootprintByReference('Ri' + str(num)) for num in range(COUNT // 3 + 1)]
    selected = itertools.chain(range(3, 28, 3), [29], range(32, 45, 3), range(47, 57, 3), [58, 61, 64, 67, 70])
    for i, j in zip(range(1, COUNT // 3 + 1), selected):
        offset = wxPointMM(dim * 0.415, -2.3) if i < 5 else wxPointMM(dim * 0.43, 0)
        deg = switches[j].GetOrientationDegrees()
        rIR[i].SetOrientationDegrees(deg + 90)
        swpos = switches[j].GetPosition().getWxPoint()
        rIR[i].SetPosition(VECTOR2I(transform(offset, swpos, -deg)))

def place_bjts():
    cols = 15
    bjt = [board.FindFootprintByReference('Q' + str(num)) for num in range(1, cols + 1)]
    r1r = [board.FindFootprintByReference('R1_r' + str(num)) for num in range(1, cols + 1)]
    r2r = [board.FindFootprintByReference('R2_r' + str(num)) for num in range(1, cols + 1)]
    xoffset = -dim * .48
    yoffset = 2.8
    for bj, r1, r2, sw in zip(bjt, r1r, r2r, switches[1:]):
        bj.SetOrientationDegrees(-90)
        r1.SetOrientationDegrees(180)
        r2.SetOrientationDegrees(180)
        swpos = sw.GetPosition().getWxPoint()
        bj.SetPosition(VECTOR2I(transform(wxPointMM(xoffset, -1.3 + yoffset), swpos, 0)))
        r1.SetPosition(VECTOR2I(transform(wxPointMM(xoffset + .3, -4.1 + yoffset), swpos, 0)))
        r2.SetPosition(VECTOR2I(transform(wxPointMM(xoffset, 1.5 + yoffset), swpos, 0)))

def place_holes_wristpad():
    pos = [(-7.75, 120.025), (-7.75, 172.025), (67.25, 172.025), (67.25, 120.025),
           (208.25, 120.025), (208.25, 172.025), (283.25, 172.025), (283.25, 120.025)]
    for i in range(1, 9):
        fp = board.FindFootprintByReference('H' + str(i))
        fp.SetPosition(VECTOR2I(wxPointMM(*pos[i - 1])))

def place_mounting_holes():
    delta = 0.6
    border = 0
    board = pcbnew.GetBoard()

    def set_position(num, x, y):
        holes[num].SetPosition(VECTOR2I(wxPointMM(x, y)))

    pos = [
            (-dim * 0.5, -dim * 0.4 - border + delta),
            (-dim * 0.5, dim * 2.5),
            (-dim * 0.5, dim * 4.2 + border - delta),
            (dim * 2.5, -dim * 0.5 - border + delta),
            (dim * 6.5, -dim * 0.5 - border + delta),
            (dim * 10.5, -dim * 0.5 - border + delta),
            (dim * 14.5, -dim * 0.5 - border + delta),
            (dim * (2 - 1 / 8), dim * 1.5 - 2),
            (dim * 5, dim * 1.5 - delta),
            (dim * 9, dim * 1.5 - delta),
            (dim * 12, dim * 1.5 - delta),
            (dim * 7.25, dim * 2.5 - delta),
            (dim * 3.3, dim * 3.55 + delta),
            (dim * 11.75, dim * 3.436 + delta),
            (dim * 15.35, dim * 1.5 - border),
            (dim * 15.25, dim * 4.25 + border - 3 * delta),
            (dim * 5.45, dim * 4.6 + border),
            (dim * 8.9, dim * 4.4 + border),
            ]

    holes = (board.FindFootprintByReference("Hs" + str(num)) for num in range(1, len(pos) + 1))
    for i, hole in enumerate(holes):
        hole.SetPosition(VECTOR2I(wxPointMM(*pos[i])))

# def draw_line(start, end, layer=pcbnew.Edge_Cuts):
def draw_line(start, end, layer=pcbnew.User_2):
    board = pcbnew.GetBoard()
    ls = pcbnew.PCB_SHAPE(board)
    ls.SetShape(pcbnew.SHAPE_T_SEGMENT)
    ls.SetStart(start)
    ls.SetEnd(end)
    ls.SetLayer(layer)
    # ls.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
    board.Add(ls)

def draw_arc(start, mid, end, layer=pcbnew.User_2):
    board = pcbnew.GetBoard()
    arc = pcbnew.PCB_SHAPE(board)
    arc.SetShape(pcbnew.SHAPE_T_ARC)
    arc.SetArcGeometry(start, mid, end)
    arc.SetLayer(layer)
    board.Add(arc)

# def draw_arc(start, center, reverse=False, angle=-90, layer=pcbnew.Edge_Cuts):
#     board = pcbnew.GetBoard()
#     arc = pcbnew.PCB_SHAPE(board)
#     arc.SetShape(pcbnew.SHAPE_T_ARC)
#     arc.SetStart(start)
#     arc.SetCenter(center)
#     arc.SetArcAngleAndEnd(-angle * 10, reverse)
#     arc.SetLayer(layer)
#     # arc.SetWidth(int(0.12 * pcbnew.IU_PER_MM))
#     board.Add(arc)


# https://www.nagwa.com/en/explainers/606170705790/
# https://www.nagwa.com/en/explainers/578165351487/
# Learn about unit vectors, expressing vector A in terms of B and C, intersection point,
# dot product, cross product, etc.

# https://www.nagwa.com/en/explainers/762143183130/
# A vector is an object that has a magnitude and a direction.
#   Vectors expressed in terms of unit vectors x, y have (x, y),
#   and others are also called directed line segments ((x1, y1), (x2, y2))
Vector = namedtuple('Vector', ('x', 'y'))

dot = lambda V, W: V.x * W.x + V.y * W.y
cross = lambda V, W: V.x * W.y - V.y * W.x
plus = lambda V, W: Vector(V.x + W.x, V.y + W.y)
minus = lambda V, W: Vector(V.x - W.x, V.y - W.y)
mult = lambda V, n: Vector(V.x * n, V.y * n)
div = lambda V, n: Vector(V.x / n, V.y / n)
midpt = lambda V, W: div(plus(V, W), 2)
magnitude = lambda V: math.sqrt(V.x ** 2 + V.y ** 2)

# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
def intersect(P, A, Q, B):
    """Return intersection point of two directed line segments."""

    if not isinstance(P, Vector):
        P, A, Q, B = (Vector(*P), Vector(*A), Vector(*Q), Vector(*B))
    R = minus(A, P)
    S = minus(B, Q)
    rs = cross(R, S)
    t = cross(minus(Q, P), div(S, rs))
    u = cross(minus(Q, P), div(R, rs))
    return plus(P, mult(R, t))

def draw_rounded(A, B, C, D, radius):
    """Draw rounded arc between directed line segments AB and CD and extend lines."""

    def endpt(Y):
        """Return end point of XY continued line."""
        YI = minus(I, Y)
        ExyI = mult(YI, (magnitudeEabI / magnitude(YI)))
        return minus(I, ExyI)

    if not isinstance(A, Vector):
        A, B, C, D = (Vector(*A), Vector(*B), Vector(*C), Vector(*D))
    AB, CD = (minus(B, A), minus(D, C))
    iangle = math.acos(dot(AB, CD) / (magnitude(AB) * magnitude(CD))) # intersection angle
    magnitudeEabI = radius / math.tan(iangle / 2) # length of segment from intersection to end pt
    I = intersect(A, B, C, D)
    Eab = endpt(B)
    Ecd = endpt(D)
    M = midpt(Eab, Ecd)
    MI = minus(I, M)
    magnitudeOI = math.sqrt(magnitudeEabI ** 2 + radius ** 2) # O is the center of rounding circle
    OI = mult(MI, magnitudeOI / magnitude(MI))
    OMarc = mult(OI, radius / magnitude(OI))
    MarcI = minus(OI, OMarc)
    Marc = minus(I, MarcI)

    vec = lambda v: VECTOR2I(wxPointMM(v.x, v.y))
    draw_arc(vec(Eab), vec(Marc), vec(Ecd))


def draw_border():
    """Draw border."""

    left = lambda X: X + VECTOR2I(wxPoint(-1, 0))
    up = lambda X: X + VECTOR2I(wxPoint(0, -1))
    radius = 8 * 1e6

    A = switches[1].GetPosition() + VECTOR2I(wxPointMM(0, dim - 10))
    B = switches[16].GetPosition() + VECTOR2I(wxPointMM(dim - 20, 0))
    draw_rounded(A, left(A), B, up(B), radius)








place_switches()
place_leds()
place_ir_resistors()
place_bjts()
place_holes_wristpad()
place_mounting_holes()
draw_border()

pcbnew.Refresh()
