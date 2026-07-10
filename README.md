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
    ```bash
    module load frameworks
    source /lus/flare/projects/FRAME-IDP/hengma/envs/agent/bin/activate
    ```

3. Run simulation
    ```bash
    cd /lus/flare/projects/FRAME-IDP/hengma/trpb/md_runs/md_sim
    python run_md.py -c aurora_test.yml
    ```

    ```yaml
    pdb_string: "/lus/flare/projects/FRAME-IDP/yuzhang/0k0000w/input_*/*inpcrd"
    output_dir: "/lus/flare/projects/FRAME-IDP/hengma/trpb/md_runs/md_sim/outputs"
    simulation_config:
        dt: 2.0
        temperature: 310.0
        sim_time: 0.1
        report_time: 10
        nonbonded_cutoff: 1.0
        pressure: 1.0
    compute_config:
        name: "aurora"
        num_nodes: 2
        account: "FRAME-IDP"
        queue: "debug-scaling"
        walltime: "1:00:00"
        scheduler_options: "#PBS -l filesystems=home:flare"
        worker_init: "module load frameworks; source /lus/flare/projects/FRAME-IDP/hengma/envs/agent/bin/activate; export TMPDIR=/tmp; export ZE_FLAT_DEVICE_HIERARCHY=FLAT "
    ```

