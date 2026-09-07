import math
from transform import Transform


def get_position_distances(
        p1: Transform,
        p2: Transform
) -> float:
    pos1 = p1.get_position()
    pos2 = p2.get_position()
    dx = pos1.x - pos2.x
    dy = pos1.y - pos2.y
    dz = pos1.z - pos2.z
    return math.sqrt(dx*dx + dy*dy + dz*dz)


def verify_distance_higher_than(
        p1: Transform,
        p2: Transform,
        distance: float
) -> bool:
    pos1 = p1.get_position()
    pos2 = p2.get_position()
    dx = pos1.x - pos2.x
    dy = pos1.y - pos2.y
    dz = pos1.z - pos2.z
    squared_dist = dx*dx + dy*dy + dz*dz
    return squared_dist > (distance * distance)
