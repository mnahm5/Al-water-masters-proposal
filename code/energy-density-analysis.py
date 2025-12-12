#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]
import numpy as np  # pyright: ignore[reportMissingImports]
from adjustText import adjust_text  # pyright: ignore[reportMissingImports]

# Load the JSON file
with open('fuel-dataset.json', 'r') as f:
    data = json.load(f)

# Extract fuel data
fuels = data['fuels']

# Calculate effective mass and volumetric energy densities
fuel_names = []
mass_energy_densities = []
volumetric_energy_densities = []

for fuel_key, fuel_data in fuels.items():
    name = fuel_data['name']

    # Skip Coal, H2_Gas, and fuels with metal oxide in name
    if name == "Coal" or name == "H2_Gas":
        continue
    if "->" in name:  # Skip metal oxide combustion fuels (e.g., "MgH2->MgO")
        continue
    # Skip pure metal oxides (Fe3O4, AlOOH, Al2O3, MgO, B2O3, SiO2, ZnO)
    if "O" in name and any(char.isdigit() or char == "O" for char in name) and "_ref" not in name:
        # Check if it's a metal oxide (contains O and numbers/O, but not a reference)
        if name in ["Fe3O4", "AlOOH", "Al2O3", "MgO", "B2O3", "SiO2", "ZnO"]:
            continue

    density = fuel_data['density']  # kg/l
    mass_energy = fuel_data['mass_energy_density']  # kWh/kg
    efficiency = fuel_data['engine_efficiency']

    # Calculate volumetric energy density
    vol_energy = mass_energy * density

    # Clean up metal names
    display_name = name.replace(" (ref)", "")

    # Replace full metal names with symbols
    metal_symbols = {
        "Iron": "Fe",
        "Aluminium": "Al",
        "Magnesium": "Mg",
        "Boron": "B",
        "Si": "Si",
        "Zinc": "Zn"
    }
    for metal, symbol in metal_symbols.items():
        if display_name == metal:
            display_name = symbol
            break

    # Simplify other fuel names
    name_simplifications = {
        "Pressure_Tank_H2": "H2",
        "Liquid_NH3": "NH3",
        "Heavy Fuel Oil": "HFO"
    }
    if display_name in name_simplifications:
        display_name = name_simplifications[display_name]

    fuel_names.append(display_name)
    mass_energy_densities.append(mass_energy)
    volumetric_energy_densities.append(vol_energy)

# Create scatter plot
plt.figure(figsize=(12, 8))
plt.scatter(mass_energy_densities, volumetric_energy_densities, s=50, alpha=0.6)

# Add labels for each point with adjustText to avoid overlap
# Calculate offset distance based on data range
x_range = max(mass_energy_densities) - min(mass_energy_densities)
y_range = max(volumetric_energy_densities) - min(volumetric_energy_densities)
offset_x = x_range * 0.00375  # 0.375% of x range
offset_y = y_range * 0.00375  # 0.375% of y range

texts = []
for i, name in enumerate(fuel_names):
    # Start text at an offset position from the point
    txt = plt.text(mass_energy_densities[i] + offset_x, 
                   volumetric_energy_densities[i] + offset_y, 
                   name,
                   fontsize=11, fontweight='bold', alpha=0.8)
    texts.append(txt)

# Adjust text positions to avoid overlap with much larger spacing
adjust_text(texts,
            mass_energy_densities, volumetric_energy_densities,
            arrowprops=dict(arrowstyle='->', color='gray', lw=0.5, alpha=0.6),
            expand_points=(1.25, 1.25),
            expand_text=(1, 1),
            force_points=0.625,
            force_text=0.625,
            lim=50,
            only_move={'points':'xy', 'text':'xy'})

plt.xlabel('Mass Energy Density (kWh/kg)', fontsize=12)
plt.ylabel('Volumetric Energy Density (kWh/L)', fontsize=12)
plt.title('Fuel Energy Density Comparison', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.savefig('fuel_energy_density.png', dpi=300, bbox_inches='tight')
print("\nPlot saved as 'fuel_energy_density.png'")

# Print summary statistics
print("\nFuel Energy Density Summary:")
print("=" * 70)
print(f"{'Fuel':<25} {'Mass (kWh/kg)':<15} {'Volumetric (kWh/L)':<20}")
print("=" * 70)
for i in range(len(fuel_names)):
    print(f"{fuel_names[i]:<25} {mass_energy_densities[i]:<15.2f} {volumetric_energy_densities[i]:<20.2f}")
print("=" * 70)