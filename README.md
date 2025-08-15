# Telemetrix Sim

**Telemetrix Sim** is a demo application designed to work with [Telemetrix](https://github.com/nick-p-34/telemetrix), by simulating a race car and emitting the generated telemetry.
It was built as a learning project and portfolio piece to demonstrate complex mathematical models and cross-system integration.

## Features
- **Vehicle presets** with real-life values (power, weight, fuel capacity, gear ratios, etc.)
- **Fictional track** preset for cars to run on, including functional pit lane and a mix of corner profiles
- **Utility class** to calculate vehicle dynamics based on vehicle attributes
- **[Telemetrix](https://github.com/nick-p-34/telemetrix) integration**, allowing data to be streamed to the `/telemetry/recent` REST endpoint

---

## Example Use Case
Imagine you’re running a car at a race event:
1. The car leaves the garage → transponder & sensors activate
2. Sensors measure car performance & parameters
3. Transponder emits values measured from car
4. Emitted values received by Telemetrix → can be displayed on pit wall

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

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. OPTIONAL - Start Telemetrix
Follow the instructions in the [Telemetrix repo](https://github.com/nick-p-34/telemetrix)

### 4. Run the application
```bash
python run.py
```
This will start the app using default values, and output the results to `telemetry_log.csv`.

---

## Run parameters

The above run command can be modified by providing values for the following parameters:

### `--enable-20hz-logging`
- **Description:** Enables high-frequency telemetry logging at 20 Hz (20 samples per second), producing more granular data.
- **Expected values:**
  - `true`: Stream full telemetry. `true` can be omitted in the command
  - `false`: Stream only timing gate events. Whole parameter can be omitted
- **Default value:** `false`
- **Usage:**
```bash
python run.py --enable-20hz-logging
```

### `--send-to-server`
- **Description:** Sends generated telemetry data to a running Telemetrix server instance instead of writing CSV files locally.
- **Expected values:**
  - `true`: Stream to Telemetrix. An instance of Telemetrix must be running (Step 3)
  - `false`: Stream to local `telemetry_log.csv` file. File is created if it does not exist
- **Default value:** `false`
- **Usage:**
```bash
python run.py --send-to-server
```

### `--stint-time-s`
- **Description:** The length, in seconds, of the simulated stint. Actual stint length will be extended to allow for completion of the final lap.
- **Expected values:** `int` or `float`, positive values
- **Default value:** `360.0`
- **Usage:**
```bash
python run.py --sim-time-s 150
```

### `--car-id`
- **Description:** The racing number of the car. Purely for customisation or identification purposes, non-essential.
- **Expected values:** `string`, in the format: `#` followed by `int`
- **Default value:** `"#34"`
- **Usage:**
```bash
python run.py --car-id "#1"
```

### `--driver`
- **Description:** The name of the driver. Purely for customisation or identification purposes, non-essential.
- **Expected values:** `string`
- **Default value:** `"Nick Parke"`
- **Usage:**
```bash
python run.py --driver "Max Verstappen"
```

### `--team`
- **Description:** The name of the team. Purely for customisation or identification purposes, non-essential.
- **Expected values:** `string`
- **Default value:** `"Zenith Racing"`
- **Usage:**
```bash
python run.py --team "Red Bull Racing"
```

### `--vehicle-preset`
- **Description:** The class of vehicle that will be used in the simulation. Determines the vehicle parameters used in calculations.
- **Expected values:**
  - `f1`: Formula One
  - `indycar`: IndyCar Series
  - `nascar`: NASCAR Cup Series
  - `lmdh`: WEC Hypercar, IMSA GTP
  - `lmp2`: WEC, IMSA LMP2
  - `gt3`: SRO GT3, IMSA GTD
  - `gt4`: SRO GT4, IMSA GSX
  - `tcr`: Touring Car, BTCC
  - `mx5`: Global Mazda MX-5 Cup
  - `vee`: Formula Vee
  - `zetec`: ICCR Fiesta Zetec, Kirkistown Fiestas
  - `legend`: ICCR Legends, MSVR Legend Cars, INEX Legends
- **Default value:** `gt3`
- **Usage:**
```bash
python run.py --vehicle-preset f1
```

---

## Example: Combining parameters

You can combine multiple parameters in a single run command.  
For example, to run the car for **1 hour**,  
**stream data to Telemetrix**,  
**disable 20Hz logging**,  
and run as the **Iron Dames**, combine the following parameters:

```bash
python run.py \
  --stint-time-s 3600 \
  --send-to-server \
  --team "Iron Dames" \
  --driver "Sarah Bovy" \
  --car-id "#85"
```

By omitting `--enable-20hz-logging` and `vehicle-preset`, their default values, `false` and `gt3` are used.
