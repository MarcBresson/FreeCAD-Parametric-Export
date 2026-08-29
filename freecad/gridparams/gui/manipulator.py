from .commands import COMMAND_NAME


class GridParamsManipulator:
    def modifyToolBars(self):
        # "Structure" is the toolbar hosting Std_VarSet ("Create a variable set"); it's
        # present in most modelling workbenches (Part, PartDesign, Draft, Arch/BIM, ...).
        return [{"append": COMMAND_NAME, "toolBar": "Structure"}]
