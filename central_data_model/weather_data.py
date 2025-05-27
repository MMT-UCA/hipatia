"""
Weather data module
Copyright © 2025 MMT department-University of Cadiz
Project Coder Pilar Monsalvete Álvarez de uribarri pilar.monsalvete@uca.es
"""


class WeatherData:
  """
  WeatherData class models a set of atmospheric conditions
  """
  def __init__(self, temperature=None, global_horizontal_radiation=None, diffuse_radiation=None,
               wind_speed=None, wind_direction=None, relative_humidity=None, pressure=None, solar_position=None):
    self._temperature = temperature
    self._global_horizontal_radiation = global_horizontal_radiation
    self._diffuse_radiation = diffuse_radiation
    self._wind_speed = wind_speed
    self._wind_direction = wind_direction
    self._relative_humidity = relative_humidity
    self._pressure = pressure
    self._solar_position = solar_position

  @property
  def temperature(self):
    """
    Get temperature in ºC
    :return: float
    """
    return self._temperature

  @property
  def global_horizontal_radiation(self):
    """
    Get global horizontal radiation in W/m2
    :return: float
    """
    return self._global_horizontal_radiation

  @property
  def diffuse_radiation(self):
    """
    Get diffuse radiation in W/m2
    :return: float
    """
    return self._diffuse_radiation

  @property
  def wind_speed(self):
    """
    Get wind speed in m/s
    :return: float
    """
    return self._wind_speed

  @property
  def wind_direction(self):
    """
    Get wind direction in radians (North = 0 and clockwise)
    :return: float
    """
    return self._wind_direction

  @property
  def relative_humidity(self):
    """
    Get relative humidity in ratio [-]
    :return: float
    """
    return self._relative_humidity

  @property
  def pressure(self):
    """
    Get pressure in Pa
    :return: float
    """
    return self._pressure

  @property
  def solar_position(self):
    """
    Get solar position as [azimuth, zenith angle] in radians
    azimuth is defined as North = 0 and growing clockwise
    zenith angle is defined as Zenith = 0, horizon = pi/2
    :return: [azimuth, zenith_angle]
    """
    return self._solar_position
