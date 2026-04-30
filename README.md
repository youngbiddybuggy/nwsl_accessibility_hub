
# ⚽ NWSL Stadium Accessibility Hub


## 📖 Project Overview
 Everyone watches women's sport now, right? Well everyone should be able to watch women's sports especially one of the most competitive leagues in the world — National Women's Soccer League. This accessibility hub  allows users to search and identify stadium’s accessibility services and features via team, stadium or match. I'm building and iterating on this project for people that want to take the guessing out of what services are available to them to ensure they can have the best possible. The accessibility data is sources from official team and stadium pages, and cross referenced with fan accounts including Reddit and StadiumJourney.com. Of the 16 teams now playing in the NWSL, 14 were included in the data collection and analysis, excluding expansion teams Boston Legacy FC and Denver Summit.

## ✨ Key Features
* **📅 Matchday Integration:** Filter the 2026 NWSL schedule to view accessibility details for specific games, including alternative/FIFA venue alerts.
* **🛡️ Team & Stadium Profiles:** Deep-dive profiles for all 16 NWSL teams (including 2026 expansion teams). Features team logos, ticket links, and guest services info.
* **🔍 Need-Based Filtering:** A search tool allowing users to find stadiums that support specific accommodations (e.g., Sensory Rooms, ASL Interpretation).
* **📊 Accessibility Grading System:** A custom 105-point tiered scoring model that grades stadiums on ADA baselines, extended access, and inclusive services.
* **📞 Guest Services Directory:** A consolidated, interactive table providing phone numbers, emails, and physical booth locations for every stadium.

## Scoring Methodology & Conditions
Stadiums are scored across three tiers and a bonus 
category for a maximum of 105 points.

─────────────────────────────────────────────────
TIER 1 — ADA Baseline                    40 points
─────────────────────────────────────────────────
Features required or expected under the Americans 
with Disabilities Act (ADA):

  Accessible Seating              10 pts
  Public Elevators                10 pts
  Accessible Parking              10 pts
  Service Animals                 10 pts

─────────────────────────────────────────────────
TIER 2 — Extended Accessibility          35 points
─────────────────────────────────────────────────
Features that go beyond ADA minimums to serve 
a broader range of disability needs:

  Wheelchair Services             10 pts
  Assisted Listening Devices      10 pts
  Closed Captioning                8 pts
  Gender Neutral Restrooms         7 pts

─────────────────────────────────────────────────
TIER 3 — Inclusive Excellence            25 points
─────────────────────────────────────────────────
Features that address invisible, sensory, and 
complex disabilities — the needs most commonly 
overlooked at sporting venues:

  Sensory Accommodations          10 pts
  Nursing Rooms                    8 pts
  Interpretation Services          7 pts

─────────────────────────────────────────────────
BONUS — Operational Excellence            3 points
─────────────────────────────────────────────────
  Standard Ticket Exchange         3 pts
  Rewards stadiums that allow 
  flexible ticket options for 
  disabled fans

─────────────────────────────────────────────────
GRADE SCALE
─────────────────────────────────────────────────
  A  90–105   Exceptional Accessibility
  B  80–89    Above Average
  C  70–79    Meets Baseline
  D  60–69    Below Baseline — Notable Gaps
  F  0–59     Significant Accessibility Gaps

How Unknown Data Is Scored
Not all stadiums publish complete accessibility 
information on their public websites.

  Confirmed (Yes)   → Full points awarded
  Not available (No) → Zero points awarded
  Unconfirmed (?)   → 20% partial credit

A lower score may reflect a lack of published 
information rather than a lack of services. 
Fans with specific needs are always encouraged 
to contact the stadium directly.

**Condition Flags**
Some features are technically available but carry conditions that create barriers in practice.

These are flagged with a ⚠️ warning and receive a reduced score based on the severity of the barrier:

  Minor condition       25% penalty
  (advance notice required)

  Moderate condition    50% penalty
  (significant barrier to access)

  Major condition       75% penalty
  (severely limited availability)

Examples in this dataset:
  → Interpretation services requiring 2+ weeks advance notice
  → Indicating service animals require prior authorization by the stadium 
  → Wheelchair services are unavailable 

What the Data Tells Us: This guide reveals meaningful gaps in how NWSL stadiums serve fans with disabilities — particularly those with invisible or complex needs.

**UNIVERSAL BASELINE**

  - Service animals are welcomed at all 16 NWSL stadiums — the one feature applied consistently across the league.
  -ADA/ Accessible seating is always available, but the process for reserving this seating is varies across stadiums. While some stadiums including Sports Illustrated, Lynn Family Stadium and CPCK are forthcoming in their policies on exchanging non-ADA tickets for ADA tickets on gamedays or as needed, others may offer this service without any indication. 

**STRONG PERFORMERS**
  Kansas City Current at CPKC Stadium, Houston Dash atShell Energy Stadium, and NJ/NY Gotham FC at Sports Illustrated Stadium lead the league with the most 
  complete and publicly documented accessibility programs.

**THE MOST SIGNIFICANT GAP**
  Interpretation services — including ASL/interpretation — are publicly confirmed at 
  only 2 of 14 stadiums: BMO Stadium (Angel City FC)and CPKC Stadium (Kansas City Current). Additionally, the availability of closed captioning on stadium video boards is confirmed in 7 of 14 stadiums.

  This directly reflects a broader pattern in sports accessibility where Deaf and hard of hearing fans face the fewest published accommodations. 
  For a sport with a growing and diverse fanbase this gap represents one of the clearest opportunities for improvement across the league.

**INVISIBLE DISABILITIES**
  Sensory accommodations including sensory rooms and sensory kits are confirmed at 12 of 114 stadiums, a strong result that reflects growing 
  awareness of diverse needs at live sporting events. Additional, data collection is needed to understand the use of these services in conjunction with stadium notifications during the use of pyrotechnics, fireworks, and light shows. 

**DATA LIMITATIONS**
  Boston Legacy FC and Denver Summit FC are 2025 expansion teams were not included in the data collection. These teams are excluded 
  from scoring.

  Additionally, several 2026 season matches are being played at temporary venues due to scheduling conflicts with the FIFA World Cup. 
  Accessibility information for these venues are not included in this guide.


## 🛠️ Tech Stack & Architecture
* **Frontend:** [Streamlit]
* **Data Manipulation:** [Pandas]
* **Data Modeling:** [NetworkX (Typed Directed Graph)]
* **Data Sources:** [Mention how you manually harvested stadium data and utilized the American Soccer Analysis API for the schedule.]

### The Graph Structure
The data is modeled as a directed graph where nodes consist of Teams, Stadiums, Accessibility Features, and Policy Pages, connected by edges like `PLAYS_AT` and `HAS_FEATURE`.

## 📂 Repository Structure
```text
nwsl-accessibility-hub/
│
├── data/
│   ├── nwsl_cleaned_new.csv       # Core stadium accessibility dataset
│   └── nwsl_schedule_2026.csv     # Cleaned matchday schedule
│
├── app.py                         # Main Streamlit application frontend
├── graph_builder.py               # NetworkX graph construction logic
├── scoring.py                     # 105-point grading and tier logic
├── clean_schedule.py              # Script to clean raw NWSL schedule data
│
└── README.md

🚀 Local Installation & Setup

To run this application locally on your machine, follow these steps:

    Clone the repository:
    Bash

    git clone [your-repo-link-here]
    cd [your-repo-folder-name]

    Install the required dependencies:
    Bash

    pip install streamlit pandas networkx

    Launch the Streamlit app:
    Bash

    streamlit run app.py

    View the app: Your default web browser will automatically open to http://localhost:8501.

🔮 Future Roadmap / Dream Scope

Looking ahead, there is so much more this guide could become. A natural next step is expanding the types of access information available including how fans can reach each stadium by public transportation, food allergy and dietary restriction options at concessions, and a way for fans to contribute their own experiences. Crowdsourced feedback from people who have actually attended matches would bring a layer of lived experience that no website scrape can capture, giving future users a more honest and complete picture of what to expect on matchday. Beyond serving fans directly, I hope this tool is useful to the teams and stadiums themselves  as a way to see where gaps exist, where they are already doing great work, and where there are opportunities to better support the fans they have and open the door to the ones they have not yet welcomed in.

Author: Allison Young * University of Michigan / SI 507 / aadyoung@umich.edu

