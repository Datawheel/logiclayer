"""Economic Complexity adapter for use in LogicLayer.

Contains a module to enable endpoints which return economic complexity
calculations, using a Tesseract OLAP server as data source.
"""

import os
import sys
import pandas as pd
from typing import Optional

import economic_complexity
from fastapi import APIRouter
from olap_client import Query, TesseractServer, Server, TesseractDataFormat

from logiclayer import LogicLayerModule


class EconomicComplexityModule(LogicLayerModule):
    """Economic Complexity calculations module class for LogicLayer.
    """

    server: "Server"

    def __init__(self,
                 server_url: Optional[str] = None,
                 server: Optional["Server"] = None):
        """Setups the server for this instance.
        """

        if server is not None:
            self.server = server
        elif server_url is not None:
            self.server = TesseractServer(server_url)
        else:
            raise ValueError("EconomicComplexityModule needs an olap_server Server or a server url")

    def setup(self, router: APIRouter):
        """Applies the configuration in the current instance to an `app`.
        """
        _setup_routes(self.server, router)

def _setup_routes(server: TesseractServer, router: APIRouter):

    @router.get('/')
    def route_root():
        pass

    @router.get('/rca')
    async def route_rca(
        cube: str,
        dd_geo: str,
        dd_product: str,
        measure: str,
        year: str
    ):
        '''Deberia especificar el año en la URL?'''

        cube = await server.fetch_cube(cube)

        query = cube.new_query()
        query.set_drilldown(dd_geo)
        query.set_drilldown(dd_product)
        query.add_measure(measure)
        query.set_cut(year) #??? De donde podia ver los metodos que acepta query? https://github.com/Datawheel/olap-client-py/blob/2a286ba458cc86e7bb6df2f04dc9012012e17524/olap_client/query.py#L165
        query.set_extension(TesseractDataFormat.JSONRECORDS)

        base_data = await server.exec_query(query)

        data = pd.read_json(base_data) #Pasar opciones, o modificar dataframe para que los indices sean geo y columnas product

        tbl = pd.pivot_table(data, index=dd_geo,
                              columns=dd_product,
                              values=measure)\
             .reset_index()\
             .set_index(dd_geo)\
             .dropna(axis=1, how="all")\
             .fillna(0)\
             .astype(float)

        result = economic_complexity.rca(tbl) #Tratar de convertir el result a un listado de diccionarios, lo mas plano posible para que fast api pueda transformarlo a json
        result = result.to_dict('index')

        '''
            1.-Parametros que van en la url /rca?cube&rca&common
            2.-Recibidos los parametros, se los debo dar a una instancia de Query para poder obtener los datos
            3.-Pasar la instancia de Query a instancia de Server para obtener los datos base (ejecutar metodo execute query)
            4.-Los datos bases de Server se los paso a la funcion de calculo del RCA 
            5.-Devolverlos en la respuesta de /rca
        '''
        return {'data': result}

    '''
        Como hago para llamar a /eci y /pci o /complexity. Debo si o si llamar a /rca para luego llamar a complexity
    '''

    @router.get('/eci')
    async def route_eci(
        cube: str,
        dd_geo: str,
        dd_product: str,
        measure: str,
        year: str,
        eci_threshold
    ):

        '''
        Hace sentido calcular para varios años? Deberia ser solo para un año? 
        '''
        rcas = route_rca(cube, dd_geo, dd_product, measure, year) # Es esto valido?

        geo_complexity, prod_complexity = economic_complexity.complexity(rcas)
        geo_complexity = geo_complexity.to_dict()

        return {'data': geo_complexity}
        
    @router.get('/pci')
    async def route_pci(
        cube: str,
        dd_geo: str,
        dd_product: str,
        measure: str,
        year: str
    ):

        rcas = route_rca(cube, dd_geo, dd_product, measure, year)

        geo_complexity, prod_complexity = economic_complexity.complexity(rcas)
        prod_complexity = prod_complexity.to_dict()

        return {'data': prod_complexity}
        