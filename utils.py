import math
from constants import G, FUEL_HEATING_VALUE_KJ_PER_KG


def clamp(v, a, b):
    return max(a, min(b, v))


def power_limited_speed(power_kw: float, CdA: float, rho: float) -> float:
    return (power_kw * 1000.0 / (0.5 * rho * CdA)) ** (1.0 / 3.0)


def corner_target_speed(radius_m: float, tyre_mu: float) -> float:
    return math.sqrt(tyre_mu * G * radius_m)


def engine_power_at_rpm(rpm, peak_kw, rpm_peak, redline):
    if rpm <= 0.0:
        return 0.0

    width = rpm_peak * 0.45
    rpm = min(rpm, redline)
    val = math.exp(-0.5 * ((rpm - rpm_peak) / width) ** 2)
    return peak_kw * val


def wheel_angular_speed_from_vehicle_speed(v_mps, wheel_radius_m):
    return v_mps / wheel_radius_m


def rpm_from_speed_and_gear(speed_mps, gear_ratio, final_drive, wheel_radius_m):
    wheel_rads = wheel_angular_speed_from_vehicle_speed(speed_mps, wheel_radius_m)
    engine_rads = wheel_rads * gear_ratio * final_drive
    return engine_rads * 60.0 / (2 * math.pi)


def max_braking_force(mass_kg, tyre_mu, g, brake_g_limit):
    return mass_kg * g * min(tyre_mu, brake_g_limit)


def fuel_consumption_lps(power_kw, engine_efficiency, fuel_density_kg_per_l):
    if power_kw <= 0.0:
        return 0.0008

    input_kW = power_kw / max(0.01, engine_efficiency)
    input_kJ_per_s = input_kW
    kg_per_s = input_kJ_per_s / FUEL_HEATING_VALUE_KJ_PER_KG
    return kg_per_s / fuel_density_kg_per_l
