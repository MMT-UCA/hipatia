"""
GeometryFactory retrieve the specific geometric module to load the given format
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
"""

from central_data_model.city import City
from helpers.utils import validate_import_export_type
from imports.geometry.geojson import Geojson


class GeometryFactory:
  """
  GeometryFactory class
  """
  def __init__(self, file_type,
               path,
               height_field=None,
               year_of_construction_field=None,
               function_field=None,
               type_field=None):
    self._file_type = '_' + file_type.lower()
    validate_import_export_type(GeometryFactory, file_type)
    self._path = path
    self._height_field = height_field
    self._year_of_construction_field = year_of_construction_field
    self._function_field = function_field
    self._type_field = type_field

  @property
  def _geojson(self) -> City:
    """
    Enrich the city by using Geojson information as data source
    :return: City
    """
    return Geojson(self._path,
                   self._height_field,
                   self._year_of_construction_field,
                   self._function_field,
                   self._type_field).city

  @property
  def city(self) -> City:
    """
    Enrich the city given to the class using the class given handler
    :return: City
    """
    return getattr(self, self._file_type, lambda: None)
