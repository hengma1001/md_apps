from __future__ import annotations

from pathlib import Path
from typing import TypeVar

from md_apps.parsl_config import ComputeConfigTypes
from pydantic import Field, field_validator
from md_apps.utils import BaseModel

T = TypeVar("T")


class SimulationConfig(BaseModel):
    """Simulation configuration."""

    dt: float = Field(
        2.0,
        description="Time step in femtoseconds.",
    )
    explicit_sol: bool = Field(
        True,
        description="Use explicit solvent model.",
    )
    temperature: float = Field(
        310,
        description="Temperature in Kelvin.",
    )
    pressure: float = Field(
        1,
        description="Pressure in bar.",
    )
    sim_time: float = Field(
        10,
        description="Simulation time in nanoseconds.",
    )
    report_time: float = Field(
        10,
        description="Report time in picoseconds.",
    )
    anisotropic_barostate: bool = Field(
        False,
        description="Use anisotropic barostat.",
    )
    nonbonded_cutoff: float = Field(
        1.0,
        description="Nonbonded cutoff in nanometers.",
    )
    init_vel: bool = Field(
        False,
        description="Initialize velocities.",
    )


class OmmSimulationSettings(BaseModel):
    """Full experiment configuration (YAML)."""

    pdb_string: str = Field(
        description="Glob string for PDB files.",
    )
    output_dir: Path = Field(
        description="Directory to store results.",
    )
    simulation_config: SimulationConfig = Field(
        description="Simulation configuration.",
    )
    compute_config: ComputeConfigTypes = Field(
        description="Compute configuration for running simulations.",
    )

    @field_validator("output_dir")
    @classmethod
    def mkdir_validator(cls, value: Path) -> Path:
        """Resolve and create the output directory."""
        value = value.resolve()
        value.mkdir(parents=True, exist_ok=True)
        return value
