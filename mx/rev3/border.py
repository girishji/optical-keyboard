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

import itertools
import math
import pcbnew
from pcbnew import VECTOR2I, wxPoint, wxPointMM

dim = 19.00
COUNT = 72
board =pcbnew.GetBoard()

switches = [board.FindFootprintByReference('S' + str(num)) for num in range(COUNT + 1)]

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

# Resources:
# https://www.nagwa.com/en/explainers/606170705790/
# https://www.nagwa.com/en/explainers/578165351487/
# Learn about unit vectors, expressing vector A in terms of B and C, intersection point,
# dot product, cross product, etc.
# https://www.nagwa.com/en/explainers/762143183130/
# A vector is an object that has a magnitude and a direction.
# A Vector is expressed as (x, y) in terms of unit vectors along x, y.
# Directed line segments are written as ((x1, y1), (x2, y2)).

# Based on:
# https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
def intersect(P, A, Q, B):
    """Return intersection point of two directed line segments."""
    R, S = (A - P, B - Q)
    rs = R.Cross(S)
    assert rs != 0, 'Lines maybe parallel or one of the points is the intersection'
    t = (Q - P).Cross(S) / rs
    return P + R.Resize(int(R.EuclideanNorm() * t))


def arc(A, B, C, D, radius):
    """Return begin, mid, and end points of arc."""
    I = intersect(A, B, C, D)
    AB, CD = (B - A, D - C)
    iangle = math.acos(AB.Dot(CD) / (AB.EuclideanNorm() * CD.EuclideanNorm())) # intersection angle
    norm_EabI = int(radius / math.tan(iangle / 2)) # length of segment from intersection to end pt
    BEab = AB.Resize((I - A).EuclideanNorm() - AB.EuclideanNorm() - norm_EabI) # AI = I - A
    Eab = B + BEab
    BEcd = CD.Resize((I - C).EuclideanNorm() - CD.EuclideanNorm() - norm_EabI)
    Ecd = D + BEcd
    M = (Eab + Ecd) / 2
    MI = I - M
    norm_OI = math.sqrt(norm_EabI ** 2 + radius ** 2) # O is the center of rounding circle
    MarcI = MI.Resize(int(norm_OI - radius))
    Marc = I - MarcI
    return (Eab, Marc, Ecd)


def corner_arc(AB, CD, radius):
    """Draw rounded arc between directed line segments AB and CD and extend lines."""
    A, B, C, D = *AB, *CD
    Eab, Marc, Ecd = arc(A, B, C, D, radius)
    draw_arc(Eab, Marc, Ecd)
    draw_line(B, Eab)
    draw_line(C, Ecd)


def rotate(V, theta):
    """Rotate a vector by angle theta."""
    sin, cos = (math.sin(math.radians(theta)), math.cos(math.radians(theta)))
    return VECTOR2I(int(cos * V.x - sin * V.y), int(sin * V.x + cos * V.y))


def draw_border():
    """Draw border."""

    mil = lambda x: int(x * 1e6)
    d  =  mil(dim / 2)
    radius, radius2 = mil(8), mil(2)
    vlen = mil(0.1) # length of vector used for starting point
    wrist = {'xoffset': mil(64), 'yoffset': mil(27), 'width': mil(88), 'height': mil(65)}

    # Create directed line segment from vector X
    left = lambda X, angle=0: (X, X + rotate(VECTOR2I(-vlen, 0), angle))
    right = lambda X, angle=0: (X, X + rotate(VECTOR2I(vlen, 0), angle))
    up = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, -vlen), angle))
    down = lambda X, angle=0: (X, X + rotate(VECTOR2I(0, vlen), angle))

    # Left bottom portion
    L = R = switches[65].GetPosition() + VECTOR2I(0, d + mil(1))
    angle = -switches[64].GetOrientationDegrees()
    M = switches[64].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle)
    corner_arc(left(L), right(M, angle), radius2)
    L = M
    M = switches[64].GetPosition() + rotate(VECTOR2I(-int(d * 1.25) - mil(1), 0), angle)
    corner_arc(left(L, angle), down(M, angle), radius2)
    L = VECTOR2I(M)
    M += rotate(VECTOR2I(radius2 + vlen, -d - mil(1)), angle)
    corner_arc(up(L, angle), left(M, angle), radius2)
    L = M
    angle2 = -switches[63].GetOrientationDegrees()
    M = switches[63].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle2)
    corner_arc(right(L, angle), right(M, angle2), radius2)
    L, angle = (M, angle2)
    angle2 = -switches[62].GetOrientationDegrees()
    M = switches[62].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle2)
    corner_arc(left(L, angle), right(M, angle2), radius2)

    # Right bottom portion
    angle = -switches[66].GetOrientationDegrees()
    S = switches[66].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle)
    corner_arc(right(R), left(S, angle), radius2)
    R = S
    S = switches[66].GetPosition() + rotate(VECTOR2I(int(d * 1.25) + mil(1), 0), angle)
    corner_arc(right(R, angle), down(S, angle), radius2)
    R = VECTOR2I(S)
    S += rotate(VECTOR2I(-radius2 - vlen, -d - mil(1)), angle)
    corner_arc(up(R, angle), right(S, angle), radius2)
    R = S
    angle2 = -switches[67].GetOrientationDegrees()
    S = switches[67].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle2)
    corner_arc(left(R, angle), left(S, angle2), radius2)
    R, angle = (S, angle2)
    angle2 = -switches[68].GetOrientationDegrees()
    S = switches[68].GetPosition() + rotate(VECTOR2I(0, d + mil(1)), angle2)
    corner_arc(right(R, angle), left(S, angle2), radius2)

    # Right wrist area
    R, angle = (S, angle2)
    S = switches[65].GetPosition() + VECTOR2I(wrist['xoffset'] + 2 * (radius + vlen),
                                              int(wrist['yoffset'] / 2) + d)
    corner_arc(right(R, angle), up(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(-radius - vlen, int(wrist['yoffset'] / 2 + mil(1)))
    corner_arc(down(R), right(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(-radius - vlen, wrist['height'] - vlen - radius)
    corner_arc(left(R), up(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(radius + vlen, radius + vlen)
    corner_arc(down(R), left(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(wrist['width'] - radius - vlen, -radius - vlen)
    corner_arc(right(R), down(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(-radius - vlen, -wrist['height'] + radius + vlen)
    corner_arc(up(R), right(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(-radius - vlen, -radius - vlen)
    corner_arc(left(R), down(S), radius)
    R = VECTOR2I(S)
    S += VECTOR2I(radius + vlen, -wrist['yoffset'] + radius)
    corner_arc(up(R), left(S), radius)
    R = S
    S = switches[15].GetPosition() + VECTOR2I(d + mil(1), 0)
    corner_arc(right(R), down(S), radius)
    R = S
    S = switches[15].GetPosition() + VECTOR2I(0, -d - mil(3))
    corner_arc(up(R), right(S), mil(4))

    # Left wrist area
    L, angle = (M, -switches[62].GetOrientationDegrees())
    M = switches[65].GetPosition() + VECTOR2I(-wrist['xoffset'] - 2 * (radius + vlen),
                                              int(wrist['yoffset'] / 2) + d)
    corner_arc(left(L, angle), up(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(radius + vlen, int(wrist['yoffset'] / 2 + mil(1)))
    corner_arc(down(L), left(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(radius + vlen, wrist['height'] - vlen - radius)
    corner_arc(right(L), up(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(-radius - vlen, radius + vlen)
    corner_arc(down(L), right(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(-wrist['width'] + radius + vlen, -radius - vlen)
    corner_arc(left(L), down(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(radius + vlen, -wrist['height'] + radius + 2 * vlen)
    corner_arc(up(L), left(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(radius + vlen, -radius - vlen)
    corner_arc(right(L), down(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(-radius - vlen, -wrist['yoffset'] + radius)
    corner_arc(up(L), right(M), radius)
    L = VECTOR2I(M)
    M += VECTOR2I(-radius - vlen, -radius - vlen)
    corner_arc(left(L), down(M), radius)
    L = M
    M = switches[1].GetPosition() + VECTOR2I(0, -d - mil(3))
    corner_arc(up(L), left(M), radius)
    draw_line(M, S)




    # A = switches[1].GetPosition() + VECTOR2I(0, -d - mil(3))
    # B = switches[45].GetPosition() + VECTOR2I(-d - mil(14.25), 0)
    # corner_arc(left(A), up(B), radius)

    # A = VECTOR2I(B)
    # B = VECTOR2I(B.x + radius + vlen, switches[72].GetPosition().y + d + nextpt + mil(1))
    # corner_arc(down(A), left(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(radius + vlen, radius + nextpt)
    # corner_arc(right(A), up(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(-radius - vlen, wrist['yoffset'] - radius)
    # corner_arc(down(A), right(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(-radius - vlen, radius + nextpt)
    # corner_arc(left(A), up(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(radius + vlen, wrist['height'] - radius - nextpt)
    # corner_arc(down(A), left(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(wrist['width'] - radius - vlen, -radius - nextpt)
    # corner_arc(right(A), down(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(-radius - vlen, -wrist['height'] + radius + nextpt)
    # corner_arc(up(A), right(B), radius)

    # A = VECTOR2I(B)
    # B += VECTOR2I(-radius - vlen, -radius - nextpt)
    # corner_arc(left(A), down(B), radius)

    # A = VECTOR2I(B)
    # ctr, angle = (switches[62].GetPosition(), switches[62].GetOrientationDegrees())
    # C, D = (VECTOR2I(0, d + mil(1)), VECTOR2I(-vlen, d + mil(1)))
    # C, D = (ctr + rotate(C, -angle), ctr + rotate(D, -angle))
    # corner_arc(up(A), (C, D), radius)

    # DC = C - D
    # A, B = (C, C + DC)
    # ctr, angle = (switches[63].GetPosition(), switches[63].GetOrientationDegrees())
    # C, D = (VECTOR2I(0, d + mil(1)), VECTOR2I(-vlen, d + mil(1)))
    # C, D = (ctr + rotate(C, -angle), ctr + rotate(D, -angle))
    # corner_arc((A, B), (C, D), radius)


def remove_border():
    board = pcbnew.GetBoard()
    for t in board.GetDrawings():
        if t.GetLayer() == pcbnew.User_2:
            board.Delete(t)




remove_border()
draw_border()
# place holes

pcbnew.Refresh()
