# Jeddinformatics

## Initial setup
```bash
pip install -r requirements.txt
```
This will install the required packages

## Running on errything
```bash
python3 main.py <your data folder>
```

## Config files
```json
{
    "$schema": "https://raw.githubusercontent.com/wolffshots/jeddinformatics/main/src/jeddinformatics/schema.json",
    "mappings": {
        "normal": "NC",
        "Normal": "NC",
        "OV": "OV",
        "UCEC": "UCEC",
        "Ovarian Cancer": "OV",
        "Uterine Cancer": "UCEC",
        "Some title": "Translated title",
        "log2(TPM)": "log<sub>2</sub>(TPM)"
    },
    "colors": {
        "NC": "blue",
        "OV": "green",
        "UCEC": "red",
        "box": "black",
        "plot_background_color": "lightgray",
        "paper_background_color": "white"
    },
    "precedence": ["NC", "normal", "Normal"],
    "jitter": 0.5,
    "line_width": 1.5,
    "point_size": 6,
    "plot_height": 540,
    "plot_width": 960
}
```

## Building and distributing
```bash
rm -fr dist && python3 -m build && python3 -m twine upload --repository testpypi dist/*
```

Rename all to OV (Ovarian canver) and UCEC (Uterine cancer) and make "normal"/"Normal" to NC (Non-cancer)

Data should look like:
```
│   
├───Gene Expression
│   └───ONCODB
│       ├───Ovarian Cancer
│       │   ├───CAS
│       │   │       data.txt
│       │   │       
│       │   ├───IPO5
│       │   │       data.txt
│       │   │       
│       │   ├───KPNA2
│       │   │       data.txt
│       │   │       
│       │   ├───KPNB1
│       │   │       data.txt
│       │   │       
│       │   ├───RAN
│       │   │       data.txt
│       │   │       
│       │   ├───TNPO1
│       │   │       data.txt
│       │   │       
│       │   └───XPO1
│       │           data.txt
│       │           
│       └───Uterine Cancer
│           ├───CAS
│           │       data.txt
│           │       
│           ├───IPO5
│           │       data.txt
│           │       
│           ├───KPNA2
│           │       data.txt
│           │       
│           ├───KPNB1
│           │       data.txt
│           │       
│           ├───RAN
│           │       data.txt
│           │       
│           ├───TNPO1
│           │       data.txt
│           │       
│           └───XPO1
│                   data.txt
│                   
└───Protein Expression
    └───UALCAN
        ├───Ovarian Cancer
        │   ├───CAS
        │   │       data.json
        │   │       
        │   ├───IPO5
        │   │       data.json
        │   │       
        │   ├───KPNA2
        │   │       data.json
        │   │       
        │   ├───KPNB1
        │   │       data.json
        │   │       
        │   ├───RAN
        │   │       data.json
        │   │       
        │   ├───TNPO1
        │   │       data.json
        │   │       
        │   └───XPO1
        │           data.json
        │           
        └───Uterine Cancer
            ├───CAS
            │       data.json
            │       
            ├───IPO5
            │       data.json
            │       
            ├───KPNA2
            │       data.json
            │       
            ├───KPNB1
            │       data.json
            │       
            ├───RAN
            │       data.json
            │       
            ├───TNPO1
            │       data.json
            │       
            └───XPO1
                    data.json
                    
```

So general form is:
```
 {gene or protein expression}
  └───{source database}
       └───{type of cancer}
            └───{gene or protein name}
                 └───{data.json or data.txt}
```
