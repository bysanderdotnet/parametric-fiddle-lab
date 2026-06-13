import cadquery as cq

length = 355
rib_height = 30
top_arch_height = 15

chinrest_x_offset = -40
chinrest_y_offset = -140
chinrest_width = 80
chinrest_length = 50
chinrest_height = 15

chinrest_base = cq.Workplane("XY").center(chinrest_x_offset, chinrest_y_offset).box(chinrest_width, chinrest_length, chinrest_height)
chinrest_base = chinrest_base.translate((0, 0, rib_height + top_arch_height + chinrest_height / 2.0))

chinrest_cutout = cq.Workplane("XY").center(chinrest_x_offset, chinrest_y_offset).sphere(chinrest_width * 0.8)
chinrest_cutout = chinrest_cutout.translate((0, 0, rib_height + top_arch_height + chinrest_height + chinrest_width * 0.8 - 5.0))

chinrest = chinrest_base.cut(chinrest_cutout)
print("chinrest generated successfully.")
