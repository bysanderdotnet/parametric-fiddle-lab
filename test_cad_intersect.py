import cadquery as cq

bridge_thickness = 5
rib_height = 30
top_arch_height = 15
bridge_central_cutout_y_offset = 15.0
bridge_central_cutout_radius = 4.0
bridge_central_cutout_inner_radius = 2.0
bridge_y_offset = 0.0

try:
    central_cutout = cq.Workplane("XZ").center(0, rib_height + top_arch_height + bridge_central_cutout_y_offset).circle(bridge_central_cutout_radius).center(0, -bridge_central_cutout_radius).circle(bridge_central_cutout_inner_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
    # Let's try cutting a box to see if it works
    box = cq.Workplane("XZ").box(50, 50, 50)
    res = box.cut(central_cutout)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
