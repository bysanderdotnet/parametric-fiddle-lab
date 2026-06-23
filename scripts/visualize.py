import sys
import argparse
import tempfile
import os
import cadquery as cq

import vtk
from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vuetify3, vtk as vtk_widgets

def load_step_as_polydata(step_file):
    shape = cq.importers.importStep(step_file)
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
        tmp_name = tmp.name
    cq.exporters.export(shape, tmp_name)

    reader = vtk.vtkSTLReader()
    reader.SetFileName(tmp_name)
    reader.Update()

    polydata = vtk.vtkPolyData()
    polydata.DeepCopy(reader.GetOutput())
    os.remove(tmp_name)
    return polydata

def create_pipeline(polydata, color):
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color)

    return actor

def main():
    parser = argparse.ArgumentParser(description="Side by side comparison of CAD models")
    parser.add_argument("generated", help="Generated STEP file")
    parser.add_argument("reference", help="Reference STEP file")

    # Parse known args so trame args don't break our argparse
    args, unknown = parser.parse_known_args()

    print(f"Loading {args.generated}...")
    poly1 = load_step_as_polydata(args.generated)
    print(f"Loading {args.reference}...")
    poly2 = load_step_as_polydata(args.reference)

    server = get_server(client_type="vue3")
    state, ctrl = server.state, server.controller

    renderer1 = vtk.vtkRenderer()
    renderer1.SetBackground(1, 1, 1)
    renderWindow1 = vtk.vtkRenderWindow()
    renderWindow1.AddRenderer(renderer1)
    renderWindowInteractor1 = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor1.SetRenderWindow(renderWindow1)
    renderWindowInteractor1.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    actor1 = create_pipeline(poly1, (0.2, 0.6, 0.8)) # Blue-ish
    renderer1.AddActor(actor1)
    renderer1.ResetCamera()

    renderer2 = vtk.vtkRenderer()
    renderer2.SetBackground(1, 1, 1)
    renderWindow2 = vtk.vtkRenderWindow()
    renderWindow2.AddRenderer(renderer2)
    renderWindowInteractor2 = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor2.SetRenderWindow(renderWindow2)
    renderWindowInteractor2.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

    actor2 = create_pipeline(poly2, (0.8, 0.6, 0.2)) # Orange-ish
    renderer2.AddActor(actor2)
    renderer2.ResetCamera()

    # Sync cameras
    renderer2.SetActiveCamera(renderer1.GetActiveCamera())

    with SinglePageLayout(server) as layout:
        layout.title.set_text("Visual Test Renderer")
        with layout.content:
            with vuetify3.VContainer(fluid=True, classes="fill-height pa-0"):
                with vuetify3.VRow(classes="fill-height", no_gutters=True):
                    with vuetify3.VCol(cols="6", classes="fill-height border-e"):
                        view1 = vtk_widgets.VtkLocalView(renderWindow1)
                    with vuetify3.VCol(cols="6", classes="fill-height"):
                        view2 = vtk_widgets.VtkLocalView(renderWindow2)

    server.start()

if __name__ == "__main__":
    main()
