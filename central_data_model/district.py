"""
District module
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
Code contributors: Peter Yefi peteryefi@gmail.com
"""

from __future__ import annotations

import logging
from typing import List, Union

import pyproj
from pyproj import Transformer

from central_data_model.weather_data import WeatherData
from central_data_model.building import Building
from central_data_model.open_area import OpenArea
from helpers.geometry_helper import GeometryHelper
from helpers.location import Location
from helpers.attributes.polygon import Polygon


class District:
  """
  District class models the district under study and its boundary conditions
  """

  def __init__(self, srs_name=None, location=None, polygon=None, boundaries_weather_data=None):
    self._city_name = None
    self._srs_name = srs_name
    self._location = location
    self._polygon = polygon
    self._boundaries_weather_data = boundaries_weather_data
    self._micro_climate_weather_data = None
    self._srs_name = srs_name
    self._buildings_dictionary = {}
    self._open_areas_dictionary = {}
    self._buildings = []
    self._open_areas = []
    self._reference_coordinates = None

  def _get_location(self) -> Location:
    if self._location is None:
      gps = pyproj.CRS('EPSG:4326')  # LatLon with WGS84 datum used by GPS units and Google Earth
      try:
        if self._srs_name in GeometryHelper.srs_transformations:
          self._srs_name = GeometryHelper.srs_transformations[self._srs_name]
        input_reference = pyproj.CRS(self._srs_name)  # Projected coordinate system from input data
      except pyproj.exceptions.CRSError as err:
        logging.error('Invalid projection reference system, please check the input data.')
        raise pyproj.exceptions.CRSError from err
      transformer = Transformer.from_crs(input_reference, gps)
      coordinates = transformer.transform(self.polygon.center_of_gravity.coordinates[0],
                                          self.polygon.center_of_gravity.coordinates[1])
      self._location = GeometryHelper.get_location(coordinates[0], coordinates[1])
    return self._location

  @property
  def country_code(self):
    """
    Get city country code
    :return: str
    """
    return self._get_location().country

  @property
  def region_code(self):
    """
    Get city region name
    :return: str
    """
    return self._get_location().region_code

  @property
  def time_zone(self) -> Union[None, float]:
    """
    Get city time_zone
    :return: None or float
    """
    return self._get_location().time_zone

  @property
  def city_name(self):
    """
    Get name of the city to which the district belongs
    :return: str
    """
    if self._city_name is None:
      return self._get_location().city
    return self._city_name

  @property
  def srs_name(self) -> Union[None, str]:
    """
    Get district's srs name
    :return: None or str
    """
    return self._srs_name

  @property
  def boundaries_weather_data(self) -> WeatherData:
    """
    Get the weather data of the boundaries of the district
    :return: WeatherData
    """
    return self._boundaries_weather_data

  @boundaries_weather_data.setter
  def boundaries_weather_data(self, value):
    """
    Set the weather data of the boundaries of the district
    :param value: WeatherData
    """
    self._boundaries_weather_data = value

  @property
  def micro_climate_weather_data(self) -> WeatherData:
    """
    Get the district weather data effected by the micro-climate
    :return: WeatherData
    """
    return self._micro_climate_weather_data

  @micro_climate_weather_data.setter
  def micro_climate_weather_data(self, value):
    """
    Set the district weather data effected by the micro-climate
    :param value: WeatherData
    """
    self._micro_climate_weather_data = value

  @property
  def buildings(self) -> Union[List[Building], None]:
    """
    Get the buildings belonging to the district
    :return: None or [Building]
    """
    return self._buildings

  @property
  def open_areas(self) -> Union[List[OpenArea], None]:
    """
    Get the open areas belonging to the district (patios, urban canyons...)
    :return: None or [OpenArea]
    """
    return self._open_areas

  def building(self, name) -> Union[Building, None]:
    """
    Retrieve the building with the given name
    :param name:str
    :return: None or Building
    """
    if name in self._buildings_dictionary:
      return self.buildings[self._buildings_dictionary[name]]
    return None

  def open_area(self, name) -> Union[OpenArea, None]:
    """
    Retrieve the open area with the given name
    :param name:str
    :return: None or OpenArea
    """
    if name in self._open_areas_dictionary:
      return self.open_areas[self._open_areas_dictionary[name]]
    return None

  def add_building(self, new_building):
    """
    Add a new Building to the district
    :param new_building:Building
    :return: None
    """
    self._buildings.append(new_building)
    self._buildings_dictionary[new_building.name] = len(self._buildings) - 1
    return None

  def add_open_area(self, new_open_area):
    """
    Add a new OpenArea to the district
    :param new_open_area:OpenArea
    :return: None
    """
    self._open_areas.append(new_open_area)
    self._open_areas_dictionary[new_open_area.name] = len(self._open_areas) - 1

  def remove_building(self, building):
    """
    Remove a Building from the district
    :param building:Building
    :return: None
    """
    if not self._buildings:
      logging.warning('impossible to remove building, the district does not have any\n')
    else:
      if building in self._buildings:
        self._buildings.remove(building)
        # regenerate hash map
        self._buildings_dictionary = {}
        for i, _building in enumerate(self._buildings):
          self._buildings_dictionary[_building.name] = i

  def remove_open_area(self, open_area):
    """
    Remove an OpenArea from the district
    :param open_area:OpenArea
    :return: None
    """
    if not self._open_areas:
      logging.warning('impossible to remove an open area, the district does not have any\n')
    else:
      if open_area in self._open_areas:
        self._open_areas.remove(open_area)
        # regenerate hash map
        self._open_areas_dictionary = {}
        for i, _open_area in enumerate(self._open_areas):
          self._open_areas_dictionary[_open_area.name] = i

  @property
  def polygon(self) -> Polygon:
    """
    Get boundary foot-print polygon
    :return: Polygon
    """
    return self._polygon

  @polygon.setter
  def polygon(self, value):
    """
    Set boundary foot-print polygon
    :param value: Polygon
    """
    self._polygon = value

  @property
  def area(self):
    """
    Get ground area of the district (m2)
    :return: float
    """
    return self.polygon.area

  @property
  def reference_coordinates(self):
    """
    Get reference coordinates to translate the points to the real geographical point in EPSG:2062
    :return: [x, y, z]
    """
    return self._reference_coordinates

  @reference_coordinates.setter
  def reference_coordinates(self, value):
    """
    Set reference coordinates to translate the points to the real geographical point in EPSG:2062
    :param value: [x, y, z]
    """
    self._reference_coordinates = value
