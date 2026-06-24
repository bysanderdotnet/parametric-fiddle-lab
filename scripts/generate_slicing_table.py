def generate_slicing_table():
    profiles = {
        "fast": {
            "layer_height": 0.28,
            "infill_density": 15
        },
        "strong": {
            "layer_height": 0.20,
            "infill_density": 40
        },
        "quality": {
            "layer_height": 0.12,
            "infill_density": 20
        },
        "lightweight": {
            "layer_height": 0.24,
            "infill_density": 5
        }
    }

    markdown = "| Profile | Layer Height (mm) | Infill Density (%) |\n"
    markdown += "|---|---|---|\n"

    for profile_name, params in profiles.items():
        markdown += f"| {profile_name.capitalize()} | {params['layer_height']:.2f} | {params['infill_density']} |\n"

    return markdown

if __name__ == "__main__":
    print(generate_slicing_table())
