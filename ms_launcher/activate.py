import bastd

from ms_launcher.ui.gather import OurPublicGatherTab


def make_redefine() -> None:
    """Redefine BombSquad classes/functions etc."""

    bastd.ui.gather.publictab.PublicGatherTab = OurPublicGatherTab


def activate() -> None:
    """Main launcher starts point."""

    make_redefine()
