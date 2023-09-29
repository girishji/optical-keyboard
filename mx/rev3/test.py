from collections import namedtuple
import math
from sys import stderr

Vector = namedtuple('Vector', ('x', 'y'))

dot = lambda v, w: v.x * w.x + v.y * w.y
cross = lambda v, w: v.x * w.y - v.y * w.x
plus = lambda v, w: Vector(v.x + w.x, v.y + w.y)
minus = lambda v, w: Vector(v.x - w.x, v.y - w.y)
mult = lambda v, n: Vector(v.x * n, v.y * n)
div = lambda v, n: Vector(v.x / n, v.y / n)
midpt = lambda v, w: div(plus(v, w), 2)
magnitude = lambda v: math.sqrt(v.x ** 2 + v.y ** 2)

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

def rounded(A, B, C, D, radius):
    '''
    >>> print(rounded((0, 1), (1,1), (3,3), (3,2), 1))
    None
    >>> print(rounded((-5, 0), (-5, 1), (-1, 6), (-2, 6), 1))
    None
    '''
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
    print(Eab, Ecd, file=stderr)
    M = midpt(Eab, Ecd)
    MI = minus(I, M)
    magnitudeOI = math.sqrt(magnitudeEabI ** 2 + radius ** 2) # O is the center of rounding circle
    OI = mult(MI, magnitudeOI / magnitude(MI))
    OMarc = mult(OI, radius / magnitude(OI))
    MarcI = minus(OI, OMarc)
    Marc = minus(I, MarcI)
    print('mid', M, 'inter', I, 'OI', OI, 'OMarc', OMarc, file=stderr)
    return (Eab, Ecd, Marc)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
