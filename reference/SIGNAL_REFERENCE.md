# Signal Reference Guide

Complete reference for all 44 signals in the RCA dataset.

---

## Battery Subsystem (19 signals)

### Cell Temperatures

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| TEMP_BATTERY_CELL_01 | Cell 1 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_02 | Cell 2 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_03 | Cell 3 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_04 | Cell 4 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_05 | Cell 5 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_06 | Cell 6 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_07 | Cell 7 temperature | °C | 20-45 | 10-55 | -10-60 |
| TEMP_BATTERY_CELL_08 | Cell 8 temperature | °C | 20-45 | 10-55 | -10-60 |

**Notes**:
- Adjacent cells (e.g., 01 and 02) share heat through conduction
- Temperature rise indicates insufficient cooling or internal issue
- Rapid rise (>1°C/min) is concerning

### Cell Voltages

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| VOLTAGE_CELL_01 | Cell 1 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_02 | Cell 2 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_03 | Cell 3 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_04 | Cell 4 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_05 | Cell 5 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_06 | Cell 6 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_07 | Cell 7 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |
| VOLTAGE_CELL_08 | Cell 8 voltage | V | 3.2-4.2 | 3.0-4.25 | 2.5-4.35 |

**Notes**:
- All cells should track together (within 50mV)
- One cell diverging indicates cell imbalance/degradation
- Voltage drops with temperature (reversible) and degradation (permanent)

### Pack-Level

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| CURRENT_BATTERY | Pack current (+ = charging) | A | -200 to 200 | -250 to 250 | -300 to 300 |
| SOC_BATTERY | State of charge | % | 10-90 | 5-95 | 0-100 |
| SOH_BATTERY | State of health | % | 80-100 | 70-100 | 50-100 |

**Notes**:
- Current positive = charging, negative = discharging
- SOC estimates remaining capacity
- SOH indicates long-term degradation

---

## Cooling Subsystem (8 signals)

### Pump

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| PUMP_COOLANT_FLOW | Pump speed command | % | 20-100 | 10-100 | 0-100 |
| PUMP_CURRENT | Pump motor current | A | 2-15 | 0.5-20 | 0-25 |

**Notes**:
- PUMP_COOLANT_FLOW is the commanded speed
- Current near 0 with non-zero command = pump failure
- Current too high = pump obstruction/failure

### Flow and Temperature

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| COOLANT_FLOW_RATE | Measured coolant flow | L/min | 5-20 | 2-25 | 0-30 |
| TEMP_COOLANT_IN | Coolant inlet temp | °C | 15-35 | 10-45 | 0-55 |
| TEMP_COOLANT_OUT | Coolant outlet temp | °C | 20-45 | 15-55 | 5-65 |

**Notes**:
- Delta T (out - in) indicates heat absorbed
- Delta T > 15°C suggests high heat load or low flow
- Inlet temp rises if fan/radiator ineffective

### Radiator Fan

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| FAN_SPEED_RADIATOR | Fan rotational speed | RPM | 0-5000 | 0-5500 | 0-6000 |
| FAN_CURRENT | Fan motor current | A | 0-25 | 0-30 | 0-35 |

**Notes**:
- Fan off (0 RPM) at low temps is normal
- Fan off when coolant hot = fan failure

### Thermal Valve

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| VALVE_THERMAL_POSITION | Thermal valve position | % | 0-100 | 0-100 | 0-100 |

**Notes**:
- 0% = full bypass (no cooling)
- 100% = full cooling mode
- Stuck valve causes temperature regulation issues

---

## Motor Subsystem (10 signals)

### Speed and Torque

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| MOTOR_SPEED_RPM | Motor rotational speed | RPM | 0-15000 | 0-16000 | 0-18000 |
| MOTOR_TORQUE | Torque output (- = regen) | Nm | -400 to 400 | -450 to 450 | -500 to 500 |

**Notes**:
- Negative torque = regenerative braking
- Speed and torque determine power output

### Temperatures

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| TEMP_MOTOR_STATOR | Stator winding temp | °C | 30-120 | 20-140 | 0-160 |
| TEMP_MOTOR_ROTOR | Rotor temp | °C | 30-130 | 20-150 | 0-170 |

**Notes**:
- Stator heats from I²R losses
- Rotor heats from hysteresis and conduction from stator
- Rotor lags stator by 15-45 seconds

### Phase Currents

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| CURRENT_MOTOR_PHASE_A | Phase A current | A | -300 to 300 | -350 to 350 | -400 to 400 |
| CURRENT_MOTOR_PHASE_B | Phase B current | A | -300 to 300 | -350 to 350 | -400 to 400 |
| CURRENT_MOTOR_PHASE_C | Phase C current | A | -300 to 300 | -350 to 350 | -400 to 400 |

**Notes**:
- Three phases are 120° apart
- Sum of all three should be ~0
- Imbalance indicates winding or inverter issue

### Vibration

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| VIBRATION_MOTOR_X | X-axis vibration | g | 0-0.5 | 0-1.0 | 0-2.0 |
| VIBRATION_MOTOR_Y | Y-axis vibration | g | 0-0.5 | 0-1.0 | 0-2.0 |
| VIBRATION_MOTOR_Z | Z-axis (axial) vibration | g | 0-0.5 | 0-1.0 | 0-2.0 |

**Notes**:
- All axes typically correlate
- Gradual increase suggests bearing wear
- Related to motor speed (higher RPM = higher baseline)

---

## Electrical Subsystem (6 signals)

### High Voltage

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| VOLTAGE_HV_BUS | HV DC bus voltage | V | 300-420 | 280-440 | 250-460 |
| CURRENT_HV_BUS | HV bus current | A | -250 to 250 | -300 to 300 | -350 to 350 |

**Notes**:
- HV bus ≈ sum of all cell voltages
- Current mirrors battery current closely

### Low Voltage

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| VOLTAGE_LV_BUS | 12V auxiliary bus | V | 11.5-14.5 | 10.5-15.5 | 9.0-16.0 |

**Notes**:
- Powers control electronics
- Low voltage can cause control issues

### Safety Systems

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| ISOLATION_RESISTANCE | HV isolation to chassis | kΩ | >500 | >100 | >0 |
| CONTACTOR_STATE_POS | Positive contactor state | bool | 0 or 1 | 0 or 1 | 0 or 1 |
| CONTACTOR_STATE_NEG | Negative contactor state | bool | 0 or 1 | 0 or 1 | 0 or 1 |

**Notes**:
- Isolation < 100 kΩ triggers safety shutdown
- Contactors: 1 = closed (connected), 0 = open
- Both contactors should match (both open or both closed)

---

## Sensor Health (1 signal)

| Signal ID | Description | Unit | Normal | Warning | Critical |
|-----------|-------------|------|--------|---------|----------|
| DATA_QUALITY_SCORE | Overall data quality | % | 95-100 | 80-100 | 0-100 |

**Notes**:
- Aggregates sensor health across system
- Drop indicates sensor issues, not necessarily real failures

---

## Signal Relationships Quick Reference

### Direct Proportional (↑ causes ↑)

| Cause | Effect | Lag |
|-------|--------|-----|
| PUMP_COOLANT_FLOW | COOLANT_FLOW_RATE | 2-5s |
| PUMP_COOLANT_FLOW | PUMP_CURRENT | <1s |
| FAN_SPEED_RADIATOR | FAN_CURRENT | <1s |
| MOTOR_TORQUE | CURRENT_MOTOR_PHASE_* | <1s |
| MOTOR_TORQUE | CURRENT_BATTERY | <1s |
| MOTOR_TORQUE | TEMP_MOTOR_STATOR | 30-60s |
| TEMP_MOTOR_STATOR | TEMP_MOTOR_ROTOR | 15-45s |
| TEMP_BATTERY_CELL_01 | TEMP_BATTERY_CELL_02 | 3-10s |

### Inverse Proportional (↑ causes ↓)

| Cause | Effect | Lag |
|-------|--------|-----|
| COOLANT_FLOW_RATE | TEMP_BATTERY_CELL_* | 15-30s |
| FAN_SPEED_RADIATOR | TEMP_COOLANT_IN | 10-20s |
| TEMP_BATTERY_CELL_* | VOLTAGE_CELL_* | 30-60s |

### Threshold Relationships

| Cause | Effect | Threshold |
|-------|--------|-----------|
| ISOLATION_RESISTANCE < 100 kΩ | CONTACTOR_STATE → 0 | Safety trip |
| TEMP_MOTOR_STATOR > 140°C | MOTOR_TORQUE limited | Thermal derate |
| TEMP_BATTERY_CELL > 55°C | CURRENT_BATTERY limited | Thermal derate |

---

## Anomaly Signatures by Failure Type

### Pump Failure
```
PUMP_COOLANT_FLOW: Step decrease
PUMP_CURRENT: Step decrease (near zero)
COOLANT_FLOW_RATE: Gradual decrease
TEMP_COOLANT_OUT: Gradual increase
TEMP_BATTERY_CELL_*: Gradual increase (cascade)
```

### Fan Failure
```
FAN_SPEED_RADIATOR: Step decrease to 0
FAN_CURRENT: Step decrease to ~0
TEMP_COOLANT_IN: Gradual increase
TEMP_COOLANT_OUT: Gradual increase
TEMP_BATTERY_CELL_*: Gradual increase
```

### Cell Imbalance
```
VOLTAGE_CELL_XX: Gradual drift (one cell only)
TEMP_BATTERY_CELL_XX: Slight increase (same cell)
SOC_BATTERY: May show increased noise
Other cells: Normal
```

### Motor Overtemperature
```
MOTOR_TORQUE: High sustained value
CURRENT_MOTOR_PHASE_*: High sustained
TEMP_MOTOR_STATOR: Gradual increase
TEMP_MOTOR_ROTOR: Gradual increase (lagged)
```

### Ground Fault
```
ISOLATION_RESISTANCE: Sudden drop
CONTACTOR_STATE_*: Immediate open (0)
VOLTAGE_HV_BUS: Immediate drop to 0
MOTOR_TORQUE: Immediate drop to 0
```

### Bearing Wear
```
VIBRATION_MOTOR_*: Gradual increase (all axes)
TEMP_MOTOR_ROTOR: Gradual increase
Efficiency: May decrease (more current for same torque)
```

---

## Signal Quality Notes

### Sampling
- All signals: 10 Hz (100ms between samples)
- 30 minutes = 18,000 samples per signal

### Noise Levels (typical)
- Temperature signals: ±0.5°C
- Voltage signals: ±10mV
- Current signals: ±2A
- Flow rate: ±0.5 L/min
- Vibration: ±0.02g

### Common Sensor Faults
- **Stuck value**: Same value for extended period
- **Spike**: Brief impossible value
- **Drift**: Gradual offset from true value
- **Noise**: Excessive random variation
