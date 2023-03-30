import opengate_core as g4
from ..UserElement import *
from scipy.spatial.transform import Rotation
from box import BoxList
import time

from ..Decorators import requires_warning


class VolumeBase(UserElement):
    """
    Store information about a geometry volume:
    - G4 objects: Solid, LogicalVolume, PhysicalVolume
    - user parameters: user_info
    - additional data such as: mother, material etc
    """

    @staticmethod
    def set_default_user_info(user_info):
        gate.UserElement.set_default_user_info(user_info)
        user_info.mother = gate.__world_name__
        user_info.material = "G4_AIR"
        user_info.translation = [0, 0, 0]
        user_info.color = [1, 1, 1, 1]
        user_info.rotation = Rotation.identity().as_matrix()
        user_info.repeat = None
        user_info.build_physical_volume = True
        # not all volumes should automatically become regions
        # (see comment in construct method):
        # user_info.make_region = True

    def __init__(self, user_info):
        super().__init__(user_info)
        # convert the list of repeat to a BoxList to easier access
        self.user_info.repeat = BoxList(self.user_info.repeat)
        # init
        self.g4_solid = None
        self.g4_logical_volume = None
        self.g4_vis_attributes = None
        # one volume may have several physical volume, this is the first one:
        self.g4_physical_volume = None
        # this list contains all volumes (including first)
        self.g4_physical_volumes = []
        self.material = None
        # self.g4_region = None # turned into property
        # used
        self.volume_engine = None

    def __del__(self):
        pass

    def __str__(self):
        s = f"Volume: {self.user_info}"
        return s

    @property
    @requires_warning("g4_logical_volume")
    def g4_region(self):
        if self.g4_logical_volume is None:
            return None
        else:
            return self.g4_logical_volume.GetRegion()

    def build_solid(self):
        gate.fatal(f'Need to overwrite "build_solid" in {self.user_info}')

    def construct(self, volume_engine):
        self.volume_engine = volume_engine
        # check placements
        ui = self.user_info
        if ui.repeat:
            if ui.translation is not None or ui.rotation is not None:
                gate.fatal(
                    f'When using "repeat", translation and rotation must be None, '
                    f"for volume : {ui.name}"
                )
        # construct solid/material/lv/pv/regions
        self.construct_solid()
        self.construct_material(volume_engine)
        self.construct_logical_volume()
        if self.user_info.build_physical_volume is True:
            self.construct_physical_volume()

    def construct_solid(self):
        # builder the G4 solid
        self.g4_solid = self.build_solid()
        # build the solid according to the type
        # self.g4_solid = self.solid_builder.Build(self.user_info)

    def construct_material(self, volume_engine):
        # retrieve or build the material
        self.material = volume_engine.find_or_build_material(self.user_info.material)

    def construct_logical_volume(self):
        self.g4_logical_volume = g4.G4LogicalVolume(
            self.g4_solid, self.material, self.user_info.name  # solid  # material
        )  # name
        # color
        self.g4_vis_attributes = g4.G4VisAttributes()
        self.g4_vis_attributes.SetColor(*self.user_info.color)
        if self.user_info.color[3] == 0:
            self.g4_vis_attributes.SetVisibility(False)
        else:
            self.g4_vis_attributes.SetVisibility(True)
        self.g4_logical_volume.SetVisAttributes(self.g4_vis_attributes)

    def construct_physical_volume(self):
        # find the mother's logical volume
        if self.user_info.mother:
            st = g4.G4LogicalVolumeStore.GetInstance()
            mother_logical = st.GetVolume(self.user_info.mother, False)
        else:
            mother_logical = None
        # consider the 3D transform -> helpers_transform.
        if self.user_info.repeat:
            self.construct_physical_volume_repeat(mother_logical)
        else:
            transform = gate.get_vol_g4_transform(self.user_info)
            check = (
                self.volume_engine.simulation_engine.simulation.user_info.check_volumes_overlap
            )
            self.g4_physical_volume = g4.G4PVPlacement(
                transform,
                self.g4_logical_volume,  # logical volume
                self.user_info.name,  # volume name
                mother_logical,  # mother volume or None if World
                False,  # no boolean operation # FIXME for BooleanVolume ?
                0,  # copy number
                check,
            )  # overlaps checking
            self.g4_physical_volumes.append(self.g4_physical_volume)

    def construct_physical_volume_repeat(self, mother_logical):
        check = (
            self.volume_engine.simulation_engine.simulation.user_info.check_volumes_overlap
        )
        i = 0
        for repeat_vol in self.user_info.repeat:
            transform = gate.get_vol_g4_transform(repeat_vol)
            v = g4.G4PVPlacement(
                transform,
                self.g4_logical_volume,  # logical volume
                repeat_vol.name,  # volume name
                mother_logical,  # mother volume or None if World
                False,  # no boolean operation
                i,  # copy number
                check,
            )  # overlaps checking
            i += 1
            self.g4_physical_volumes.append(v)
        self.g4_physical_volume = self.g4_physical_volumes[0]
