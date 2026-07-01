from md_apps import omm_simulation

inpcrd = "/homes/heng.ma/Research/nlrp3/md_runs/r10_tmd_adp/inputs/input_NLRP3-apo-inactive-ADP/NLRP3-apo-inactive-ADP.inpcrd"

prmtop = "/homes/heng.ma/Research/nlrp3/md_runs/r10_tmd_adp/inputs/input_NLRP3-apo-inactive-ADP/NLRP3-apo-inactive-ADP.prmtop"

omm_run = omm_simulation(pdb_file=inpcrd, top_file=prmtop)
omm_run.run_sim(path="./test_run")
