
# Workshop Plan: Intelligent Building Digitalization

## Overview
This workshop guides an LLM or automation agent through the digitalization of an intelligent building, using a consistent use case and explicit, stepwise instructions. The plan is structured for clarity, consistency, and ease of parsing by LLMs.

### Learning Objectives
- Understand platform basics and entity management
- Compare and implement two data modeling approaches
- Provision sensors and deploy a control application
- Demonstrate semantic interoperability using knowledge graphs

---

## Use Case Definition

**Scenario:**
- 1 office building
- 3 floors
- 10 office rooms per floor
- Each office room contains:
  - 1 temperature sensor
  - 1 humidity sensor
  - 1 CO2 sensor
  - 1 air ventilation unit
  - 1 radiator thermostat
  - 1 fan coil unit for cooling

---

## WS01 Platform Basics and Interactions

**Objectives:**
- Introduce the platform
- Set up the platform environment
- Perform a health check
- Execute CRUD (Create, Read, Update, Delete) operations on entities

**Instructions:**
1. Initialize and configure the platform.
2. Verify platform health status.
3. Create, read, update, and delete sample entities (e.g., rooms, devices).

---

## WS02 Data Modeling Approaches

**Objectives:**
- Learn and compare two data modeling strategies
- Create virtual representations of the building using both approaches

**Approaches:**
1. **Object-Oriented:** Model real-world objects (rooms, sensors, actuators) and their relationships as entities.
2. **Hierarchical:** Model only upper-level objects (e.g., locations) as entities; represent sensors/actuators as properties of those entities.

**Instructions:**
1. Define entities for both approaches based on the use case.
2. Implement both models on the platform.
3. For each model, perform these tasks:
   - a. Read the CO2 level of one room and of all rooms (note which approach is easier for each query).
   - b. Replace a defective temperature sensor (describe steps and metadata handling in each model).
   - c. Add occupancy sensors to all rooms (describe how each model adapts to this change).
4. Summarize the pros and cons of each approach.

---

## WS03 Sensor Provisioning and Application Deployment

**Assumption:** Use the object-oriented data model for this section.

**Objectives:**
- Connect a simulated temperature sensor and radiator thermostat to the platform
- Deploy a simple controller application

**Instructions:**
1. Create a simulation script (refer to `simulation.py`) for:
   - a. Temperature sensor (publishes readings via MQTT)
   - b. Radiator thermostat (receives control commands via MQTT)
2. Ensure MQTT supports authentication and encryption.
3. Register the simulated devices on the platform.
4. Create a service group for the devices.
5. Read temperature data via the platform.
6. Deploy a simple PID controller to adjust the radiator based on temperature readings.

---

## WS04 Semantic Interoperability

**Assumption:** Continue using the object-oriented data model.

**Objectives:**
- Export the building’s knowledge graph from the platform
- Import the graph into a graph database (graphDB)
- Query the graph using SPARQL

**Instructions:**
1. Export the knowledge graph from the platform.
2. Import the graph into graphDB and ensure access is available.
3. Reference: [Semantic IoT BACS Tutorial](https://github.com/djs0109/tutorials.semantic-iot.bacs/blob/main/tutorial.ipynb)
4. Use SPARQL queries to extract information from the graphDB.

---

## Notes for LLMs
- Follow all instructions step by step.
- Use explicit entity names and relationships as defined in the use case.
- Document any assumptions or deviations from the plan.
