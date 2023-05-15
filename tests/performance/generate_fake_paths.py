from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple
from uuid import UUID, uuid4

import click
import numpy as np
import pandas as pd

from ata_api.helpers.enums import SiteName

rng = np.random.default_rng()


@dataclass
class User:
    site_name: SiteName
    user_id: UUID = field(default_factory=uuid4)

    def convert_to_path(self) -> Tuple[str, str]:
        return f"{self.site_name}/{self.user_id.hex}"


@click.command()
@click.option("-n", "--num-samples", required=True, type=int)
@click.option("--freq-afla", default=0.1, type=float)
@click.option("--freq-dfp", default=0.2, type=float)
@click.option("--freq-ov", default=0.2, type=float)
@click.option("--freq-19", default=0.5, type=float)
def main(num_samples: int, freq_afla: float, freq_dfp: float, freq_ov: float, freq_19: float) -> None:
    num_afro_la, num_dallas_free_press, num_open_vallejo, num_the_19th = rng.multinomial(
        n=num_samples, pvals=[freq_afla, freq_dfp, freq_ov, freq_19]
    )

    paths = pd.Series(
        [
            *[User(site_name=SiteName.AFRO_LA).convert_to_path() for _ in range(num_afro_la)],
            *[User(site_name=SiteName.DALLAS_FREE_PRESS).convert_to_path() for _ in range(num_dallas_free_press)],
            *[User(site_name=SiteName.OPEN_VALLEJO).convert_to_path() for _ in range(num_open_vallejo)],
            *[User(site_name=SiteName.THE_19TH).convert_to_path() for _ in range(num_the_19th)],
        ],
        name="path",
    )

    assert paths.nunique() == len(paths)

    paths.sample(frac=1).to_csv(
        f"{Path(__file__).parent}/paths_{num_samples}.csv",
        index=False,
        header=False,
    )


if __name__ == "__main__":
    main()
