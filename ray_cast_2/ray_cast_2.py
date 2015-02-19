"""My attempt at a basic raycasting program.

Taken from: http://www.permadi.com/tutorial/raycast/
"""

from __future__ import print_function
from math import cos, sin, tan, fabs, radians, trunc, sqrt
from functools import partial

import pygame
pygame.init()

def create_map():
    map = []

    map.append([1] * 64)
    for i in range(62):
        map.append([2] + ([0] * 62) + [3])
    map.append([1] * 64)

    #map = [
    #[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #[1, 0, 0, 2, 2, 2, 0, 0, 0, 1],
    #[1, 0, 0, 2, 0, 2, 0, 0, 0, 1],
    #[1, 0, 0, 2, 2, 2, 0, 0, 0, 1],
    #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #[1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    #[1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    #]

       
    return map

def get_distance_to_plane(fov, screen_width):
    """Works out the distance from the p to the plane."""
    fov_radians = radians(fov / 2)
    half_screen_width = screen_width / 2
    return half_screen_width / tan(fov_radians)

def get_horiz_intersect(p_coord, ray_angle, cell_size, map):
    # Unpacking the co-ordinate tuple
    p_x, p_y = p_coord

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find the unit y coordinate of the first grid hit
    if ray_angle <= 180:
        a_y = trunc(p_y / cell_size) * cell_size - 1
    else:
        a_y = trunc(p_y / cell_size) * cell_size + cell_size
    
    # Find the unit x coordinate of the first grid hit
    a_x = p_x + (p_y - a_y) / tan(radians(ray_angle))

    # Getting grid coordinates of a_y and a_x
    a_y_grid = get_grid_coord(a_y)
    a_x_grid = get_grid_coord(a_x)

    # Checking if our first intersection is a wall.
    if a_x_grid >= 0 and a_y_grid >= 0:
        if map[a_x_grid][a_y_grid] > 0:
            return (a_x_grid, a_y_grid)
    else:
        return None

    # Finding the size of the triangle that we keep adding for each stage
    y_a = -cell_size if ray_angle <= 180 or ray_angle == 360 else cell_size
    x_a = 64 / tan(radians(ray_angle))

    # Setting up the variables for the loop
    x, y = a_x, a_y

    # Keep adding on the triangle
    # until we find a hit
    while 1:
        x = x + x_a
        y = y + y_a

        x_grid = get_grid_coord(x)
        y_grid = get_grid_coord(y)

        if x_grid >= 0 and y_grid >= 0:
            if map[x_grid][y_grid] > 0:
                return (x_grid, y_grid)
        else:
            return None
def get_vert_intersect(p_coord, ray_angle, cell_size, map):
    # Unpacking the co-ordinate tuple
    p_x, p_y = p_coord

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find Bx
    if ray_angle < 90 or ray_angle > 270:
        b_x = trunc(p_x / cell_size) * cell_size + cell_size
    else:
        b_x = trunc(p_x / cell_size) * cell_size - 1

    b_y = p_y + (p_x - b_x) * tan(radians(ray_angle))

    # Find Xa and Ya
    if ray_angle < 90 or ray_angle > 270:
        x_a = cell_size
    else:
        x_a = -cell_size

    y_a = cell_size * tan(radians(ray_angle))

    x_new = b_x
    y_new = b_y

    while 1:
        a_x_grid = get_grid_coord(x_new)
        a_y_grid = get_grid_coord(y_new)
        
        if a_x_grid >= 0 and a_y_grid >= 0:
            if map[a_x_grid][a_y_grid] > 0:
                return (a_x_grid, a_y_grid)
        else:
            return None
    
        x_old = x_new
        y_old = y_new

        # Changed to -y_a, seems to work now
        x_new = x_old + x_a
        y_new = y_old - y_a

def get_distance_to_wall(p_coord, wall_coord, ray, fov, column_angle):
    p_x, p_y = p_coord
    wall_x, wall_y = wall_coord

    distance = sqrt(((p_x - wall_x) ** 2) + ((p_y - wall_y) ** 2))

    beta = (-0.5 * fov) + (ray * column_angle)

    get_undistorted_distance = lambda dist, angle : dist * cos(radians(angle))
  
    return get_undistorted_distance(distance, beta)

def handle_input(p_angle, p_coord, cell_size, world_length):
    for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    pass
                elif event.key == pygame.K_DOWN:
                    pass
                elif event.key == pygame.K_RIGHT:
                    p_angle -= 15
                elif event.key == pygame.K_LEFT:
                    p_angle += 15
                elif event.key == pygame.K_w:
                    new_y= p_coord[1] - cell_size
                    if new_y <= 0:
                        new_y = cell_size
                    p_coord = (p_coord[0], new_y)
                elif event.key == pygame.K_s:
                    new_y= p_coord[1] + cell_size
                    if new_y >= world_length * cell_size:
                        new_y = world_length - cell_size
                    p_coord = (p_coord[0], new_y)
                elif event.key == pygame.K_a:
                    new_x = p_coord[0] - cell_size
                    if new_x <= 0:
                        new_x = cell_size
                    p_coord = (new_x, p_coord[1])
                elif event.key == pygame.K_d:
                    new_x = p_coord[0] + cell_size
                    if new_x >= world_length * cell_size:
                        new_x = world_length - cell_size
                    p_coord = (new_x, p_coord[1])

    p_angle = fix_angle(p_angle)
    return p_angle, p_coord

def fix_angle(p_angle):
    if p_angle <= 0:
            p_angle = 360 + p_angle
    if p_angle >= 360:
            p_angle = 0 + p_angle - 360
    if p_angle == 0:
        p_angle = 360.0
    return p_angle

def modify_functions(map, cell_size, screen):
    get_horiz = partial(get_horiz_intersect, map = map, cell_size = cell_size)
    get_vert = partial(get_vert_intersect, map = map, cell_size = cell_size)

    get_slice_height = lambda plane_dist, wall_dist, cell_size : \
        (cell_size / wall_dist) * plane_dist
    get_slice_height = partial(get_slice_height, cell_size = cell_size)      
                        
    get_line_start = lambda height, screen_h : (screen_h / 2) - (height / 2)
    get_line_start = partial(get_line_start, screen_h = screen.get_height())
    
    get_line_end = lambda height, screen_h : (screen_h / 2) + (height / 2)
    get_line_end = partial(get_line_end, screen_h = screen.get_height())

    return get_horiz, get_vert, get_slice_height, get_line_start, get_line_end

def main():
    map = create_map()
    screen = pygame.display.set_mode((320, 200))
    clock = pygame.time.Clock()

    fov = 90.0

    # Setting our start location (Each cell is 64 units)
    p_coord = (3 * 64, 2 * 64)

    # 0 east, 90 north etc
    p_angle = 300

    cell_size = 64

    # Working out the distance from our camera to the visual plane
    plane_dist = get_distance_to_plane(fov, screen.get_width())

    # Getting the angle of a ray (column)
    column_angle = fov / screen.get_width()

    get_horiz, get_vert, get_slice_height, get_line_start, get_line_end = (
        modify_functions(map, cell_size, screen))

    colours = {1 : (0xFF, 0x00, 0x00),  # Red
               2 : (0x00, 0xFF, 0x00),  # Green
               3 : (0x00, 0x00, 0xFF)}  # Blue

    while 1:
        clock.tick(20)

        background = pygame.Surface(screen.get_size())
        background.fill((0x00, 0x00, 0x00))

        for ray in range(screen.get_width()):
            x_hit = None
            y_hit = None

            x_dist = None
            y_dist = None

            ray_angle = (p_angle + (fov / 2)) - (column_angle * ray)
            
            ray_angle = fix_angle(ray_angle)
            try:
                x_hit = get_horiz(p_coord, ray_angle)
            except IndexError:
                pass
            else:
                if x_hit:
                    x_dist = get_distance_to_wall(
                        p_coord, x_hit, ray, fov, column_angle)

            try:
                y_hit = get_vert(p_coord, ray_angle)
            except IndexError:
                pass
            else:
                if y_hit:
                    y_dist = get_distance_to_wall(
                        p_coord, y_hit, ray, fov, column_angle)

            if y_dist and not x_dist:
                dist = y_dist
                hit = y_hit
            elif x_dist and not y_dist:
                dist = x_dist
                hit = x_hit
            else:
                if x_dist <= y_dist:
                    dist = x_dist
                    hit = x_hit
                else:
                    dist = y_dist
                    hit = y_hit

            slice_height = get_slice_height(plane_dist, dist)

            start_line = (ray, get_line_start(slice_height))
            end_line = (ray, get_line_end(slice_height))
            
            hit_x, hit_y = hit
            wall_index = map[hit_x][hit_y]
            colour = colours[wall_index]

            pygame.draw.line(background, colour, end_line, start_line)

        # Rendering the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()

        p_angle, p_coord = handle_input(p_angle, p_coord, cell_size, len(map))

        print("Angle : {0} Co-ordinate: {1}".format(
            p_angle, (p_coord[0] / cell_size, p_coord[1] / cell_size)))

if __name__ == "__main__":
    main()
