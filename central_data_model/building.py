"""
Building module
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guille Gutierrez guillermo.gutierrezmorote@concordia.ca
Code contributors: Pilar Monsalvete Alvarez de Uribarri pilar.monsalvete@concordia.ca
"""

import logging
from typing import List, Union, TypeVar

import numpy as np
import helpers.constants as cte
from central_data_model.building_demand.internal_zone import InternalZone
from central_data_model.building_demand.thermal_zone import ThermalZone
from central_data_model.building_demand.surface import Surface
from central_data_model.city_object import CityObject

District = TypeVar('District')


class Building(CityObject):
  """
  Building(CityObject) class
  """
  def __init__(self, name, surfaces, year_of_construction, function, terrains=None, city=None):
    super().__init__(name, surfaces)
    self._city = city
    self._basement_heated = None
    self._attic_heated = None
    self._terrains = terrains
    self._year_of_construction = year_of_construction
    self._function = function
    self._average_storey_height = None
    self._storeys_above_ground = None
    self._floor_area = None
    self._roof_type = None
    self._internal_zones = None
    self._thermal_zones_from_internal_zones = None
    self._aliases = []
    self._type = 'building'
    self._cold_water_temperature = {}
    self._heating_demand = {}
    self._cooling_demand = {}
    self._lighting_electrical_demand = {}
    self._appliances_electrical_demand = {}
    self._domestic_hot_water_heat_demand = {}
    self._heating_consumption = {}
    self._cooling_consumption = {}
    self._domestic_hot_water_consumption = {}
    self._distribution_systems_electrical_consumption = {}
    self._onsite_electrical_production = {}
    self._eave_height = None
    self._energy_systems = None
    self._systems_archetype_name = None
    self._grounds = []
    self._roofs = []
    self._walls = []
    self._internal_walls = []
    self._ground_walls = []
    self._attic_floors = []
    self._interior_slabs = []
    for surface_id, surface in enumerate(self.surfaces):
      self._min_x = min(self._min_x, surface.lower_corner[0])
      self._min_y = min(self._min_y, surface.lower_corner[1])
      self._min_z = min(self._min_z, surface.lower_corner[2])
      self._max_x = max(self._max_x, surface.upper_corner[0])
      self._max_y = max(self._max_y, surface.upper_corner[1])
      self._max_z = max(self._max_z, surface.upper_corner[2])
      surface.id = surface_id
      if surface.type == cte.GROUND:
        self._grounds.append(surface)
      elif surface.type == cte.WALL:
        self._walls.append(surface)
      elif surface.type == cte.ROOF:
        self._roofs.append(surface)
      elif surface.type == cte.INTERIOR_WALL:
        self._internal_walls.append(surface)
      elif surface.type == cte.GROUND_WALL:
        self._ground_walls.append(surface)
      elif surface.type == cte.ATTIC_FLOOR:
        self._attic_floors.append(surface)
      elif surface.type == cte.INTERIOR_SLAB:
        self._interior_slabs.append(surface)
      else:
        logging.error('Building %s [%s] has an unexpected surface type %s.', self.name, self.aliases, surface.type)

  @property
  def internal_zones(self) -> List[InternalZone]:
    """
    Get building internal zones
    For Lod up to 3, there is only one internal zone which corresponds to the building shell.
    In LoD 4 there can be more than one. In this case the definition of surfaces and floor area must be redefined.
    :return: [InternalZone]
    """
    if self._internal_zones is None:
      self._internal_zones = [InternalZone(self.surfaces, self.floor_area, self.volume)]
    return self._internal_zones

  @property
  def thermal_zones_from_internal_zones(self) -> Union[None, List[ThermalZone]]:
    """
    Get building thermal zones
    :return: [ThermalZone]
    """
    if self._thermal_zones_from_internal_zones is None:
      self._thermal_zones_from_internal_zones = []
      for internal_zone in self.internal_zones:
        if internal_zone.thermal_zones_from_internal_zones is None:
          self._thermal_zones_from_internal_zones = None
          return self._thermal_zones_from_internal_zones
        self._thermal_zones_from_internal_zones.append(internal_zone.thermal_zones_from_internal_zones[0])
    return self._thermal_zones_from_internal_zones

  @property
  def grounds(self) -> List[Surface]:
    """
    Get building ground surfaces
    :return: [Surface]
    """
    return self._grounds

  @property
  def roofs(self) -> List[Surface]:
    """
    Get building roof surfaces
    :return: [Surface]
    """
    return self._roofs

  @property
  def walls(self) -> List[Surface]:
    """
    Get building wall surfaces
    :return: [Surface]
    """
    return self._walls

  @property
  def internal_walls(self) -> List[Surface]:
    """
    Get building internal wall surfaces
    :return: [Surface]
    """
    return self._internal_walls

  @property
  def terrains(self) -> Union[None, List[Surface]]:
    """
    Get city object terrain surfaces
    :return: [Surface]
    """
    return self._terrains

  @property
  def attic_heated(self) -> Union[None, int]:
    """
    Get if the city object attic is heated
    0: no attic in the building
    1: attic exists but is not heated
    2: attic exists and is heated
    :return: None or int
    """
    return self._attic_heated

  @attic_heated.setter
  def attic_heated(self, value):
    """
    Set if the city object attic is heated
    0: no attic in the building
    1: attic exists but is not heated
    2: attic exists and is heated
    :param value: int
    """
    if value is not None:
      self._attic_heated = int(value)

  @property
  def basement_heated(self) -> Union[None, int]:
    """
    Get if the city object basement is heated
    0: no basement in the building
    1: basement exists but is not heated
    2: basement exists and is heated
    :return: None or int
    """
    return self._basement_heated

  @basement_heated.setter
  def basement_heated(self, value):
    """
    Set if the city object basement is heated
    0: no basement in the building
    1: basement exists but is not heated
    2: basement exists and is heated
    :param value: int
    """
    if value is not None:
      self._basement_heated = int(value)

  @property
  def year_of_construction(self):
    """
    Get building year of construction
    :return: int
    """
    return self._year_of_construction

  @year_of_construction.setter
  def year_of_construction(self, value):
    """
    Set building year of construction
    :param value: int
    """
    if value is not None:
      self._year_of_construction = int(value)

  @property
  def function(self) -> Union[None, str]:
    """
    Get building function
    :return: None or str
    """
    return self._function

  @function.setter
  def function(self, value):
    """
    Set building function
    :param value: str
    """
    if value is not None:
      self._function = str(value)

  @property
  def average_storey_height(self) -> Union[None, float]:
    """
    Get building average storey height in meters
    :return: None or float
    """
    if len(self.internal_zones) > 1:
      self._average_storey_height = 0
      for internal_zone in self.internal_zones:
        self._average_storey_height += internal_zone.mean_height / len(self.internal_zones)
    else:
      if self.internal_zones[0].thermal_archetype is None:
        self._average_storey_height = None
      else:
        self._average_storey_height = self.internal_zones[0].thermal_archetype.average_storey_height
    return self._average_storey_height

  @average_storey_height.setter
  def average_storey_height(self, value):
    """
    Set building average storey height in meters
    :param value: float
    """
    if value is not None:
      self._average_storey_height = float(value)

  @property
  def storeys_above_ground(self) -> Union[None, int]:
    """
    Get building storeys number above ground
    :return: None or int
    """
    if self._storeys_above_ground is None:
      if self.eave_height is not None and self.average_storey_height is not None:
        self._storeys_above_ground = int(self.eave_height / self.average_storey_height)
    return self._storeys_above_ground

  @storeys_above_ground.setter
  def storeys_above_ground(self, value):
    """
    Set building storeys number above ground
    :param value: int
    """
    if value is not None:
      self._storeys_above_ground = int(value)

  @property
  def cold_water_temperature(self) -> {float}:
    """
    Get cold water temperature in degrees Celsius
    :return: dict{[float]}
    """
    return self._cold_water_temperature

  @cold_water_temperature.setter
  def cold_water_temperature(self, value):
    """
    Set cold water temperature in degrees Celsius
    :param value: dict{[float]}
    """
    self._cold_water_temperature = value

  @property
  def heating_demand(self) -> dict:
    """
    Get heating demand in J
    :return: dict{[float]}
    """
    return self._heating_demand

  @heating_demand.setter
  def heating_demand(self, value):
    """
    Set heating demand in J
    :param value: dict{[float]}
    """
    self._heating_demand = value

  @property
  def cooling_demand(self) -> dict:
    """
    Get cooling demand in J
    :return: dict{[float]}
    """
    return self._cooling_demand

  @cooling_demand.setter
  def cooling_demand(self, value):
    """
    Set cooling demand in J
    :param value: dict{[float]}
    """
    self._cooling_demand = value

  @property
  def lighting_electrical_demand(self) -> dict:
    """
    Get lighting electrical demand in J
    :return: dict{[float]}
    """
    return self._lighting_electrical_demand

  @lighting_electrical_demand.setter
  def lighting_electrical_demand(self, value):
    """
    Set lighting electrical demand in J
    :param value: dict{[float]}
    """
    self._lighting_electrical_demand = value

  @property
  def appliances_electrical_demand(self) -> dict:
    """
    Get appliances electrical demand in J
    :return: dict{[float]}
    """
    return self._appliances_electrical_demand

  @appliances_electrical_demand.setter
  def appliances_electrical_demand(self, value):
    """
    Set appliances electrical demand in J
    :param value: dict{[float]}
    """
    self._appliances_electrical_demand = value

  @property
  def domestic_hot_water_heat_demand(self) -> dict:
    """
    Get domestic hot water heat demand in J
    :return: dict{[float]}
    """
    return self._domestic_hot_water_heat_demand

  @domestic_hot_water_heat_demand.setter
  def domestic_hot_water_heat_demand(self, value):
    """
    Set domestic hot water heat demand in J
    :param value: dict{[float]}
    """
    self._domestic_hot_water_heat_demand = value

  @property
  def lighting_peak_load(self) -> Union[None, dict]:
    """
    Get lighting peak load in W
    :return: dict{[float]}
    """
    results = {}
    peak_lighting = 0
    peak = 0
    for thermal_zone in self.thermal_zones_from_internal_zones:
      lighting = thermal_zone.lighting
      for schedule in lighting.schedules:
        peak = max(schedule.values) * lighting.density * thermal_zone.total_floor_area
        if peak > peak_lighting:
          peak_lighting = peak
    results[cte.MONTH] = [peak for _ in range(0, 12)]
    results[cte.YEAR] = [peak]
    return results

  @property
  def appliances_peak_load(self) -> Union[None, dict]:
    """
    Get appliances peak load in W
    :return: dict{[float]}
    """
    results = {}
    peak_appliances = 0
    peak = 0
    for thermal_zone in self.thermal_zones_from_internal_zones:
      appliances = thermal_zone.appliances
      for schedule in appliances.schedules:
        peak = max(schedule.values) * appliances.density * thermal_zone.total_floor_area
        if peak > peak_appliances:
          peak_appliances = peak
    results[cte.MONTH] = [peak for _ in range(0, 12)]
    results[cte.YEAR] = [peak]
    return results

  @property
  def eave_height(self):
    """
    Get building eave height in meters
    :return: float
    """
    if self._eave_height is None:
      self._eave_height = 0
      for wall in self.walls:
        self._eave_height = max(self._eave_height, wall.upper_corner[2]) - self.simplified_polyhedron.min_z
    return self._eave_height

  @property
  def roof_type(self):
    """
    Get roof type for the building flat or pitch
    :return: str
    """
    if self._roof_type is None:
      self._roof_type = 'flat'
      for roof in self.roofs:
        grads = np.rad2deg(roof.zenith_angle)
        if 355 > grads > 5:
          self._roof_type = 'pitch'
          break
    return self._roof_type

  @roof_type.setter
  def roof_type(self, value):
    """
    Set roof type for the building flat or pitch
    :return: str
    """
    self._roof_type = value

  @property
  def floor_area(self):
    """
    Get building floor area in square meters
    :return: float
    """
    if self._floor_area is None:
      self._floor_area = 0
      for surface in self.surfaces:
        if surface.type == 'Ground':
          self._floor_area += surface.perimeter_polygon.area
    return self._floor_area

  @property
  def is_conditioned(self):
    """
    Get building heated flag
    :return: Boolean
    """
    if self.internal_zones is None:
      return False
    for internal_zone in self.internal_zones:
      if internal_zone.usages is not None:
        for usage in internal_zone.usages:
          if usage.thermal_control is not None:
            return True
    return False

  @property
  def aliases(self):
    """
    Get the alias name for the building
    :return: str
    """
    return self._aliases

  def add_alias(self, value):
    """
    Add a new alias for the building
    """
    self._aliases.append(value)
    if self.city is not None:
      self.city.add_building_alias(self, value)

  @property
  def city(self) -> District:
    """
    Get the city containing the building
    :return: District
    """
    return self._city

  @city.setter
  def city(self, value):
    """
    Set the city containing the building
    """
    self._city = value

  @property
  def usages_percentage(self):
    """
    Get the usages and percentages for the building
    """
    _usage = ''
    for internal_zone in self.internal_zones:
      if internal_zone.usages is None:
        continue
      for usage in internal_zone.usages:
        _usage = f'{_usage}{usage.name}_{usage.percentage} '
    return _usage.rstrip()

  @property
  def energy_systems_archetype_name(self):
    """
    Get energy systems archetype name
    :return: str
    """
    return self._systems_archetype_name

  @energy_systems_archetype_name.setter
  def energy_systems_archetype_name(self, value):
    """
    Set energy systems archetype name
    :param value: str
    """
    self._systems_archetype_name = value
