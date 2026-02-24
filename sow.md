# Statement of Work (SOW)

**Project:** State-Driven Multi-Axis Motion Control System
**Revision:** 1.0 (State Model Emphasis)

---

## 1. Project Overview

This project will deliver a (state-driven?) motion control system and GUI for a mechanical assembly consisting of:
(names can be changed)
* Aperture Wheel (rotary)
* Filter Wheel (rotary)
* Carousel Wheel (rotary)
* Linear Stage

The system probably should be designed around **explicitly defined valid state configurations**. Motion shall only occur when the system is in a valid state and shall transition between states in a controlled and verifiable manner.

The Carousel Wheel and Linear Stage have interdependent motion constraints and must not move simultaneously unless explicitly allowed by defined state rules.

---

## 2. Design Philosophy

This system might want to be implemented as a **finite state machine (FSM)**.

Key principle:

> Motion is not a command. Motion is a transition between valid states.

No axis may enter a state that violates valid states. I would make valid states an admin facing table (json or somehting) as long as it doesn't add time to delivery over hardcoding. This can be an upgrade.


## 3. Axis State Definitions

Each wheel (Aperture, Filter, Carousel) and the linear stage shall support the following primary states (suggested):

### 3.1 Common Axis States

* `UNMANAGED`
  Axis is not under active control of the system. Position is not trusted.

* `AT_POSITION`
  Axis is stationary and confirmed at a valid cell via active switch.

* `AT_HOME`
  Axis is stationary and confirmed at HOME (an active location defined by relative distance between cell positions).

* `MOVING_TO_POSITION`
  Axis is actively moving toward a commanded position.

* `FAULT`
  Axis has encountered an error condition.

---

## 4. Valid State Rules

### 4.1 General Validity

For any axis:

* `AT_POSITION` requires:

  * Exactly one valid active-cell switch asserted
  * No motion command in progress

* `MOVING_TO_POSITION` requires:

  * A valid target position
  * No fault condition
  * Motion interlocks satisfied

* `UNMANAGED` prohibits:

  * Automated motion commands
  * Position trust for interlocks

---

## 5. Carousel and linear stage Dependency Rules

The Carousel Wheel and Linear Stage have mechanical interaction constraints.

### 5.1 Interlock Requirements

The following rules must be enforced:

1. The Carousel Wheel shall not enter `MOVING_TO_POSITION` unless:

   * Stage is in a defined `CLEAR` state (mechanically safe position)

2. The Stage shall not enter `MOVING_TO_DOCK` unless:

   * Carousel Wheel is in `AT_POSITION`
   * Carousel Wheel is not `MOVING_TO_POSITION`

3. Simultaneous motion of Carousel and linear stage is prohibited unless explicitly defined in a future configuration.

4. Any violation of these rules shall:

   * Prevent motion command execution
   * Log the attempted invalid transition
   * Generate operator notification

---

## 6. State Transition Model

Each axis shall follow controlled transitions (suggested):

```
UNMANAGED → AT_POSITION (after validation or homing)statement of work and 
AT_POSITION → MOVING_TO_POSITION (upon valid command)
MOVING_TO_POSITION → AT_POSITION (upon successful switch confirmation)
MOVING_TO_POSITION → FAULT (timeout, switch error, or stop event)
FAULT → UNMANAGED or AT_POSITION (after operator reset and validation)
```

Transitions that do not conform to defined rules shall be rejected.

---

## 7. Motion Strategies

Two motion modes are possible and combination of the 2 is probably ideal. Whatever is fastest at the moment:

### 7.1 Switch-Search Mode

* Move until active-cell switch transition (FE).
* Confirm stable switch.
* Transition to `AT_POSITION`.

### 7.2 Step-Based Mode with Verification

* Move calibrated step count.
* Verify correct switch.
* If mismatch:

  * Attempt recovery via search mode.
  * If recovery fails, enter `FAULT`.

---

## 8. GUI Requirements

The GUI shall:

* Display current state per axis:

  * State (`UNMANAGED`, `AT_POSITION`, `MOVING`, `FAULT`)
  * Current detected cell
  * Target cell (if moving)

* Prevent invalid motion commands based on dependency rules.

* Provide:

  * Move commands
  * Stop command
  * Reset command
  * Emergency Stop (E-Stop)

---

## 9. Emergency Stop (E-Stop)

The GUI shall include a visible E-Stop control.

E-Stop shall:

* Immediately command motion halt to all axes.
* Force any `MOVING_TO_POSITION` state to transition to `FAULT`.
* Require operator reset before further commands.
* Log timestamp and system state snapshot.

Software E-Stop shall not override hardware safety chains.

---

## 10. Logging Requirements

The system shall log:
(suggested. all controller errors should be logged. logging depth could be a paramter in the gui? Log format could just be a text file)
* All state transitionsstatement of work and 
* All attempted invalid transitions
* Motion commands
* Interlock denials
* Switch state snapshots during faults
* E-Stop activations
* Timeouts and controller errors

Logs shall be persistent and timestamped.

---

## 11. Acceptance Criteria

System acceptance requires:

* No axis can enter an undefined state.
* No invalid cross-axis transition is permitted.
* Carousel and linear stage interlocks prevent mechanical conflict.
* All transitions are logged.
* Fault conditions are recoverable through defined reset flow.
* System operates through full position cycles without entering undefined state.

---

## 12. Updatable Extension Model

This SOW shall serve as a living state model template.



