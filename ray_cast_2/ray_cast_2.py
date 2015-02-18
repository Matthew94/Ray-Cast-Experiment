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
        map.append([2] + [0] * 62 + [3])
    map.append([1] * 64)
       
    return map

def get_distance_to_plane(fov, screen_width):
    """Works out the distance from the player to the plane."""
    fov_radians = radians(fov / 2)
    half_screen_width = screen_width / 2
    return half_screen_width / tan(fov_radians)

def get_horiz_intersect(player_coord, ray_angle, cell_size, map):
    # Unpacking the co-ordinate tuple
    player_x, player_y = player_coord

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find the unit y coordinate
    # of the first grid hit
    if ray_angle <= 180:
        a_y = trunc(player_y / cell_size) * cell_size - 1
    else:
        a_y = trunc(player_y / cell_size) * cell_size + cell_size
    
    # Find the unit x coordinate
    # of the first grid hit
    a_x = player_x + (player_y - a_y) / tan(radians(ray_angle))

    # Getting grid coordinates
    # of a_y and a_x
    a_y_grid = get_grid_coord(a_y)
    a_x_grid = get_grid_coord(a_x)

    # Checking if our first intersection is a wall.
    if map[a_x_grid][a_y_grid] > 0:
        return (a_x_grid, a_y_grid)

    # Finding the size of the triangle
    # that we keep adding for each stage
    y_a = -cell_size if ray_angle <= 180 else cell_size
    x_a = 64 / tan(radians(ray_angle))

    # Setting up the variables for the loop
    x = a_x
    y = a_y

    # Keep adding on the triangle
    # until we find a hit
    while 1:
        x = x + x_a
        y = y + y_a

        x_grid = get_grid_coord(x)
        y_grid = get_grid_coord(y)

        if map[x_grid][y_grid] > 0:
            return (x_grid, y_grid)

def get_vert_intersect(player_coord, ray_angle, cell_size, map):
    # Unpacking the co-ordinate tuple
    player_x, player_y = player_coord

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find Bx
    if ray_angle < 90 or ray_angle > 270:
        b_x = trunc(player_x / cell_size) * cell_size + cell_size
    else:
        b_x = trunc(player_x / cell_size) * cell_size - 1

    b_y = player_y + (player_x - b_x) * tan(radians(ray_angle))

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
        
        if map[a_x_grid][a_y_grid] > 0:
            return (a_x_grid, a_y_grid)
    
        x_old = x_new
        y_old = y_new

        # Changed to -y_a, seems to work now
        x_new = x_old + x_a
        y_new = y_old - y_a

def get_distance_to_wall(player_coord, point_coord, player_angle, ray_angle):
    player_x, player_y = player_coord
    point_x, point_y = point_coord

    distance = sqrt(((player_x - point_x) ** 2) + 
                    ((player_y - point_y) ** 2))

    angle = player_angle - ray_angle

    get_undistorted_distance = lambda dist, angle : dist * cos(radians(angle))
  
    return get_undistorted_distance(distance, angle)

def get_slice_height(cell_size, plane_dist, wall_dist):
    return (cell_size / wall_dist) * plane_dist

def handle_input(player_angle, player_coord, cell_size, world_length):
    for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    new_x = player_coord[0] - 20
                    if new_x < 0:
                        new_x = cell_size
                    player_coord = (new_x, player_coord[1])
                elif event.key == pygame.K_DOWN:
                    new_x = player_coord[0] + 20
                    if new_x < 0:
                        new_x = world_length - cell_size
                    player_coord = (new_x, player_coord[1])
                elif event.key == pygame.K_RIGHT:
                    player_angle -= 15
                elif event.key == pygame.K_LEFT:
                    player_angle += 15
    if player_angle <= 0:
            player_angle = 360 + player_angle
    if player_angle >= 360:
            player_angle = 0 + player_angle - 360
    if player_angle == 0:
        player_angle += 1
    return player_angle, player_coord

def main():
    map = create_map()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()

    fov = 60.0

    # Setting our start location (Each cell is 64 units)
    player_coord = (96, 224)

    # 0 east, 90 north etc
    player_angle = 270

    cell_size = 64

    # Working out the distance from our camera to the visual plane
    plane_dist = get_distance_to_plane(fov, screen.get_width())

    # Getting the angle of a ray (column)
    column_angle = fov / float(screen.get_width())

    get_horiz = partial(get_horiz_intersect, 
                          map = map, cell_size = cell_size)

    get_vert = partial(get_vert_intersect,
                         map = map, cell_size = cell_size)

    get_slice_h = partial(get_slice_height, cell_size = cell_size)      
                        
    get_line_start = lambda height, screen_h : (screen_h / 2) - (height / 2)
    get_line_start = partial(get_line_start, screen_h = screen.get_height())
    
    get_line_end = lambda height, screen_h : (screen_h / 2) + (height / 2)
    get_line_end = partial(get_line_end, screen_h = screen.get_height())

    colours = {1 : (0xFF, 0x00, 0x00),
               2 : (0x00, 0xFF, 0x00),
               3 : (0x00, 0x00, 0xFF)}

    while 1:
        clock.tick(20)

        background = pygame.Surface(screen.get_size())
        background.fill((0x00, 0x00, 0x00))

        for ray in range(screen.get_width()):
            hit = None
            ray_angle = (player_angle + (fov / 2)) - (column_angle * ray)

            try:
                hit = get_horiz(player_coord, ray_angle)
            except IndexError:
                hit = get_vert(player_coord, ray_angle)

            dist = get_distance_to_wall(
                player_coord, hit, player_angle, ray_angle)

            slice_height = get_slice_h(plane_dist = plane_dist, 
                                       wall_dist = dist)

            start_line = (ray, get_line_start(slice_height))
            end_line = (ray, get_line_end(slice_height))
            
            colour = colours[map[hit[0]][hit[1]]]

            pygame.draw.line(
                background, colour, end_line, start_line)

        # Rendering the screen
        screen.blit(background, (0, 0))
        pygame.display.flip()

        player_angle, player_coord = handle_input(
            player_angle, player_coord, cell_size, len(map))

        print("Angle : {0} Co-ordinate: {1}".format(
            player_angle, (player_coord[0] / cell_size,
                           player_coord[1] / cell_size)))

if __name__ == "__main__":
    main()
