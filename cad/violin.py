import cadquery as cq

def create_violin_body(length=355, lower_bout=208, upper_bout=168, c_bout=110, top_thickness=4, back_thickness=4, rib_thickness=4, top_arch_height=15, back_arch_height=15, rib_height=30, f_hole_length=70, f_hole_spacing=80, f_hole_width=8.0, f_hole_profile="slot", f_hole_top_radius=4.0, f_hole_bottom_radius=5.0, neck_length=130, neck_width=30, neck_height=20, bridge_width=40, bridge_height=30, bridge_thickness=5, bridge_radius=20.0, bridge_cutout_radius=5.0, bridge_cutout_y_offset=10.0, bridge_foot_length=10.0, bridge_foot_height=5.0, soundpost_radius=3, soundpost_x_offset=15, soundpost_y_offset=-15, bass_bar_length=200, bass_bar_width=5, bass_bar_height=10, bass_bar_x_offset=-15, bass_bar_y_offset=0, tailpiece_length=110, tailpiece_width_top=40, tailpiece_width_bottom=20, tailpiece_thickness=5, purfling_groove_depth=1.0, fingerboard_length=270.0, fingerboard_width_top=24.0, fingerboard_width_bottom=42.0, fingerboard_thickness=5.0, pegbox_length=70.0, pegbox_width=24.0, pegbox_depth=20.0, pegbox_thickness=5.0, peg_hole_radius=3.0, peg_spacing=15.0, endpin_length=20.0, endpin_radius=4.0, nut_length=5.0, nut_width=24.0, nut_height=8.0, saddle_length=5.0, saddle_width=30.0, saddle_height=6.0, scroll_radius=10.0, scroll_width=20.0):
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

    body = total_volume.cut(cavity_volume)

    # Add F-holes
    if f_hole_profile == "slot":
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0, 0),
            (-f_hole_spacing / 2.0, 0)
        ]).slot2D(f_hole_length, f_hole_width, 90).extrude(1000).translate((0, 0, -500))
    elif f_hole_profile == "classic":
        # Slot at 80% length
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0, 0),
            (-f_hole_spacing / 2.0, 0)
        ]).slot2D(f_hole_length * 0.8, f_hole_width, 90)

        # Add top circles
        f_holes_tool = f_holes_tool.pushPoints([
            (f_hole_spacing / 2.0, f_hole_length * 0.4),
            (-f_hole_spacing / 2.0, f_hole_length * 0.4)
        ]).circle(f_hole_top_radius)

        # Add bottom circles
        f_holes_tool = f_holes_tool.pushPoints([
            (f_hole_spacing / 2.0, -f_hole_length * 0.4),
            (-f_hole_spacing / 2.0, -f_hole_length * 0.4)
        ]).circle(f_hole_bottom_radius)

        f_holes_tool = f_holes_tool.extrude(1000).translate((0, 0, -500))
    else:
        # Fallback to slot
        f_holes_tool = cq.Workplane("XY").pushPoints([
            (f_hole_spacing / 2.0, 0),
            (-f_hole_spacing / 2.0, 0)
        ]).slot2D(f_hole_length, f_hole_width, 90).extrude(1000).translate((0, 0, -500))

    # Cut f-holes only through the top part by intersecting the cutting tool with a box above rib_height/2
    f_holes_tool = f_holes_tool.intersect(cq.Workplane("XY").box(1000, 1000, 1000).translate((0, 0, 500 + rib_height/2)))
    body = body.cut(f_holes_tool)

    # Add Neck
    neck = cq.Workplane("XY").center(0, length / 2.0 + neck_length / 2.0).box(neck_width, neck_length, neck_height)
    neck = neck.translate((0, 0, rib_height - neck_height / 2.0))

    final_body = body.union(neck)

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
        peg = cq.Workplane("YZ").center(peg_y, rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0).circle(peg_hole_radius).extrude(pegbox_width + 20, both=True)
        if pegs is None:
            pegs = peg
        else:
            pegs = pegs.union(peg)

    final_body = final_body.union(pegbox)
    if pegs is not None:
        final_body = final_body.union(pegs)

    # Add Scroll
    scroll_y = pegbox_center_y + pegbox_length / 2.0 + scroll_radius
    scroll = cq.Workplane("YZ").center(scroll_y, rib_height - neck_height / 2.0 + pegbox_depth / 2.0 - neck_height / 2.0).circle(scroll_radius).extrude(scroll_width, both=True)
    final_body = final_body.union(scroll)

    # Add Nut
    nut_y = length / 2.0 + neck_length
    nut = cq.Workplane("XY").center(0, nut_y + nut_length / 2.0).box(nut_width, nut_length, nut_height)
    nut = nut.translate((0, 0, rib_height + nut_height / 2.0))
    final_body = final_body.union(nut)

    # Add Fingerboard
    # Trapezoid from nut towards bridge
    fb_pts = [
        (-fingerboard_width_top / 2.0, nut_y),
        (fingerboard_width_top / 2.0, nut_y),
        (fingerboard_width_bottom / 2.0, nut_y - fingerboard_length),
        (-fingerboard_width_bottom / 2.0, nut_y - fingerboard_length)
    ]
    fingerboard = cq.Workplane("XY").polyline(fb_pts).close().extrude(fingerboard_thickness)
    fingerboard = fingerboard.translate((0, 0, rib_height))
    final_body = final_body.union(fingerboard)

    # Add Bridge
    # Create base block
    bridge_base = cq.Workplane("XY").box(bridge_width, bridge_thickness, bridge_height)
    bridge_base = bridge_base.translate((0, 0, rib_height + top_arch_height + bridge_height / 2.0))
    # Create cylinder for curved top
    # Cylinder length is bridge_thickness (along Y). Radius is bridge_radius.
    bridge_top_cyl_solid = cq.Solid.makeCylinder(bridge_radius, bridge_thickness, cq.Vector(0, -bridge_thickness/2.0, rib_height + top_arch_height + bridge_height - bridge_radius), cq.Vector(0, 1, 0))
    bridge_top_cyl = cq.Workplane("XY").add(bridge_top_cyl_solid)
    # Intersect to get curved top
    bridge = bridge_base.intersect(bridge_top_cyl)

    # Add Feet Cutout
    foot_cutout_width = bridge_width - 2 * bridge_foot_length
    foot_cutout = cq.Workplane("XY").box(foot_cutout_width, bridge_thickness * 2, bridge_foot_height * 2)
    foot_cutout = foot_cutout.translate((0, 0, rib_height + top_arch_height))
    bridge = bridge.cut(foot_cutout)

    # Add Cutouts
    cutout_left = cq.Workplane("XZ").center(-bridge_width / 4.0, rib_height + top_arch_height + bridge_cutout_y_offset).circle(bridge_cutout_radius).extrude(bridge_thickness * 2).translate((0, -bridge_thickness, 0))
    cutout_right = cq.Workplane("XZ").center(bridge_width / 4.0, rib_height + top_arch_height + bridge_cutout_y_offset).circle(bridge_cutout_radius).extrude(bridge_thickness * 2).translate((0, -bridge_thickness, 0))
    bridge = bridge.cut(cutout_left).cut(cutout_right)

    final_body = final_body.union(bridge)

    # Add Soundpost (spanning the cavity)
    soundpost = cq.Workplane("XY").center(soundpost_x_offset, soundpost_y_offset).circle(soundpost_radius).extrude(rib_height + top_arch_height + back_arch_height).translate((0, 0, -back_arch_height))
    soundpost = soundpost.intersect(cavity_volume)
    final_body = final_body.union(soundpost)

    # Add Bass Bar
    bb_top_cyl_x, bb_top_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness)
    bb_bottom_cyl_x, bb_bottom_cyl_y = get_cylinders(top_arch_height, rib_height - top_thickness - bass_bar_height)

    bass_bar_full = cq.Workplane("XY").center(bass_bar_x_offset, bass_bar_y_offset).rect(bass_bar_width, bass_bar_length).extrude(rib_height + top_arch_height).translate((0, 0, 0))
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

    if purfling_groove_depth > 0:
        # A simple purfling groove around the perimeter of the top plate.
        purfling_cutter = cq.Workplane("XY").polyline(pts).close().offset2D(-2.0).extrude(1000).translate((0, 0, -500))
        inner_cutter = cq.Workplane("XY").polyline(pts).close().offset2D(-3.0).extrude(1000).translate((0, 0, -500))
        purfling_wall = purfling_cutter.cut(inner_cutter)

        # Now bound it to only cut the top plate by purfling_groove_depth.
        # The top surface maxes out at rib_height + top_arch_height.
        z_cut_start = rib_height + top_arch_height - purfling_groove_depth
        top_bounding_box = cq.Workplane("XY").box(1000, 1000, 1000).translate((0, 0, z_cut_start + 500))
        purfling_tool = purfling_wall.intersect(top_bounding_box)

        final_body = final_body.cut(purfling_tool)

    return final_body

import argparse
import json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate parametric violin body.")
    parser.add_argument("--length", type=float, default=355, help="Length of the body")
    parser.add_argument("--lower_bout", type=float, default=208, help="Width of the lower bout")
    parser.add_argument("--upper_bout", type=float, default=168, help="Width of the upper bout")
    parser.add_argument("--c_bout", type=float, default=110, help="Width of the c-bout")
    parser.add_argument("--top_thickness", type=float, default=4, help="Top plate thickness")
    parser.add_argument("--back_thickness", type=float, default=4, help="Back plate thickness")
    parser.add_argument("--rib_thickness", type=float, default=4, help="Rib thickness")
    parser.add_argument("--top_arch_height", type=float, default=15, help="Arch height of the top plate")
    parser.add_argument("--back_arch_height", type=float, default=15, help="Arch height of the back plate")
    parser.add_argument("--rib_height", type=float, default=30, help="Height of the ribs")
    parser.add_argument("--f_hole_length", type=float, default=70, help="Length of the F-holes")
    parser.add_argument("--f_hole_spacing", type=float, default=80, help="Spacing between the F-holes")
    parser.add_argument("--f_hole_width", type=float, default=8.0, help="Width of the F-holes")
    parser.add_argument("--f_hole_profile", type=str, default="slot", help="Profile of the F-holes (slot or classic)")
    parser.add_argument("--f_hole_top_radius", type=float, default=4.0, help="Top radius of classic F-holes")
    parser.add_argument("--f_hole_bottom_radius", type=float, default=5.0, help="Bottom radius of classic F-holes")
    parser.add_argument("--neck_length", type=float, default=130, help="Length of the neck")
    parser.add_argument("--neck_width", type=float, default=30, help="Width of the neck")
    parser.add_argument("--neck_height", type=float, default=20, help="Height/thickness of the neck")
    parser.add_argument("--bridge_width", type=float, default=40, help="Width of the bridge")
    parser.add_argument("--bridge_height", type=float, default=30, help="Height of the bridge")
    parser.add_argument("--bridge_thickness", type=float, default=5, help="Thickness of the bridge")
    parser.add_argument("--bridge_radius", type=float, default=20.0, help="Radius of the bridge top curvature")
    parser.add_argument("--bridge_cutout_radius", type=float, default=5.0, help="Radius of the bridge cutouts")
    parser.add_argument("--bridge_cutout_y_offset", type=float, default=10.0, help="Vertical offset of the bridge cutouts")
    parser.add_argument("--bridge_foot_length", type=float, default=10.0, help="Length of the bridge feet")
    parser.add_argument("--bridge_foot_height", type=float, default=5.0, help="Height of the bridge feet cutout")
    parser.add_argument("--soundpost_radius", type=float, default=3, help="Radius of the soundpost")
    parser.add_argument("--soundpost_x_offset", type=float, default=15, help="X offset of the soundpost")
    parser.add_argument("--soundpost_y_offset", type=float, default=-15, help="Y offset of the soundpost")
    parser.add_argument("--bass_bar_length", type=float, default=200, help="Length of the bass bar")
    parser.add_argument("--bass_bar_width", type=float, default=5, help="Width of the bass bar")
    parser.add_argument("--bass_bar_height", type=float, default=10, help="Height of the bass bar")
    parser.add_argument("--bass_bar_x_offset", type=float, default=-15, help="X offset of the bass bar")
    parser.add_argument("--bass_bar_y_offset", type=float, default=0, help="Y offset of the bass bar")
    parser.add_argument("--tailpiece_length", type=float, default=110, help="Length of the tailpiece")
    parser.add_argument("--tailpiece_width_top", type=float, default=40, help="Width of the tailpiece near bridge")
    parser.add_argument("--tailpiece_width_bottom", type=float, default=20, help="Width of the tailpiece near saddle")
    parser.add_argument("--tailpiece_thickness", type=float, default=5, help="Thickness of the tailpiece")
    parser.add_argument("--purfling_groove_depth", type=float, default=1.0, help="Depth of the purfling groove")
    parser.add_argument("--fingerboard_length", type=float, default=270.0, help="Length of the fingerboard")
    parser.add_argument("--fingerboard_width_top", type=float, default=24.0, help="Width of the fingerboard near the nut")
    parser.add_argument("--fingerboard_width_bottom", type=float, default=42.0, help="Width of the fingerboard near the bridge")
    parser.add_argument("--fingerboard_thickness", type=float, default=5.0, help="Thickness of the fingerboard")
    parser.add_argument("--pegbox_length", type=float, default=70.0, help="Length of the pegbox")
    parser.add_argument("--pegbox_width", type=float, default=24.0, help="Width of the pegbox")
    parser.add_argument("--pegbox_depth", type=float, default=20.0, help="Depth of the pegbox")
    parser.add_argument("--pegbox_thickness", type=float, default=5.0, help="Wall thickness of the pegbox")
    parser.add_argument("--peg_hole_radius", type=float, default=3.0, help="Radius of the peg holes")
    parser.add_argument("--peg_spacing", type=float, default=15.0, help="Spacing between pegs")
    parser.add_argument("--endpin_length", type=float, default=20.0, help="Length of the endpin")
    parser.add_argument("--endpin_radius", type=float, default=4.0, help="Radius of the endpin")
    parser.add_argument("--nut_length", type=float, default=5.0, help="Length of the nut")
    parser.add_argument("--nut_width", type=float, default=24.0, help="Width of the nut")
    parser.add_argument("--nut_height", type=float, default=8.0, help="Height of the nut")
    parser.add_argument("--saddle_length", type=float, default=5.0, help="Length of the saddle")
    parser.add_argument("--saddle_width", type=float, default=30.0, help="Width of the saddle")
    parser.add_argument("--saddle_height", type=float, default=6.0, help="Height of the saddle")
    parser.add_argument("--scroll_radius", type=float, default=10.0, help="Radius of the scroll")
    parser.add_argument("--scroll_width", type=float, default=20.0, help="Width of the scroll")
    args = parser.parse_args()

    params = {
        "length": args.length,
        "lower_bout": args.lower_bout,
        "upper_bout": args.upper_bout,
        "c_bout": args.c_bout,
        "top_thickness": args.top_thickness,
        "back_thickness": args.back_thickness,
        "rib_thickness": args.rib_thickness,
        "top_arch_height": args.top_arch_height,
        "back_arch_height": args.back_arch_height,
        "rib_height": args.rib_height,
        "f_hole_length": args.f_hole_length,
        "f_hole_spacing": args.f_hole_spacing,
        "f_hole_width": args.f_hole_width,
        "f_hole_profile": args.f_hole_profile,
        "f_hole_top_radius": args.f_hole_top_radius,
        "f_hole_bottom_radius": args.f_hole_bottom_radius,
        "neck_length": args.neck_length,
        "neck_width": args.neck_width,
        "neck_height": args.neck_height,
        "bridge_width": args.bridge_width,
        "bridge_height": args.bridge_height,
        "bridge_thickness": args.bridge_thickness,
        "bridge_radius": args.bridge_radius,
        "bridge_cutout_radius": args.bridge_cutout_radius,
        "bridge_cutout_y_offset": args.bridge_cutout_y_offset,
        "bridge_foot_length": args.bridge_foot_length,
        "bridge_foot_height": args.bridge_foot_height,
        "soundpost_radius": args.soundpost_radius,
        "soundpost_x_offset": args.soundpost_x_offset,
        "soundpost_y_offset": args.soundpost_y_offset,
        "bass_bar_length": args.bass_bar_length,
        "bass_bar_width": args.bass_bar_width,
        "bass_bar_height": args.bass_bar_height,
        "bass_bar_x_offset": args.bass_bar_x_offset,
        "bass_bar_y_offset": args.bass_bar_y_offset,
        "tailpiece_length": args.tailpiece_length,
        "tailpiece_width_top": args.tailpiece_width_top,
        "tailpiece_width_bottom": args.tailpiece_width_bottom,
        "tailpiece_thickness": args.tailpiece_thickness,
        "purfling_groove_depth": args.purfling_groove_depth,
        "fingerboard_length": args.fingerboard_length,
        "fingerboard_width_top": args.fingerboard_width_top,
        "fingerboard_width_bottom": args.fingerboard_width_bottom,
        "fingerboard_thickness": args.fingerboard_thickness,
        "pegbox_length": args.pegbox_length,
        "pegbox_width": args.pegbox_width,
        "pegbox_depth": args.pegbox_depth,
        "pegbox_thickness": args.pegbox_thickness,
        "peg_hole_radius": args.peg_hole_radius,
        "peg_spacing": args.peg_spacing,
        "endpin_length": args.endpin_length,
        "endpin_radius": args.endpin_radius,
        "nut_length": args.nut_length,
        "nut_width": args.nut_width,
        "nut_height": args.nut_height,
        "saddle_length": args.saddle_length,
        "saddle_width": args.saddle_width,
        "saddle_height": args.saddle_height,
        "scroll_radius": args.scroll_radius,
        "scroll_width": args.scroll_width
    }

    violin = create_violin_body(**params)

    # Calculate volume and estimated mass
    volume_mm3 = violin.val().Volume()
    mass_g = volume_mm3 * 1.24e-3 # PLA density ~ 1.24 g/cm^3
    params["volume_mm3"] = volume_mm3
    params["mass_g"] = mass_g

    # Export to step
    cq.exporters.export(violin, "violin_body.step")

    # Export parameters to JSON
    with open("violin_body.json", "w") as f:
        json.dump(params, f, indent=4)
