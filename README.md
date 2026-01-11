# HKU AIA project

Only about phase 2. AIA mainly cares about medical and health insurance products, so, in the first step we try to gather information relevant to health/medical.

# Installation & Setup

It is recommended to install Python3.11 or above and `pip` for downloading required packages. It is STRONGLY RECOMMENDED to create a virtual environment for this project.

To download all required files from this repo, run

```
git clone https://github.com/LeeHengYu/hku-aia-project.git
```

If you have `python3` installed on your machine, run the following:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Task 2: Data crawling

### Census data
- [x] HK Census and Stat department
- [ ] US Census (API always broken)

### Financial (stocks and bonds)
- [ ] HK Stock (FUTU needs auth setup, considering using Bloomberg Terminal)
- [ ] US Stock 
- [x] HK Bond Yield
- [x] US Bond Yield

### Financial Statements / Reports
- [x] AIA Group 
- [x] FWD
- [x] Prudential
- [ ] Manulife

### Insurance brochures
- [x] AIA Group 
- [x] FWD
- [x] Prudential
- [x] Manulife

### Medical
- [x] CHP
- [ ] Hospital Authority

# Task 3: AI & GCP

Some helper function to upload data to Cloud Storage. Needs to setup permission key or auth using Google Cloud CLI.