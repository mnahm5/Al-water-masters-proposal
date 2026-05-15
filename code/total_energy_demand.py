total_HFO_demand_million_tonnes = 200 # 2025 estimate
total_HFO_demand_kg = total_HFO_demand_million_tonnes * 10^6 * 10^3

HFO_energy_per_kg = 11.6 # kWh/kg
total_primary_energy_HFO_kWh = total_HFO_demand_kg * HFO_energy_per_kg

HFO_engine_efficiency = 0.5
total_final_energy_HFO_kWh = total_primary_energy_HFO_kWh * HFO_engine_efficiency

# Aluminum fuel total lifecycle round trip efficiency is 20-25%
Al_round_trip_eff = 0.20
AL_engine_eff = 0.4

total_primary_energy_Al_kWh = total_final_energy_HFO_kWh / AL_engine_eff
Al_energy_density_kWh = 8.63 # kWh/kg
total_Al_needed_kg = total_primary_energy_Al_kWh / Al_energy_density_kWh

total_Al_needed_million_tonnes = total_Al_needed_kg / (10^6*10^3)

print(total_Al_needed_million_tonnes)