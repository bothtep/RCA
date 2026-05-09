# Vehicle Systems Domain Primer

This guide introduces the vehicle systems you'll be analyzing. Understanding the domain helps interpret signals and identify plausible causal relationships.

---

## Overview: Electric Vehicle Architecture

An electric vehicle (EV) consists of several interconnected subsystems:

```
┌─────────────────────────────────────────────────────────────┐
│                      Vehicle                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Battery   │───▶│   Motor     │───▶│  Wheels     │     │
│  │   Pack      │    │  Inverter   │    │             │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                 │                                  │
│         ▼                 ▼                                  │
│  ┌─────────────────────────────────────┐                    │
│  │        Cooling System               │                    │
│  │  (Pump → Coolant → Radiator → Fan)  │                    │
│  └─────────────────────────────────────┘                    │
│                      │                                       │
│  ┌─────────────────────────────────────┐                    │
│  │     Electrical Distribution         │                    │
│  │   (HV Bus, LV Bus, Contactors)      │                    │
│  └─────────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Battery System

### Components

| Component | Function |
|-----------|----------|
| **Cells** | Store electrical energy (lithium-ion) |
| **BMS** | Battery Management System - monitors and protects |
| **Contactors** | High-voltage switches to connect/disconnect pack |
| **Fuses** | Over-current protection |

### Key Signals

| Signal | What It Measures | Normal Range |
|--------|-----------------|--------------|
| TEMP_BATTERY_CELL_XX | Cell temperature | 20-45°C |
| VOLTAGE_CELL_XX | Individual cell voltage | 3.2-4.2V |
| CURRENT_BATTERY | Pack current (+ = charging) | -200 to +200A |
| SOC_BATTERY | State of Charge (remaining capacity) | 10-90% |
| SOH_BATTERY | State of Health (degradation) | 80-100% |

### Physical Relationships

1. **Temperature → Voltage**: High temperature accelerates degradation, reducing voltage
2. **Current → Temperature**: High current (I²R losses) generates heat
3. **Cell-to-Cell Heat**: Adjacent cells share heat through conduction
4. **SOC → Voltage**: SOC correlates with average cell voltage

### Common Failure Modes

| Failure | Root Cause Signal | Cascade Pattern |
|---------|-------------------|-----------------|
| Thermal runaway | TEMP_BATTERY_CELL rises | Temp↑ → Voltage↓ → More heat |
| Cell imbalance | One VOLTAGE_CELL drifts | Weak cell → Extra current → Heating |
| Capacity loss | SOH_BATTERY decreases | Less range, more charging |

---

## Cooling System

### Components

| Component | Function |
|-----------|----------|
| **Coolant Pump** | Circulates liquid coolant |
| **Coolant Loop** | Pipes carrying coolant to battery/motor |
| **Radiator** | Heat exchanger (coolant → air) |
| **Fan** | Forces air through radiator |
| **Thermal Valve** | Routes coolant (bypass or cooling) |

### Key Signals

| Signal | What It Measures | Normal Range |
|--------|-----------------|--------------|
| PUMP_COOLANT_FLOW | Pump speed command | 20-100% |
| PUMP_CURRENT | Pump motor current | 2-15A |
| COOLANT_FLOW_RATE | Measured flow | 5-20 L/min |
| TEMP_COOLANT_IN | Coolant entering battery | 15-35°C |
| TEMP_COOLANT_OUT | Coolant leaving battery | 20-45°C |
| FAN_SPEED_RADIATOR | Fan RPM | 0-5000 RPM |
| FAN_CURRENT | Fan motor current | 0-25A |
| VALVE_THERMAL_POSITION | Valve position | 0-100% |

### Physical Relationships

1. **Pump Flow → Coolant Flow**: Direct proportional (with slight lag)
2. **Pump Speed → Pump Current**: Higher speed = more current
3. **Flow Rate → Temperature**: Less flow = less heat removal = higher temps
4. **Fan Speed → Inlet Temp**: More fan = cooler radiator = cooler inlet
5. **Delta T (out - in)**: Indicates heat absorbed from battery

### Common Failure Modes

| Failure | Root Cause Signal | Cascade Pattern |
|---------|-------------------|-----------------|
| Pump failure | PUMP_COOLANT_FLOW drops | Flow↓ → Temps↑ → Derate |
| Fan failure | FAN_SPEED_RADIATOR = 0 | Inlet temp↑ → All temps↑ |
| Valve stuck | VALVE_THERMAL_POSITION fixed | Wrong routing → Temp issues |
| Coolant leak | COOLANT_FLOW_RATE drops | Gradual flow↓ → Temps↑ |

---

## Motor/Drivetrain System

### Components

| Component | Function |
|-----------|----------|
| **Motor** | Converts electrical energy to mechanical |
| **Inverter** | Converts DC to 3-phase AC |
| **Stator** | Stationary motor windings |
| **Rotor** | Rotating part with magnets |
| **Bearings** | Support rotor, reduce friction |

### Key Signals

| Signal | What It Measures | Normal Range |
|--------|-----------------|--------------|
| MOTOR_SPEED_RPM | Rotational speed | 0-15000 RPM |
| MOTOR_TORQUE | Torque output | -400 to +400 Nm |
| TEMP_MOTOR_STATOR | Stator winding temperature | 30-120°C |
| TEMP_MOTOR_ROTOR | Rotor temperature | 30-130°C |
| CURRENT_MOTOR_PHASE_A/B/C | Phase currents | -300 to +300A |
| VIBRATION_MOTOR_X/Y/Z | Vibration levels | 0-0.5g |

### Physical Relationships

1. **Torque → Current**: More torque requires more phase current
2. **Torque → Stator Temp**: Sustained high torque heats windings (I²R)
3. **Stator → Rotor Temp**: Heat transfers from stator to rotor
4. **Vibration**: All axes correlate (bearing issues affect all)
5. **Vibration → Rotor Temp**: Worn bearings create friction heat

### Common Failure Modes

| Failure | Root Cause Signal | Cascade Pattern |
|---------|-------------------|-----------------|
| Overtemperature | TEMP_MOTOR_STATOR high | Sustained load → Heat → Derate |
| Bearing wear | VIBRATION increases | Gradual vib↑ → Friction → Heat |
| Winding fault | Phase current anomaly | Current spike → Trip |

---

## Electrical System

### Components

| Component | Function |
|-----------|----------|
| **HV Bus** | High-voltage DC distribution (300-420V) |
| **LV Bus** | Low-voltage (12V) for controls |
| **Contactors** | Main battery disconnect switches |
| **Isolation Monitor** | Detects ground faults |

### Key Signals

| Signal | What It Measures | Normal Range |
|--------|-----------------|--------------|
| VOLTAGE_HV_BUS | Main bus voltage | 300-420V |
| CURRENT_HV_BUS | Bus current | -250 to +250A |
| VOLTAGE_LV_BUS | 12V system voltage | 11.5-14.5V |
| ISOLATION_RESISTANCE | HV to chassis isolation | >500 kΩ |
| CONTACTOR_STATE_POS/NEG | Contactor status | 0 (open) or 1 (closed) |

### Physical Relationships

1. **Cell Voltages → HV Bus**: HV bus ≈ sum of all cell voltages
2. **Isolation → Contactor**: Low isolation triggers safety disconnect
3. **HV Bus → Motor**: Low bus voltage limits available torque
4. **Contactor → HV Bus**: Open contactors = 0V bus

### Common Failure Modes

| Failure | Root Cause Signal | Cascade Pattern |
|---------|-------------------|-----------------|
| Ground fault | ISOLATION drops | Safety trip → Contactors open → Shutdown |
| Undervoltage | VOLTAGE_HV_BUS low | Limited power → Derate → Stop |
| Contactor weld | CONTACTOR_STATE stuck | Can't disconnect safely |

---

## Causal Relationships Summary

### Primary Causal Chains

```
Pump Failure Chain:
PUMP_COOLANT_FLOW↓ → COOLANT_FLOW_RATE↓ → TEMP_COOLANT_OUT↑ → 
TEMP_BATTERY_CELL↑ → VOLTAGE_CELL↓ → SOC_BATTERY affected

Fan Failure Chain:
FAN_SPEED↓ → TEMP_COOLANT_IN↑ → TEMP_COOLANT_OUT↑ → 
TEMP_BATTERY_CELL↑ → (similar to pump failure)

Motor Overload Chain:
MOTOR_TORQUE↑ (sustained) → CURRENT_MOTOR↑ → TEMP_MOTOR_STATOR↑ → 
TEMP_MOTOR_ROTOR↑ → Derate or shutdown

Ground Fault Chain:
ISOLATION_RESISTANCE↓ → CONTACTOR_STATE = 0 → VOLTAGE_HV_BUS = 0 →
MOTOR_TORQUE = 0 (immediate shutdown)

Battery Degradation Chain:
VOLTAGE_CELL↓ (one cell) → TEMP_BATTERY_CELL↑ (that cell) →
SOC estimation affected → Capacity reduced
```

### Typical Lag Times

| Cause | Effect | Typical Lag |
|-------|--------|-------------|
| Pump command | Flow change | 2-5 seconds |
| Flow change | Coolant temp | 10-20 seconds |
| Coolant temp | Battery temp | 15-30 seconds |
| Battery temp | Cell voltage | 30-60 seconds |
| Torque command | Motor current | <1 second |
| Motor current | Stator temp | 30-120 seconds |
| Vibration increase | Rotor temp | 1-5 minutes |
| Isolation drop | Contactor trip | <2 seconds |

---

## Tips for RCA

### What Makes a Good Root Cause

1. **Changes First**: Root cause should show anomaly before others
2. **Physically Upstream**: Should be able to affect downstream signals
3. **Matches Pattern**: Failure pattern should match known failure modes
4. **Explainable**: You can articulate why this caused the cascade

### Red Flags (Probably NOT Root Cause)

1. **Changes Last**: Late-changing signals are effects, not causes
2. **Isolated Change**: If only one signal changes with no cascade
3. **No Physical Path**: Can't explain how it would affect others
4. **Sensor Fault**: Sudden impossible values (e.g., -40°C) suggest bad sensor

### Common Mistakes

1. **Correlation ≠ Causation**: Two signals moving together doesn't mean one caused the other
2. **Ignoring Lags**: The root cause signal changes BEFORE its effects
3. **Missing Domain Knowledge**: Some relationships are non-obvious (e.g., voltage drops when hot)
4. **Control Scenario Trap**: Normal operation shouldn't have a root cause identified

---

## Glossary

| Term | Definition |
|------|------------|
| **SOC** | State of Charge - remaining battery capacity (%) |
| **SOH** | State of Health - battery degradation level (%) |
| **HV** | High Voltage (typically 300-420V in EVs) |
| **LV** | Low Voltage (12V auxiliary system) |
| **Derate** | Reduce power/performance to protect components |
| **Thermal Runaway** | Uncontrolled temperature increase in battery |
| **Contactor** | High-current electrical switch |
| **Isolation** | Electrical separation between HV and chassis |
| **BMS** | Battery Management System |
| **Inverter** | DC to AC power converter |

---

## Further Learning

- **Electric Vehicle Technology Explained** by James Larminie
- **Battery Management Systems** by Davide Andrea
- **Tesla Model 3/Y Emergency Response Guide** (publicly available)
- **SAE Standards**: J1772, J2464, J2578 (EV safety)
