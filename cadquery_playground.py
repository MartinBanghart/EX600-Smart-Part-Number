import cadquery as cq
from ocp_vscode import show # pip install ocp_vscode
import trimesh # pip install cadquery trimesh pygltflib

# -------------------------------------------------
# ---------------- MODELING A PART ----------------
# -------------------------------------------------

# Simple Part Model
# result = (
#     cq.Workplane("XY")
#     .box(
#         50, # Length (50 mm) - X
#         50, # Width  (50 mm) - Y
#         10  # Height (10 mm) - Z
#         )
#     .faces(">Z") # Selects the face whose normal points in the positive Z direction.
#     .workplane() # Places a sketch plane on the selected face.
#     .hole(15) # Creates a through-hole:
#                 # -- Diameter: 15 mm
#                 # -- Located at the workplane origin (center of the top face)
#                 # -- By default goes completely through the part
# )

# show(result)

# # Save STEP
# cq.exporters.export(result, "outputs/bracket.step")

# # Save STL
# cq.exporters.export(result, "outputs/bracket.stl")

# # Convert STL -> GLB
# mesh = trimesh.load("outputs/bracket.stl")
# mesh.export("outputs/bracket.glb")

# print("Exported STEP, STL, and GLB")


# -------------------------------------------------
# -------------- MODELING AN ASSEMBLY -------------
# -------------------------------------------------
import cadquery as cq

part = (
    cq.Workplane("XY")
    .box(50, 50, 10)
    .faces(">Z")
    .workplane()
    .hole(15)
)

assy = cq.Assembly()

assy.add(part, name="Part1")

assy.add(
    part,
    name="Part2",
    loc=cq.Location(cq.Vector(50, 0, 0))
)

show(assy)