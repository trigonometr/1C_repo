import handler

image = handler.load_image("./image.png")
threshold_image = handler.cvt_to_bin(image)
bin_map = threshold_image.tolist()
cells = handler.find_cells(bin_map, threshold_image.shape)

figures = handler.get_figures(cells, bin_map)
figure_line = handler.get_fig_line(figures)
line = handler.get_points(figure_line, cells)

image_cp = image.copy()
handler.draw_line(image_cp, line)

handler.save_img(image_cp)
