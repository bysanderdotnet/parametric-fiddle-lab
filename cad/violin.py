import cadquery as cq
import math

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, top_thickness=4, back_thickness=4, rib_thickness=4, top_arch_height=15, back_arch_height=15, rib_height=30, f_hole_length=70, f_hole_spacing=80, f_hole_width=8.0, f_hole_profile="slot", f_hole_top_radius=4.0, f_hole_bottom_radius=5.0, f_hole_x_offset=0.0, f_hole_y_offset=0.0, f_hole_angle=90.0, neck_length=130, neck_width_top=24, neck_width_bottom=34, neck_height=20, neck_angle=5.0, bridge_width_bottom=40, bridge_width_top=30, bridge_height=30, bridge_thickness=5, bridge_radius=20.0, bridge_inner_curve_radius=8.0, bridge_side_cutout_radius=6.0, bridge_cutout_radius=5.0, bridge_cutout_y_offset=10.0, bridge_central_cutout=True, bridge_central_cutout_radius=4.0, bridge_central_cutout_y_offset=15.0, bridge_foot_length=10.0, bridge_foot_width=5.0, bridge_foot_height=5.0, bridge_cutouts=True, bridge_y_offset=0.0, soundpost_radius=3, soundpost_x_offset=15, soundpost_y_offset=-15, bass_bar_length=200, bass_bar_width=5, bass_bar_height=10, bass_bar_x_offset=-15, bass_bar_y_offset=0, bass_bar_angle=0.0, tailpiece_length=110, tailpiece_width_top=40, tailpiece_width_bottom=20, tailpiece_thickness=5, purfling_groove_depth=1.0, purfling_groove_width=1.0, purfling_groove_offset=2.0, fingerboard_length=270.0, fingerboard_width_top=24.0, fingerboard_width_bottom=42.0, fingerboard_thickness=5.0, fingerboard_radius=42.0, pegbox_length=70.0, pegbox_width=24.0, pegbox_depth=20.0, pegbox_thickness=5.0, pegbox_angle=5.0, peg_hole_radius=3.0, peg_spacing=15.0, peg_length=40.0, peg_width=20.0, peg_head_thickness=5.0, endpin_length=20.0, endpin_radius=4.0, nut_length=5.0, nut_width=24.0, nut_height=8.0, saddle_length=5.0, saddle_width=30.0, saddle_height=6.0, scroll_radius=10.0, scroll_width=20.0, chinrest_x_offset=-40.0, chinrest_y_offset=-140.0, chinrest_width=80.0, chinrest_length=50.0, chinrest_height=15.0, fine_tuner_radius=2.0, fine_tuner_height=8.0, chinrest_cutout_radius=64.0, chinrest_cutout_depth=5.0, c_bout_cutout_radius=40.0, top_block_width=40.0, top_block_length=15.0, bottom_block_width=40.0, bottom_block_length=15.0):
    """
    Generate a simplified parametric violin body.
    """
    pts = [
        (0, -length / 2.0),
        (lower_bout / 2.0, -length * 0.25),
        (c_bout / 2.0, 0),
        (upper_bout / 2.0, length * 0.25),
        (0, length / 2.0),
        (-upper_bout / 2.0, length * 0.25),
        (-c_bout / 2.0, 0),
        (-lower_bout / 2.0, -length * 0.25)
    ]

    # Helper to create an arched cylinder intersection
    def get_cylinders(arch_height, z_offset, mirror=False):
        r_x = ( (lower_bout/2)**2 + arch_height**2 ) / (2 * arch_height)
        cyl_x = cq.Workplane("XZ").center(0, -r_x + arch_height + z_offset).circle(r_x).extrude(length, both=True)
        r_y = ( (length/2)**2 + arch_height**2 ) / (2 * arch_height)
        cyl_y = cq.Workplane("YZ").center(0, -r_y + arch_height + z_offset).circle(r_y).extrude(lower_bout, both=True)
        if mirror:
            cyl_x = cyl_x.mirror("XY")
            cyl_y = cyl_y.mirror("XY")
        return cyl_x, cyl_y

    # Outer bounding domes
    out_top_cyl_x, out_top_cyl_y = get_cylinders(top_arch_height, rib_height)
    out_back_cyl_x, out_back_cyl_y = get_cylinders(back_arch_height, 0, mirror=True)

    # Total volume bounding box
    total_volume = cq.Workplane("XY").polyline(pts).close().extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    total_volume = total_volume.intersect(out_top_cyl_x).intersect(out_top_cyl_y).intersect(out_back_cyl_x).intersect(out_back_cyl_y)

    # Inner cavity domes
    in_top_cyl_x, in_top_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness)
    # Fix back cavity offset: moving it by -back_thickness before mirror means it ends up inside
    # Wait, get_cylinders uses mirror=True.
    # The outer dome starts at z_offset=0 and curves to -back_arch_height.
    # The inner dome should start at z_offset=back_thickness.
    # When mirrored, it starts at -back_thickness and curves to -back_arch_height - back_thickness.
    # But wait, we want the cavity to NOT reach the bottom. So the cavity should curve down to -back_arch_height + back_thickness.
    # So the inner back dome should have arch_height = back_arch_height?
    # If we use the same arch_height, translating by back_thickness (in the positive Z before mirroring, so -back_thickness after)
    # means it shifts downwards by back_thickness.
    # But we want the cavity to shift UPWARDS by back_thickness relative to the outer dome.
    # So before mirroring, we should shift DOWNWARDS by back_thickness (so z_offset = -back_thickness).
    # Then after mirror, it will be shifted UPWARDS by back_thickness!
    in_back_cyl_x, in_back_cyl_y = get_cylinders(back_arch_height, -back_thickness, mirror=True)

    # Cavity volume
    cavity_volume = cq.Workplane("XY").polyline(pts).close().offset2D(-rib_thickness).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    cavity_volume = cavity_volume.intersect(in_top_cyl_x).intersect(in_top_cyl_y).intersect(in_back_cyl_x).intersect(in_back_cyl_y)

    c_bout_cutter_out = cq.Workplane("XY").pushPoints([
        (c_bout / 2.0 + c_bout_cutout_radius, 0),
        (-c_bout / 2.0 - c_bout_cutout_radius, 0)
    ]).circle(c_bout_cutout_radius).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    total_volume = total_volume.cut(c_bout_cutter_out)

    c_bout_cutter_in = cq.Workplane("XY").pushPoints([
        (c_bout / 2.0 + c_bout_cutout_radius, 0),
        (-c_bout / 2.0 - c_bout_cutout_radius, 0)
    ]).circle(c_bout_cutout_radius + rib_thickness).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    cavity_volume = cavity_volume.cut(c_bout_cutter_in)


    # Top and bottom blocks (leaving material by cutting from cavity_volume)
    top_block_cutter = cq.Workplane("XY").center(0, length / 2.0).box(top_block_width, top_block_length * 2, rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height + (rib_height + top_arch_height + back_arch_height)/2))
    bottom_block_cutter = cq.Workplane("XY").center(0, -length / 2.0).box(bottom_block_width, bottom_block_length * 2, rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height + (rib_height + top_arch_height + back_arch_height)/2))

    cavity_volume = cavity_volume.cut(top_block_cutter)
    cavity_volume = cavity_volume.cut(bottom_block_cutter)

    body = total_volume.cut(cavity_volume)


    # Add F-holes
    if f_hole_profile == "slot":
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset),
            (-f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset)
        ]).slot2D(f_hole_length, f_hole_width, f_hole_angle).extrude(1000).translate((0, 0, -500))
    elif f_hole_profile == "classic":
        # Calculate dx, dy offsets based on f_hole_angle (0 angle means horizontal slot, 90 means vertical)
        angle_rad = math.radians(f_hole_angle)
        dx = (f_hole_length * 0.4) * math.cos(angle_rad)
        dy = (f_hole_length * 0.4) * math.sin(angle_rad)

        # Slot at 80% length
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset),
            (-f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset)
        ]).slot2D(f_hole_length * 0.8, f_hole_width, f_hole_angle)

        # Add top circles
        f_holes_tool = f_holes_tool.pushPoints([
            (f_hole_spacing / 2.0 + dx + f_hole_x_offset, f_hole_y_offset + dy),
            (-f_hole_spacing / 2.0 + dx + f_hole_x_offset, f_hole_y_offset + dy)
        ]).circle(f_hole_top_radius)

        # Add bottom circles
        f_holes_tool = f_holes_tool.pushPoints([
            (f_hole_spacing / 2.0 - dx + f_hole_x_offset, f_hole_y_offset - dy),
            (-f_hole_spacing / 2.0 - dx + f_hole_x_offset, f_hole_y_offset - dy)
        ]).circle(f_hole_bottom_radius)

        f_holes_tool = f_holes_tool.extrude(1000).translate((0, 0, -500))
    else:
        # Fallback to slot
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset),
            (-f_hole_spacing / 2.0 + f_hole_x_offset, f_hole_y_offset)
        ]).slot2D(f_hole_length, f_hole_width, f_hole_angle).extrude(1000).translate((0, 0, -500))

    # Cut f-holes only through the top part by intersecting the cutting tool with a box above rib_height/2
    f_holes_tool = f_holes_tool.intersect(cq.Workplane("XY").box(1000, 1000, 1000).translate((0, 0, 500 + rib_height/2)))
    body = body.cut(f_holes_tool)

    # Create Neck Assembly Group
    # Add Neck
    neck_pts = [
        (-neck_width_bottom / 2.0, length / 2.0),
        (neck_width_bottom / 2.0, length / 2.0),
        (neck_width_top / 2.0, length / 2.0 + neck_length),
        (-neck_width_top / 2.0, length / 2.0 + neck_length)
    ]
    neck = cq.Workplane("XY").polyline(neck_pts).close().extrude(neck_height)
    neck = neck.translate((0, 0, rib_height - neck_height))

    neck_assembly = neck

    # Add Pegbox and Pegs
    pegbox_center_y = length / 2.0 + neck_length + nut_length + pegbox_length / 2.0
    pegbox_outer = cq.Workplane("XY").center(0, pegbox_center_y).box(pegbox_width, pegbox_length, pegbox_depth)
    pegbox_outer = pegbox_outer.translate((0, 0, rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0))

    pegbox_inner = cq.Workplane("XY").center(0, pegbox_center_y).box(pegbox_width - 2 * pegbox_thickness, pegbox_length - 2 * pegbox_thickness, pegbox_depth + 10)
    pegbox_inner = pegbox_inner.translate((0, 0, rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0))

    pegbox = pegbox_outer.cut(pegbox_inner)

    # Add Pegs
    peg_y_start = length / 2.0 + neck_length + nut_length + pegbox_thickness + peg_hole_radius + 5.0
    pegs = None
    for i in range(4):
        peg_y = peg_y_start + i * peg_spacing
        # Create a peg cylinder spanning across the pegbox (X axis)
        peg_z = rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0
        peg = cq.Workplane("YZ").center(peg_y, peg_z).circle(peg_hole_radius).extrude(peg_length, both=True)

        # Add peg head
        head_x = peg_length if i % 2 == 0 else -peg_length
        peg_head = cq.Workplane("YZ").center(peg_y, peg_z).circle(peg_width / 2.0).extrude(peg_head_thickness).translate((head_x, 0, 0))
        if i % 2 != 0:
            # If extruding normally, it goes in positive X direction. When at -peg_length,
            # we want it to extrude outward (more negative X) or translate appropriately.
            # extrude(5.0) on YZ creates solid from x=0 to x=5.
            # When translated by -peg_length, it goes from -peg_length to -peg_length + 5.
            # To make it symmetrical sticking out, we should place it starting at -peg_length
            # and going out, so we need a negative extrusion or translate by -peg_length - 5.0.
            peg_head = cq.Workplane("YZ").center(peg_y, peg_z).circle(peg_width / 2.0).extrude(-peg_head_thickness).translate((head_x, 0, 0))

        peg = peg.union(peg_head)

        if pegs is None:
            pegs = peg
        else:
            pegs = pegs.union(peg)

    # Add Scroll
    scroll_y = pegbox_center_y + pegbox_length / 2.0 + scroll_radius
    scroll = cq.Workplane("YZ").center(scroll_y, rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0).circle(scroll_radius).extrude(scroll_width, both=True)

    if pegbox_angle != 0.0:
        rot_axis_start = (1, length / 2.0 + neck_length + nut_length, rib_height - neck_height / 2.0)
        rot_axis_end = (-1, length / 2.0 + neck_length + nut_length, rib_height - neck_height / 2.0)
        pegbox = pegbox.rotate(rot_axis_start, rot_axis_end, pegbox_angle)
        if pegs is not None:
            pegs = pegs.rotate(rot_axis_start, rot_axis_end, pegbox_angle)
        scroll = scroll.rotate(rot_axis_start, rot_axis_end, pegbox_angle)

    neck_assembly = neck_assembly.union(pegbox)
    if pegs is not None:
        neck_assembly = neck_assembly.union(pegs)
    neck_assembly = neck_assembly.union(scroll)

    # Add Nut
    nut_y = length / 2.0 + neck_length
    nut = cq.Workplane("XY").center(0, nut_y + nut_length / 2.0).box(nut_width, nut_length, nut_height)
    nut = nut.translate((0, 0, rib_height + nut_height / 2.0))
    neck_assembly = neck_assembly.union(nut)

    # Add Fingerboard
    # Trapezoid from nut towards bridge
    fb_pts = [
        (-fingerboard_width_top / 2.0, nut_y),
        (fingerboard_width_top / 2.0, nut_y),
        (fingerboard_width_bottom / 2.0, nut_y - fingerboard_length),
        (-fingerboard_width_bottom / 2.0, nut_y - fingerboard_length)
    ]
    fingerboard_base = cq.Workplane("XY").polyline(fb_pts).close().extrude(fingerboard_thickness)

    # Create cylinder for curved top
    # Cylinder length is fingerboard_length (along Y). Radius is fingerboard_radius.
    fb_top_cyl_solid = cq.Solid.makeCylinder(
        fingerboard_radius,
        fingerboard_length,
        cq.Vector(0, nut_y, fingerboard_thickness - fingerboard_radius),
        cq.Vector(0, -1, 0)
    )
    fb_top_cyl = cq.Workplane("XY").add(fb_top_cyl_solid)

    # Intersect to get curved top
    fingerboard = fingerboard_base.intersect(fb_top_cyl)

    fingerboard = fingerboard.translate((0, 0, rib_height))
    neck_assembly = neck_assembly.union(fingerboard)

    # Rotate neck assembly
    if neck_angle != 0.0:
        # Rotation point is the base of the neck
        rot_axis_start = (1, length / 2.0, rib_height)
        rot_axis_end = (-1, length / 2.0, rib_height)
        neck_assembly = neck_assembly.rotate(rot_axis_start, rot_axis_end, neck_angle)

    final_body = body.union(neck_assembly)

    # Add Bridge
    # Create base block
    bridge_pts = [
        (-bridge_width_bottom / 2.0, 0),
        (bridge_width_bottom / 2.0, 0),
        (bridge_width_top / 2.0, bridge_height),
        (-bridge_width_top / 2.0, bridge_height)
    ]
    bridge_base = cq.Workplane("XZ").polyline(bridge_pts).close().extrude(bridge_thickness)
    bridge_base = bridge_base.translate((0, bridge_y_offset - bridge_thickness/2.0, rib_height + top_arch_height))
    # Create cylinder for curved top
    # Cylinder length is bridge_thickness (along Y). Radius is bridge_radius.
    bridge_top_cyl_solid = cq.Solid.makeCylinder(bridge_radius, bridge_thickness, cq.Vector(0, bridge_y_offset - bridge_thickness/2.0, rib_height + top_arch_height + bridge_height - bridge_radius), cq.Vector(0, 1, 0))
    bridge_top_cyl = cq.Workplane("XY").add(bridge_top_cyl_solid)
    # Intersect to get curved top
    bridge = bridge_base.intersect(bridge_top_cyl)

    # Expand feet if bridge_foot_width > bridge_thickness
    if bridge_foot_width > bridge_thickness:
        foot_left_x = -bridge_width_bottom / 2.0 + bridge_foot_length / 2.0
        foot_right_x = bridge_width_bottom / 2.0 - bridge_foot_length / 2.0

        foot_box_left = cq.Workplane("XY").center(foot_left_x, bridge_y_offset).box(bridge_foot_length, bridge_foot_width, bridge_foot_height).translate((0, 0, rib_height + top_arch_height + bridge_foot_height / 2.0))
        foot_box_right = cq.Workplane("XY").center(foot_right_x, bridge_y_offset).box(bridge_foot_length, bridge_foot_width, bridge_foot_height).translate((0, 0, rib_height + top_arch_height + bridge_foot_height / 2.0))

        bridge = bridge.union(foot_box_left).union(foot_box_right)

    # Add Feet Cutout
    foot_cutout_width = bridge_width_bottom - 2 * bridge_foot_length
    max_thickness = max(bridge_thickness, bridge_foot_width)
    foot_cutout = cq.Workplane("XY").center(0, bridge_y_offset).box(foot_cutout_width, max_thickness * 2, bridge_foot_height * 2)
    foot_cutout = foot_cutout.translate((0, 0, rib_height + top_arch_height))
    bridge = bridge.cut(foot_cutout)

    # Add Cutouts
    if bridge_cutouts:
        w_at_cutout = bridge_width_bottom + (bridge_width_top - bridge_width_bottom) * (bridge_cutout_y_offset / bridge_height)
        cutout_left = cq.Workplane("XZ").center(-w_at_cutout / 4.0, rib_height + top_arch_height + bridge_cutout_y_offset).circle(bridge_cutout_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
        cutout_right = cq.Workplane("XZ").center(w_at_cutout / 4.0, rib_height + top_arch_height + bridge_cutout_y_offset).circle(bridge_cutout_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
        bridge = bridge.cut(cutout_left).cut(cutout_right)

    # Add Central Cutout
    if bridge_central_cutout:
        central_cutout = cq.Workplane("XZ").center(0, rib_height + top_arch_height + bridge_central_cutout_y_offset).circle(bridge_central_cutout_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
        bridge = bridge.cut(central_cutout)

    # Add Side Cutouts
    side_cutout_y = rib_height + top_arch_height + bridge_height / 2.0
    w_at_side_cutout = bridge_width_bottom + (bridge_width_top - bridge_width_bottom) * (0.5)
    side_cutout_left = cq.Workplane("XZ").center(-w_at_side_cutout / 2.0 - bridge_inner_curve_radius + bridge_side_cutout_radius, side_cutout_y).circle(bridge_inner_curve_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
    side_cutout_right = cq.Workplane("XZ").center(w_at_side_cutout / 2.0 + bridge_inner_curve_radius - bridge_side_cutout_radius, side_cutout_y).circle(bridge_inner_curve_radius).extrude(bridge_thickness * 2).translate((0, bridge_y_offset - bridge_thickness, 0))
    bridge = bridge.cut(side_cutout_left).cut(side_cutout_right)

    final_body = final_body.union(bridge)

    # Add Soundpost (spanning the cavity)
    soundpost = cq.Workplane("XY").center(soundpost_x_offset, soundpost_y_offset).circle(soundpost_radius).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    soundpost = soundpost.intersect(cavity_volume)
    final_body = final_body.union(soundpost)

    # Add Bass Bar
    bb_top_cyl_x, bb_top_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness)
    bb_bottom_cyl_x, bb_bottom_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness - bass_bar_height)

    bass_bar_full = cq.Workplane("XY").center(bass_bar_x_offset, bass_bar_y_offset).rect(bass_bar_width, bass_bar_length).extrude(rib_height + top_arch_height).rotate((bass_bar_x_offset, bass_bar_y_offset, 0), (bass_bar_x_offset, bass_bar_y_offset, 1), bass_bar_angle)
    bass_bar_full = bass_bar_full.intersect(bb_top_cyl_x).intersect(bb_top_cyl_y)
    bass_bar_full = bass_bar_full.cut(bb_bottom_cyl_x.intersect(bb_bottom_cyl_y))

    final_body = final_body.union(bass_bar_full)

    # Add Endpin
    # Protruding from the bottom of the violin (y = -length/2)
    endpin = cq.Workplane("XZ").center(0, rib_height / 2.0).circle(endpin_radius).extrude(endpin_length, both=True)
    endpin = endpin.translate((0, -length / 2.0, 0))
    final_body = final_body.union(endpin)

    # Add Saddle
    saddle = cq.Workplane("XY").center(0, -length / 2.0 + saddle_length / 2.0).box(saddle_width, saddle_length, saddle_height)
    saddle = saddle.translate((0, 0, rib_height + saddle_height / 2.0))
    final_body = final_body.union(saddle)

    # Add Tailpiece
    # A simple trapezoidal shape from Y = -length/2.0 towards the bridge
    tp_pts = [
        (-tailpiece_width_bottom / 2.0, 0),
        (tailpiece_width_bottom / 2.0, 0),
        (tailpiece_width_top / 2.0, tailpiece_length),
        (-tailpiece_width_top / 2.0, tailpiece_length)
    ]
    tailpiece = cq.Workplane("XY").polyline(tp_pts).close().extrude(tailpiece_thickness)
    # Translate so the wide part is near the bridge, narrow part near bottom
    tailpiece = tailpiece.translate((0, -length / 2.0, rib_height + top_arch_height))

    final_body = final_body.union(tailpiece)

    # Add Fine Tuners
    num_strings = 4
    string_spacing = tailpiece_width_top / num_strings
    fine_tuners = None
    for i in range(num_strings):
        x_pos = -tailpiece_width_top / 2.0 + string_spacing / 2.0 + i * string_spacing
        y_pos = -length / 2.0 + tailpiece_length - fine_tuner_radius * 2
        z_pos = rib_height + top_arch_height + tailpiece_thickness
        tuner = cq.Workplane("XY").center(x_pos, y_pos).circle(fine_tuner_radius).extrude(fine_tuner_height)
        tuner = tuner.translate((0, 0, z_pos))
        if fine_tuners is None:
            fine_tuners = tuner
        else:
            fine_tuners = fine_tuners.union(tuner)

    final_body = final_body.union(fine_tuners)

    if purfling_groove_depth > 0:
        # A simple purfling groove around the perimeter of the top plate.
        purfling_cutter = cq.Workplane("XY").polyline(pts).close().offset2D(-purfling_groove_offset).extrude(1000).translate((0, 0, -500))
        inner_cutter = cq.Workplane("XY").polyline(pts).close().offset2D(-(purfling_groove_offset + purfling_groove_width)).extrude(1000).translate((0, 0, -500))
        purfling_wall = purfling_cutter.cut(inner_cutter)

        # Now bound it to only cut the top plate by purfling_groove_depth.
        # The top surface maxes out at rib_height + top_arch_height.
        z_cut_start = rib_height + top_arch_height - purfling_groove_depth
        top_bounding_box = cq.Workplane("XY").box(1000, 1000, 1000).translate((0, 0, z_cut_start + 500))
        purfling_tool = purfling_wall.intersect(top_bounding_box)

        final_body = final_body.cut(purfling_tool)

    # Add Chinrest
    # A simple block placed at the lower left bout, curved on top
    chinrest_base = cq.Workplane("XY").center(chinrest_x_offset, chinrest_y_offset).box(chinrest_width, chinrest_length, chinrest_height)
    # Translate to be attached to the top of the violin
    chinrest_base = chinrest_base.translate((0, 0, rib_height + top_arch_height + chinrest_height / 2.0))

    # Cut out a sphere to make it curved/ergonomic
    chinrest_cutout = cq.Workplane("XY").center(chinrest_x_offset, chinrest_y_offset).sphere(chinrest_cutout_radius)
    # Place sphere slightly above the top surface to carve out the top
    chinrest_cutout = chinrest_cutout.translate((0, 0, rib_height + top_arch_height + chinrest_height + chinrest_cutout_radius - chinrest_cutout_depth))

    chinrest = chinrest_base.cut(chinrest_cutout)

    final_body = final_body.union(chinrest)

    return final_body, bridge

import argparse
import json
import inspect
import os
import sys

# Param names/types/help come from the shared spec; defaults from this
# module's create_violin_body signature (single source of truth).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from common.params import NAMES, add_arguments

if __name__ == "__main__":
    defaults = {n: p.default for n, p in inspect.signature(create_violin_body).parameters.items()}
    parser = argparse.ArgumentParser(description="Generate parametric violin body.")
    add_arguments(parser, defaults)
    args = parser.parse_args()

    params = {name: getattr(args, name) for name in NAMES}

    violin, bridge = create_violin_body(**params)

    # Calculate volume and estimated mass
    volume_mm3 = violin.val().Volume()
    mass_g = volume_mm3 * 1.24e-3 # PLA density ~ 1.24 g/cm^3
    params["volume_mm3"] = volume_mm3
    params["mass_g"] = mass_g

    bridge_volume_mm3 = bridge.val().Volume()
    bridge_mass_g = bridge_volume_mm3 * 1.24e-3
    params["bridge_volume_mm3"] = bridge_volume_mm3
    params["bridge_mass_g"] = bridge_mass_g

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
