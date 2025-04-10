"""
Open area module
Copyright © 2024 MMT department-University of Cadiz
Project Coder Pilar Monsalvete pilar.monsalvete@uca.es
"""

from typing import List, Union
from central_data_model.building import Building


class OpenArea:
  """
  This class models open areas in cities where the air volume is to be studied, such as patios, urban canyons...
  """

  def __init__(self):
    self._buildings = None
    self._air_body = None

  # todo: this will depend on how the libraries typically model body meshes
  def air_body(self):
    """
    Get the air volume as a 3D body
    :return: Body
    """
    return self._air_body

  def buildings(self) -> Union[None, List[Building]]:
    """
    Get the buildings adjacent to the open area
    :return: None or [Building]
    """
    return self._buildings
