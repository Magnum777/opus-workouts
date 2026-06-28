# AI-Powered Antenna Modeling Research

> Research date: 2026-06-27
> Researcher: Nova (for OpusMagnum / WR4MG)

---

## 🤖 AI + Antenna Design

### Antenna Forge — AI-Driven Inverse Design

**Project:** antenna-forge (GitHub: 1ove9/antenna-forge)
**Status:** Active open-source project with live in-browser playground

**What it does:**
- AI-driven inverse antenna design — specify desired performance, AI generates antenna geometry
- Uses real NEC2 + openEMS simulation engines in the loop
- Iterative optimization: AI proposes design → NEC2 simulates → AI refines

**Architecture:**
- `yaf_ai` — AI/ML core (generative models)
- `yaf_core` — Geometry engine
- `yaf_solvers` — NEC2 + openEMS integration
- `yaf_api` — REST API
- `yaf_worker` — Background job processing

**Use case for ham radio:**
- Design optimal wire antennas for specific bands/space constraints
- Optimize existing antennas for better SWR/gain patterns
- Generate novel antenna configurations humans might not think of

**Limitation:** Currently focused on general antenna design, not specifically ham radio bands (though adaptable).

---

## 📊 Traditional Tools with AI Enhancement

### EZNEC + AutoEZ

**EZNEC Pro+** — Industry standard NEC-based antenna modeling
**AutoEZ** — Automation layer that enables:
- Variable substitution in antenna models
- Batch simulation sweeps
- Optimization loops (brute force approach)

**How AI could enhance:**
- Replace brute-force sweeps with ML-guided parameter search
- Train neural network on EZNEC output to predict optimal configs
- Use genetic algorithms instead of grid search

**Current approach (non-AI):**
- Define wire geometry with variables
- Run AutoEZ sweeps across parameter space
- Find best SWR/gain combination manually

### NEC2 + Python Scripts

**GitHub: RFingAdam/mcp-nec2-antenna**
- MCP server for NEC2 wire antenna simulation
- Supports dipole, Yagi, vertical, loop, inverted-V
- Returns gain patterns, impedance, VSWR
- Can be integrated with AI workflows via MCP protocol

**Use case:** Build custom AI antenna optimizer using NEC2 as backend simulator.

---

## 🧠 Machine Learning Approaches

### Neural Network Surrogate Models

**Concept:** Train NN on thousands of NEC2/EZNEC simulations to create instant predictor.

**Benefits:**
- EZNEC simulation takes seconds/minutes per antenna
- Trained NN predicts performance in milliseconds
- Enables real-time interactive optimization

**Training data needed:**
- Wire geometry parameters (length, height, angles)
- Environmental factors (ground type, height above ground)
- Frequency bands of interest
- Output: Gain, SWR, radiation pattern, impedance

### Genetic Algorithms for Antenna Optimization

**Evolutionary approach:**
1. Generate random antenna population
2. Simulate each with NEC2
3. Score based on fitness function (SWR + gain + bandwidth)
4. Select best performers
5. Crossover + mutation to create next generation
6. Repeat until convergence

**AI enhancement:** Replace random mutation with learned mutation operators that have higher probability of improving fitness.

---

## 🛠️ Practical Applications for Ham Radio

### Scenario 1: HOA-Friendly Antenna Design

**Constraint:** No visible antennas, limited space (balcony, attic)
**AI approach:** 
- Input: Available space (3m x 2m balcony), bands (20m, 40m)
- AI generates compact loaded dipole / loop configurations
- Optimize for best compromise between size and efficiency

### Scenario 2: Multi-Band Wire Antenna Optimization

**Constraint:** Single feedpoint, multiple bands (80m-10m)
**AI approach:**
- Optimize trap positions / loading coil values
- Find best wire geometry for flat SWR across bands
- Consider height above ground effects

### Scenario 3: Portable POTA Antenna

**Constraint:** Quick deploy, light weight, multi-band
**AI approach:**
- Optimize EFHW wire length for multiple harmonic bands
- Find best counterpoise/radial configuration
- Balance efficiency vs packability

---

## 🔗 Tools and Resources

**Software:**
- Antenna Forge: https://github.com/1ove9/antenna-forge
- EZNEC: https://eznec.com/
- AutoEZ: https://ac6la.com/autoez.html
- NEC2 Python: https://github.com/RFingAdam/mcp-nec2-antenna

**Learning Resources:**
- NEC2 manual (method of moments theory)
- EZNEC tutorial videos (KB9VBR has good ones)
- Antenna modeling forums (QRZ, eHam)

**Hardware needed for serious modeling:**
- Modern multi-core CPU (simulations are CPU-bound)
- Optional: GPU for neural network training
- Large RAM for complex geometry meshes

---

## 📝 Research Notes

**What we learned:**
- True AI antenna design is emerging but not turnkey yet
- Best current approach: EZNEC + AutoEZ for manual optimization
- Antenna Forge shows promise for automated inverse design
- NEC2 via Python enables custom AI integration
- Ham-specific AI antenna tools don't exist yet — opportunity for development

**Next steps for deeper research:**
- [ ] Install and test Antenna Forge locally
- [ ] Create NEC2 dataset of common ham antenna designs
- [ ] Train simple NN to predict SWR from wire geometry
- [ ] Build web interface for antenna optimization

---

*Saved to Night School: docs/night-school/ham-radio-ai/*
