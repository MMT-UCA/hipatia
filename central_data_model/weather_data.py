"""
Weather data module
Copyright © 2025 MMT department-University of Cadiz
Project Coder Pilar Monsalvete Álvarez de uribarri pilar.monsalvete@uca.es
"""

from helpers.attributes.time_series import TimeSeries


class WeatherData:
  """
  WeatherData class models a set of atmospheric conditions
  """
  def __init__(self, temperature=None, global_horizontal_radiation=None, diffuse_radiation=None,
               wind_speed=None, wind_direction=None, relative_humidity=None, pressure=None):
    self._temperature = temperature
    self._global_horizontal_radiation = global_horizontal_radiation
    self._diffuse_radiation = diffuse_radiation
    self._wind_speed = wind_speed
    self._wind_direction = wind_direction
    self._relative_humidity = relative_humidity
    self._pressure = pressure

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
