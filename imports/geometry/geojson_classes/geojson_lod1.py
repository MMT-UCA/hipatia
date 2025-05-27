from helpers.attributes.polygon import Polygon
from central_data_model.building import Building
from central_data_model.building_demand.internal_zone import InternalZone
from central_data_model.building_demand.surface import Surface
from imports.geometry.geojson_classes.geojson_base import GeoJsonBase
from imports.geometry.geojson_classes.geojson_lod0 import GeoJsonLOD0
import numpy as np


class GeoJsonLOD1(GeoJsonBase):
  def __init__(self, transformer, reference_coordinates):
    self._transformer = transformer
    self._reference_coordinates = reference_coordinates
    self._parser = GeoJsonLOD0(self._transformer, self._reference_coordinates)

  def parse(self, geometry, building_name, building_aliases, function, usages, year_of_construction, extrusion_height, storey_height):
    self._max_z = max(self._max_z, extrusion_height)
    if storey_height is None:
      storey_height = extrusion_height
    storeys = int(extrusion_height/storey_height)
    extrusion_height = storey_height * storeys

    lod0_building = self._parser.parse(geometry, building_name, building_aliases, function, usages, year_of_construction)
    volume = 0
    surfaces = []
    internal_zones = []
    for ground in lod0_building.grounds:
      area = ground.solid_polygon.area
      internal_volume = area * storey_height
      for storey in range(0, storeys):
        roof_coordinates = []
        floor_coordinates = []
        zone = []
        for coordinate in ground.solid_polygon.coordinates:
          roof_coordinate = np.array([coordinate[0], coordinate[1], extrusion_height * (storey + 1)])
          floor_coordinate = np.array([coordinate[0], coordinate[1], extrusion_height * storey])
          # create the roof
          roof_coordinates.insert(0, roof_coordinate)
          # create the ground
          floor_coordinates.append(floor_coordinate)
        roof_polygon = Polygon(roof_coordinates)
        floor_polygon = Polygon(floor_coordinates)
        roof_polygon.area = area
        floor_polygon.area = area
        roof = Surface(roof_polygon, roof_polygon)
        floor = Surface(floor_polygon, floor_polygon)
        surfaces.append(roof)
        surfaces.append(floor)
        zone.append(roof)
        zone.append(floor)
        # adding a wall means add the point coordinates and the next point coordinates with Z's height and 0
        coordinates_length = len(roof.solid_polygon.coordinates)
        for i, coordinate in enumerate(roof.solid_polygon.coordinates):
          j = i + 1
          if j == coordinates_length:
            j = 0
          next_coordinate = roof.solid_polygon.coordinates[j]
          wall_coordinates = [
            np.array([coordinate[0], coordinate[1], extrusion_height * storey]),
            np.array([next_coordinate[0], next_coordinate[1], extrusion_height * storey]),
            np.array([next_coordinate[0], next_coordinate[1], next_coordinate[2]]),
            np.array([coordinate[0], coordinate[1], coordinate[2]])
          ]
          polygon = Polygon(wall_coordinates)
          wall = Surface(polygon, polygon)
          surfaces.append(wall)
          zone.append(wall)

        internal_zones.append(InternalZone(zone, area, internal_volume))
      volume += internal_volume

    building = Building(f'{building_name}', surfaces, year_of_construction, function)
    for alias in building_aliases:
      building.add_alias(alias)
    building.volume = volume
    building.storeys_above_ground = storeys
    self._max_x = self._parser._max_x
    self._max_y = self._parser._max_y
    self._min_x = self._parser._min_x
    self._min_y = self._parser._min_y
    return building
