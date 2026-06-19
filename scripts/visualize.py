import sys
import cadquery as cq

if len(sys.argv) < 2:
    print("Usage: python visualize.py <step_file> [output.stl]")
    sys.exit(1)

step_file = sys.argv[1]
output_file = sys.argv[2] if len(sys.argv) > 2 else "visualization.stl"

# Loading STEP file
print(f"Loading {step_file}...")
shape = cq.importers.importStep(step_file)

print(f"Exporting to {output_file}...")
cq.exporters.export(shape, output_file)
print(f"Exported as {output_file}")
