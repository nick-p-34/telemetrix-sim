import argparse
import constants
from sim import Sim
from track import SEGMENTS, GATES
from vehicle import VEHICLE_PARAMS, VEHICLE_PRESETS


def main():
    parser = argparse.ArgumentParser(description="Race Simulator")
    parser.add_argument("--enable-20hz-logging", action="store_true", help="When writing to the CSV file, include all telemetry events (20 per second) in the file")
    parser.add_argument("--send-to-server", action="store_true", help="Send telemetry data to server instead of the CSV file. Telemetrix must be running")
    parser.add_argument("--sim-time-s", type=float, default=360.0, help="Simulated session length in seconds.")
    parser.add_argument("--car-id", type=str, default="#34")
    parser.add_argument("--driver", type=str, default="Nick Parke")
    parser.add_argument("--team", type=str, default="Zenith Racing")
    parser.add_argument("--vehicle-preset", type=str, default="gt3", help="Which vehicle preset to use. E.g. \"f1\", \"lmdh\"")
    args = parser.parse_args()

    constants.ENABLE_20HZ_LOGGING = args.enable_20hz_logging
    constants.SEND_TO_SERVER = args.send_to_server

    preset_name = args.vehicle_preset

    if preset_name not in VEHICLE_PRESETS:
        print(f"Unknown vehicle preset '{preset_name}', using default (GT3).")
        params = VEHICLE_PARAMS

    else:
        params = VEHICLE_PRESETS[preset_name]

    params = dict(params)
    params["preset_name"] = preset_name

    sim = Sim(params, SEGMENTS, GATES, dt=constants.DT)
    sim.state.position_m = 0.0
    sim.state.speed_mps = 5.0
    sim.state.fuel_l = params["fuel_capacity_l"]
    sim.state.tyre_wear = 0.0
    sim.state.gear = 1

    events = sim.run(sim_time_s=args.sim_time_s, car_id=args.car_id, driver=args.driver, team=args.team)
    print(f"Sim produced {len(events)} telemetry events.")


if __name__ == "__main__":
    main()
