from __future__ import annotations

import argparse
import asyncio
import glob
import logging
import os
import signal
from argparse import ArgumentParser
from pathlib import Path

from academy.exchange.cloud import spawn_http_exchange
from academy.logging.recommended import recommended_logging
from academy.manager import Manager
from parsl.concurrent import ParslPoolExecutor

from md_apps.agents import OpenMMSimulationAgent
from md_apps.api import OmmSimulationSettings as SimSettings

EXCHANGE_PORT = 5346
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", required=True)
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    cfg = SimSettings.from_yaml(args.config)
    cfg.dump_yaml(cfg.output_dir / "params.yaml")

    recommended_logging("INFO", logfile=cfg.output_dir / "runtime.log")

    # Create Parsl configuration from compute config
    parsl_config = cfg.compute_config.get_parsl_config(
        cfg.output_dir / "run-info",
    )

    gpu_executor = ParslPoolExecutor(parsl_config)

    # Handle `kill <pid>` (SIGTERM). Parsl workers survive the main
    # process dying, and normal interpreter shutdown hangs after
    # atexit cleans up the DFK. Using os._exit() after shutdown
    # sidesteps the hang while still tearing down workers cleanly.
    def _handle_sigterm(*_: object) -> None:
        gpu_executor.shutdown(wait=False)
        os._exit(0)

    signal.signal(signal.SIGTERM, _handle_sigterm)

    pdb_files = glob.glob(cfg.pdb_string)[:4]
    logging.info(f"Found {len(pdb_files)} PDB files to simulate: {pdb_files}")

    with spawn_http_exchange(
        "localhost",
        EXCHANGE_PORT,
    ) as factory:
        try:
            async with await Manager.from_exchange_factory(
                factory=factory,
                executors=gpu_executor,
            ) as manager:

                # Spawn a simulation agent for each PDB file
                n_workers = 2
                sim_agents = await asyncio.gather(
                    *[
                        manager.launch(
                            OpenMMSimulationAgent,
                            kwargs={
                                "sim_config": cfg.simulation_config,
                                "output_dir": cfg.output_dir,
                            },
                        )
                        for _ in range(n_workers)
                    ]
                )

                results = await asyncio.gather(
                    *[
                        agent.simulate([Path(pdb_file) for pdb_file in pdb_files[i::n_workers]])
                        for i, agent in enumerate(sim_agents)
                    ]
                )
                logging.info(f"Simulation results: {results}")

        finally:
            gpu_executor.shutdown(wait=True)


if __name__ == "__main__":
    asyncio.run(main())

# pdb_files = glob.glob("lus/flare/projects/FRAME-IDP/hengma/nlrp3/md_sim/inputs/input_nlrp3_*/nlrp3_*.inpcrd")
