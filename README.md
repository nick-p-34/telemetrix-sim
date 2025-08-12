# Telemetrix Sim

**Telemetrix Sim** is a demo application designed to work with Telemetrix, by simulating a race car and emitting the generated telemetry.
It was built as a learning project and portfolio piece to demonstrate complex mathematical models and cross-system integration.

## Features
- **Vehicle presets** with real-life values (power, weight, fuel capacity, gear ratios, etc.)
- **Track preset** for cars to run on, including functional pitlane and a mix of corners
- **Utility class** to calculate vehicle dynamics based on vehicle attributes
- **Telemetrix integration**, allowing data to be streamed to the `/telemetry/recent` REST endpoint

---

## Example Use Case
Imagine you’re running a car at a race event:
1. The car leaves the garage → transponder & sensors activate
2. Sensors measure car performance & parameters
3. Transponder emits values measured from car
4. Emitted values are received by Telemetrix → data can be displayed on pit wall

---

## Tech Stack
- Python 3.13
- requests 2.31.0

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/nick-p-34/telemetrix-sim.git
cd telemetrix-sim
```

### 2. OPTIONAL - Start Telemetrix
Follow the instructions in the [Telemetrix repo](https://github.com/nick-p-34/telemetrix)

### 3. Run the application
```bash
python run.py
```
This will start the app using default values.

---

## Run parameters

The above command can be modified by providing values for the following parameters:

### `--enable-20hz-logging`
- **Description:** Enables high-frequency telemetry logging at 20 Hz (20 samples per second), producing more granular data.
- **Expected values:** `true` or `false`
- **Default value:** `false`
- **Usage:**
```bash
python run.py --enable-20hz-logging
```

### `--send-to-server`
- **Description:** Sends generated telemetry data to a running Telemetrix server instance instead of writing CSV files locally.
- **Expected values:** `true` or `false`
- **Default value:** `false`
- **Usage:**
```bash
python run.py --send-to-server
```

### `--sim-time-s`
- **Description:** The length, in seconds, of the simulated session. Actual session length will be extended to allow for completion of the final lap.
- **Expected values:** `int` or `float`, positive values
- **Default value:** `360.0`
- **Usage:**
```bash
python run.py --sim-time-s 150
```

### `--car-id`
- **Description:** The racing number of the car. Purely for customisation or identification purposes, non essential.
- **Expected values:** `string`, in the format: `#` followed by `int`
- **Default value:** `#34`
- **Usage:**
```bash
python run.py --car-id #1
```

### `--driver`
- **Description:** The name of the driver. Purely for customisation or identification purposes, non essential.
- **Expected values:** `string`
- **Default value:** `"Nick Parke"`
- **Usage:**
```bash
python run.py --driver "Max Verstappen"
```

### `--team`
- **Description:** The name of the team. Purely for customisation or identification purposes, non essential.
- **Expected values:** `string`
- **Default value:** `"Zenith Racing"`
- **Usage:**
```bash
python run.py --team "Red Bull Racing"
```

### `--vehicle-preset`
- **Description:** The class of vehicle that will be used in the simulation. Determines the vehicle parameters used in calculations.
- **Expected values:** `gt3`, `f1`, `tcr`, `lmdh`
- **Default value:** `gt3`
- **Usage:**
```bash
python run.py --vehicle-preset f1
```

---

## Example: Combining parameters

You can combine multiple parameters in a single run command.  
For example, to create a **1-hour session**,  
**stream data to Telemetrix**,  
**disable 20Hz logging**,  
and run as the **Iron Dames**
by combining the following parameters:

```bash
python run.py \
  --sim-time-s 3600 \
  --send-to-server \
  --vehicle-preset gt3 \
  --team "Iron Dames" \
  --driver "Sarah Bovy" \
  --car-id #85
```
