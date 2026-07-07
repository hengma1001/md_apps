from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from academy.agent import Agent, action
from academy.handle import Handle
from pydantic import BaseModel

from md_apps import omm_simulation
from md_apps.utils import dict_to_yaml

# from academy.manager import Manager


class SimMetadata(BaseModel):
    """Metadata for a simulation."""

    pdb_file: Path
    sim_config: dict


class SimulationAgent(Agent, ABC):
    """Base agent for running simulations.

    Subclass and override ``run_simulation`` to provide custom
    simulation logic. Use ``agent_on_startup`` to initialize
    expensive state (e.g., load an ML model).

    The ``simulate`` action offloads ``run_simulation`` to a
    thread pool via ``agent_run_sync`` since MD simulations
    are typically blocking.

    Parameters
    ----------

    """

    logger: logging.Logger

    def __init__(
        self,
    ) -> None:
        super().__init__()

    async def agent_on_startup(self) -> None:
        """Initialize the agent.

        Override to add custom startup logic (e.g., loading a
        model). Always call ``await super().agent_on_startup()``
        first.
        """
        # logging = logging.getLogger(type(self).__name__)
        logging.info("started")

    @abstractmethod
    def run_simulation(self, pdb_file: Path) -> Path:
        """Run a simulation for the given metadata.

        Override this method in a subclass to provide custom
        simulation logic. Has access to ``self`` for any
        state initialized in ``__init__`` or
        ``agent_on_startup``.

        Parameters
        ----------
        metadata : SimMetadata
            The simulation metadata (walker weight, restart
            file, parent progress coordinate, etc.).

        Returns
        -------
        Path
            The simulation result path
        """
        ...

    @action
    async def simulate(self, pdb_files: list[Path]) -> list[Path]:
        """Run the simulation and send result."""
        run_paths = []
        for pdb_file in pdb_files:
            logging.info(f"running sim {pdb_file.name} ")

            # Run the simulation in a thread to avoid blocking the event loop
            run_path = await self.agent_run_sync(self.run_simulation, pdb_file)
            run_paths += [Path(run_path)]
            logging.info(f"sim {pdb_file.name} complete")
        return run_paths


class OpenMMSimulationAgent(SimulationAgent):
    """OpenMM simulation agent.

    Subclass of SimulationAgent that runs OpenMM simulations.
    """

    def __init__(
        self,
        sim_config: dict,
        output_dir: Path,
    ) -> None:
        super().__init__()
        self.sim_config = sim_config
        self.output_dir = output_dir

    def run_simulation(self, pdb_file: Path) -> Path:
        """Run an OpenMM simulation for the given metadata.

        Parameters
        ----------
        sim_config : dict
            The simulation configuration (time step, temperature, etc.).
        output_dir : Path
            The directory to store simulation results.

        Returns
        -------
        Path
            The simulation result path
        """
        top_file = str(pdb_file).replace(".inpcrd", ".prmtop")
        logging.info(f"Running OpenMM simulation for {pdb_file} with top file {top_file}")

        run_path = f"{self.output_dir}/{pdb_file.stem}_run"
        sim_config = f"{run_path}/sim_config.yaml"
        if Path(sim_config).exists():
            logging.info(f"Simulation config {sim_config} already exists. Skipping simulation.")
            return Path(run_path)

        omm_run = omm_simulation(
            str(pdb_file),
            top_file,
            **self.sim_config,
        )
        omm_run.run_sim(path=run_path)

        dict_to_yaml(omm_run.get_setup(), f"{run_path}/sim_config.yaml")
        return Path(run_path)
