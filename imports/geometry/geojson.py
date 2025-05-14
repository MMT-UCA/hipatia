"""
Geojson module parses geojson files and import the geometry into the city model structure
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guillermo Gutierrez Guillermo.GutierrezMorote@concordia.ca
"""

import uuid
import json

import numpy as np

from pyproj import Transformer

import helpers.constants as cte
from helpers.geometry_helper import GeometryHelper
from imports.geometry.helpers.imports_geometry_helper import GeometryHelper as igh
from helpers.attributes.polygon import Polygon
from central_data_model.building import Building
from central_data_model.building_demand.surface import Surface
from central_data_model.district import District
from central_data_model.city import City


class Geojson:
  """
  Geojson class
  """
  _X = 0
  _Y = 1

  def __init__(self,
               path,
               extrusion_height_field=None,
               year_of_construction_field=None,
               function_field=None,
               type_field=None):
    # todo: destination epsg should change according actual the location
    self._transformer = Transformer.from_crs('epsg:4326', 'epsg:2062')
    self._min_x = cte.MAX_FLOAT
    self._min_y = cte.MAX_FLOAT
    self._max_x = cte.MIN_FLOAT
    self._max_y = cte.MIN_FLOAT
    self._max_z = 0
    self._city = None
    self._district = None
    self._extrusion_height_field = extrusion_height_field
    self._year_of_construction_field = year_of_construction_field
    self._function_field = function_field
    self._type_field = type_field
    with open(path, 'r', encoding='utf8') as json_file:
      self._geojson = json.loads(json_file.read())

  def _save_bounds(self, x, y):
    if x > self._max_x:
      self._max_x = x
    if x < self._min_x:
      self._min_x = x
    if y > self._max_y:
      self._max_y = y
    if y < self._min_y:
      self._min_y = y

  @staticmethod
  def _find_wall(line_1, line_2):
    for i in range(0, 2):
      j = 1 - i
      point_1 = line_1[i]
      point_2 = line_2[j]
      distance = GeometryHelper.distance_between_points(point_1, point_2)
      if distance > 1e-2:
        return False
    return True

  def _store_shared_percentage_to_walls(self, city, city_mapped):
    for building in city.buildings:
      if building.name not in city_mapped.keys():
        for wall in building.walls:
          wall.percentage_shared = 0
        continue
      building_mapped = city_mapped[building.name]
      for wall in building.walls:
        percentage = 0
        ground_line = []
        for point in wall.perimeter_polygon.coordinates:
          if point[2] < 0.5:
            ground_line.append(point)
        for entry in building_mapped:
          if building_mapped[entry]['shared_points'] <= 2:
            continue
          line = [building_mapped[entry]['line_start'], building_mapped[entry]['line_end']]
          neighbour_line = [building_mapped[entry]['neighbour_line_start'],
                            building_mapped[entry]['neighbour_line_end']]
          neighbour_height = city.city_object(building_mapped[entry]['neighbour_name']).max_height
          if self._find_wall(line, ground_line):
            line_shared = (GeometryHelper.distance_between_points(line[0], line[1]) +
                           GeometryHelper.distance_between_points(neighbour_line[0], neighbour_line[1]) -
                           GeometryHelper.distance_between_points(line[1], neighbour_line[0]) -
                           GeometryHelper.distance_between_points(line[0], neighbour_line[1])) / 2
            percentage_ground = line_shared / GeometryHelper.distance_between_points(line[0], line[1])
            percentage_height = neighbour_height / building.max_height
            percentage_height = min(percentage_height, 1)
            percentage += percentage_ground * percentage_height
        wall.percentage_shared = percentage

  @property
  def city(self) -> City:
    """
    Get city out of a Geojson file
    """
    if self._city is None:
      buildings = []
      lod = 0
      for feature in self._geojson['features']:
        extrusion_height = 0
        if self._extrusion_height_field is not None:
          extrusion_height = float(feature['properties'][self._extrusion_height_field])
          lod = 1
          self._max_z = max(self._max_z, extrusion_height)
        year_of_construction = None
        if self._year_of_construction_field is not None:
          year_of_construction = int(feature['properties'][self._year_of_construction_field])
        function = None
        if self._function_field is not None:
          function = str(feature['properties'][self._function_field])
        feature_type = None
        if self._type_field is not None:
          feature_type = str(feature['properties'][self._function_field])
        geometry = feature['geometry']
        if 'id' in feature:
          building_name = feature['id']
        else:
          building_name = uuid.uuid4()

        if str(geometry['type']).lower() == 'polygon':
          buildings.append(self._parse_polygon(geometry['coordinates'],
                                               building_name,
                                               function,
                                               year_of_construction,
                                               extrusion_height,
                                               feature_type))

        elif str(geometry['type']).lower() == 'multipolygon':
          buildings.append(self._parse_multi_polygon(geometry['coordinates'],
                                                     building_name,
                                                     function,
                                                     year_of_construction,
                                                     extrusion_height,
                                                     feature_type))
        else:
          raise NotImplementedError(f'Geojson geometry type [{geometry["type"]}] unknown')
      # todo: this is only valid for one district per city, refactor!!
      self._city = City(lower_corner=[self._min_x, self._min_y, 0.0],
                        upper_corner=[self._max_x, self._max_y, self._max_z],
                        srs_name='epsg:2062')
      self._district = District('epsg:2062', [self._min_x, self._min_y, 0.0], [self._max_x, self._max_y, self._max_z])
      for building in buildings:
        # Do not include "small building-like structures" to buildings
        if building.floor_area >= 25:
          self._district.add_building(building)
      self._city.add_district(self._district)

    return self._city

  def _polygon_coordinates_to_3d(self, polygon_coordinates):
    transformed_coordinates = ''
    for coordinate in polygon_coordinates:
      transformed = self._transformer.transform(coordinate[self._Y], coordinate[self._X])
      self._save_bounds(transformed[self._X], transformed[self._Y])
      transformed_coordinates = f'{transformed_coordinates} {transformed[self._X]} {transformed[self._Y]} 0.0'
    return transformed_coordinates.lstrip(' ')

  def _parse_polygon(self, coordinates, building_name, function, year_of_construction, extrusion_height, feature_type):
    surfaces = []
    for polygon_coordinates in coordinates:
      points = igh.points_from_string(
        igh.remove_last_point_from_string(
          self._polygon_coordinates_to_3d(polygon_coordinates)
        )
      )
      points = igh.invert_points(points)
      polygon = Polygon(points)
      polygon.area = igh.ground_area(points)
      surface = Surface(polygon, polygon)
      if surface.type == cte.GROUND:
        surfaces.append(surface)
      else:
        distance = cte.MAX_FLOAT
        hole_connect = 0
        surface_connect = 0
        for hole_index, hole_coordinate in enumerate(polygon.coordinates):
          for surface_index, ground_coordinate in enumerate(surfaces[-1].solid_polygon.coordinates):
            current_distance = GeometryHelper.distance_between_points(hole_coordinate, ground_coordinate)
            if current_distance < distance:
              distance = current_distance
              hole_connect = hole_index
              surface_connect = surface_index

        hole = polygon.coordinates[hole_connect:] + polygon.coordinates[:hole_connect] + [polygon.coordinates[hole_connect]]
        prefix_coordinates = surfaces[-1].solid_polygon.coordinates[:surface_connect+1]
        trail_coordinates = surfaces[-1].solid_polygon.coordinates[surface_connect:]
        coordinates = prefix_coordinates + hole + trail_coordinates
        polygon = Polygon(coordinates)
        polygon.area = igh.ground_area(coordinates)
        surfaces[-1] = Surface(polygon, polygon)
    if len(surfaces) > 1:
      raise ValueError('too many surfaces!!!!')
    if feature_type is "building":
      building = Building(f'{building_name}', surfaces, year_of_construction, function)
      if extrusion_height == 0:
        return building

      volume = 0
      for ground in building.grounds:
        volume += ground.solid_polygon.area * extrusion_height
        roof_coordinates = []
        # adding a roof means invert the polygon coordinates and change the Z value
        for coordinate in ground.solid_polygon.coordinates:
          roof_coordinate = np.array([coordinate[0], coordinate[1], extrusion_height])
          # insert the roof rotated already
          roof_coordinates.insert(0, roof_coordinate)
        roof_polygon = Polygon(roof_coordinates)
        roof_polygon.area = ground.solid_polygon.area
        roof = Surface(roof_polygon, roof_polygon)
        surfaces.append(roof)
        # adding a wall means add the point coordinates and the next point coordinates with Z's height and 0
        coordinates_length = len(roof.solid_polygon.coordinates)
        for i, coordinate in enumerate(roof.solid_polygon.coordinates):
          j = i + 1
          if j == coordinates_length:
            j = 0
          next_coordinate = roof.solid_polygon.coordinates[j]
          wall_coordinates = [
            np.array([coordinate[0], coordinate[1], 0.0]),
            np.array([next_coordinate[0], next_coordinate[1], 0.0]),
            np.array([next_coordinate[0], next_coordinate[1], next_coordinate[2]]),
            np.array([coordinate[0], coordinate[1], coordinate[2]])
          ]
          polygon = Polygon(wall_coordinates)
          wall = Surface(polygon, polygon)
          surfaces.append(wall)
        building = Building(f'{building_name}', surfaces, year_of_construction, function)
        building.volume = volume
        return building
    elif feature_type is "boundaries":
      # todo: read!!!
      print("Read boundaries")
    else:
      # todo: save exception: Feature not imported
      pass

  def _parse_multi_polygon(self, polygons_coordinates, building_name, function, year_of_construction, extrusion_height):
    surfaces = []
    for coordinates in polygons_coordinates:
      for polygon_coordinates in coordinates:
        points = igh.points_from_string(
          igh.remove_last_point_from_string(
            self._polygon_coordinates_to_3d(polygon_coordinates)
          )
        )
        points = igh.invert_points(points)
        polygon = Polygon(points)
        polygon.area = igh.ground_area(points)
        surface = Surface(polygon, polygon)
        if surface.type == cte.GROUND:
          surfaces.append(surface)
        else:
          distance = cte.MAX_FLOAT
          hole_connect = 0
          surface_connect = 0
          for hole_index, hole_coordinate in enumerate(polygon.coordinates):
            for surface_index, ground_coordinate in enumerate(surfaces[-1].solid_polygon.coordinates):
              current_distance = GeometryHelper.distance_between_points(hole_coordinate, ground_coordinate)
              if current_distance < distance:
                distance = current_distance
                hole_connect = hole_index
                surface_connect = surface_index
          hole = polygon.coordinates[hole_connect:] + polygon.coordinates[:hole_connect]
          prefix_coordinates = surfaces[-1].solid_polygon.coordinates[:surface_connect]
          trail_coordinates = surfaces[-1].solid_polygon.coordinates[surface_connect:]
          coordinates = prefix_coordinates + hole + [hole[0]] + trail_coordinates
          polygon = Polygon(coordinates)
          polygon.area = igh.ground_area(coordinates)
          surfaces[-1] = Surface(polygon, polygon)
    building = Building(f'{building_name}', surfaces, year_of_construction, function)
    if extrusion_height == 0:
      return building

    volume = 0
    for ground in building.grounds:
      volume += ground.solid_polygon.area * extrusion_height
      roof_coordinates = []
      # adding a roof means invert the polygon coordinates and change the Z value
      for coordinate in ground.solid_polygon.coordinates:
        roof_coordinate = np.array([coordinate[0], coordinate[1], extrusion_height])
        # insert the roof rotated already
        roof_coordinates.insert(0, roof_coordinate)
      roof_polygon = Polygon(roof_coordinates)
      roof_polygon.area = ground.solid_polygon.area
      roof = Surface(roof_polygon, roof_polygon)
      surfaces.append(roof)
      # adding a wall means add the point coordinates and the next point coordinates with Z's height and 0
      coordinates_length = len(roof.solid_polygon.coordinates)
      for i, coordinate in enumerate(roof.solid_polygon.coordinates):
        j = i + 1
        if j == coordinates_length:
          j = 0
        next_coordinate = roof.solid_polygon.coordinates[j]
        wall_coordinates = [
          np.array([coordinate[0], coordinate[1], 0.0]),
          np.array([next_coordinate[0], next_coordinate[1], 0.0]),
          np.array([next_coordinate[0], next_coordinate[1], next_coordinate[2]]),
          np.array([coordinate[0], coordinate[1], coordinate[2]])
        ]
        polygon = Polygon(wall_coordinates)
        wall = Surface(polygon, polygon)
        surfaces.append(wall)
      building = Building(f'{building_name}', surfaces, year_of_construction, function)
      building.volume = volume
    return building
