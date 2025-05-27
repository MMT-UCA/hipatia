"""
TestHipatiaTemplate
Copyright © 2025 MMT department-University of Cadiz
Project Coder Pilar Monsalvete pilar.monsalvete@uca.es
"""

from pathlib import Path
from unittest import TestCase

from imports.geometry_factory import GeometryFactory
from modules.this_module_does_nothing import ThisModuleDoesNothing


class TestHipatiaTemplate(TestCase):
  """
  Thi is a template for hipatia modules
  Load testing
  """

  def setUp(self) -> None:
    """
    Test setup
    :return: None
    """
    self._city = None
    self._example_path = (Path(__file__).parent / 'data').resolve()
    self._output_path = (Path(__file__).parent / 'outputs').resolve()

  def test_hipatia_template(self):
    """
    Hipatia template for any use
    """
    # 1. file with the geometrical information
    file = Path(self._example_path / 'buildings.geojson').resolve()
    # 2. The data model is firstly created here with geometrical information
    district = GeometryFactory('geojson',
                               path=file,
                               height_field='height',
                               year_of_construction_field="yoc",
                               type_field="feature_type").district
    # 3. If you want to create new objects (or save information in the already created)
    # with info from other files, do it here

    # 4. Use the data model to call your module
    this_module_does_nothing = ThisModuleDoesNothing()
    for building in district.buildings:
      this_module_does_nothing.do_nothing(building.name)

    print(district.reference_coordinates)
    for building in district.buildings:
      for surface in building.surfaces:
        print(surface.perimeter_polygon.coordinates)
      print(f'District area = {district.area} m2')
