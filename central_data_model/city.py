"""
City module
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

from central_data_model.district import District
from helpers.geometry_helper import GeometryHelper
from helpers.location import Location
from helpers.attributes.time_series import TimeSeries


class City:
  """
  City class models the boundary conditions of the districts under study
  """

  def __init__(self, temperature=None, global_horizontal_radiation=None, diffuse_radiation=None,
               wind_speed=None, wind_direction=None, relative_humidity=None, pressure=None, districts=None,
               srs_name=None, location=None, lower_corner=None, upper_corner=None):
    self._name = None
    self._temperature = temperature
    self._global_horizontal_radiation = global_horizontal_radiation
    self._diffuse_radiation = diffuse_radiation
    self._wind_speed = wind_speed
    self._wind_direction = wind_direction
    self._relative_humidity = relative_humidity
    self._pressure = pressure
    self._districts = []
    self._srs_name = srs_name
    self._location = location
    self._lower_corner = lower_corner
    self._upper_corner = upper_corner

  # @todo: should be here, but srs_name belongs to [District]
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
      coordinates = transformer.transform(self._lower_corner[0], self._lower_corner[1])
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
  def name(self):
    """
    Get city name
    :return: str
    """
    if self._name is None:
      return self._get_location().city
    return self._name

  @property
  def districts(self) -> Union[List[District], None]:
    """
    Get districts affected by the boundary conditions of the city
    :return: None or [District]
    """
    return self._districts

  @property
  def temperature(self) -> TimeSeries:
    """
    Get temperature in ºC
    :return: TimeSeries
    """
    return self._temperature

  @property
  def global_horizontal_radiation(self) -> TimeSeries:
    """
    Get global horizontal radiation in W/m2
    :return: TimeSeries
    """
    return self._global_horizontal_radiation

  @property
  def diffuse_radiation(self) -> TimeSeries:
    """
    Get diffuse radiation in W/m2
    :return: TimeSeries
    """
    return self._diffuse_radiation

  @property
  def wind_speed(self) -> TimeSeries:
    """
    Get wind speed in m/s
    :return: TimeSeries
    """
    return self._wind_speed

  @property
  def wind_direction(self) -> TimeSeries:
    """
    Get wind direction in degrees (East=0)
    :return: TimeSeries
    """
    return self._wind_direction

  @property
  def relative_humidity(self) -> TimeSeries:
    """
    Get relative humidity in ratio [-]
    :return: TimeSeries
    """
    return self._relative_humidity

  @property
  def pressure(self) -> TimeSeries:
    """
    Get pressure in Pa
    :return: TimeSeries
    """
    return self._pressure

  def add_district(self, new_district):
    """
    Add a new District to the district
    :param new_district:District
    :return: None
    """
    self._districts.append(new_district)
    return None

