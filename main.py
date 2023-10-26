#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Local imports
from gameoflife import Simulation


simulation = Simulation(
    board_size=(50, 50),
    speed=1,
    living_rate=.1,
    export=True,
    filename='export',
    fps=20
)
