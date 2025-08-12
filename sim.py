import math
import random
import time
from typing import List, Dict, Optional
from state import CarState, TelemetryEvent
from track import Segment
import track
from utils import (
    clamp,
    power_limited_speed,
    corner_target_speed,
    engine_power_at_rpm,
    rpm_from_speed_and_gear,
    max_braking_force,
    fuel_consumption_lps,
)
from sender import send_event
import constants


class Sim:
    def __init__(self, params: dict, segments: List[Segment], gates: Dict[int, float], dt: float = 0.05):
        self.params = params
        self.segments = segments
        self.lap_length = segments[-1].cumulative_end
        self.last_lap_start_time: Optional[float] = 0.0
        self.dt = dt
        self.gates = gates

        self.state = CarState()
        self.state.fuel_l = self.params.get("fuel_capacity_l", 0.0)
        self._shift_end_time: float = 0.0
        self.event_count: int = 0
        self.prev_gate_index = max(self.gates.keys())
        self.prev_gate_time = 0.0
        self.last_print = time.time()

        self.segment_targets = [self.compute_segment_target(seg) for seg in self.segments]

        self.driver_params = {
            "driver_skill": self.params.get("driver_skill", 0.9),
            "steering_response_time": self.params.get("steering_response_time", 0.12),
            "steering_noise_std_deg": self.params.get("steering_noise_std_deg", 1.5),
            "lap_bias_std_deg": self.params.get("lap_bias_std_deg", 3.0),
            "aggressiveness": self.params.get("aggressiveness", 0.5),
            "steering_ratio_variation": self.params.get("steering_ratio_variation", 0.02),
        }

        self.driver_state = {"target_wheel_deg": 0.0, "actual_wheel_deg": 0.0,
                             "lap_bias_deg": random.gauss(0.0, self.driver_params["lap_bias_std_deg"])}
        self._last_lap_for_bias = self.state.lap

    def compute_segment_target(self, seg: Segment) -> float:
        mu = self.params["tyre_mu_initial"] * (1.0 - self.state.tyre_wear * 0.5)

        if seg.typ == "arc" and seg.radius and seg.radius > 5.0:
            v = corner_target_speed(seg.radius, mu)  # m/s
            return max(6.0, v * 0.92)

        else:
            v = power_limited_speed(self.params["peak_power_kw"], self.params["CdA"], self.params["air_density"])
            return v * 0.98

    def find_segment_index(self, pos: float) -> int:
        p = pos % self.lap_length

        for i, s in enumerate(self.segments):
            if s.cumulative_start <= p < s.cumulative_end:
                return i

        return len(self.segments) - 1

    def update(self, dt: float):
        s = self.state
        p = s.position_m % self.lap_length
        seg_idx = self.find_segment_index(s.position_m)
        seg = self.segments[seg_idx]

        base_mu = self.params["tyre_mu_initial"] * (1.0 - s.tyre_wear * 0.5)

        if seg.typ == "arc" and seg.radius and seg.radius > 1.0:
            wheelbase = self.params.get("wheelbase_m", 2.8)
            steering_ratio = self.params.get("steering_ratio", 14.0)
            steering_lock = self.params.get("steering_lock_deg", 180.0)

            delta_rad = math.atan2(wheelbase, seg.radius)
            ideal_front_deg = math.degrees(delta_rad)
            ideal_wheel_deg = ideal_front_deg * steering_ratio

            if s.lap != self._last_lap_for_bias:
                self.driver_state["lap_bias_deg"] = random.gauss(0.0, self.driver_params["lap_bias_std_deg"])
                self._last_lap_for_bias = s.lap

            desired_wheel_deg = ideal_wheel_deg

            if seg.direction == "L":
                desired_wheel_deg = -abs(desired_wheel_deg)

            elif seg.direction == "R":
                desired_wheel_deg = abs(desired_wheel_deg)

            sr_variation = 1.0 + random.gauss(0.0, self.driver_params["steering_ratio_variation"])
            desired_wheel_deg = (desired_wheel_deg * sr_variation) + self.driver_state["lap_bias_deg"]

            rt = max(0.01, self.driver_params["steering_response_time"])
            alpha = (dt / (rt + 1e-9))
            self.driver_state["target_wheel_deg"] += alpha * (desired_wheel_deg - self.driver_state["target_wheel_deg"])

            skill = clamp(self.driver_params["driver_skill"], 0.0, 1.0)
            noise_std = max(0.0, self.driver_params["steering_noise_std_deg"]) * (1.0 - skill)
            noise = random.gauss(0.0, noise_std)

            hand_rt = max(0.02, self.driver_params["steering_response_time"] * 0.6)
            hand_alpha = (dt / (hand_rt + 1e-9))
            self.driver_state["actual_wheel_deg"] += hand_alpha * (
                        (self.driver_state["target_wheel_deg"] + noise) - self.driver_state["actual_wheel_deg"])

            s.steering_deg = clamp(self.driver_state["actual_wheel_deg"], -steering_lock, steering_lock)

            steering_error = abs(self.driver_state["actual_wheel_deg"] - ideal_wheel_deg)

            lock = steering_lock
            k_penalty = 0.6
            aggress = clamp(self.driver_params["aggressiveness"], 0.0, 1.0)
            grip_penalty = (k_penalty * (steering_error / (lock + 1e-9))) * (1.0 - skill) * (1.0 - 0.4 * aggress)
            grip_penalty = clamp(grip_penalty, 0.0, 0.7)
            effective_mu = base_mu * (1.0 - grip_penalty)

            target_speed = max(6.0, corner_target_speed(seg.radius, effective_mu) * 0.92)

        else:
            target_speed = power_limited_speed(self.params["peak_power_kw"], self.params["CdA"], self.params["air_density"]) * 0.98
            rt = max(0.05, self.driver_params["steering_response_time"])
            alpha = (dt / (rt + 1e-9))

            self.driver_state["target_wheel_deg"] += alpha * (0.0 - self.driver_state["target_wheel_deg"])
            hand_rt = max(0.02, self.driver_params["steering_response_time"] * 0.6)
            hand_alpha = (dt / (hand_rt + 1e-9))

            self.driver_state["actual_wheel_deg"] += hand_alpha * (self.driver_state["target_wheel_deg"] - self.driver_state["actual_wheel_deg"])
            s.steering_deg = clamp(self.driver_state["actual_wheel_deg"], -self.params.get("steering_lock_deg", 180.0), self.params.get("steering_lock_deg", 180.0))

        outlap_speed_mps = track.OUTLAP_SPEED_KMH / 3.6
        outlap_end_pos = track.OUTLAP_END_POS_M % self.lap_length
        pos_on_lap = s.position_m % self.lap_length

        if s.lap == 1 and pos_on_lap < outlap_end_pos:
            target_speed = min(target_speed, outlap_speed_mps)

        speed = s.speed_mps
        speed_err = target_speed - speed
        kp = 0.8
        kd = 0.1
        accel_cmd = clamp(kp * speed_err - kd * 0.0, -5.0, 7.0)

        if accel_cmd >= 0:
            s.throttle = clamp(accel_cmd / 6.0, 0.0, 1.0)
            s.brake = 0.0

        else:
            s.brake = clamp(-accel_cmd / 7.0, 0.0, 1.0)
            s.throttle = 0.0

        if seg.typ == "arc" and seg.radius and seg.radius < 60.0:
            seg_end_dist = seg.cumulative_end - p if seg.cumulative_end > p else (
                        self.lap_length - p + seg.cumulative_end)

            if seg_end_dist < 40.0:
                s.brake = max(s.brake, 0.8)

        best_gear = s.gear
        best_score = float('inf')

        for g_idx, gr in enumerate(self.params["gear_ratios"], start=1):
            rpm_guess = rpm_from_speed_and_gear(speed, gr, self.params["final_drive"], self.params["wheel_radius_m"])
            rpm_target = 0.65 * self.params["power_rpm_peak"]
            score = abs(rpm_guess - rpm_target)

            if rpm_guess > self.params["redline_rpm"]:
                score += 1e4

            if score < best_score:
                best_score = score
                best_gear = g_idx

        if best_gear != s.gear:
            s.gear = best_gear
            s.rpm = min(self.params["redline_rpm"], s.rpm * 1.05 + 200.0)
            self._shift_end_time = s.time_s + self.params.get("gear_shift_duration", 0.05)
            s.throttle = 0.0

        gr = self.params["gear_ratios"][s.gear - 1]
        s.rpm = rpm_from_speed_and_gear(s.speed_mps, gr, self.params["final_drive"], self.params["wheel_radius_m"])
        s.rpm = clamp(s.rpm, 700.0, self.params["redline_rpm"])

        available_kw = engine_power_at_rpm(s.rpm, self.params["peak_power_kw"], self.params["power_rpm_peak"], self.params["redline_rpm"])

        if getattr(self, "_shift_end_time", 0.0) > s.time_s:
            available_kw = 0.0

        else:
            self._shift_end_time = 0.0

        if s.speed_mps > 1.0:
            wheel_force_from_power = (available_kw * 1000.0 * self.params["drivetrain_eff"]) / max(1e-3, s.speed_mps)

        else:
            wheel_force_from_power = (available_kw * 1000.0 * self.params["drivetrain_eff"]) / 1.0

        drive_force = wheel_force_from_power * s.throttle

        F_aero = 0.5 * self.params["air_density"] * self.params["CdA"] * (s.speed_mps ** 2)
        F_roll = self.params["c_rr"] * self.params["mass_kg_with_fuel"] * constants.G

        max_brake_force = max_braking_force(self.params["mass_kg_with_fuel"],
                                            self.params["tyre_mu_initial"] * (1.0 - s.tyre_wear * 0.5),
                                            constants.G, self.params["brake_max_g"])
        brake_force = s.brake * max_brake_force

        net_force = drive_force - F_aero - F_roll - brake_force
        accel = net_force / self.params["mass_kg_with_fuel"]

        s.speed_mps = max(0.0, s.speed_mps + accel * dt)

        mech_power_used = available_kw * s.throttle
        fuel_lps = fuel_consumption_lps(mech_power_used, self.params["engine_efficiency"],
                                        self.params["fuel_density_kg_per_l"])
        s.fuel_l = max(0.0, s.fuel_l - fuel_lps * dt)

        lat_accel = 0.0
        if seg.typ == "arc" and seg.radius and seg.radius > 1.0:
            lat_accel = (s.speed_mps ** 2) / seg.radius

        wear_inc = self.params["tyre_wear_rate_base"] * (1.0 + abs(lat_accel) / (0.5 * constants.G)) * (
                    1.0 + 0.5 * s.throttle + 0.5 * s.brake)
        s.tyre_wear = clamp(s.tyre_wear + wear_inc * dt, 0.0, 0.99)

        s.steering_deg = clamp(s.steering_deg, -self.params.get("steering_lock_deg", 180.0),
                               self.params.get("steering_lock_deg", 180.0))

        prev_pos = s.position_m
        s.position_m += s.speed_mps * dt
        s.time_s += dt

        if prev_pos % self.lap_length > s.position_m % self.lap_length:
            s.lap += 1

        return {
            "accel": accel,
            "available_kw": available_kw,
            "mech_power_used_kw": mech_power_used,
            "fuel_lps": fuel_lps,
            "lat_accel": lat_accel,
            "segment_idx": seg_idx,
            "target_speed": target_speed,
            "steering_wheel_deg": s.steering_deg,
        }

    def check_gates_and_emit(self, car_id: str = "#34", driver: str = "Nick Parke", team: str = "Zenith Racing"):
        s = self.state
        prev_pos = (s.position_m - s.speed_mps * self.dt) % self.lap_length
        cur_pos = s.position_m % self.lap_length

        for gate_no, gate_dist in self.gates.items():
            gd = gate_dist % self.lap_length
            crossed = False

            if prev_pos <= cur_pos:
                if prev_pos < gd <= cur_pos:
                    crossed = True

            else:
                if prev_pos < gd <= self.lap_length or 0.0 <= gd <= cur_pos:
                    crossed = True

            if crossed:
                split_time = s.time_s - self.prev_gate_time
                self.prev_gate_time = s.time_s
                self.prev_gate_index = gate_no

                if gate_no == max(self.gates.keys()):
                    if self.last_lap_start_time is None:
                        self.last_lap_start_time = s.time_s
                        lap_time = None

                    else:
                        lap_time = s.time_s - self.last_lap_start_time
                        self.last_lap_start_time = s.time_s

                    if s.lap <= 1:
                        lap_time = None

                else:
                    lap_time = None

                evt = TelemetryEvent(
                    timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    carId=car_id,
                    driver=driver,
                    team=team,
                    lap=s.lap,
                    gate=gate_no,
                    split_time=round(split_time, 3),
                    speed_kmh=round(s.speed_mps * 3.6, 3),
                    rpm=int(round(s.rpm)),
                    gear=s.gear,
                    throttle=round(s.throttle, 3),
                    brake=round(s.brake, 3),
                    steering_deg=round(s.steering_deg, 2),
                    fuel_l=round(s.fuel_l, 3),
                    tyre_wear=round(s.tyre_wear, 4),
                    lap_time=round(lap_time, 3) if lap_time is not None else None,
                    race_time=round(s.time_s, 3),
                    extra={"position_m": round(s.position_m % self.lap_length, 3)},
                )

                self.event_count += 1
                self._emit_event(evt)

    def _emit_event(self, evt: TelemetryEvent):
        j = {
            "carId": evt.carId,
            "driver": evt.driver,
            "team": evt.team,
            "vehicle_class": self.params.get("preset_name"),
            "lap": evt.lap,
            "speed": evt.speed_kmh,
            "rpm": evt.rpm,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "gate": evt.gate,
            "split_time": evt.split_time,
            "gear": evt.gear,
            "throttle": evt.throttle,
            "brake": evt.brake,
            "steering_deg": evt.steering_deg,
            "fuel_l": evt.fuel_l,
            "tyre_wear": evt.tyre_wear,
            "lap_time": evt.lap_time,
            "race_time": evt.race_time,
            "position_m": evt.extra.get("position_m"),
        }

        if constants.ENABLE_20HZ_LOGGING or evt.gate is not None:
            send_event(j)

    def emit_current_telemetry_event(self, car_id: str = "#34", driver: str = "Nick Parke", team: str = "Zenith Racing"):
        s = self.state
        evt = TelemetryEvent(
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            carId=car_id,
            driver=driver,
            team=team,
            lap=s.lap,
            gate=None,
            split_time=None,
            speed_kmh=round(s.speed_mps * 3.6, 3),
            rpm=int(round(s.rpm)),
            gear=s.gear,
            throttle=round(s.throttle, 3),
            brake=round(s.brake, 3),
            steering_deg=round(s.steering_deg, 2),
            fuel_l=round(s.fuel_l, 3),
            tyre_wear=round(s.tyre_wear, 4),
            lap_time=None,
            race_time=round(s.time_s, 3),
            extra={"position_m": round(s.position_m % self.lap_length, 3)},
        )

        self.event_count += 1
        self._emit_event(evt)

    def run(self, sim_time_s: float = 200.0, car_id: str = "#34", driver: str = "Nick Parke", team: str = "Zenith Racing"):
        steps = int(sim_time_s / self.dt)

        for _ in range(steps):
            diagnostics = self.update(self.dt)

            self.check_gates_and_emit(car_id, driver, team)

            if constants.ENABLE_20HZ_LOGGING:
                self.emit_current_telemetry_event(car_id, driver, team)

            if random.random() < 0.02:
                self.segment_targets = [self.compute_segment_target(seg) for seg in self.segments]

        return self.event_count
