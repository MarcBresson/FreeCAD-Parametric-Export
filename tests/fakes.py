"""Minimal FreeCAD Document/Object doubles -- only the surface gui/persistence.py touches."""


class FakeViewObject:
    def __init__(self):
        self.Visibility = True
        self.Proxy = None


class FakeObject:
    def __init__(self, doc, name, type_id="App::FeaturePython", also_derived_from=()):
        self.Document = doc
        self.Name = name
        self.Label = name
        self.TypeId = type_id
        self.Proxy = None
        self.ViewObject = FakeViewObject()
        self._also_derived_from = set(also_derived_from)
        self.Group = []
        self.InList = []

    def addProperty(
        self,
        prop_type,
        name,
        group="",
        doc="",
        attr=0,
        read_only=False,
        hidden=False,
        **kwargs,
    ):
        if not hasattr(self, name):
            setattr(self, name, False if "Bool" in prop_type else "")
        return self

    def isDerivedFrom(self, type_name):
        return type_name == self.TypeId or type_name in self._also_derived_from


def group(parent, *children):
    """Set parent.Group = children, mirroring FreeCAD's auto-maintained InList
    back-references (a Group-typed link makes each child's InList include parent)."""
    parent.Group = list(children)
    for child in children:
        child.InList = list(child.InList) + [parent]
    return parent


def consume(consumer, *inputs):
    """Mimic e.g. a boolean's Base/Tool linking to inputs, without Group nesting."""
    for obj in inputs:
        obj.InList = list(obj.InList) + [consumer]
    return consumer


class FakeDocument:
    def __init__(self, name="Doc"):
        self.Name = name
        self.Objects = []
        self._by_name = {}

    def addObject(self, type_id, base_name):
        name = base_name
        suffix = 1
        while name in self._by_name:
            suffix += 1
            name = f"{base_name}{suffix:03d}"
        obj = FakeObject(self, name, type_id)
        self._by_name[name] = obj
        self.Objects.append(obj)
        return obj

    def getObject(self, name):
        return self._by_name.get(name)

    def recompute(self):
        pass
