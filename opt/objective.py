import json

def evaluate_objective():
    mass_g = 400.0 # Default if fail
    volume_mm3 = 300000.0 # Default if fail
    a0_freq = 300.0
    a1_freq = 450.0 # Default if fail
    cbr_freq = 300.0 # Default if fail
    b1_minus_freq = 400.0 # Default if fail
    b1_plus_freq = 500.0 # Default if fail
    top_thickness_val = 4.0 # Default if fail
    back_thickness_val = 4.0 # Default if fail
    bridge_mass_g = 2.0 # Default if fail
    soundpost_mass_g = 1.0 # Default if fail
    bass_bar_mass_g = 5.0 # Default if fail
    tailpiece_mass_g = 10.0 # Default if fail
    chinrest_mass_g = 15.0 # Default if fail
    fine_tuners_mass_g = 0.5 # Default if fail
    saddle_mass_g = 1.0 # Default if fail
    strings_mass_g = 1.5 # Default if fail
    nut_mass_g = 2.0 # Default if fail
    pegs_mass_g = 5.0 # Default if fail
    fingerboard_mass_g = 10.0 # Default if fail
    endpin_mass_g = 2.0 # Default if fail
    neck_mass_g = 15.0 # Default if fail
    scroll_mass_g = 5.0 # Default if fail
    top_block_mass_g = 10.0 # Default if fail
    bottom_block_mass_g = 10.0 # Default if fail
    corner_blocks_mass_g = 10.0 # Default if fail

    try:
        with open("violin_body.json", "r") as f:
            body_res = json.load(f)
            mass_g = body_res.get("mass_g", mass_g)
            volume_mm3 = body_res.get("volume_mm3", volume_mm3)
            top_thickness_val = body_res.get("top_thickness", top_thickness_val)
            back_thickness_val = body_res.get("back_thickness", back_thickness_val)
            bridge_mass_g = body_res.get("bridge_mass_g", bridge_mass_g)
            soundpost_mass_g = body_res.get("soundpost_mass_g", soundpost_mass_g)
            bass_bar_mass_g = body_res.get("bass_bar_mass_g", bass_bar_mass_g)
            tailpiece_mass_g = body_res.get("tailpiece_mass_g", tailpiece_mass_g)
            chinrest_mass_g = body_res.get("chinrest_mass_g", chinrest_mass_g)
            fine_tuners_mass_g = body_res.get("fine_tuners_mass_g", fine_tuners_mass_g)
            saddle_mass_g = body_res.get("saddle_mass_g", saddle_mass_g)
            strings_mass_g = body_res.get("strings_mass_g", strings_mass_g)
            nut_mass_g = body_res.get("nut_mass_g", nut_mass_g)
            pegs_mass_g = body_res.get("pegs_mass_g", pegs_mass_g)
            fingerboard_mass_g = body_res.get("fingerboard_mass_g", fingerboard_mass_g)
            endpin_mass_g = body_res.get("endpin_mass_g", endpin_mass_g)
            neck_mass_g = body_res.get("neck_mass_g", neck_mass_g)
            scroll_mass_g = body_res.get("scroll_mass_g", scroll_mass_g)
            top_block_mass_g = body_res.get("top_block_mass_g", top_block_mass_g)
            bottom_block_mass_g = body_res.get("bottom_block_mass_g", bottom_block_mass_g)
            corner_blocks_mass_g = body_res.get("corner_blocks_mass_g", corner_blocks_mass_g)
    except FileNotFoundError:
        print("Warning: violin_body.json not found")

    try:
        with open("structural_results.json", "r") as f:
            struct_res = json.load(f)
            # fallback in case structural_results has updated mass
            mass_g = struct_res.get("mass_g", mass_g)

            struct_modes = struct_res.get("eigenmodes", [])

            # Find CBR, B1-, and B1+ modes explicitly
            b1_found = False
            for mode in struct_modes:
                desc = mode.get("description", "")
                if "CBR" in desc:
                    cbr_freq = mode.get("frequency_hz", cbr_freq)
                elif "B1-" in desc:
                    b1_minus_freq = mode.get("frequency_hz", b1_minus_freq)
                    b1_found = True
                elif "B1+" in desc:
                    b1_plus_freq = mode.get("frequency_hz", b1_plus_freq)

            # Fallback if no B1- description is found: use the 2nd mode > 100Hz
            if not b1_found:
                real_modes = [m for m in struct_modes if m.get("frequency_hz", 0) > 100.0]
                if len(real_modes) > 1:
                    b1_minus_freq = real_modes[1].get("frequency_hz", b1_minus_freq)
                elif len(real_modes) == 1:
                    b1_minus_freq = real_modes[0].get("frequency_hz", b1_minus_freq)
    except FileNotFoundError:
        print("Warning: structural_results.json not found")

    try:
        with open("acoustic_results.json", "r") as f:
            ac_res = json.load(f)
            # Find A0 and A1 modes explicitly
            modes = ac_res.get("cavity_modes", [])
            a0_found = False
            for mode in modes:
                desc = mode.get("description", "")
                if "A0" in desc:
                    a0_freq = mode.get("frequency_hz", a0_freq)
                    a0_found = True
                elif "A1" in desc:
                    a1_freq = mode.get("frequency_hz", a1_freq)

            if not a0_found and modes:
                # Fallback to first mode if no A0 description is found
                a0_freq = modes[0].get("frequency_hz", a0_freq)
    except FileNotFoundError:
        print("Warning: acoustic_results.json not found")

    # Simple fitness: error of A0 frequency from 290Hz and B1- from 400Hz, plus a small penalty for mass and volume
    target_a0 = 290.0
    target_struct = 400.0

    score = abs(a0_freq - target_a0) + abs(b1_minus_freq - target_struct) + (mass_g * 0.1) + (volume_mm3 * 1e-4) + (top_thickness_val * 5.0) + (back_thickness_val * 5.0) + (bridge_mass_g * 5.0) + (soundpost_mass_g * 5.0) + (bass_bar_mass_g * 5.0) + (tailpiece_mass_g * 5.0) + (chinrest_mass_g * 5.0) + (fine_tuners_mass_g * 5.0) + (saddle_mass_g * 5.0) + (strings_mass_g * 5.0) + (nut_mass_g * 5.0) + (pegs_mass_g * 5.0) + (fingerboard_mass_g * 5.0) + (endpin_mass_g * 5.0) + (neck_mass_g * 5.0) + (scroll_mass_g * 5.0) + (top_block_mass_g * 5.0) + (bottom_block_mass_g * 5.0) + (corner_blocks_mass_g * 5.0)
    result_str = f"Result: A0={a0_freq:.1f}Hz, A1={a1_freq:.1f}Hz, CBR={cbr_freq:.1f}Hz, B1-={b1_minus_freq:.1f}Hz, B1+={b1_plus_freq:.1f}Hz, Mass={mass_g:.1f}g, BridgeMass={bridge_mass_g:.2f}g, SoundpostMass={soundpost_mass_g:.2f}g, BassBarMass={bass_bar_mass_g:.2f}g, TailpieceMass={tailpiece_mass_g:.2f}g, ChinrestMass={chinrest_mass_g:.2f}g, FineTunersMass={fine_tuners_mass_g:.2f}g, SaddleMass={saddle_mass_g:.2f}g, StringsMass={strings_mass_g:.2f}g, NutMass={nut_mass_g:.2f}g, PegsMass={pegs_mass_g:.2f}g, FingerboardMass={fingerboard_mass_g:.2f}g, EndpinMass={endpin_mass_g:.2f}g, NeckMass={neck_mass_g:.2f}g, ScrollMass={scroll_mass_g:.2f}g, TopBlockMass={top_block_mass_g:.2f}g, BottomBlockMass={bottom_block_mass_g:.2f}g, CornerBlocksMass={corner_blocks_mass_g:.2f}g, Volume={volume_mm3:.1f}mm3, Top={top_thickness_val:.1f}mm, Back={back_thickness_val:.1f}mm -> Score={score:.2f}"

    return score, result_str
