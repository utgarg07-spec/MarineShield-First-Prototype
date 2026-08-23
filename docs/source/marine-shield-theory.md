# **MarineShield — Complete Theory and Presentation Content**

## **For SIH1655: Detecting Oil Spills at Marine Environment Using AIS + Satellite Data**

One correction before the content: **the exact official wording of SIH1655 should be copied verbatim from the SIH portal/problem-statement document you have**, because I should not reconstruct an official problem statement from memory. The working title consistently used in our discussion is:

> **SIH1655 — Detecting Oil Spills at Marine Environment using AIS + Satellite Data**

Everything below is built around that scope.

---

# **1. ORIGINAL PROBLEM STATEMENT AND PROBLEM CONTEXT**

## **Problem Statement**

### **SIH1655 — Detecting Oil Spills at Marine Environment using AIS + Satellite Data**

The central challenge is to use **satellite observations and Automatic Identification System (AIS) vessel information** to detect marine oil spills and support the identification or investigation of potential sources.

The problem is larger than image classification.

A useful operational interpretation is:

```
Satellite observes ocean
        ↓
Possible oil slick detected
        ↓
Is it actually petroleum oil?
        ↓
Where and when was it likely released?
        ↓
Which vessels or other sources were compatible?
        ↓
Where will the oil move?
        ↓
What ecosystems/infrastructure are threatened?
        ↓
What should responders prioritize?
```

That is the basis of **MarineShield**.

---

## **Why is this problem important?**

Marine oil pollution can spread rapidly across large areas. By the time an oil slick is visually confirmed or reported manually, it may already have moved significantly from its original release location.

Authorities responding to a spill need answers to several different questions:

1. **Has an actual spill occurred?**  
2. **Where is it located?**  
3. **How large is the affected area?**  
4. **Is the dark region actually oil or a natural look-alike?**  
5. **When and where might the release have occurred?**  
6. **Which vessels were present during the likely release window?**  
7. **Where is the spill likely to move?**  
8. **Which coastlines, mangroves, fisheries or protected areas are threatened?**

NOAA describes oil-spill trajectory modelling as a way to predict where spilled oil is likely to travel and which environmentally or culturally sensitive areas may be at risk. Such predictions help responders decide where to deploy containment and cleanup resources.

---

# **2. THE FUNDAMENTAL TECHNOLOGY CONCEPTS**

## **2.1 What is SAR?**

**SAR stands for Synthetic Aperture Radar.**

Unlike an ordinary camera, a SAR satellite actively sends microwave signals toward the Earth and measures the returned energy.

Simplified:

```
Satellite
    ↓ microwave signal
Ocean surface
    ↓ reflected/scattered energy
Satellite sensor
    ↓
SAR image
```

SAR is useful for marine monitoring because radar imaging can operate independently of sunlight and can work under many weather conditions where optical imagery is limited. Global Fishing Watch describes SAR as an active microwave imaging technique that can detect objects at sea and is useful under cloud cover, rain, daylight and darkness.

---

## **2.2 Why does oil appear differently in SAR imagery?**

The ocean surface normally contains small waves called **capillary waves**.

These waves scatter radar energy.

When oil spreads on the surface, it can dampen some of these small waves.

Therefore:

```
Normal rough ocean
      ↓
More radar backscatter

Oil-covered smoother surface
      ↓
Lower backscatter
      ↓
Dark region in SAR
```

However, this creates the biggest challenge:

> **A dark SAR region is not automatically an oil spill.**

Other phenomena can produce similar signatures.

Examples:

* low-wind areas  
* biogenic slicks  
* natural films  
* ship wakes  
* calm water zones  
* other oceanographic phenomena

Research on SAR oil-spill detection explicitly identifies look-alikes such as wind slicks and ship wakes as a major source of false detections.

This is why MarineShield uses **two stages**:

```
Stage 1:
Detect candidate slick

        ↓

Stage 2:
Verify whether it is likely petroleum oil
```

---

# **3. WHAT IS AIS?**

AIS stands for **Automatic Identification System**.

Ships equipped with AIS transmit information that can include:

* vessel identity  
* MMSI  
* position  
* speed  
* course  
* heading  
* timestamp  
* other vessel information

This creates a vessel movement trail.

Example:

```
Time        Latitude    Longitude    Speed    Heading

08:00       X           Y            12 kn    185°
08:10       X           Y            11 kn    188°
08:20       X           Y            12 kn    190°
```

From this, we can reconstruct an approximate vessel trajectory.

Global Fishing Watch provides APIs and datasets related to AIS vessel presence, vessel identity and SAR vessel detections.

---

# **4. WHY COMBINE AIS AND SATELLITE DATA?**

Neither data source is sufficient alone.

## **Satellite alone**

Satellite imagery may show:

> Something unusual exists here.

But it may not identify the vessel responsible.

---

## **AIS alone**

AIS may show:

> These vessels were present in this region.

But it does not prove that an oil spill occurred.

---

## **Combined intelligence**

```
SAR satellite
      +
AIS vessel tracks
      +
SAR vessel observations
      +
Wind/current information
      +
GIS environmental layers
              ↓
       Incident intelligence
```

This is the fundamental logic of MarineShield.

---

# **5. THE MARINESHIELD SOLUTION**

## **Full incident lifecycle**

MarineShield is an **explainable maritime incident intelligence platform**.

Its workflow is:

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
ASSESS THREAT
   ↓
PRIORITIZE RESPONSE
   ↓
ALERT
   ↓
DOCUMENT
```

The system does not stop after saying:

> “Oil detected.”

It attempts to support the complete investigation and response workflow.

---

# **6. EXPLAINING THE PPT / SLIDE-BY-SLIDE THEORY**

## **Slide 1 — Title**

### **MarineShield**

**Explainable Oil Spill Detection, Source Investigation and Response Intelligence System**

Subtitle:

> **Satellite SAR + AIS + Environmental Intelligence for Marine Incident Response**

The key word is **explainable**.

We are not building a black-box system that simply outputs a culprit.

---

# **Slide 2 — The Problem**

Current marine monitoring faces a fragmented information problem.

Different questions require different data:

```
Is there oil?
    → Satellite imagery

Who was nearby?
    → AIS

Was a vessel actually observed?
    → SAR vessel detection

Where did it originate?
    → Backward drift

Where will it go?
    → Forward drift

What is threatened?
    → GIS

What should happen first?
    → Decision-support logic
```

The operational challenge is connecting these pieces.

---

# **Slide 3 — Why Current Detection Is Not Enough**

A simple architecture would be:

```
Satellite
   ↓
AI
   ↓
Oil spill detected
```

The weakness is obvious.

It does not answer:

* false positive or actual oil?  
* source?  
* release time?  
* future trajectory?  
* environmental threat?  
* response priority?

MarineShield expands detection into an **incident investigation pipeline**.

---

# **Slide 4 — Core Solution**

```
                 SENTINEL-1 SAR
                        +
                     AIS DATA
                        +
                WIND + OCEAN CURRENT
                        +
                  ENVIRONMENTAL GIS
                          ↓
                     MARINESHIELD
                          ↓
          Detect → Investigate → Forecast → Respond
```

---

# **Slide 5 — Oil Spill Detection**

### **Model 1: Spill Segmentation**

Input:

```
Sentinel-1 SAR image
```

Output:

```
Pixel-wise probability map
        ↓
Oil slick mask
        ↓
Geospatial spill polygon
```

A segmentation model is preferred over simple image-level classification because we need to know **where the suspected spill is**, not merely whether the whole image contains oil.

Possible architectures:

* U-Net  
* DeepLabV3+  
* SegFormer

The final model should be selected based on validation performance rather than claiming all architectures will be deployed.

---

# **Slide 6 — Look-Alike Rejection**

This is a separate classification/verification stage.

```
Candidate dark region
        ↓
 ┌──────┼───────────────┐
 ↓      ↓               ↓
Oil   Biogenic        Low wind
       slick

        +
Ship wake
        +
Other
```

Why separate this from segmentation?

Because:

```
Segmentation asks:
WHERE is the suspicious region?

Verification asks:
WHAT is the suspicious region?
```

These are different machine-learning tasks.

---

# **Slide 7 — Spill Severity**

Exact oil volume cannot be reliably claimed from SAR without strong validation.

Therefore MarineShield uses a more defensible approach:

```
Low severity
      ↓
Moderate severity
      ↓
High severity
```

Potential inputs include:

* estimated slick area  
* SAR intensity characteristics  
* texture  
* contextual information

This severity estimate feeds into response prioritization.

---

# **Slide 8 — SAR Vessel Detection**

Ships can also be detected directly in SAR imagery.

```
SAR scene
    ↓
Vessel detection model
    ↓
Observed vessels
```

This is important because AIS is not a complete observation of everything at sea.

Global Fishing Watch provides SAR vessel detection data derived from Sentinel-1 and explicitly supports AIS-matched and unmatched detections.

---

# **Slide 9 — AIS–SAR Reconciliation**

We compare:

```
SAR-observed vessel
         ↕
AIS-reported vessel
```

Possible matching features:

* spatial distance  
* timestamp difference  
* heading difference  
* speed compatibility  
* vessel dimensions/type where available

Example:

```
SAR Detection #12

Nearest AIS vessel:
Distance: 0.7 km
Time difference: 4 min
Heading difference: 5°

Match confidence: High
```

Unmatched vessels are flagged for investigation.

They are **not automatically declared guilty or illegal**.

---

# **Slide 10 — Dark Vessel and AIS Anomaly Intelligence**

MarineShield checks for:

* SAR-detected vessels without an AIS match  
* AIS transmission gaps  
* unusual loitering  
* route deviations  
* abnormal speed changes  
* unusual turning patterns

Output:

> **Requires investigation**

Not:

> **Confirmed offender**

This distinction is essential for credibility and bias reduction.

---

# **Slide 11 — Release Reconstruction**

A major weakness of naive vessel attribution is:

> “The closest vessel is probably responsible.”

That is bad logic.

Oil moves after release.

Therefore MarineShield first estimates:

```
Detected slick
       +
Historical wind
       +
Ocean currents
       ↓
Backward drift analysis
       ↓
Likely release region
       +
Likely release time window
```

Then candidate vessels are evaluated against that reconstructed event.

---

# **Slide 12 — Source Hypothesis Generation**

MarineShield does not force every incident to have a known vessel.

Possible hypotheses:

```
H1 → Vessel A
H2 → Vessel B
H3 → Vessel C
H4 → Untracked vessel
H5 → Non-vessel source
H6 → Unknown
```

This prevents the system from inventing certainty.

---

# **Slide 13 — Evidence-Based Attribution**

For each hypothesis:

### **Supporting evidence**

* spatial compatibility  
* temporal compatibility  
* trajectory compatibility  
* drift compatibility  
* vessel characteristics  
* behavioral indicators

### **Contradictory evidence**

* incompatible timing  
* incompatible path  
* insufficient evidence  
* environmental inconsistency  
* AIS uncertainty

Conceptually:

Score(H) = w_s S_spatial + w_t S_temporal + w_r S_trajectory + w_d S_drift + w_v S_vessel + w_b S_behavior - w_c C_contradiction

Where each term measures compatibility between the hypothesis and observed evidence.

The score is an **evidence ranking**, not automatically a legal probability.

---

# **Slide 14 — Explainability**

Example:

```
VESSEL A

Rank: 1

Supporting:
✓ Present during estimated release window
✓ Path intersects release region
✓ Drift-compatible
✓ AIS gap detected

Contradicting:
⚠ Limited environmental certainty

Evidence quality:
MEDIUM
```

This allows an investigator to understand the result.

---

# **Slide 15 — Unknown Is a Valid Output**

A scientifically honest system must be capable of saying:

> **Unknown source. More evidence required.**

If no hypothesis crosses a defined threshold:

```
UNKNOWN SOURCE
      ↓
Expand AIS search
      ↓
Check earlier SAR observations
      ↓
Search unmatched vessels
      ↓
Expand time window
      ↓
Recalculate hypotheses
```

This reduces false attribution.

---

# **Slide 16 — Counterfactual Attribution**

Suppose Vessel A ranks first.

We ask:

> What happens if Vessel A is removed from the candidate set?

Example:

```
Normal ranking

A → 0.82
B → 0.37
C → 0.21
```

Without A:

```
B → 0.39
C → 0.24
Unknown → 0.31
```

If the ranking collapses without A, A may have genuinely strong explanatory importance.

If B simply becomes almost equal, the evidence is weak.

This is a **robustness check**, not a separate model.

---

# **Slide 17 — Forward Drift Prediction**

Once the current spill geometry is known:

```
Spill geometry
      +
Wind
      +
Ocean current
      ↓
Oil trajectory model
      ↓
+6h
+12h
+24h
+48h
```

NOAA uses GNOME, the General NOAA Operational Modeling Environment, to model likely oil movement and trajectory.

MarineShield proposes using an established model such as GNOME/PyGNOME instead of attempting to invent ocean-physics equations during a hackathon.

---

# **Slide 18 — Uncertainty**

Oil movement should not be represented as one perfect line.

Instead:

```
Best estimate
       +
Uncertainty region
       +
Probability distribution
```

Uncertainty can arise from:

* wind errors  
* current uncertainty  
* SAR detection uncertainty  
* uncertain release time  
* uncertain release location

The purpose is to communicate what the system knows and what it does not know.

---

# **Slide 19 — Threat Zone Analysis**

Predicted spill geometry is intersected with GIS layers.

Examples:

* mangroves  
* marine protected areas  
* coastlines  
* fisheries  
* ports  
* coastal infrastructure

```
Predicted oil trajectory
            ↓
     Spatial intersection
            ↓
 Threatened assets
            ↓
 Estimated time to impact
```

---

# **Slide 20 — Response Priority**

Instead of creating five overlapping scores, MarineShield creates one decision-oriented metric.

Conceptually:

Priority = f(Severity, Environmental Sensitivity, Impact Probability, Time Urgency, Evidence Quality)

The exact function must be calibrated and normalized.

Example:

```
MARINESHIELD RESPONSE PRIORITY

87 / 100

CRITICAL

Mangrove ETA: 12 hours
Fishing area ETA: 19 hours
Port ETA: 41 hours
```

---

# **Slide 21 — Response and Alert Engine**

The response engine combines:

```
Detection confidence
       +
Severity
       +
Threatened assets
       +
Time to impact
       +
Evidence quality
       ↓
Response recommendation
```

Example:

### **LOW**

Monitor.

### **MEDIUM**

Increase observation.

### **HIGH**

Prepare response resources.

### **CRITICAL**

Escalate immediately and prioritize containment.

The first implementation should use transparent rules rather than a black-box recommendation model.

---

# **Slide 22 — Next-Best Observation**

MarineShield cannot control a satellite.

Therefore it should not claim:

> “We automatically task Sentinel-1.”

Instead, it asks:

> **Where would the next available observation be most useful?**

Inputs:

```
Forecast uncertainty
       +
Spill movement
       +
Sensitive ecosystems
       ↓
Priority observation region
```

This is decision support.

---

# **Slide 23 — What-If Simulator**

Users can modify environmental assumptions.

For example:

```
Scenario A:
Wind = current estimate

Mangrove impact = 18 h
```

```
Scenario B:
Wind stronger

Mangrove impact = 12 h
```

This helps response planners understand sensitivity to changing conditions.

---

# **Slide 24 — Historical Incident Time Machine**

This is one of the strongest features.

```
Historical incident
       ↓
Select time
       ↓
Use only information available at that time
       ↓
Run full pipeline
       ↓
Detection
Verification
Attribution
Forecast
Threat analysis
       ↓
Compare with documented outcome
```

This avoids hindsight bias.

Evaluation can include:

### **Detection**

* Precision  
* Recall  
* F1  
* IoU  
* Dice score

### **Vessel detection**

* Precision  
* Recall  
* mAP

### **Attribution**

Where reliable ground truth exists:

* Top-1 accuracy  
* Top-3 accuracy  
* Mean Reciprocal Rank

### **Drift**

* spatial forecast error  
* overlap between predicted and observed regions where available

---

# **Slide 25 — Active Learning**

Analyst feedback becomes controlled training data.

```
System output
      ↓
Human review

Oil confirmed
False alarm
Look-alike
Uncertain
      ↓
Verified feedback dataset
      ↓
Periodic retraining
```

The system should not blindly retrain from every user click.

---

# **7. TECHNICAL APPROACH**

## **Overall Architecture**

```
                    DATA SOURCES
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
   Sentinel-1           AIS            Wind/Current
       │                 │                  │
       ▼                 │                  │
SAR Processing           │                  │
       │                 │                  │
       ▼                 │                  │
Oil Segmentation         │                  │
       │                 │                  │
       ▼                 │                  │
Look-Alike Filter        │                  │
       │                 │                  │
       ▼                 ▼                  │
SAR Vessel Detection ── AIS Reconciliation │
       │                 │                  │
       └──────────┬──────┘                  │
                  ▼                         │
          Release Reconstruction ◄──────────┘
                  │
                  ▼
           Source Hypotheses
                  │
                  ▼
       Evidence + Contradiction Engine
                  │
                  ▼
            Source Ranking
                  │
          ┌───────┴────────┐
          ▼                ▼
    Backward Analysis   Forward GNOME
                            │
                            ▼
                     Threat Analysis
                            │
                            ▼
                    Response Priority
                            │
                            ▼
                     WebGIS Dashboard
```

---

# **8. TECHNOLOGY STACK**

| Technology | Why it is needed |
| ----- | ----- |
| Python | Scientific computing, ML, geospatial analysis |
| PyTorch | Deep-learning models |
| Sentinel-1 SAR | Primary satellite observation source |
| ESA SNAP | SAR preprocessing |
| GDAL/Rasterio | Geospatial raster processing |
| GeoPandas | Vector geospatial analysis |
| Shapely | Geometry operations |
| PyProj | Coordinate transformation |
| PostgreSQL | Structured data storage |
| PostGIS | Spatial database queries |
| FastAPI | Backend/API layer |
| React | Interactive frontend |
| MapLibre/Leaflet/Mapbox GL | WebGIS visualization |
| GNOME/PyGNOME | Oil trajectory modelling |
| Global Fishing Watch APIs/data | AIS and SAR vessel intelligence where appropriate |
| Environmental data APIs | Wind/current forcing |
| Object storage | SAR scenes and generated outputs |

### **Important design principle**

Every technology exists because the problem requires it.

Example:

> **PostGIS is needed because MarineShield repeatedly performs spatial queries between spill polygons, vessel trajectories and environmental zones.**

Not:

> “We used PostGIS because it is an industry technology.”

---

# **9. FEASIBILITY**

## **Is the project technically feasible?**

Yes, if scoped correctly.

The mistake would be trying to build:

* a new satellite  
* a global real-time monitoring network  
* a new ocean-physics engine  
* a perfect vessel-culprit AI  
* legal-grade forensic software

MarineShield does not need to do those things.

Instead, it integrates existing scientific and data infrastructure.

### **Existing components**

| Capability | Feasibility |
| ----- | ----- |
| SAR oil detection | High |
| Segmentation datasets/models | Available |
| Look-alike classification | Feasible |
| AIS vessel analysis | Feasible |
| SAR vessel detection | Available |
| AIS–SAR matching | Feasible |
| GNOME trajectory modelling | Existing scientific infrastructure |
| GIS threat analysis | Straightforward |
| WebGIS dashboard | High |
| Perfect source attribution | Not feasible; evidence ranking instead |

Global Fishing Watch already provides datasets for AIS vessel presence and Sentinel-1-derived SAR vessel detections, including unmatched detections.

The feasibility comes from **combining established components**, not pretending to invent every component from zero.

---

# **10. VIABILITY**

## **Why could this system actually be useful?**

MarineShield can operate as a **decision-support layer** on top of existing data sources.

Potential deployment:

```
Satellite data available
       ↓
Automatic processing
       ↓
Incident created
       ↓
Vessel investigation
       ↓
Drift forecast
       ↓
Threat analysis
       ↓
Human authority reviews evidence
```

The system does not replace:

* Coast Guard  
* pollution response agencies  
* oceanographers  
* investigators

It reduces the time required to transform raw data into an actionable investigation.

The viable role is:

> **Human-in-the-loop maritime decision support.**

---

# **11. USE CASES**

## **Use Case 1 — Suspected illegal discharge**

A SAR image reveals a suspicious slick.

MarineShield:

1. detects the slick  
2. rejects possible look-alikes  
3. reconstructs release region  
4. searches vessel activity  
5. checks AIS gaps  
6. compares SAR vessels  
7. ranks source hypotheses  
8. generates an evidence report

---

## **Use Case 2 — Accidental tanker spill**

A spill is detected near a shipping route.

MarineShield:

```
Detect
↓
Forecast trajectory
↓
Identify threatened coast
↓
Estimate arrival time
↓
Prioritize containment
```

---

## **Use Case 3 — Coastal ecosystem protection**

The predicted trajectory approaches:

* mangroves  
* coral ecosystems  
* protected areas

MarineShield calculates threat level and urgency.

---

## **Use Case 4 — Maritime surveillance**

Authorities can investigate:

* AIS gaps  
* SAR-only vessels  
* suspicious trajectories

This supports broader maritime situational awareness.

---

## **Use Case 5 — Historical investigation and training**

Past incidents can be replayed to:

* evaluate algorithms  
* train operators  
* compare predictions with documented outcomes

---

# **12. SDG ALIGNMENT**

## **Primary: SDG 14 — Life Below Water**

MarineShield directly supports the goal of reducing marine pollution and protecting marine ecosystems.

Relevant connection:

```
Earlier detection
       ↓
Faster response
       ↓
Reduced spread
       ↓
Lower ecological damage
```

---

## **SDG 13 — Climate Action**

Marine and environmental monitoring supports adaptation and resilience to environmental hazards.

The connection is secondary, not the primary SDG claim.

---

## **SDG 9 — Industry, Innovation and Infrastructure**

The project applies:

* AI  
* satellite observation  
* geospatial systems  
* digital infrastructure

to environmental monitoring.

---

## **SDG 12 — Responsible Consumption and Production**

Marine pollution monitoring can support accountability and improved environmental management.

---

## **SDG 11 — Sustainable Cities and Communities**

Coastal cities and infrastructure can be protected through earlier identification of environmental threats.

### **Best SDG framing**

```
PRIMARY:
SDG 14

SECONDARY:
SDG 9
SDG 12
SDG 13
SDG 11
```

Do not claim alignment with every SDG.

---

# **13. IMPACT AND BENEFITS**

## **Environmental Impact**

Potential benefits:

* earlier spill identification  
* improved monitoring  
* faster prioritization of threatened ecosystems  
* protection of mangroves and coastal habitats  
* improved marine pollution intelligence

---

## **Operational Impact**

Instead of manually combining multiple data sources:

```
Satellite analyst
+
AIS analyst
+
Ocean modeller
+
GIS analyst
```

MarineShield integrates these into one incident view.

This can reduce investigation friction.

---

## **Investigative Impact**

Traditional proximity logic:

> Vessel closest to spill.

MarineShield:

```
Spatial compatibility
+
Temporal compatibility
+
Trajectory
+
Drift reconstruction
+
AIS anomalies
+
SAR observations
+
Contradictory evidence
```

This produces a more defensible investigation.

---

## **Economic Impact**

Potentially threatened assets include:

* fisheries  
* ports  
* coastal tourism  
* shipping infrastructure  
* coastal ecosystems

The system should not claim exact economic savings unless evaluated using real operational data.

---

# **14. ACCESSIBILITY**

A technically advanced system is useless if operators cannot interpret it.

MarineShield should include:

## **1. Visual-first WebGIS**

```
Map
+
Spill polygon
+
Vessel tracks
+
Forecast
+
Threat zones
```

rather than forcing users to read raw coordinates.

---

## **2. Plain-language explanations**

Instead of:

> Attribution score = 0.7821

Show:

> Vessel A is ranked first because its route intersects the estimated release region and timing is compatible.

---

## **3. Evidence breakdown**

Every major result should have:

* supporting evidence  
* contradictory evidence  
* data limitations

---

## **4. Low-bandwidth mode**

Possible features:

* cached incidents  
* lightweight maps  
* simplified status view  
* downloadable reports

---

## **5. Accessible UI**

The final interface should consider:

* color-blind-safe status indicators  
* text labels in addition to colors  
* keyboard navigation where practical  
* readable contrast  
* responsive layout

---

# **15. SCALABILITY**

MarineShield should scale in layers.

## **Local scale**

```
One incident
↓
One geographic region
```

## **Regional scale**

```
Multiple coastal regions
↓
Batch satellite processing
```

## **Larger scale**

The architecture can scale through:

* tiled SAR processing  
* asynchronous background jobs  
* spatial indexing with PostGIS  
* containerized ML inference  
* independent microservices where justified  
* caching of static GIS layers

The database design should avoid loading every vessel trajectory into memory.

Instead:

```
Spatial index
+
Temporal filter
+
Candidate selection
```

reduces unnecessary computation.

---

# **16. EFFICIENCY**

Efficiency should be built into the architecture.

## **Model efficiency**

Do not run every model on every pixel.

Use:

```
SAR scene
   ↓
Candidate detection
   ↓
Crop suspicious regions
   ↓
Run expensive verification
```

---

## **Geospatial efficiency**

For attribution:

```
All vessels in ocean
        ✗
```

Instead:

```
Estimated release region
+
Estimated time window
        ↓
Spatial-temporal query
        ↓
Small candidate vessel set
        ↓
Evidence ranking
```

---

## **Data efficiency**

* cache satellite metadata  
* store processed products  
* avoid repeated API calls  
* process only changed/new scenes  
* use tiled raster operations

---

# **17. BIAS REDUCTION AND RESPONSIBLE AI**

This is important because the system can rank vessels.

## **Problem: False accusation bias**

If the system always chooses the highest-scoring vessel:

> “Vessel A caused the spill.”

it can create harmful false certainty.

### **Solution**

Allow:

```
Vessel A
Vessel B
Dark vessel
Non-vessel source
UNKNOWN
```

---

## **Problem: Data coverage bias**

AIS coverage is not uniform.

Some vessels:

* may not broadcast continuously  
* may be outside reception coverage  
* may not be represented in a particular dataset

Therefore:

> Missing AIS does not equal guilt.

---

## **Problem: Geographic bias**

A model trained on one ocean region may perform poorly in another.

Mitigation:

* geographically separated train/test sets  
* cross-region validation  
* historical incident evaluation  
* confidence monitoring

---

## **Problem: Environmental bias**

Different conditions:

* wind  
* sea state  
* sensor angle  
* geography

may affect SAR appearance.

Mitigation:

* diverse training data  
* hard-negative examples  
* uncertainty reporting  
* look-alike verification

---

## **Problem: Automation bias**

Operators may trust AI excessively.

Mitigation:

```
AI output
    +
Evidence
    +
Contradictions
    +
Data quality
    +
Human review
```

The final decision remains with the authorized human operator.

---

# **18. THE STRONGEST JUDGING-PANEL MESSAGE**

The project should not be pitched as:

> “We made an AI model to detect oil spills.”

That undersells the project and is highly saturated.

The correct positioning is:

> **MarineShield converts fragmented satellite, vessel, environmental and GIS data into an explainable incident intelligence chain—from suspected spill detection to source investigation, trajectory forecasting and response prioritization.**

The strongest demonstration is:

```
ONE REAL/HISTORICAL INCIDENT
          ↓
Satellite observation
          ↓
Oil verification
          ↓
Release reconstruction
          ↓
Vessel/source hypotheses
          ↓
Explainable evidence ranking
          ↓
Forward drift forecast
          ↓
Threatened ecosystem
          ↓
Response priority
          ↓
Compare prediction with documented outcome
```

That proves an end-to-end system rather than a collection of disconnected AI features.

---

# **19. REFERENCES AND DATA/TECHNOLOGY LINKS**

## **Official / Primary Technical Sources**

* [NOAA — Oil Spill Trajectory](https://oceanservice.noaa.gov/facts/oil-spill-trajectory.html?utm_source=chatgpt.com)  
   Explains how oil trajectory prediction supports response decisions.  
* [Global Fishing Watch APIs](https://globalfishingwatch.org/our-apis/?utm_source=chatgpt.com)  
   Overview of vessel, AIS, SAR and related datasets.  
* [Global Fishing Watch API Documentation](https://globalfishingwatch.org/our-apis/documentation?utm_source=chatgpt.com)  
   Detailed information on AIS vessel presence and Sentinel-1 SAR vessel detections.  
* [Global Fishing Watch Sentinel-1 Vessel Detection Dataset](https://globalfishingwatch.org/platform-update/2024-may-global-fishing-watch-apis-new-dataset-in-4wings-api-featuring-vessel-detections-from-sentinel-1-sar/?utm_source=chatgpt.com)  
   Useful for understanding AIS-matched and unmatched SAR vessel observations.  
* [RUS Copernicus Training — Oil Spill Mapping with Sentinel-1](https://www.youtube.com/watch?v=Jm1kIZBhJK0&utm_source=chatgpt.com)  
   Practical training resource for Sentinel-1 oil-spill mapping.

## **Research References**

* [SAR-Based Marine Oil Spill Detection Using DeepSegFusion](https://arxiv.org/abs/2601.12015?utm_source=chatgpt.com)  
   Relevant to segmentation, false positives and look-alike phenomena.  
* [Near-Real-Time Marine Oil Spill Detection in SAR Imagery](https://arxiv.org/abs/2605.17217?utm_source=chatgpt.com)  
   Recent research discussing SAR-based oil-spill segmentation and evaluation.  
* [Global Fishing Watch Research Paper](https://arxiv.org/abs/1609.08756?utm_source=chatgpt.com)  
   Background on large-scale vessel movement analysis using AIS.

## **Important official starting points to verify for implementation**

* NOAA GNOME  
* [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/?utm_source=chatgpt.com)  
* [ESA Sentinel-1 Mission](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-1?utm_source=chatgpt.com)  
* [Global Fishing Watch](https://globalfishingwatch.org/our-apis/?utm_source=chatgpt.com)  
* [United Nations SDG 14 — Life Below Water](https://sdgs.un.org/goals/goal14?utm_source=chatgpt.com)

## **Bottom line**

**MarineShield's defensible contribution is not inventing a new satellite algorithm for every stage.** It is the integration of proven capabilities into a single, explainable operational pipeline:

Detection -> Verification -> Release Reconstruction -> Source Investigation -> Forecast -> Threat Assessment -> Response Priority

The weakest alternative paths I would discard are:

* **Detection-only platform:** technically easy but saturated and incomplete. [Certain]  
* **Black-box “culprit prediction” model:** lacks sufficient clean source-vessel ground truth and is difficult to defend. [Likely]  
* **Custom ocean-physics engine:** wastes hackathon effort duplicating mature scientific tools such as GNOME. [Certain]

The final architecture is strongest when presented as an **explainable decision-support system with humans retaining investigative and operational authority**. [Certain]
