# MD apps
Scaling MD runs

## Getting Started

### Set up the topology for the protein simulation.

1. (Optional) Build the conda environment
    ```bash
    module load mamba
    mamba create -n md_setup python=3.12
    mamba activate md_setup
    pip install git+https://github.com/hengma1001/md_setup.git
    mamba install pymol-open-source ambertools
    ```
    Other dependencies might also need to be installed, which can be done via `mamba`.

2. Load the conda env
    ```bash
    conda activate /lus/flare/projects/FRAME-IDP/hengma/envs/md_setup/
    ```

3. Run the set up script
    ```bash
    cd /lus/flare/projects/FRAME-IDP/hengma/trpb/md_runs/inputs/
    python param_amber_single.py
    ```

### Run the simulation

1. (Optional) Build the python environment
    It's really tricky at this point.

2. Load the python env

3. Run simulation


