import cv2
import math


def load_image(name):
    image = cv2.imread(name)
    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return image


def cvt_to_bin(image):
    ret, threshold_image = cv2.threshold(image, 127, 1, 0)
    return threshold_image


def get_cells(first_cell, x_offset, y_offset):

    cells = [[[[-1, -1], [-1, -1]]for j in range(3)] for i in range(3)]
    for x in range(3):
        for y in range(3):
            cell_x0 = first_cell[0][0] + x * x_offset
            cell_y0 = first_cell[0][1] + y * y_offset

            cell_x1 = first_cell[1][0] + x * x_offset
            cell_y1 = first_cell[1][1] + y * y_offset

            cells[x][y] = [[cell_x0, cell_y0], [cell_x1, cell_y1]]
    return cells


def find_cells(bin_map, image_shape):

    got_borders = False
    cell_height = 0
    left_borders = [[-1, -1], [-1, -1]]
    border_thickness = 0

    for x in range(0, image_shape[1]):
        if got_borders:
            break
        for y in range(0, image_shape[0]):
            if (not got_borders) and bin_map[y][x] == [0, 0, 0]:
                left_borders[0] = [x, y]
                border_thickness += 1
                while bin_map[y][x] == [0, 0, 0]:
                    y += 1
                    border_thickness += 1
                while bin_map[y][x] != [0, 0, 0]:
                    y += 1
                    cell_height += 1
                got_borders = True
                break

    cell_width = cell_height

    first_cell = [[-1,-1], [-1, left_borders[0][1] - 1]]

    x = left_borders[0][0] + cell_width
    while bin_map[first_cell[1][1]][x] != [0, 0, 0]:
        x += 1
    first_cell[1][0] = x - 1
    first_cell[0][0] = x - cell_width
    first_cell[0][1] = first_cell[1][1] - cell_height + 1

    return get_cells(first_cell,
                     cell_width + border_thickness,
                     cell_height + border_thickness)


def rect_middle(rect):
    coordinates = [-1, -1]
    coordinates[0] = (rect[0][0] + rect[1][0]) // 2
    coordinates[1] = (rect[0][1] + rect[1][1]) // 2

    return coordinates


def cell_is_empty(cell, mid_y, bin_map):
    for x in range(cell[0][0] + 1, cell[1][0]):
        if bin_map[mid_y][x] == [0, 0, 0]:
            return False
    return True


def get_figures(cells, bin_map):

    figures = [[-math.inf for j in range(3)] for i in range(3)]

    for x in range(3):
        for y in range(3):
            mid = rect_middle(cells[x][y])
            if bin_map[mid[1]][mid[0]] == [0, 0, 0]:
                figures[x][y] = 1
            elif cell_is_empty(cells[x][y], mid[1], bin_map):
                figures[x][y] = -math.inf
            else:
                figures[x][y] = 0

    return figures


def get_fig_line(figures):
    for x in range(3):
        x_sum = 0
        for y in range(3):
            x_sum += figures[x][y]
        if x_sum == 0 or x_sum == 3:
            return [x, -1]
    for y in range(3):
        y_sum = 0
        for x in range(3):
            y_sum += figures[x][y]
        if y_sum == 0 or y_sum == 3:
            return [-1, y]
    diag_sum = 0
    main_diag = [(i, i) for i in range(3)]
    for x, y in main_diag:
        diag_sum += figures[x][y]
    if diag_sum == 0 or diag_sum == 1:
        return [2]

    diag_sum = 0
    sub_diag = [(i, 2-i) for i in range(3)]
    for x, y in sub_diag:
        diag_sum += figures[x][y]
    if diag_sum == 0 or diag_sum == 1:
        return [-2]
    return []


def get_points(fig_line, cells):
    if not fig_line:
        return
    if fig_line == [2]:
        return [cells[0][0][0], cells[2][2][1]]
    if fig_line == [-2]:
        return [[cells[0][2][0][0], cells[0][2][1][1]], [cells[2][0][1][0], cells[2][0][0][1]]]
    if fig_line[0] == -1:
        mid_y = rect_middle(cells[0][fig_line[0]])[1]
        return [[cells[0][fig_line[0]][0][0], mid_y], [cells[2][fig_line[0]][1][0], mid_y]]
    if fig_line[1] == -1:
        mid_x = rect_middle(cells[fig_line[1]][0])[0]
        return [[mid_x, cells[fig_line[1]][0][0][1]], [mid_x, cells[fig_line[1]][2][1][1]]]


def draw_line(image, line):
    cv2.line(image, tuple(line[0]), tuple(line[1]), (0, 0, 0), 5)


def save_img(image):
    cv2.imwrite("result.png", image)