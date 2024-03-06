from ..exception import warning, fatal
from ..base import GateObject
from ..image import sum_itk_images
from pathlib import Path


def _setter_hook_belongs_to(self, belongs_to):
    try:
        belongs_to_name = belongs_to.name
    except AttributeError:
        belongs_to_name = belongs_to
    return belongs_to_name


def _setter_hook_path(self, path):
    return Path(path)


class ActorOutput(GateObject):
    user_info_defaults = {
        "belongs_to": (
            None,
            {
                "doc": "Name of the actor to which this output belongs.",
                "setter_hook": _setter_hook_belongs_to,
                "required": True,
            },
        ),
        "data_path": (
            None,
            {
                "doc": "Path to the data represented by this actor output. "
                "Relative paths and filenames are taken "
                "relative to the global simulation output folder "
                "set via the Simulation.output_path option. ",
            },
        ),
        "keep_data_in_memory": (
            True,
            {
                "doc": "Should the data be kept in memory after the end of the simulation? "
                "Otherwise, it is only stored on disk and needs to be re-loaded manually. "
                "Careful: Large data structures like a phase space need a lot of memory.",
            },
        ),
        "keep_data_per_run": (
            False,
            {
                "doc": "In case the simulation has multiple runs, should separate results per run be kept?"
            },
        ),
        "merge_data_from_runs": (
            True,
            {
                "doc": "In case the simulation has multiple runs, should results from separate runs be merged?"
            },
        ),
    }

    def __init__(self, *args, actor_user_input=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Store the user_info dictionary of the associated actor for convenience:
        self.actor_user_input = actor_user_input

        self.data_per_run = None  # holds the data per run in memory
        self.merged_data = None  # holds the data merged from multiple runs in memory

    @property
    def data(self):
        if len(self.data_per_run) > 1:
            warning(
                f"You are using the convenience property 'data' to access the data in this actor output. "
                f"This returns you the data from the first run, but the actor output stores "
                f"data from {len(self.data_per_run)} runs. "
                f"To access them, use 'data_per_run[RUN_INDEX]' instead or 'merged_data'. "
            )
        return self.data_per_run[0]

    def merge_data_from_runs(self):
        raise NotImplementedError(
            f"Your are calling this method from the base class {type(self).__name__}, "
            f"but it should be implemented in the specific derived class"
        )

    def load_data(self):
        raise NotImplementedError(
            f"Your are calling this method from the base class {type(self).__name__}, "
            f"but it should be implemented in the specific derived class"
        )

    def get_output_path(self, run_index=None):
        if run_index is None:
            return self.data_path
        else:
            return self.data_path.with_name(
                self.data_path.stem + f"_run{run_index:03f}" + self.data_path.suffix
            )

    def close(self):
        if self.keep_data_per_run is False:
            self.data_per_run = None
        if self.keep_data_in_memory is False:
            self.data_per_run = None
            self.merged_data = None
        super().close()


class ActorOutputImage(ActorOutput):
    user_info_defaults = {
        "merge_method": (
            "sum",
            {
                "doc": "How should images from runs be merged?",
                "allowed_values": ("sum",),
            },
        ),
    }

    def merge_data_from_runs(self):
        if self.merge_method == "sum":
            self.merged_data = sum_itk_images(self.data_per_run)


class ActorOutputRoot(ActorOutput):
    user_info_defaults = {
        "merge_method": (
            "append",
            {
                "doc": "How should images from runs be merged?",
                "allowed_values": ("append",),
            },
        ),
    }

    def merge_data_from_runs(self):
        if self.merge_method == "append":
            raise NotImplementedError("Appending ROOT files not yet implemented.")
