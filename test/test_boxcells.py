"""
TestBoxCells
Copyright © 2025 MMT department-University of Cadiz
Project Coder Pilar Monsalvete pilar.monsalvete@uca.es
"""

from pathlib import Path
from unittest import TestCase

from imports.geometry_factory import GeometryFactory


class TestBoxCells(TestCase):
  """
  Test Canyon workflow
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

  def test_box_cells(self):
    """
    Test canyon workflow
    """
    file = Path(self._example_path / 'hipatia_1.geojson').resolve()
    city = GeometryFactory('geojson',
                           path=file,
                           height_field='height',
                           year_of_construction_field="yoc",
                           type_field="type").city

    for building in city.districts[0].buildings:
      for ground in building.grounds:
        for point in ground.perimeter_polygon.points:
          print(point.coordinates)
      print()

      print(building.name, building.year_of_construction, building.max_height)

      print()

