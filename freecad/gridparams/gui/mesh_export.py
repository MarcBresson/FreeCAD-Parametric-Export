"""Export a list of FreeCAD objects to a .3mf mesh file. Ported from the macro's save_mesh."""


def export_objects(objects, export_path):
    export_path = export_path.with_suffix(".3mf")
    import Mesh

    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(str(export_path))
        Mesh.export(objects, str(export_path), options)
    else:
        Mesh.export(objects, str(export_path))
