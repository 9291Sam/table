import numpy as np
import magpylib as magpy
from scipy.spatial.transform import Rotation as R

# Import the getFT function from the magpylib-force extension.
# This is the dedicated tool for force and torque calculations.
from magpylib_force import getFT

# --- 1. Define System Parameters ---
# All units must be SI (meters, Tesla) for magpylib v5+

# --- Geometry ---
# These represent the cylindrical electromagnets on the faces of your robot.
cylinder_diameter_m = 0.012  # 12 mm diameter
cylinder_length_m = 0.015   # 15 mm length

# --- Positioning ---
# This simulates the interaction between magnets on adjacent faces of tiled dodecagons.
# The angle between the normals of adjacent faces in a dodecagon tiling is 30 degrees.
angle_deg = 30.0
# This is the desired gap between the closest points of the magnet faces.
gap_mm = 10

# --- Magnet Properties ---
# This simulates the strength of a powered electromagnet's core.
# Using a typical value for strong NdFeB magnets.
magnet_pol_T = 1.3

print(f"Simulating two magnets on adjacent dodecagon faces...")
print(f"Angle: {angle_deg:.2f} degrees, Face Gap Approx: {gap_mm} mm")

# --- 2. Create Magpylib Objects ---
# Create the stationary source magnet, centered at the origin.
# Its polarization is along the +Z axis.
source_magnet = magpy.magnet.Cylinder(
    polarization=(0, 0, magnet_pol_T),
    dimension=(cylinder_diameter_m, cylinder_length_m)
)

# Create the target magnet, which will experience the force.
# To create an attractive force, its polarization must be opposite.
target_magnet = magpy.magnet.Cylinder(
    polarization=(0, 0, -magnet_pol_T),
    dimension=(cylinder_diameter_m, cylinder_length_m)
)

# --- 3. Position and Orient the Magnets for Tiling Geometry ---
# We position the target magnet as if it's on an adjacent dodecagon face.

# First, calculate the initial center-to-center distance for a face-to-face setup.
center_to_center_dist = (cylinder_length_m / 2) + (gap_mm / 1000) + (cylinder_length_m / 2)

# Set the target magnet's initial position along the Z-axis.
target_magnet.position = (0, 0, center_to_center_dist)

# Now, rotate the target magnet into its final orientation.
# This rotation simulates the angle of the adjacent dodecagon face.
# We pivot the rotation around the center of the source magnet's face
# to create an intuitive "hinge" motion.
pivot_point = (0, 0, cylinder_length_m / 2)

# CORRECTED: The .rotate() method requires a scipy Rotation object.
# We create this object from our desired angle and axis.
rotation_to_apply = R.from_euler('y', angle_deg, degrees=True)
target_magnet.rotate(rotation=rotation_to_apply, anchor=pivot_point)


# --- 4. Prepare for Force Calculation ---
# Set the numerical integration mesh on the target object.
# This is a critical step required by magpylib-force.
target_magnet.meshing = (5, 5, 5)

# The getFT function requires sources and targets to be in lists.
sources_list = [source_magnet]
targets_list = [target_magnet]

# --- 5. Compute Force and Torque ---
# Call the getFT function from the magpylib-force extension.
force_and_torque_data = getFT(sources_list, targets_list, anchor=(0, 0, 0))

# --- 6. Extract and Display Results ---
# The output for a single target is a 2D array of shape (2, 3).
force_N = force_and_torque_data[0]
torque_Nm = force_and_torque_data[1]

print("\n--- Simulation Results ---")
print(f"Force vector (Fx, Fy, Fz):  ({force_N[0]:.4f}, {force_N[1]:.4f}, {force_N[2]:.4f}) Newtons")
print(f"Torque vector (Tx, Ty, Tz): ({torque_Nm[0]:.4f}, {torque_Nm[1]:.4f}, {torque_Nm[2]:.4f}) Newton-meters")

# Provide a more intuitive measure of the forces
# For this angled geometry, both attraction and shear are significant.
# A negative Fz indicates attraction towards the source magnet.
# A positive Fx indicates a shearing force trying to slide the magnets apart.
attractive_force = -force_N[2]
shear_force = force_N[0]
total_force_magnitude = np.linalg.norm(force_N)


print(f"\nAttractive Force Component (Z-axis): {attractive_force:.4f} N")
print(f"Shear Force Component (X-axis):      {shear_force:.4f} N")
print(f"Total Force Magnitude:               {total_force_magnitude:.4f} N")


# --- 7. (Optional) Visualize the System ---
# This helps confirm the geometry is correct.
print("\nShowing system geometry...")
magpy.show(source_magnet, target_magnet, backend='matplotlib')
