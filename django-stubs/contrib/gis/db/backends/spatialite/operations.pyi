from typing import Any

from django.contrib.gis.db.backends.base.operations import BaseSpatialOperations
from django.contrib.gis.db.backends.utils import SpatialOperator as SpatialOperator
from django.db.backends.sqlite3.operations import DatabaseOperations

class SpatialiteNullCheckOperator(SpatialOperator): ...

class SpatiaLiteOperations(BaseSpatialOperations, DatabaseOperations):
    name: str = ...
    spatialite: bool = ...
    Adapter: Any = ...
    collect: str = ...
    extent: str = ...
    makeline: str = ...
    unionagg: str = ...
    gis_operators: Any = ...
    disallowed_aggregates: Any = ...
    select: str = ...
    function_names: Any = ...
    @property
    def unsupported_functions(self): ...
    @property
    def spatial_version(self): ...
    def geo_db_type(self, f: Any) -> None: ...
    def get_distance(self, f: Any, value: Any, lookup_type: Any): ...
    def geos_version(self): ...
    def proj_version(self): ...
    def lwgeom_version(self): ...
    def spatialite_version(self): ...
    def spatialite_version_tuple(self): ...
    def spatial_aggregate_name(self, agg_name: Any): ...
    def geometry_columns(self): ...
    def spatial_ref_sys(self): ...
    def get_geometry_converter(self, expression: Any): ...
