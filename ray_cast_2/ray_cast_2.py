"""My attempt at a basic raycasting program.

Taken from: http://www.permadi.com/tutorial/raycast/
"""

from __future__ import print_function
from math import cos, sin, tan, fabs, radians, trunc, sqrt
from functools import partial
import pygame
pygame.init()

def create_world_map():
    world_map = []

    world_map.append([1] * 64)
    for i in range(62):
        world_map.append([2] + [0] * 62 + [3])
    world_map.append([1] * 64)
       
    return world_map

def get_distance_to_plane(fov, screen_width):
    """Works out the distance from the player to the plane."""
    fov_radians = radians(fov / 2)
    half_screen_width = screen_width / 2
    return half_screen_width / tan(fov_radians)

def check_horizontal_intersections(
        world_map, player_coordinate, player_angle, cell_size):
    # Unpacking the co-ordinate tuple
    player_x, player_y = player_coordinate

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find the unit y coordinate
    # of the first grid hit
    if player_angle <= 180:
        a_y = trunc(player_y / cell_size) * cell_size - 1
    else:
        a_y = trunc(player_y / cell_size) * cell_size + cell_size
    
    # Find the unit x coordinate
    # of the first grid hit
    a_x = player_x + (player_y - a_y) / tan(radians(player_angle))

    # Getting grid coordinates
    # of a_y and a_x
    a_y_grid = get_grid_coord(a_y)
    a_x_grid = get_grid_coord(a_x)

    # Checking if our first intersection is a wall.
    if world_map[a_x_grid][a_y_grid] > 0:
        return (a_x_grid, a_y_grid)

    # Finding the size of the triangle
    # that we keep adding for each stage
    y_a = -cell_size if player_angle <= 180 else cell_size
    x_a = 64 / tan(radians(player_angle))

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

        if world_map[x_grid][y_grid] > 0:
            return (x_grid, y_grid)

def check_vertical_intersections(
        world_map, player_coordinate, player_angle, cell_size):
    # Unpacking the co-ordinate tuple
    player_x, player_y = player_coordinate

    # Function for getting the grid coordinate
    # of a unit coordinate
    get_grid_coord = lambda coord, cell_size : trunc(coord / cell_size) 
    get_grid_coord = partial(get_grid_coord, cell_size = cell_size)

    # Find Bx
    if player_angle < 90 or player_angle > 270:
        b_x = trunc(player_x / cell_size) * cell_size + cell_size
    else:
        b_x = trunc(player_x / cell_size) * cell_size - 1

    b_y = player_y + (player_x - b_x) * tan(radians(player_angle))

    # Find Xa and Ya
    if player_angle < 90 or player_angle > 270:
        x_a = cell_size
    else:
        x_a = -cell_size

    y_a = cell_size * tan(radians(player_angle))

    x_new = b_x
    y_new = b_y

    while 1:
        a_x_grid = get_grid_coord(x_new)
        a_y_grid = get_grid_coord(y_new)
        
        if world_map[a_x_grid][a_y_grid] > 0:
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

def main():
    # 10x10 world map with a column in the middle
    world_map = create_world_map()
    
    # Setting a 320x200 screen
    screen = pygame.display.set_mode((640, 480))

    # Setting up our clock
    clock = pygame.time.Clock()

    # Setting our fov
    fov = 60.0

    # Setting our start location
    # Middle of (1, 2)
    # Each cell is 64 units
    # So 1 cell + 1/2 a cell = 96
    start = (96, 224)

    # Setting the camera angle
    # 0 == east, 90 north etc
    player_angle = 270

    # Size of each side of each cell
    cell_size = 64

    # Working out the distance from our camera to the wall
    plane_dist = get_distance_to_plane(fov, screen.get_width())

    # Getting the angle of a ray (column)
    column_angle = fov / float(screen.get_width())

    # Will be updated in the loop
    player_coord = start

    # To ease typing
    check_horiz = partial(check_horizontal_intersections,
                          world_map = world_map,
                          cell_size = cell_size)

    check_vert = partial(check_vertical_intersections,
                         world_map = world_map,
                         cell_size = cell_size)

    get_slice_h = partial(get_slice_height, cell_size = cell_size)      
                        
    get_line_start = lambda height, screen_h : (screen_h / 2) - (height / 2)
    get_line_end = lambda height, screen_h : (screen_h / 2) + (height / 2)
    
    get_line_start = partial(get_line_start, screen_h = screen.get_height())
    get_line_end = partial(get_line_end, screen_h = screen.get_height())

    colours = {1 : (0xFF, 0x00, 0x00),
               2 : (0x00, 0xFF, 0x00),
               3 : (0x00, 0x00, 0xFF)}

    # The start of our game loop
    while True:
        # Recording a new loop
        clock.tick(20)

        # Setting up our background
        background = pygame.Surface(screen.get_size())
        background.fill((0x00, 0x00, 0x00))

        # Going over each column of pixels
        # To work out how to draw each line
        # After this, the screen is rendered
        for ray in range(screen.get_width()):
            ray_angle = (player_angle + (fov / 2)) - (column_angle * ray)

            try:
                hit = check_horiz(player_coordinate = player_coord, 
                                  player_angle = ray_angle)
            except IndexError:
                hit = check_vert(player_coordinate = player_coord, 
                                 player_angle = ray_angle)

            dist = get_distance_to_wall(
                player_coord, hit, player_angle, ray_angle)

            slice_height = get_slice_h(plane_dist = plane_dist, 
                                       wall_dist = dist)

            start_line = (ray, get_line_start(slice_height))
            end_line = (ray, get_line_end(slice_height))
            
            colour = colours[world_map[hit[0]][hit[1]]]

            pygame.draw.line(
                background, colour, end_line, start_line)
        screen.blit(background, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player_coord = (player_coord[0] - 20, player_coord[1])
                elif event.key == pygame.K_DOWN:
                   player_coord = (player_coord[0] + 20, player_coord[1])
                elif event.key == pygame.K_RIGHT:
                    player_angle -= 15
                elif event.key == pygame.K_LEFT:
                    player_angle += 15
            if player_angle <= 0:
                    player_angle = 360 + player_angle
            if player_angle >= 360:
                    player_angle = 0 + player_angle - 360
            if player_angle == 0:
                player_angle += 0.000001

if __name__ == "__main__":
    main()
