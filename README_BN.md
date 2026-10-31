# BANKGUARD BD — বাংলা সেটআপ গাইড

Dashboard-এর Layout তোমার দেওয়া H2O GUARD Screenshot অনুসরণ করে তৈরি: gradient header, পাঁচটি sensor card, status strip, বাম পাশে live trend graph এবং ডান পাশে risk gauge। শুধু metrics ও project content BANKGUARD BD অনুযায়ী।

**প্রজেক্ট:** Real-Time Riverbank Erosion & Slope Instability Monitoring  
**Controller:** ESP32 DevKit V1  
**Dashboard:** Streamlit  
**Cloud data bridge:** ThingSpeak

> সতর্কতা: এটি বিশ্ববিদ্যালয়ের প্রদর্শনীর জন্য একটি শিক্ষামূলক Prototype। এর Risk Indicator কোনো বৈজ্ঞানিকভাবে যাচাইকৃত নদীভাঙনের পূর্বাভাস বা সরকারি জরুরি সতর্কতা নয়। বাস্তবে ব্যবহারের আগে দীর্ঘমেয়াদি মাঠপর্যায়ের পরীক্ষা ও বিশেষজ্ঞ যাচাই প্রয়োজন।

## ১. ZIP Extract করো

`BANKGUARD_BD_Streamlit_GitHub_Ready.zip` ফাইলটি Download করে Extract করো। ভেতরে `BANKGUARD_BD_Streamlit` নামে Folder পাবে।

## ২. কম্পিউটারে Dashboard চালাও

১. Python 3.11 বা 3.12 Install করো: https://www.python.org/downloads/  
২. VS Code Install করো: https://code.visualstudio.com/  
৩. VS Code খুলে **File → Open Folder** থেকে `BANKGUARD_BD_Streamlit` Folder নির্বাচন করো।  
৪. **Terminal → New Terminal** খুলে নিচের Command চালাও:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

৫. Dashboard চালাও:

```bash
streamlit run app.py
```

৬. Browser-এ `http://localhost:8501` খুলবে। প্রথমে Sidebar থেকে **Demo Mode** নির্বাচন করে চারটি Scenario দেখো:
- Stable bank
- Early warning
- Active erosion
- Critical instability

Demo Mode-এর data কৃত্রিমভাবে তৈরি করা। এটিকে বাস্তব Sensor reading বলে দেখাবে না।

## ৩. ThingSpeak Channel তৈরি

১. https://thingspeak.mathworks.com/ এ যাও এবং Account তৈরি/Sign in করো।  
২. **Channels → My Channels → New Channel** নির্বাচন করো।  
৩. Channel name দাও: `BANKGUARD BD`  
৪. নিচের Field-গুলো Enable করে নাম দাও:

| Field | নাম | Unit |
|---|---|---|
| 1 | Bank_Distance | cm |
| 2 | Slope_Tilt | degree |
| 3 | Soil_Moisture | % |
| 4 | River_Distance | cm |
| 5 | Flow_Rate | L/min |

৫. Save করো।  
৬. Channel-এর **API Keys** tab খুলে Write API Key ও Read API Key আলাদা করে রাখো।

Free ThingSpeak account-এ একই Channel-এ অন্তত ১৫ সেকেন্ড ব্যবধানে data upload করতে হয়। আমাদের ESP32 code ২০ সেকেন্ড পরপর upload করে।

## ৪. Streamlit-এর Secret সেট করো

Project Folder-এর `.streamlit` Folder খুলে `secrets.toml.example` ফাইলটির Copy তৈরি করো। Copy-টির নাম দাও `secrets.toml`।

ফাইলটি খুলে নিজের তথ্য বসাও:

```toml
THINGSPEAK_CHANNEL_ID = "তোমার_CHANNEL_ID"
THINGSPEAK_READ_API_KEY = "তোমার_READ_API_KEY"
```

এটি GitHub-এ Upload করবে না। `.gitignore` ফাইলে এটি বাদ দেওয়া আছে।

Public ThingSpeak Channel হলে Read API Key ফাঁকা রাখা যায়। Private Channel হলে Read API Key প্রয়োজন।

## ৫. ESP32 Wiring

ESP32 DevKit V1-এর জন্য:

| Component | ESP32 Pin |
|---|---|
| Bank HC-SR04 TRIG | GPIO 16 |
| Bank HC-SR04 ECHO | GPIO 18 — Voltage Divider দিয়ে |
| River HC-SR04 TRIG | GPIO 19 |
| River HC-SR04 ECHO | GPIO 23 — Voltage Divider দিয়ে |
| MPU6050 SDA | GPIO 21 |
| MPU6050 SCL | GPIO 22 |
| Soil Sensor AO | GPIO 34 |
| YF-S201 Signal | GPIO 27 — Optional |

**সতর্কতা:**
- ESP32 GPIO 3.3V logic ব্যবহার করে। HC-SR04 ECHO-এর 5V output সরাসরি ESP32-তে দেবে না। প্রতিটি ECHO-তে Voltage Divider ব্যবহার করো।
- Soil sensor-এর AO যেন 3.3V-এর বেশি না হয়। প্রয়োজন হলে Voltage Divider ব্যবহার করো।
- Pump সরাসরি ESP32 GPIO থেকে চালাবে না। আলাদা উপযুক্ত Power Supply এবং MOSFET/Transistor Driver ব্যবহার করো।
- সব Sensor Signal Circuit-এর GND Common রাখো।
- ESP32 ও Breadboard পানি থেকে দূরে রাখো।

## ৬. Arduino IDE-তে Firmware Upload

১. Arduino IDE Install করো।  
২. Board Manager থেকে **esp32 by Espressif Systems** Install করো।  
৩. Library Manager থেকে Install করো:
   - Adafruit MPU6050
   - Adafruit Unified Sensor
৪. `hardware` Folder-এর `secrets.h.example` Copy করে একই Folder-এ `secrets.h` নামে Save করো।  
৫. `secrets.h`-এ নিজের Wi-Fi ও ThingSpeak Write API Key বসাও:

```cpp
#define WIFI_SSID "তোমার_WIFI_NAME"
#define WIFI_PASSWORD "তোমার_WIFI_PASSWORD"
#define THINGSPEAK_WRITE_API_KEY "তোমার_WRITE_API_KEY"
```

৬. `hardware/BANKGUARD_ESP32.ino` Arduino IDE-তে Open করো।  
৭. নিজের মডেল অনুযায়ী Calibration Value ঠিক করো:
   - `BANK_BASELINE_CM`: স্থির অবস্থায় Bank Sensor থেকে মাটির দূরত্ব।
   - `TILT_BASELINE_DEG`: MPU6050 স্থির অবস্থায় যে angle দেখায়।
   - `SOIL_DRY_RAW`: শুকনো মাটিতে ADC reading।
   - `SOIL_WET_RAW`: ভেজা মাটিতে ADC reading।
   - `RIVER_SENSOR_HEIGHT_CM`: River Sensor থেকে Channel Bottom-এর দূরত্ব।
   - `FLOW_PULSES_PER_LITER`: Flow Sensor-এর calibration value।

৮. Tools → Board → ESP32 Dev Module নির্বাচন করো।  
৯. সঠিক COM Port নির্বাচন করো।  
১০. Upload চাপো।  
১১. Serial Monitor খুলে Baud Rate `115200` নির্বাচন করো।

## ৭. GitHub-এ Upload

১. GitHub Account-এ Sign in করো: https://github.com/  
২. **New repository** চাপো।  
৩. Repository name দাও: `bankguard-bd-dashboard`।  
৪. Public নির্বাচন করলে সহজে Streamlit deploy করতে পারবে।  
৫. GitHub Desktop ব্যবহার করলে Hidden `.streamlit` Folder-সহ সব ফাইল সহজে Commit করা যায়।  
৬. ZIP Extract করা Project Folder-এর ফাইলগুলো Repository-তে রাখো।  
৭. Commit message দাও: `Initial BANKGUARD BD dashboard`।  
৮. **Publish repository / Push origin** চাপো।

**কখনো Upload করবে না:**
- `.streamlit/secrets.toml`
- `hardware/secrets.h`
- `.venv/`

শুধু `.example` ফাইলগুলো GitHub-এ থাকবে।

## ৮. Streamlit Community Cloud-এ Deploy

১. https://share.streamlit.io/ খুলে GitHub দিয়ে Sign in করো।  
২. Streamlit-কে GitHub access অনুমতি দাও।  
৩. **Create app** চাপো।  
৪. Repository: `bankguard-bd-dashboard` নির্বাচন করো।  
৫. Branch: `main` নির্বাচন করো।  
৬. Main file path: `app.py` দাও।  
৭. **Advanced settings → Secrets**-এ এই দুই লাইন বসাও:

```toml
THINGSPEAK_CHANNEL_ID = "তোমার_CHANNEL_ID"
THINGSPEAK_READ_API_KEY = "তোমার_READ_API_KEY"
```

৮. Deploy চাপো।  
৯. Build শেষ হলে তোমার Dashboard-এর `*.streamlit.app` Link তৈরি হবে।

## ৯. Judges-এর সামনে Demonstration

১. প্রথমে Demo Mode-এ Dashboard-এর Feature দেখাও।  
২. এরপর ThingSpeak Live নির্বাচন করো।  
৩. ESP32 চালু করে Wi-Fi ও Cloud upload নিশ্চিত করো।  
৪. Stable অবস্থায় Bank Distance ও Tilt Baseline Record করো।  
৫. Pump চালিয়ে ধীরে ধীরে পানি প্রবাহিত করো।  
৬. Soil Moisture, Bank Distance ও Tilt-এর পরিবর্তন দেখাও।  
৭. মোবাইল/ল্যাপটপে Live Graph ও Risk Indicator দেখাও।

**মনে রাখবে:** Demo Mode-এর simulated data এবং Live Mode-এর actual sensor data কখনো এক করে দেখাবে না।

## ১০. সমস্যা হলে

| সমস্যা | সমাধান |
|---|---|
| `ModuleNotFoundError` | `py -m pip install -r requirements.txt` চালাও |
| `streamlit` command পাওয়া যাচ্ছে না | `.venv` Activate করে `py -m streamlit run app.py` চালাও |
| ThingSpeak data আসছে না | Channel ID, Field mapping, Wi-Fi ও Write API Key পরীক্ষা করো |
| Private Channel পড়তে পারছে না | Read API Key পরীক্ষা করো |
| Data stale দেখাচ্ছে | ESP32 power, Wi-Fi ও upload interval পরীক্ষা করো |
| Bank retreat শূন্য | Sensor orientation ও baseline পরীক্ষা করো |
| Soil percentage ভুল | Dry ও wet soil-এ ADC calibration করো |
| MPU6050 কাজ করছে না | SDA=21, SCL=22, VCC ও GND পরীক্ষা করো |

## ১১. Security

- `secrets.toml` এবং `secrets.h` GitHub-এ Upload করবে না।
- Write API Key কাউকে প্রকাশ করবে না।
- Key প্রকাশ হয়ে গেলে ThingSpeak থেকে নতুন Key তৈরি করবে।
- ESP32 example HTTPS ব্যবহার করে, কিন্তু সহজ Prototype-এর জন্য certificate verification বন্ধ রাখা হয়েছে। বাস্তব ব্যবহারে সঠিক Root CA Certificate যাচাই করতে হবে।

---
**BANKGUARD BD | BAUET Poster Spark 2026**


## ১২. নতুন UI সম্পর্কে

এই version-এ Dashboard Layout তোমার দেওয়া H2O GUARD Screenshot-এর খুব কাছাকাছি করে বানানো হয়েছে:

- বাম পাশে dark sidebar
- উপরে gradient hero header
- একই style-এর ৫টি metric card
- status strip
- বাম পাশে line chart
- ডান পাশে semicircle gauge
- নিচে AI performance, hotspot detection, response cards
- সবশেষে ৪টি pilot status card

শুধু project content H2O GUARD থেকে BANKGUARD BD অনুযায়ী বদলানো হয়েছে।
