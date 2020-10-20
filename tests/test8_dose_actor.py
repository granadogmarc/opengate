#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gam
import platform
from scipy.spatial.transform import Rotation

# global log level
gam.log.setLevel(gam.DEBUG)

# create the simulation
sim = gam.Simulation()

# verbose and GUI
sim.set_g4_verbose(False)
sim.set_g4_visualisation_flag(False)

# set random engine
sim.set_g4_random_engine("MersenneTwister", 123456)

#  change world size
m = gam.g4_units('m')
world = sim.get_volume('World')
world.size = [1 * m, 1 * m, 1 * m]

# add a simple fake volume to test hierarchy
# translation and rotation like in the Gate macro
fake = sim.add_volume('Box', 'fake')
cm = gam.g4_units('cm')
fake.size = [40 * cm, 40 * cm, 40 * cm]
fake.translation = [1 * cm, 2 * cm, 3 * cm]
fake.rotation = Rotation.from_euler('x', 10, degrees=True).as_matrix()
fake.material = 'G4_AIR'
fake.color = [1, 0, 1, 1]

# waterbox
waterbox = sim.add_volume('Box', 'waterbox')
waterbox.mother = 'fake'
waterbox.size = [10 * cm, 10 * cm, 10 * cm]
waterbox.translation = [-3 * cm, -2 * cm, -1 * cm]
waterbox.rotation = Rotation.from_euler('y', 20, degrees=True).as_matrix()
waterbox.material = 'G4_WATER'
waterbox.color = [0, 0, 1, 1]

# default source for tests
source = sim.add_source('TestProtonTime', 'mysource')
MeV = gam.g4_units('MeV')
Bq = gam.g4_units('Bq')
source.energy = 150 * MeV
nm = gam.g4_units('nm')
source.radius = 1 * nm
source.activity = 3000 * Bq

# add dose actor
dose = sim.add_actor('DoseActor', 'dose')
dose.save = 'output/test8-edep.mhd'
dose.attachedTo = 'waterbox'
dose.dimension = [99, 99, 99]
mm = gam.g4_units('mm')
dose.spacing = [2 * mm, 2 * mm, 2 * mm]
dose.translation = [2 * mm, 3 * mm, -2 * mm]

# add stat actor
stats = sim.add_actor('SimulationStatisticsActor', 'Stats')

# create G4 objects
sim.initialize()

# explicit check overlap (already performed during initialize)
sim.check_geometry_overlaps(verbose=True)

# print info
print(sim.dump_volumes())

# verbose
sim.g4_apply_command('/tracking/verbose 0')
# sim.g4_com("/run/verbose 2")
# sim.g4_com("/event/verbose 2")
# sim.g4_com("/tracking/verbose 1")

# start simulation
gam.source_log.setLevel(gam.RUN)
sim.start()

# print results at the end
stat = sim.actors_info.Stats.g4_actor
print(stat)

d = sim.actors_info.dose.g4_actor
print(d)

# tests
stats_ref = gam.read_stat_file('./gate_test8_dose_actor/output/stat.txt')
gam.assert_stats(stat, stats_ref, 0.01)
gam.assert_images('output/test8-edep.mhd', 'gate_test8_dose_actor/output/output-Edep.mhd', tolerance=0.1)

gam.test_ok()