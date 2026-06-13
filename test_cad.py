import cadquery as cq
bridge_width = 40
bridge_thickness = 5
bridge_height = 30
rib_height = 30
top_arch_height = 15
bridge_radius = 20.0
bridge_base = cq.Workplane("XY").box(bridge_width, bridge_thickness, bridge_height)
bridge_base = bridge_base.translate((0, 0, rib_height + top_arch_height + bridge_height / 2.0))

# Try creating cylinder by revolving or explicit solid
cyl = cq.Solid.makeCylinder(bridge_radius, bridge_thickness, cq.Vector(0, -bridge_thickness/2, rib_height + top_arch_height + bridge_height - bridge_radius), cq.Vector(0, 1, 0))
cyl_wp = cq.Workplane("XY").add(cyl)

bridge = bridge_base.intersect(cyl_wp)
print("Bridge Solid count:", len(bridge.solids().vals()))
