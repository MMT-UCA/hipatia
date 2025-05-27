"""
Geojson module parses geojson files and import the geometry into the city model structure
SPDX - License - Identifier: LGPL - 3.0 - or -later
Copyright © 2022 Concordia CERC group
Project Coder Guillermo Gutierrez Guillermo.GutierrezMorote@concordia.ca
"""
import json
import uuid

from pyproj import Transformer

from central_data_model.district import District
from imports.geometry.geojson_classes.geojson_lod0 import GeoJsonLOD0
from imports.geometry.geojson_classes.geojson_lod1 import GeoJsonLOD1


class Geojson:
  """
  Geojson class
  """

  def __init__(self,
               path,
               aliases_field=None,
               extrusion_height_field=None,
               year_of_construction_field=None,
               type_of_feature_field=None,
               function_field=None,
               usages_field=None,
               storey_height_field=None,
               function_to_hub=None,
               usages_to_hub=None,
               hub_crs=None
               ):
    self._hub_crs = hub_crs
    if hub_crs is None:
      self._hub_crs = 'epsg:2062'
    self._transformer = Transformer.from_crs('epsg:4326', self._hub_crs)

    self._district = None
    self._district_polygon = None
    self._buildings = []

    self._aliases_field = aliases_field
    self._extrusion_height_field = extrusion_height_field
    self._year_of_construction_field = year_of_construction_field
    self._type_of_feature_field = type_of_feature_field
    self._function_field = function_field
    self._usages_field = usages_field
    self._storey_height_field = storey_height_field
    self._function_to_hub = function_to_hub
    self._usages_to_hub = usages_to_hub
    with open(path, 'r', encoding='utf8') as json_file:
      self._geojson = json.loads(json_file.read())

  @property
  def district(self) -> District:
    """
    Get city out of a Geojson file
    """
    # todo: re-structure so the reference comes automatically from the geojson read
    reference_coordinates = [374480.491975, 218839.658365, 0]
    parser = GeoJsonLOD0(self._transformer, reference_coordinates)
    lod1_parser = GeoJsonLOD1(self._transformer, reference_coordinates)
    lod = 0
    if self._district is None:
      for feature in self._geojson['features']:
        extrusion_height = None
        storey_height = None
        if self._extrusion_height_field is not None:
          extrusion_height = float(feature['properties'][self._extrusion_height_field])
          parser = lod1_parser
          lod = 1
          if self._storey_height_field is not None:
            storey_height = float(feature['properties'][self._storey_height_field])

        year_of_construction = None
        if self._year_of_construction_field is not None:
          year_of_construction = int(feature['properties'][self._year_of_construction_field])

        type_of_feature = None
        if self._type_of_feature_field is not None:
          type_of_feature = feature['properties'][self._type_of_feature_field]

        function = None
        if self._function_field is not None:
          function = str(feature['properties'][self._function_field])
          if self._function_to_hub is not None:
            if function in self._function_to_hub:
              function = self._function_to_hub[function]

        usages = None
        if self._usages_field is not None:
          if self._usages_field in feature['properties']:
            usages = feature['properties'][self._usages_field]
            if self._usages_to_hub is not None:
              usages = self._usages_to_hub(usages)

        geometry = feature['geometry']

        if 'id' in feature:
          building_name = feature['id']
        elif 'id' in feature['properties']:
          building_name = feature['properties']['id']
        else:
          building_name = uuid.uuid4()

        building_aliases = []
        if self._aliases_field is not None:
          for alias_field in self._aliases_field:
            building_aliases.append(feature['properties'][alias_field])

        if lod == 0:
          if lod == 0:
            if type_of_feature == 'building':
              self._buildings.append(parser.parse(
                geometry,
                building_name,
                building_aliases,
                function,
                usages,
                year_of_construction))
            elif type_of_feature == 'boundaries':
              if self._district_polygon is None:
                self._district_polygon = parser.parse(
                  geometry,
                  building_name,
                  building_aliases,
                  function,
                  usages,
                  year_of_construction,
                  extrusion_height,
                  storey_height)
              else:
                # todo: catch the error
                print("More than one polygon defining the district!!")
            else:
              # todo: will we have more types of features??
              pass
        else:
          if type_of_feature == 'building':
            self._buildings.append(
              parser.parse(
                geometry,
                building_name,
                building_aliases,
                function,
                usages,
                year_of_construction,
                extrusion_height,
                storey_height))
          elif type_of_feature == 'boundaries':
            if self._district_polygon is None:
              self._district_polygon = parser.parse(
                geometry,
                building_name,
                building_aliases,
                function,
                usages,
                year_of_construction,
                extrusion_height,
                storey_height)
            else:
              # todo: catch the error
              print("More than one polygon defining the district!!")
          else:
            # todo: will we have more types of features??
            pass
    self._district = parser.district(self._hub_crs)
    self._district.reference_coordinates = reference_coordinates
    self._district.polygon = self._district_polygon.surfaces[0].perimeter_polygon
    for building in self._buildings:
      # Do not include "small building-like structures" to buildings
      if building.floor_area >= 25:
        self._district.add_building(building)
    return self._district
