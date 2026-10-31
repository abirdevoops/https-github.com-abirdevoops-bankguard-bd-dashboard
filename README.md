# BANKGUARD BD — Riverbank Intelligence Command Center

The interface follows the supplied H2O GUARD reference layout: gradient header, five sensor cards, a full-width status strip, a live trend panel, and a right-side risk gauge. BANKGUARD-specific readings and Bangladesh river-monitoring context replace the waterlogging metrics.

**Real-time riverbank erosion and slope-instability monitoring prototype**  
Designed for a student hardware + software demonstration in Bangladesh.

The dashboard uses a dark navy / teal visual theme and supports:

- Demo mode with clearly labelled simulated readings
- ThingSpeak live data from an ESP32
- Bank retreat calculation against a calibrated baseline
- Slope tilt, soil moisture and river-level monitoring
- A transparent prototype risk indicator (0–100)
- Live trend charts, a schematic digital twin and an event panel

> **Important:** BANKGUARD BD is an educational prototype. Its risk score is a rule-based demonstration indicator, not a scientifically validated erosion forecast, official warning, or substitute for BWDB/local authority monitoring. Field validation and engineering review are required before any real-world use.

## 1. Project files

```text
BANKGUARD_BD_Streamlit/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml.example
└── hardware/
    ├── BANKGUARD_ESP32.ino
    └── secrets.h.example
```

## 2. Run the dashboard on your computer

### Step 1 — Install Python

Install Python 3.11 or 3.12 from https://www.python.org/downloads/.

During installation on Windows, tick **Add Python to PATH**.

### Step 2 — Extract the ZIP

Extract `BANKGUARD_BD_Streamlit.zip` to a folder, for example:

`C:\Users\YourName\Desktop\BANKGUARD_BD_Streamlit`

### Step 3 — Open the folder in VS Code

Install Visual Studio Code if needed: https://code.visualstudio.com/

In VS Code choose **File → Open Folder** and select the extracted project folder.

### Step 4 — Open the terminal

In VS Code choose **Terminal → New Terminal**.

Run:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

If `py` does not work, try `python` instead.

### Step 5 — Start the dashboard

```bash
streamlit run app.py
```

Your browser should open:

`http://localhost:8501`

Start with **Demo Mode**. Try Stable bank, Early warning, Active erosion and Critical instability from the sidebar.

## 3. Create a ThingSpeak channel

1. Open https://thingspeak.mathworks.com/ and create/sign in to a MathWorks account.
2. Open **Channels → My Channels → New Channel**.
3. Set the channel name to `BANKGUARD BD`.
4. Enable and name these fields exactly:

| ThingSpeak field | Field name | Unit |
|---|---|---|
| Field 1 | Bank_Distance | cm |
| Field 2 | Slope_Tilt | degree |
| Field 3 | Soil_Moisture | % |
| Field 4 | River_Distance | cm |
| Field 5 | Flow_Rate | L/min |

5. Save the channel.
6. Open **API Keys**.
7. Copy the **Write API Key** for the ESP32 firmware.
8. Copy the **Read API Key** for the Streamlit dashboard if the channel is private.

ThingSpeak free accounts have a minimum 15-second update interval per channel. The supplied ESP32 sketch uploads every 20 seconds to stay above that limit.

## 4. Configure Streamlit secrets

### Local computer

1. Open the `.streamlit` folder.
2. Make a copy of `secrets.toml.example`.
3. Rename the copy to `secrets.toml`.
4. Replace the placeholders:

```toml
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"
THINGSPEAK_READ_API_KEY = "YOUR_READ_API_KEY"
```

5. Save it.

Do not upload `secrets.toml` to GitHub. It is excluded by `.gitignore`.

### Streamlit Community Cloud

When deploying, open **Advanced settings → Secrets** and paste the same two lines into the Secrets box. Save/deploy.

## 5. ESP32 sensor wiring

Board: ESP32 DevKit V1.

| Component | ESP32 connection |
|---|---|
| Bank HC-SR04 TRIG | GPIO 16 |
| Bank HC-SR04 ECHO | GPIO 18 through voltage divider |
| River HC-SR04 TRIG | GPIO 19 |
| River HC-SR04 ECHO | GPIO 23 through voltage divider |
| MPU6050 SDA | GPIO 21 |
| MPU6050 SCL | GPIO 22 |
| Capacitive soil sensor AO | GPIO 34 |
| YF-S201 flow signal | GPIO 27 (optional) |
| Sensor grounds | Common GND |

**Electrical safety:**
- ESP32 GPIO pins are 3.3V logic. Do not connect a 5V HC-SR04 ECHO signal directly to an ESP32 pin. Use a voltage divider for each ECHO.
- Verify that the soil sensor's analog output never exceeds 3.3V. Use a divider if necessary.
- Use a separate suitable supply and MOSFET/transistor driver for the water pump. Never power a pump directly from an ESP32 GPIO.
- Keep the ESP32 and exposed electronics away from water.
- Connect grounds together for the sensor signal circuits.
- MPU6050 must be mounted firmly on a small plate that moves with the model bank.

## 6. Upload the ESP32 firmware

1. Open Arduino IDE.
2. Install the ESP32 board package by Espressif Systems.
3. In Library Manager install:
   - Adafruit MPU6050
   - Adafruit Unified Sensor
4. Copy `hardware/secrets.h.example` to `hardware/secrets.h`.
5. Open `hardware/BANKGUARD_ESP32.ino`.
6. Fill in Wi-Fi name/password and ThingSpeak Write API key in `secrets.h`.
7. Check sensor wiring and calibration constants in the sketch.
8. Select **ESP32 Dev Module** and the correct COM port.
9. Upload the sketch.
10. Open Serial Monitor at 115200 baud.

The firmware sends:
- Field 1: bank distance in cm
- Field 2: tilt angle in degrees
- Field 3: soil moisture percentage
- Field 4: river sensor distance in cm
- Field 5: flow rate in L/min (optional; zero if disabled)

The ESP32 uploads every 20 seconds. The Streamlit dashboard can refresh every 10 seconds, but a new sensor record will only arrive after the next accepted ThingSpeak upload.

### Important calibration

- `BANK_BASELINE_CM`: distance from the fixed bank sensor to the stable bank face.
- `TILT_BASELINE_DEG`: stable tilt reading after the MPU6050 is mounted.
- `SOIL_DRY_RAW` and `SOIL_WET_RAW`: measure your own sensor readings in dry and wet soil before setting these.
- `RIVER_SENSOR_HEIGHT_CM`: distance from the river sensor to the channel bottom.
- `FLOW_PULSES_PER_LITER`: calibrate the YF-S201 against a measured water volume. If no flow sensor is installed, set `USE_FLOW_SENSOR` to `false`.

The Streamlit sidebar has corresponding baseline settings. Make sure they match your physical setup.

## 7. Deploy on Streamlit Community Cloud

1. Sign in to GitHub: https://github.com/
2. Create a new repository named `bankguard-bd-dashboard`.
3. Keep it Public for the easiest deployment, or grant Streamlit access if you choose Private.
4. Upload all project files and folders from the extracted ZIP. Do not upload:
   - `.venv/`
   - `.streamlit/secrets.toml`
   - `hardware/secrets.h`
5. Commit the files to the `main` branch.
6. Open https://share.streamlit.io/
7. Sign in with GitHub and authorize Streamlit.
8. Click **Create app**.
9. Select your repository: `bankguard-bd-dashboard`.
10. Branch: `main`.
11. Main file path: `app.py`.
12. Open **Advanced settings → Secrets** and paste:

```toml
THINGSPEAK_CHANNEL_ID = "YOUR_CHANNEL_ID"
THINGSPEAK_READ_API_KEY = "YOUR_READ_API_KEY"
```

13. Click **Deploy**.
14. Wait for the app to build and open the generated `*.streamlit.app` URL.

When you push code changes to the connected GitHub repository, Community Cloud normally updates the app automatically.

## 8. How to demonstrate it to judges

1. Open the deployed dashboard in a phone or laptop.
2. Use Demo Mode first to explain the interface.
3. For actual hardware demonstration, select **ThingSpeak Live** and enter your channel ID/read key if not stored in secrets.
4. Start the water-flow experiment.
5. Record the stable bank distance and tilt baseline.
6. Let the water gradually affect the soil bank.
7. Show the bank-distance, moisture and tilt readings changing.
8. Show the dashboard trend and prototype risk indicator updating.

Never present simulated readings as real experimental results. Clearly label the demo mode.

## 9. Troubleshooting

| Problem | Check |
|---|---|
| `ModuleNotFoundError` | Run `py -m pip install -r requirements.txt` |
| Streamlit command not found | Activate `.venv`, then run `py -m streamlit run app.py` |
| ThingSpeak has no data | Check Channel ID, field mapping, Wi-Fi and Write API Key |
| Private channel returns no data | Check the Read API Key |
| Data appears stale | Check ESP32 power/Wi-Fi; free ThingSpeak writes are limited to one per 15 seconds |
| Bank retreat is negative/zero | Recheck sensor orientation and stable baseline |
| Soil percentage is wrong | Calibrate dry and wet raw ADC readings |
| MPU6050 tilt is unstable | Fix the module firmly and set the baseline after mounting |

## 10. Security

- Never commit `secrets.toml` or `hardware/secrets.h`.
- Never publish your ThingSpeak Write API Key.
- If a key is exposed, regenerate it in ThingSpeak.
- The ESP32 example uses HTTPS with certificate verification disabled for a beginner prototype. For a production deployment, install and validate the correct root CA certificate.

## 11. Research honesty

This dashboard visualizes sensor readings and calculates a transparent, rule-based prototype risk indicator. It does not provide a validated prediction of real riverbank failure. A real deployment requires calibrated instruments, long-term field measurements, geotechnical validation and review by qualified authorities.

---
**BANKGUARD BD | BAUET Poster Spark 2026**
