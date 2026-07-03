from md_apps import omm_simulation

inpcrd = "/nfs/lambda_stor_01/homes/heng.ma/Research/nlrp3/nlrp3/md_runs/smol_screen_2gbi_bms/inputs/input_nlrp3_active_llr_5/nlrp3_active_llr_5.inpcrd"

prmtop = "/nfs/lambda_stor_01/homes/heng.ma/Research/nlrp3/nlrp3/md_runs/smol_screen_2gbi_bms/inputs/input_nlrp3_active_llr_5/nlrp3_active_llr_5.prmtop"

omm_run = omm_simulation(pdb_file=inpcrd, top_file=prmtop, explicit_sol=False)
omm_run.run_sim(path="./test_run")
