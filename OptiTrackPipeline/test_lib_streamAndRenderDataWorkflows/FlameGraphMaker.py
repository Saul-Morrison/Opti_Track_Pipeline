import subprocess
import sys
sys.path.append("c:/users/saulm/anaconda3/lib/site-packages")


# Path to the target script to profile
target_script = "C:/Users/saulm/OneDrive/cambridge/IIB/IIB Project - Augmented Reality/Opti_Track_Pipeline/OptiTrackPipeline/SendGodotData.py"

# Step 1: Run pyflame to capture stack traces
# The -o flag specifies the output file for the stack traces
with open("OptiTrackPipeline/lib_streamAndRenderDataWorkflows/pyflame_output.txt", "w") as out_file:
    subprocess.run(["py-spy", "record", "-o", "GodotFlameGraph.txt", "--rate", "100", "--format", "speedscope", "--", "python", target_script], check=True)
# Step 2: Generate the flame graph using flamegraph.pl
# The output will be a SVG file (flamegraph.svg)

print("Flame graph generated: flamegraph.svg")