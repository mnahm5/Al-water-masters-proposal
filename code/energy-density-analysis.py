#!/usr/bin/env python3
import json
import matplotlib.pyplot as plt  # pyright: ignore[reportMissingImports]
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

eff_mass_energy_densities = []
eff_volumetric_energy_densities = []

categories = []

for fuel_key, fuel_data in fuels.items():
    name = fuel_data['name']

    # Skip Coal, H2_Gas, and fuels with metal oxide in name
    if name == "Coal" or name == "H2_Gas" or name == "CNG":
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

    # Default calculation
    eff_mass_energy_density = mass_energy * efficiency
    eff_volumetric_energy_density = vol_energy * efficiency

    # Determine category for coloring
    if display_name in ["H2", "NH3"]:
        category = "Simple Electro-fuels"
    elif display_name in ["Diesel", "Petrol", "Methanol", "Ethanol", "LNG", "LPG"]:
        category = "Synthetic Hydrocarbons"
    elif display_name in ["Fe", "Al", "Mg", "B", "Si", "Zn"]:
        category = "Simple Metal Fuels"
    elif display_name in ["MgH2", "AlH3", "LiAlH4", "NaBH4", "LiBH4", "NaAlH4"]:
        category = "Metal Hydrides"
    elif display_name == "HFO":
        category = "HFO"
    else:
        category = "Other"

    fuel_names.append(display_name)
    mass_energy_densities.append(mass_energy)
    volumetric_energy_densities.append(vol_energy)
    eff_mass_energy_densities.append(eff_mass_energy_density)
    eff_volumetric_energy_densities.append(eff_volumetric_energy_density)
    categories.append(category)

# Create scatter plot
color_map = {
    "Simple Electro-fuels": "#3498db",  # Blue
    "Synthetic Hydrocarbons": "#e74c3c",   # Red
    "Simple Metal Fuels": "#2ecc71",    # Green
    "Metal Hydrides": "#f39c12", # Orange
    "HFO": "#9b59b6"             # Purple
}

plt.figure(figsize=(12, 8))
for category in color_map.keys():
    mask = [cat == category for cat in categories]
    x = [mass_energy_densities[i] for i in range(len(mask)) if mask[i]]
    y = [volumetric_energy_densities[i] for i in range(len(mask)) if mask[i]]
    plt.scatter(x, y, s=50, alpha=0.6, color=color_map[category], label=category)

plt.legend(loc='best', fontsize=10)

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
plt.grid(True, alpha=0.7, linestyle='-', linewidth=1.2, color='grey')
plt.savefig('fuel_energy_density.png', dpi=300, bbox_inches='tight')
plt.savefig('../images/simplified_fuel_energy_density.png', dpi=300, bbox_inches='tight')
print("\nPlot saved as 'fuel_energy_density.png'")

# Print summary statistics
print("\nFuel Energy Density Summary:")
print("=" * 70)
print(f"{'Fuel':<25} {'Mass (kWh/kg)':<15} {'Volumetric (kWh/L)':<20}")
print("=" * 70)
for i in range(len(fuel_names)):
    print(f"{fuel_names[i]:<25} {mass_energy_densities[i]:<15.2f} {volumetric_energy_densities[i]:<20.2f}")
print("=" * 70)

# Adjust metal fuels to use their oxide effective energy densities
metal_oxide_map = {
    "Fe": "Fe3O4",
    "Al": ["Al2O3", "AlOOH"],  # Al has two oxides
    "Mg": "MgO",
    "B": "B2O3",
    "Si": "SiO2",
    "Zn": "ZnO"
}

# For Al, we'll need to process both oxides separately
adjusted_fuel_names = []
adjusted_eff_mass_energy = []
adjusted_eff_vol_energy = []
adjusted_categories = []

for i, name in enumerate(fuel_names):
    if name in metal_oxide_map:
        # This is a simple metal fuel, replace with oxide(s)
        oxide_names = metal_oxide_map[name]
        if not isinstance(oxide_names, list):
            oxide_names = [oxide_names]

        for oxide_name in oxide_names:
            # Find the oxide in the original fuels data
            oxide_fuel = next((fuels[k] for k in fuels if fuels[k]['name'] == oxide_name), None)
            if oxide_fuel:
                oxide_density = oxide_fuel['density']
                oxide_mass_energy = oxide_fuel['mass_energy_density']
                oxide_efficiency = oxide_fuel['engine_efficiency']

                adjusted_fuel_names.append(oxide_name)
                adjusted_eff_mass_energy.append(oxide_mass_energy * oxide_efficiency)
                adjusted_eff_vol_energy.append(oxide_mass_energy * oxide_efficiency * oxide_density)
                adjusted_categories.append(categories[i])
    else:
        # Keep non-metal fuels as is
        adjusted_fuel_names.append(name)
        adjusted_eff_mass_energy.append(eff_mass_energy_densities[i])
        adjusted_eff_vol_energy.append(eff_volumetric_energy_densities[i])
        adjusted_categories.append(categories[i])

# Replace the original lists with adjusted ones for the second plot
fuel_names_for_plot2 = adjusted_fuel_names
eff_mass_energy_densities = adjusted_eff_mass_energy
eff_volumetric_energy_densities = adjusted_eff_vol_energy
categories_for_plot2 = adjusted_categories

plt.figure(figsize=(12, 8))
for category in color_map.keys():
    mask = [cat == category for cat in categories_for_plot2]
    x = [eff_mass_energy_densities[i] for i in range(len(mask)) if mask[i]]
    y = [eff_volumetric_energy_densities[i] for i in range(len(mask)) if mask[i]]
    plt.scatter(x, y, s=50, alpha=0.6, color=color_map[category], label=category)

plt.legend(loc='best', fontsize=10)

# Add labels for each point with adjustText to avoid overlap
# Calculate offset distance based on data range
x_range = max(eff_mass_energy_densities) - min(eff_mass_energy_densities)
y_range = max(eff_volumetric_energy_densities) - min(eff_volumetric_energy_densities)
offset_x = x_range * 0.00375  # 0.375% of x range
offset_y = y_range * 0.00375  # 0.375% of y range

texts = []
for i, name in enumerate(fuel_names_for_plot2):
    # Start text at an offset position from the point
    txt = plt.text(eff_mass_energy_densities[i] + offset_x,
                   eff_volumetric_energy_densities[i] + offset_y,
                   name,
                   fontsize=11, fontweight='bold', alpha=0.8)
    texts.append(txt)

# Adjust text positions to avoid overlap with much larger spacing
adjust_text(texts,
            eff_mass_energy_densities, eff_volumetric_energy_densities,
            arrowprops=dict(arrowstyle='->', color='gray', lw=0.5, alpha=0.6),
            expand_points=(1.25, 1.25),
            expand_text=(1, 1),
            force_points=0.625,
            force_text=0.625,
            lim=50,
            only_move={'points':'xy', 'text':'xy'})

plt.xlabel('Eff. Mass Energy Density (kWh/kg)', fontsize=12)
plt.ylabel('Eff. Volumetric Energy Density (kWh/L)', fontsize=12)
plt.title('Eff. Fuel Energy Density Comparison', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.7, linestyle='-', linewidth=1.2, color='grey')
plt.savefig('eff_fuel_energy_density.png', dpi=300, bbox_inches='tight')
plt.savefig('../images/eff_fuel_energy_density.png', dpi=300, bbox_inches='tight')
print("\nPlot saved as 'eff_fuel_energy_density.png'")