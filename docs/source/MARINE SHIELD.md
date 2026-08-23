# **MARINE SHIELD** 

# **\- Final Master Plan**

## **Explainable Oil Spill Detection, Source Investigation and Response Intelligence System**

### **Core idea**

MarineShield is not just:

> **“AI detects oil spills from satellite images.”**

That is too narrow and already crowded.

The complete system answers the full incident lifecycle:

### **1\. Did an oil spill occur?**

### **2\. Is it really oil or a SAR look-alike?**

### **3\. Where and when was the likely release?**

### **4\. Which source hypothesis best explains it?**

### **5\. Could an untracked vessel or non-vessel source explain it?**

### **6\. Where will the spill move?**

### **7\. What ecosystem, infrastructure, and economic assets are threatened?**

### **8\. What should authorities prioritize?**

### **9\. Who should be alerted?**

### **10\. What evidence supports every conclusion?**

### **11\. How certain is the system at every stage?**

### **12\. How would the system have performed during a real historical incident?**

That is the final scope.

---

# **1\. The three pillars of novelty**

Do **not** present twenty different features as twenty innovations. The final solution should be framed around three central innovations.

## **Novelty 1 — Cross-modal maritime evidence fusion**

```
Satellite SAR
      +
AIS / vessel tracks
      +
SAR vessel observations
      +
Wind and ocean currents
      +
Environmental GIS
      +
Historical incident information
              ↓
       ONE INCIDENT MODEL
```

MarineShield does not rely on one model making one prediction. It fuses independent evidence sources into a coherent incident investigation.

---

## **Novelty 2 — Explainable source investigation**

The system never says:

> "AI says Vessel A caused the spill."

Instead:

```
Vessel A — PROBABLE SOURCE

Supporting evidence
✓ Present in release window
✓ Trajectory intersects release region
✓ Spatially compatible
✓ Drift backtracking compatible
✓ Vessel characteristics compatible

Contradictory evidence
⚠ 17-minute AIS gap
⚠ Heading uncertainty

Behavioral indicators
⚠ Unusual loitering

Evidence quality: MEDIUM
```

This is the **Evidence \+ Contradiction Engine**. It evaluates both what supports a hypothesis and what weakens it.

---

## **Novelty 3 — Backward \+ Forward Incident Intelligence**

### **BACKWARD**

```
Observed slick
      ↓
Where did it originate?
      ↓
When was it released?
      ↓
Which source hypotheses explain it?
```

### **FORWARD**

```
Observed slick
      ↓
Where will it move?
      ↓
What will it impact?
      ↓
How urgent is the response?
      ↓
What should happen next?
```

This is the strongest single narrative for the judging panel.

---

# **2\. Final Master Architecture**

```
                         DATA ACQUISITION
                                │
        ┌───────────────────────┼────────────────────────┐
        │                       │                        │
        ▼                       ▼                        ▼
   SENTINEL-1 SAR              AIS                ENVIRONMENT
        │                       │                 Wind / Current
        │                       │                        │
        ▼                       │                        │
   SAR PREPROCESSING            │                        │
        │                       │                        │
        ▼                       │                        │
   OIL SEGMENTATION             │                        │
        │                       │                        │
        ▼                       │                        │
 LOOK-ALIKE VERIFICATION        │                        │
        │                       │                        │
        ▼                       │                        │
   PROBABLE OIL SLICK           │                        │
        │                       │                        │
        ├──────────────┐        │                        │
        ▼              ▼        ▼                        │
 SPILL ANALYSIS   SAR VESSEL DETECTION                  │
        │              │        │                        │
        │              └────────┴───────────┐            │
        │                                   ▼            │
        │                          AIS–SAR RECONCILIATION│
        │                                   │            │
        └───────────────────────┬───────────┘            │
                                ▼                        │
                 RELEASE TIME + LOCATION ESTIMATION ◄────┘
                                │
                                ▼
                        CANDIDATE HYPOTHESES
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
          Vessel A         Untracked Vessel    Non-vessel Source
              │                 │                  │
              └─────────────────┴──────────────────┘
                                │
                                ▼
                  EVIDENCE + CONTRADICTION ENGINE
                                │
                                ▼
                    SOURCE STATUS / RANKING
                                │
                  ┌─────────────┴──────────────┐
                  ▼                            ▼
          BACKWARD ANALYSIS               FORWARD ANALYSIS
                  │                            │
                  ▼                            ▼
             Source logic                 GNOME / PyGNOME
                                               │
                                               ▼
                                    DRIFT + UNCERTAINTY
                                               │
                                               ▼
                                     THREAT-ZONE ANALYSIS
                                               │
                                               ▼
                                      RESPONSE PRIORITY
                                               │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                       ALERT / ACTION     NEXT OBSERVATION   WHAT-IF
                              │               PLANNER       SIMULATOR
                              └────────────────┼────────────────┘
                                               ▼
                                         WEBGIS DSS
                                               │
                               ┌───────────────┼───────────────┐
                               ▼               ▼               ▼
                         INCIDENT REPORT   DATA QUALITY    FIELD MODE

                         HISTORICAL INCIDENT TIME MACHINE
                                               │
                                               ▼
                                   FULL PIPELINE EVALUATION
```

This is the architecture I would freeze.

---

# **3\. Detection Intelligence Layer**

## **Module A — Sentinel-1 SAR preprocessing**

Pipeline:

```
Sentinel-1 GRD
      ↓
Orbit correction
      ↓
Noise handling
      ↓
Radiometric calibration
      ↓
Speckle filtering
      ↓
Terrain/geometric correction where appropriate
      ↓
dB conversion
      ↓
Tiling + normalization
      ↓
ML-ready data
```

Raw satellite data is not treated like a normal PNG image. The remote-sensing pipeline remains a dedicated subsystem.

---

## **Module B — Oil-spill segmentation**

### **Model responsibility**

```
SAR scene
    ↓
pixel-wise oil probability
    ↓
oil mask
    ↓
spill polygon
```

Use **one primary segmentation architecture and one benchmark alternative**, rather than presenting four architectures as though all will be built. The project should benchmark and select based on validation performance.

Output:

* spill polygon  
* centroid  
* estimated area  
* segmentation confidence  
* image-quality indicators

Metrics:

* IoU  
* Dice/F1  
* precision  
* recall  
* false-positive rate  
* inference time

Pixel accuracy alone is not a meaningful primary metric because oil can occupy only a small fraction of a SAR scene.

---

## **Module C — Look-Alike Rejection**

A dark region in SAR is **not automatically petroleum oil**.

The verification layer distinguishes:

```
Candidate dark region
       │
 ┌─────┼───────────────┐
 │     │               │
Oil  Biogenic       Low-wind
      slick           area
 │
Ship wake / other phenomenon
```

This remains separate from segmentation because the two tasks solve different problems.

---

## **Module D — Spill Severity and Thickness Class**

Do not claim exact oil volume from SAR unless properly validated.

Instead, add a **coarse severity/thickness classification**:

```
SHEEN
   ↓
MODERATE
   ↓
THICK / HIGH-SEVERITY
```

using SAR texture and contextual indicators.

This feeds into response prioritization because two spills with equal area may require different responses.

---

# **4\. Maritime Intelligence Layer**

## **Module E — SAR Vessel Detection**

Detect vessels directly from SAR.

```
SAR image
     ↓
Ship detector
     ↓
Observed vessel positions
```

This provides an independent observation channel.

---

## **Module F — AIS–SAR Reconciliation**

This should **not be an ML model**.

Use deterministic geospatial matching:

```
Distance
+
Timestamp difference
+
Heading difference
+
Speed difference
+
Vessel dimensions
       ↓
MATCH SCORE
```

Example:

```
SAR Vessel #17

AIS Candidate A

Distance:          0.8 km
Time difference:   3 min
Heading difference: 4°
Speed difference:  0.6 kn

Match score: 0.94
```

This is simpler, explainable, and scientifically easier to defend.

---

## **Module G — Dark Vessel and AIS Anomaly Intelligence**

This extends reconciliation rather than duplicating it.

The system investigates:

* SAR-observed vessels without an AIS match  
* AIS gaps around the estimated release window  
* sudden stops  
* route deviation  
* loitering  
* unusual turns  
* abnormal speed changes

Output:

> **Vessel exhibits anomalous behavior requiring investigation.**

Not:

> **Vessel illegally dumped oil.**

If enough historical data becomes available, the rule system can later be augmented with anomaly detection methods.

---

# **5\. Release Reconstruction Layer**

This is one of the most important additions.

The system should **not jump directly from detected slick to nearby vessels**.

Instead:

```
Detected slick
       ↓
Backward drift modelling
       +
Wind/current history
       ↓
LIKELY RELEASE REGION
       +
LIKELY RELEASE TIME WINDOW
       ↓
Search vessel trajectories
```

Output:

```
Estimated release

Time:
08:40–10:15 UTC

Region:
8.7 km² uncertainty area

Confidence:
Medium
```

Only vessels physically compatible with that region and time window enter the strongest candidate set.

This removes the weak logic:

> "The closest vessel is probably responsible."

---

# **6\. Source Attribution Layer**

## **Candidate hypotheses**

The system must evaluate more than vessels.

```
H1 — Vessel A
H2 — Vessel B
H3 — Vessel C
H4 — Untracked / dark vessel
H5 — Non-vessel source
H6 — Unknown
```

This prevents forced attribution.

---

## **Evidence \+ Contradiction Engine**

For each hypothesis:

### **Supporting evidence**

* spatial compatibility  
* temporal compatibility  
* trajectory compatibility  
* drift/backtracking compatibility  
* vessel characteristics  
* behavioral anomaly indicators

### **Contradictory evidence**

* incompatible timing  
* incompatible trajectory  
* environmental inconsistency  
* AIS uncertainty  
* missing supporting observations

Conceptually:

E(H)=ws​Sspatial​+wt​Stemporal​+wr​Strajectory​+wd​Sdrift​+wv​Svessel​+wb​Sbehavior​−wc​Ccontradiction​

The weights are **not arbitrary final numbers**. They are initially defined as a transparent evidence framework and later calibrated using historical evaluation.

---

## **Counterfactual Attribution**

If Vessel A ranks first:

> What happens if Vessel A is removed?

Example:

```
WITH Vessel A

A: 0.78
B: 0.34
Unknown: 0.19
```

Then:

```
WITHOUT Vessel A

B: 0.41
Unknown: 0.32
```

This tests whether Vessel A is genuinely dominant or merely slightly ahead in a weak ranking.

---

## **Unknown Source Engine**

If evidence is insufficient:

```
SOURCE STATUS

⚫ UNKNOWN

No hypothesis currently
crosses the validated evidence threshold.
```

Then trigger:

```
Expand AIS search
      ↓
Check historical AIS gaps
      ↓
Search SAR-only vessels
      ↓
Backtrack further
      ↓
Check earlier observations
      ↓
Recalculate
```

The ability to say **“unknown”** is a strength, not a missing feature.

---

# **7\. Forward Drift Intelligence**

Use GNOME/PyGNOME rather than inventing ocean physics.

```
Current spill geometry
        +
Wind
        +
Ocean currents
        ↓
Ensemble simulations
        ↓
+6h
+12h
+24h
+48h
```

Do not display one falsely precise deterministic line.

Display:

```
Best estimate trajectory
        +
Uncertainty / probability cone
```

This is scientifically more honest and visually stronger.

---

# **8\. Threat and Impact Intelligence**

Intersect predicted spill geometry with:

* mangroves  
* marine protected areas  
* coastline  
* fishing zones  
* ports  
* coastal infrastructure

Calculate:

* predicted arrival time  
* overlap  
* affected area  
* environmental sensitivity  
* confidence of impact

Add a rough **economic/environmental exposure estimate** where credible public data exists—for example, affected sensitive area or fishing activity at risk—rather than inventing a precise rupee damage number.

---

# **9\. MarineShield Response Priority**

Do not create separate overlapping “severity,” “risk,” “threat,” and “alert” scores.

Create one central decision metric:

## **MarineShield Response Priority**

Conceptually:

Priority=Severity×Environmental Sensitivity×Probability of Impact×Time Urgency×Evidence Quality

The exact normalization and combination must be defined carefully rather than multiplying arbitrary raw percentages.

Output:

```
MARINESHIELD PRIORITY

87 / 100

🔴 CRITICAL

Mangrove:       14 h
Protected area: 21 h
Fishing zone:   29 h
Port:           43 h
```

This directly answers:

> **What should authorities act on first?**

---

# **10\. Response & Alert Intelligence Engine**

This combines the previously separate:

* risk assessment  
* response recommendation  
* automatic alerting

into one module.

Inputs:

```
Detection confidence
+
Spill severity
+
Source investigation status
+
Drift forecast
+
Threatened assets
+
Time to impact
+
Environmental sensitivity
+
Data quality
        ↓
RESPONSE & ALERT ENGINE
```

Outputs:

### **LOW**

Monitor.

### **MEDIUM**

Increase observation.

### **HIGH**

Notify relevant authorities and prepare response.

### **CRITICAL**

Immediate incident escalation and response preparation.

Example:

```
🚨 CRITICAL INCIDENT

Spill area: 8.4 km²
Detection confidence: High

Mangrove ETA: 12 h
Fishing zone ETA: 19 h

Recommended:
→ Prepare containment resources
→ Notify relevant coastal authorities
→ Increase surveillance
→ Investigate top-ranked source hypothesis
→ Prioritize next observation zone
```

The first implementation should be a deterministic rule engine, not another black-box AI model.

---

# **11\. Active Satellite Re-scan / Next-Best Observation**

The feature must be framed correctly.

MarineShield does **not control Sentinel-1**.

Instead, it calculates:

> **Where would the next available observation provide the highest information value?**

```
Current spill
      ↓
Drift prediction
      +
Prediction uncertainty
      +
Sensitive ecosystems
      ↓
NEXT-BEST OBSERVATION ZONE
```

Example:

```
Priority Observation Zone

42 km²

Reason:
High forecast uncertainty
+
Sensitive mangrove region
```

This can later integrate with available commercial or institutional observation/tasking workflows, but the hackathon prototype should focus on the decision recommendation, not falsely claim autonomous satellite tasking.

---

# **12\. What-If Scenario Simulator**

This is a genuine decision-support feature.

The operator changes assumptions:

```
Wind speed
Wind direction
Current speed
Current direction
```

Then:

```
BASELINE

Mangrove arrival: 18 h
```

versus:

```
SCENARIO

Mangrove arrival: 12 h

Difference: -6 h
```

The purpose is not to let users play with random sliders. It allows response planners to examine environmental uncertainty and sensitivity.

---

# **13\. End-to-End Uncertainty and Data Quality Layer**

Every major subsystem contributes uncertainty.

```
SAR quality
    ↓
Segmentation
    ↓
Oil verification
    ↓
Release estimation
    ↓
AIS coverage
    ↓
Drift uncertainty
    ↓
Attribution confidence
    ↓
Impact confidence
```

Dashboard example:

```
DATA QUALITY

SAR             82%
AIS             71%
Wind            91%
Current         63%
GIS coverage    88%

OVERALL EVIDENCE QUALITY

MEDIUM

Primary limitation:
Current-field uncertainty
```

These values must represent defined quality metrics, not invented percentages.

---

# **14\. Historical Incident Time Machine**

This should be one of the headline demo features.

Instead of:

> "Here are our test metrics."

The judge sees:

```
HISTORICAL INCIDENT

Select:
Date + time
       ↓
FREEZE AVAILABLE INFORMATION
       ↓
Run MarineShield
       ↓
Detection
Verification
Release reconstruction
Source hypotheses
Forecast
Threat analysis
       ↓
Advance 6 hours
       ↓
Advance 12 hours
       ↓
Compare with documented outcome
```

The critical principle:

> Only use information that would have been available at that point in time.

This prevents hindsight bias.

Evaluate:

### **Detection**

* IoU  
* F1  
* precision  
* recall

### **Vessel detection**

* precision  
* recall  
* mAP

### **Attribution**

* Top-1  
* Top-3  
* MRR, where ground truth supports it

### **Drift**

* spatial trajectory error

### **End-to-end**

* processing latency  
* alert generation time  
* response-priority accuracy against documented outcomes where measurable

---

# **15\. Active Learning Feedback Loop**

When an analyst reviews an incident:

```
Candidate
    ↓
Confirmed oil
False alarm
Look-alike
Uncertain
    ↓
Feedback stored
    ↓
Dataset expansion
    ↓
Periodic model retraining
```

This gives a clear answer to:

> **How does the system improve over time?**

The system should not silently retrain itself on every click. Analyst-verified feedback enters a controlled training dataset.

---

# **16\. Incident Report Generator**

One-click deterministic report generation.

## **MARINESHIELD INCIDENT REPORT**

### **Incident**

* Incident ID  
* detection time  
* coordinates  
* estimated area  
* severity class

### **Detection evidence**

* SAR scene  
* segmentation confidence  
* oil verification  
* data quality

### **Source investigation**

* candidate hypotheses  
* vessel tracks  
* SAR–AIS discrepancies  
* supporting evidence  
* contradictory evidence

### **Forecast**

* \+6h  
* \+12h  
* \+24h  
* \+48h  
* uncertainty range

### **Threat assessment**

* ecosystems  
* infrastructure  
* estimated arrival  
* response priority

### **Recommended response**

* urgency  
* actions  
* relevant stakeholder categories

The report can support operational documentation and investigation workflows. It should **not be described as legal proof or automatically MARPOL-compliant evidence unless formally validated for that use**.

---

# **17\. Offline / Low-Bandwidth Field Mode**

This is a supporting deployment feature, not a separate intelligence module.

Provide:

* lightweight mobile view  
* cached latest incident state  
* low-bandwidth map/data mode  
* optional SMS/status-query concept

This matters because coastal field operations may not always have reliable connectivity.

---

# **18\. Indian Data Strategy**

This needs to be explicit because the judging notes identified a real weakness: **Global Fishing Watch AIS coverage may not be sufficient for all Indian coastal scenarios**.

Therefore:

```
PRIMARY / PUBLIC DATA

Sentinel-1
+
Global AIS sources
+
Historical incident records
+
Wind/current datasets
+
Environmental GIS
```

Supplement where access is available with Indian maritime/oceanographic sources such as:

* INCOIS-derived oceanographic products  
* DG Shipping or other authorized maritime data sources  
* ISRO/Indian Earth-observation sources where relevant

The architecture must support multiple AIS/environmental providers rather than being hard-coded around one external API.

---

# **19\. Final Technology Stack**

Every component needs a reason.

| Technology | Why MarineShield needs it |
| ----- | ----- |
| **Python** | Scientific processing, ML, remote sensing, attribution logic |
| **PyTorch** | Train/infer segmentation, classification, vessel models |
| **SNAP/GDAL/Rasterio** | Process and read SAR geospatial raster data |
| **GeoPandas/Shapely/PyProj** | Spatial operations and coordinate transformations |
| **PostgreSQL \+ PostGIS** | Store/query vessel tracks, spill geometries, GIS layers |
| **FastAPI** | Expose models and incident intelligence as APIs |
| **GNOME/PyGNOME** | Established oil trajectory modelling |
| **React** | Operational dashboard |
| **MapLibre/Mapbox/Leaflet** | Interactive WebGIS |
| **Copernicus Data Space** | Satellite data access |
| **AIS providers/APIs** | Vessel trajectory intelligence |
| **Environmental datasets/APIs** | Wind/current forcing |
| **Object/file storage** | SAR scenes, generated products and reports |

Do not use Google Earth Engine merely because it sounds impressive. Use it only if it materially simplifies acquisition or processing in the prototype.

---

# **20\. Final Six-Person Division**

| Member | Ownership |
| ----- | ----- |
| **1** | Satellite acquisition, Sentinel-1 preprocessing, dataset pipeline |
| **2** | Oil segmentation, look-alike classifier, SAR vessel detection |
| **3** | AIS ingestion, PostGIS, trajectory processing, AIS–SAR reconciliation, behavioral features |
| **4** | Release time/location estimation, evidence \+ contradiction engine, hypothesis ranking, uncertainty |
| **5** | GNOME/PyGNOME, forward/backward drift, threat analysis, what-if simulator, historical replay/evaluation |
| **6** | FastAPI integration, React/WebGIS, response & alert intelligence, incident reports, field mode |

The responsibilities interact, but each person owns a real subsystem.

---

# **21\. What the Judge Should Experience**

Do not demo every feature separately.

Demo **one incident**.

### **Minute 1 — Detection**

```
New SAR observation
      ↓
Possible slick
```

### **Minute 2 — Verification**

```
Oil: high confidence
Look-alike probability: low
```

### **Minute 3 — Investigation**

```
Estimate:
Release region
Release time window
```

### **Minute 4 — Source hypotheses**

```
Vessel A
Vessel B
Untracked vessel
Non-vessel source
Unknown
```

### **Minute 5 — Explainability**

Click Vessel A:

```
Supporting evidence
Contradictions
Behavior anomalies
Data limitations
Counterfactual result
```

### **Minute 6 — Forward intelligence**

```
+6h
+12h
+24h
+48h

Uncertainty cone
```

### **Minute 7 — Threat**

```
Mangrove: 14 h
Fishing zone: 22 h

Priority: CRITICAL
```

### **Minute 8 — Action**

```
Recommended response
Who should be alerted
Next-best observation zone
```

### **Final moment**

Open the **Historical Incident Time Machine** and show:

> “This is not only a live-looking dashboard. We can replay a documented incident and measure how the entire pipeline performs.”

That is your strongest credibility demonstration.

---

# **22\. What We Explicitly Do NOT Claim**

This matters for the judging panel.

### **We do not claim:**

❌ continuous global real-time monitoring

Instead:

> Processes newly available satellite observations and other incoming data.

### **We do not claim:**

❌ a vessel is legally guilty

Instead:

> Ranks source hypotheses based on available evidence.

### **We do not claim:**

❌ exact oil volume from SAR

Instead:

> Provides an experimental/coarse severity or thickness class where validated.

### **We do not claim:**

❌ exact deterministic spill movement

Instead:

> Provides forecast trajectories with uncertainty.

### **We do not claim:**

❌ 90% attribution probability unless calibrated

Instead:

> Evidence score / calibrated confidence depending on available validation.

### **We do not claim:**

❌ Global Fishing Watch solves Indian AIS coverage

Instead:

> The system supports supplementary Indian maritime and oceanographic data sources.

This careful framing directly addresses the judging notes.

---

# **Final Product Definition**

## **MarineShield**

### **An Explainable Maritime Incident Intelligence Platform**

```
DETECT
   ↓
VERIFY
   ↓
RECONSTRUCT
   ↓
INVESTIGATE
   ↓
ATTRIBUTE OR DECLARE UNKNOWN
   ↓
FORECAST
   ↓
ASSESS THREATS
   ↓
PRIORITIZE RESPONSE
   ↓
ALERT
   ↓
RECOMMEND NEXT OBSERVATION
   ↓
DOCUMENT
   ↓
LEARN FROM VERIFIED INCIDENTS
```

The final architecture preserves the distinct contributions from the different proposals: SAR detection and preprocessing, look-alike rejection, vessel detection, AIS reconciliation, behavioral anomalies, release reconstruction, evidence and contradiction analysis, unknown-source handling, counterfactual attribution, uncertainty propagation, drift ensembles, threat analysis, response priority, what-if simulation, next-best observation planning, historical replay, active learning, deterministic reporting, and low-bandwidth access. The overlap has been removed by placing them into one continuous incident-intelligence pipeline.

**This is the version I would treat as the final master architecture.**

