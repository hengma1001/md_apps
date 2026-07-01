import json
import os

import openmm as omm
import openmm.app as app
import openmm.unit as u
import parmed as pmd

# from .openmm_reporter import ContactMapReporter
from .utils import build_logger, yml_base

logger = build_logger()


class omm_simulation(yml_base):
    """
    Run simulation with OpenMM

    Parameters
    ----------
    pdb_file : ``str``
        Coordinates file (.gro, .pdb, ...), This file contains
        the atom positions and possibly PBC (periodic boundary
        condition) box in the system.

    top_file : ``str``
        Topology file contains the interactions in the system

    check_point : ``str``
        Checkpoint file from previous simulations to continue a
        run. Default evaluates to `None`, meaning to run fresh
        simulation

    GPU_id : ``str`` or ``int``
        The device ids of GPU to use for running the simulation.
        Use strings, '0,1' for example, to use more than 1 GPU,

    output_traj : ``str``
        The output trajectory file (.dcd), This is the file
        stores all the coordinates information of the MD
        simulation results.

    output_log : ``str``
        The output log file (.log). This file stores the MD
        simulation status, such as steps, time, potential energy,
        temperature, speed, etc.

    output_cm : ``str``, optional
        The h5 file contains contact map information.
        Default is None

    report_time : ``int``
        The frequency to write an output in ps. Default is 10

    sim_time : ``int``
        The length of the simulation trajectory in ns. Default is 10

    dt : ``float``
        The time step of the simulation in fs. Default is 2

    explicit_sol : ``bool``
        Whether the system contains explicit water model

    temperature : ``float``
        Simulation temperature in K, default is 300

    pressure : ``float``
        Simulation pressure in bar, default is 1

    nonbonded_cutoff: ``float``
        Cutoff distance for nonbonded interactions in nm, default is
        1
    init_vel : ``bool``
        Initializing velocity, default is False
    """

    def __init__(
        self,
        pdb_file,
        top_file,
        checkpoint=None,
        gpu_id=0,
        output_traj="output.dcd",
        output_log="output.log",
        # output_cm=None,
        report_time=10,
        sim_time=10,
        dt=2.0,
        explicit_sol=True,
        temperature=300.0,
        pressure=1.0,
        anisotropic_barostate=False,
        nonbonded_cutoff=1.0,
        init_vel=False,
        custom_force=None,
    ) -> None:

        super().__init__()
        # inputs
        self.pdb_file = pdb_file
        self.top_file = top_file
        self.checkpoint = checkpoint
        self.gpu_id = str(gpu_id)

        # outputs
        self.output_traj = output_traj
        self.output_log = output_log
        self.report_time = report_time * u.picoseconds
        self.sim_time = sim_time * u.nanoseconds

        # sim setup
        self.dt = dt * u.femtoseconds
        self.explicit_sol = explicit_sol
        self.temperature = temperature
        self.pressure = pressure
        self.anisotropic_barostate = anisotropic_barostate
        self.custom_force = custom_force
        self.nonbonded_cutoff = nonbonded_cutoff * u.nanometers
        self.init_vel = init_vel

        # force field
        self.base_dir = os.getcwd()

    def get_setup(self):
        return {"pdb_file": self.pdb_file, "top_file": self.top_file, "checkpoint": self.checkpoint}

    def build_system(self):
        system_setup = {
            "nonbondedMethod": app.PME,
            "nonbondedCutoff": self.nonbonded_cutoff,
            "constraints": app.HBonds,
        }

        pdb = pmd.load_file(self.top_file, xyz=self.pdb_file)
        if not self.explicit_sol:
            system_setup["implicitSolvent"] = app.GBn2
            pdb.box = None
        system = pdb.createSystem(**system_setup)

        if self.pressure and self.explicit_sol:
            if self.anisotropic_barostate:
                system.addForce(
                    omm.MonteCarloAnisotropicBarostat(
                        (self.pressure, self.pressure, self.pressure) * u.bar,
                        self.temperature * u.kelvin,
                        False,
                        False,
                        True,
                    )
                )
            else:
                system.addForce(omm.MonteCarloBarostat(self.pressure * u.bar, self.temperature * u.kelvin))

        if self.custom_force:
            system.addForce(self.custom_force)

        self.system = system
        self.top = pdb

    def build_simulation(self):
        self.build_system()
        if self.temperature:
            integrator = omm.LangevinMiddleIntegrator(self.temperature * u.kelvin, 1 / u.picosecond, self.dt)
        else:
            integrator = omm.VerletIntegrator(self.dt)

        try:
            platform = omm.Platform_getPlatformByName("CUDA")
            properties = {"DeviceIndex": str(self.gpu_id), "CudaPrecision": "mixed"}
        except Exception:
            platform = omm.Platform_getPlatformByName("OpenCL")
            properties = {"DeviceIndex": str(self.gpu_id)}

        simulation = app.Simulation(self.top.topology, self.system, integrator, platform, properties)
        self.simulation = simulation

    def minimizeEnergy(self):
        self.simulation.context.setPositions(self.top.positions)
        self.simulation.minimizeEnergy()

    def add_reporters(self):
        report_freq = int(self.report_time / self.dt)
        self.simulation.reporters.append(app.DCDReporter(self.output_traj, report_freq))
        self.simulation.reporters.append(
            app.StateDataReporter(
                self.output_log,
                report_freq,
                step=True,
                time=True,
                speed=True,
                potentialEnergy=True,
                temperature=True,
                totalEnergy=True,
            )
        )
        self.simulation.reporters.append(app.CheckpointReporter("checkpnt.chk", report_freq))

    def run_sim(self, path="./"):
        if not os.path.exists(path):
            os.makedirs(path)

        self.build_simulation()
        # skip minimization if check point exists
        if self.checkpoint:
            self.simulation.loadCheckpoint(self.checkpoint)
        else:
            self.minimizeEnergy()

        os.chdir(path)
        self.add_reporters()
        # clutchy round up method
        nsteps = int(self.sim_time / self.dt + 0.5)
        logger.info(f"  Running simulation for {nsteps} steps. ")
        self.simulation.step(nsteps)
        os.chdir(self.base_dir)
