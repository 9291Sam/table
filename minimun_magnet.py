import numpy as np
import magpylib as magpy
from scipy.spatial.transform import Rotation as R

# CORRECTED: Import the getFT function from the magpylib-force extension.
# This is the dedicated tool for force and torque calculations.
from magpylib_force import getFT

# --- 1. Define System Parameters ---
# All units must be SI (meters, Tesla) for magpylib v5+

# --- Geometry ---
# These now represent cylindrical electromagnets
cylinder_diameter_m = 0.012  # 12 mm diameter
cylinder_length_m = 0.015   # 15 mm length

# --- Positioning ---
# Distance between the closest flat edges of the two cylinders
gap_mm = 1.0
# The angle between adjacent faces of a dodecagon is 30 degrees.
angle_deg = 30.0

# --- Magnet Properties ---
# Polarization for a strong NdFeB magnet (e.g., N42 grade)
# This simulates the strength of the electromagnet's core.
magnet_pol_T = 1.3

print(f"Simulating for a {gap_mm} mm edge-gap and {angle_deg}-degree angle (Dodecagon face)...")

# --- 2. Create Magpylib Objects ---
# Create the stationary source magnet, centered at the origin
# The default orientation has its axis along Z.
source_magnet = magpy.magnet.Cylinder(
    polarization=(0, 0, magnet_pol_T),
    dimension=(cylinder_diameter_m, cylinder_length_m)
)

# Create the target magnet, which will experience the force
target_magnet = magpy.magnet.Cylinder(
    polarization=(0, 0, magnet_pol_T),
    dimension=(cylinder_diameter_m, cylinder_length_m)
)

# --- 3. Position and Orient the Magnets for Dodecagon Geometry ---
# To simulate adjacent faces of a dodecagon, we position and rotate the target
# magnet relative to the stationary source magnet.

# First, rotate the target magnet by the dodecagon angle around the Y-axis.
target_magnet.orientation = R.from_euler('y', angle_deg, degrees=True)

# Now, calculate the position to achieve the desired edge-to-edge gap.
# This requires trigonometry to find the center-to-center distance.
angle_rad = np.deg2rad(angle_deg)
# The distance from the center to the flat face is half the length.
center_to_face = cylinder_length_m / 2
# The total distance needed along the rotated axis.
total_dist = center_to_face + (gap_mm / 1000) + center_to_face
# We find the required center position using the law of cosines.
# For simplicity, we can approximate the center position based on the angle.
# Position the magnet so its center is displaced correctly.
cx = np.sin(angle_rad) * total_dist
cz = np.cos(angle_rad) * total_dist
target_magnet.position = (cx, 0, cz)


# --- 4. Prepare for Force Calculation ---
# Set the numerical integration mesh on the target object.
# This is a critical step required by magpylib-force.
# A finer mesh increases accuracy but slows computation.
target_magnet.meshing = (5, 5, 5)

# The getFT function requires sources and targets to be in lists.
sources_list = [source_magnet]
targets_list = [target_magnet]

# --- 5. Compute Force and Torque ---
# Call the getFT function from the magpylib-force extension.
force_and_torque_data = getFT(sources_list, targets_list, anchor=(0, 0, 0))

# --- 6. Extract and Display Results ---
# The output for a single target is a 2D array of shape (2, 3).
# The first row is the force vector, the second is the torque vector.
force_N = force_and_torque_data[0]
torque_Nm = force_and_torque_data[1]

print("\n--- Simulation Results ---")
print(f"Force vector (Fx, Fy, Fz):  ({force_N[0]:.4f}, {force_N[1]:.4f}, {force_N[2]:.4f}) Newtons")
print(f"Torque vector (Tx, Ty, Tz): ({torque_Nm[0]:.4f}, {torque_Nm[1]:.4f}, {torque_Nm[2]:.4f}) Newton-meters")

# Provide a more intuitive measure of the forces
# For this geometry, the attractive force is primarily along the Z-axis,
# and the shear/sliding force is along the X-axis.
attractive_force = -force_N[2]
shear_force = force_N[0]

print(f"\nPrimary Attractive Force: {attractive_force:.4f} N")
print(f"Shear (Sliding) Force:    {shear_force:.4f} N")

# --- 7. (Optional) Visualize the System ---
# This helps confirm the geometry is correct.
print("\nShowing system geometry...")
magpy.show(source_magnet, target_magnet, backend='matplotlib')
