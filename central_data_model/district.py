"""
District module
Copyright © 2025 MMT department-University of Cadiz
Project Coder Pilar Monsalvete pilar.monsalvete@uca.es
"""

import logging
from typing import List, Union

from central_data_model.building import Building
from central_data_model.open_area import OpenArea


class District:
  """
  This class models areas under study, containing any relevant city objets
  """

  def __init__(self, srs_name, lower_corner=None, upper_corner=None):
    self._city = None
    self._srs_name = srs_name
    self._lower_corner = lower_corner
    self._upper_corner = upper_corner
    self._name = None
    self._buildings_dictionary = {}
    self._open_areas_dictionary = {}
    self._buildings = []
    self._open_areas = []

  @property
  def city(self):
    """
    Get city to which the district belongs
    :return: City
    """
    return self._city

  @property
  def srs_name(self) -> Union[None, str]:
    """
    Get district's srs name
    :return: None or str
    """
    return self._srs_name

  @property
  def lower_corner(self) -> List[float]:
    """
    Get district lower corner
    :return: [x,y,z]
    """
    return self._lower_corner

  @lower_corner.setter
  def lower_corner(self, value):
    """
    Set district lower corner
    :param value: [x,y,z]
    """
    self._lower_corner = value

  @property
  def upper_corner(self) -> List[float]:
    """
    Get district upper corner
    :return: [x,y,z]
    """
    return self._upper_corner

  @upper_corner.setter
  def upper_corner(self, value):
    """
    Set district upper corner
    :param value: [x,y,z]
    """
    self._upper_corner = value

  @property
  def name(self):
    """
    Get district name
    :return: str
    """
    return self._name

  @name.setter
  def name(self, value):
    """
    Set district name
    :param value:str
    """
    if value is not None:
      self._name = str(value)

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
