# Rescue Model

## Requirements
- Python >= 3.10 (if you have an older version, it's better to install 3.10 as a separate version instead of upgrading - potential trouble galore)

## Installation
- To ensure all packages are installed, run <br />
`pip install -r requirements.txt` <br />
from the project's home directory. <br />

## Usage
- To run the model without visualization, run <br />
`python3.10 run.py inputs/<your-input-file>` <br />
- To run the model with visualization, run <br />
`python3.10 runWithVisuals.py inputs/<your-input-file>` <br />
WARNING! Due to the visualization module's perpetual activity and the necessity to run in the main thread, the process needs to be killed manually after each execution

## Input
The input format is as follows: <br />
```
<timeLimit> <gridWidth> <gridHeight> <robotCount> <assetCount> <humanCount> <exitCount>
<assetPosX> <assetPosY> <assetValue> <assetWeight>
.
. (description line for each asset)
.
<humanPosX> <humanPosY> <isConscious>
.
. (description line for each human)

.
<exitPosX> <exitPosY>
.
. (description line for each exit)
.
```
Example input file in `inputs/exampleInput.in`