import os
import sys

# Ensure the root directory is in sys.path so we can import from common
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.params import SPEC

def generate_parameter_table(output_file="docs/parameters.md"):
    """Generates a Markdown table of all parameters from common.params.SPEC."""
    out_dir = os.path.dirname(output_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    lines = [
        "# Resonant Violin Lab Parameters",
        "",
        "| Parameter | Type | Range/Options | Description |",
        "|---|---|---|---|"
    ]

    for name, kind, opt, help_text in SPEC:
        range_str = "None"
        if opt:
            if kind == "float":
                range_str = f"[{opt[0]}, {opt[1]}]"
            elif kind == "bool" or kind == "str":
                range_str = ", ".join(map(str, opt))
            else:
                range_str = str(opt)

        lines.append(f"| `{name}` | `{kind}` | {range_str} | {help_text} |")

    lines.append("")

    md_content = "\n".join(lines)

    with open(output_file, "w") as f:
        f.write(md_content)

    print(f"Generated parameter table at: {output_file}")
    return md_content

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate a markdown table of all parameter sweeps.")
    parser.add_argument("--output", type=str, default="docs/parameters.md", help="Path to output markdown file.")
    args = parser.parse_args()

    generate_parameter_table(args.output)
