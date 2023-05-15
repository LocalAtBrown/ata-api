from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple
from uuid import UUID, uuid4

import click
import pandas as pd

from ata_api.helpers.enums import SiteName


@dataclass
class User:
    site_name: SiteName
    user_id: UUID = field(default_factory=uuid4)

    def convert_to_path(self) -> Tuple[str, str]:
        return f"{self.site_name}/{self.user_id.hex}"


@click.command()
@click.option("--afro-la", default=0, type=int)
@click.option("--dallas-free-press", default=0, type=int)
@click.option("--open-vallejo", default=0, type=int)
@click.option("--the-19th", default=0, type=int)
def main(afro_la: int, dallas_free_press: int, open_vallejo: int, the_19th: int) -> None:
    paths = pd.Series(
        [
            *[User(site_name=SiteName.AFRO_LA).convert_to_path() for _ in range(afro_la)],
            *[User(site_name=SiteName.DALLAS_FREE_PRESS).convert_to_path() for _ in range(dallas_free_press)],
            *[User(site_name=SiteName.OPEN_VALLEJO).convert_to_path() for _ in range(open_vallejo)],
            *[User(site_name=SiteName.THE_19TH).convert_to_path() for _ in range(the_19th)],
        ],
        name="path",
    )

    assert paths.nunique() == len(paths)

    paths.to_csv(
        f"{Path(__file__).parent}/paths_{afro_la}_{dallas_free_press}_{open_vallejo}_{the_19th}.csv", index=False, header=False
    )


if __name__ == "__main__":
    main()
