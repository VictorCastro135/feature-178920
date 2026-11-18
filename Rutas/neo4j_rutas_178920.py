import os
from neo4j import GraphDatabase

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


URI = os.environ["NEO4J_URI"]
USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER") or "neo4j"
PASSWORD = os.environ["NEO4J_PASSWORD"]


CYPHER_CREAR_GRAFO_RUTAS = """
// 1. Hoja de Ruta
MERGE (hr:HojaRuta {id: 'HR-PC-001'})
SET hr.nombre = 'Ensamble Gaming PC',
    hr.estado = 'LIBERADA',
    hr.version = 1

// 2. Etapas de la Ruta
MERGE (e1:EtapaRuta {id: 'ET-01'})
SET e1.orden = 1, e1.nombre = 'Preparacion de chasis y fuente', e1.tiempo_ejecucion_min = 20, e1.dias_espera = 0

MERGE (e2:EtapaRuta {id: 'ET-02'})
SET e2.orden = 2, e2.nombre = 'Instalacion de placa, CPU y RAM', e2.tiempo_ejecucion_min = 35, e2.dias_espera = 0

MERGE (e3:EtapaRuta {id: 'ET-03'})
SET e3.orden = 3, e3.nombre = 'Pruebas de encendido y estres', e3.tiempo_ejecucion_min = 45, e3.dias_espera = 1

// 3. Centros de Trabajo
MERGE (ct1:CentroTrabajo {id: 'CT-ENSAMBLE'})
SET ct1.nombre = 'Linea de Ensamble PC'

MERGE (ct2:CentroTrabajo {id: 'CT-QA'})
SET ct2.nombre = 'Estacion de Pruebas'

// 4. Recursos
MERGE (r1:Recurso {id: 'REC-TEC-01'})
SET r1.nombre = 'Tecnico de Ensamble', r1.tipo = 'Mano de obra'

MERGE (r2:Recurso {id: 'REC-BANCO-01'})
SET r2.nombre = 'Banco de Pruebas Electricas', r2.tipo = 'Equipo'

// 5. Materiales
MERGE (m1:Material {id: 'MAT-GAB-01'})
SET m1.nombre = 'Gabinete ATX'

MERGE (m2:Material {id: 'MAT-CPU-01'})
SET m2.nombre = 'Procesador Gaming'

MERGE (m3:Material {id: 'MAT-RAM-01'})
SET m3.nombre = 'Memoria RAM 16GB'

// 6. Relaciones
MERGE (hr)-[:TIENE_ETAPA]->(e1)
MERGE (hr)-[:TIENE_ETAPA]->(e2)
MERGE (hr)-[:TIENE_ETAPA]->(e3)

MERGE (e1)-[:SIGUIENTE]->(e2)
MERGE (e2)-[:SIGUIENTE]->(e3)

MERGE (e1)-[:SE_EJECUTA_EN]->(ct1)
MERGE (e2)-[:SE_EJECUTA_EN]->(ct1)
MERGE (e3)-[:SE_EJECUTA_EN]->(ct2)

MERGE (e1)-[:USA_RECURSO]->(r1)
MERGE (e3)-[:USA_RECURSO]->(r2)

MERGE (e1)-[c1:CONSUME_MATERIAL]->(m1)
SET c1.cantidad = 1

MERGE (e2)-[c2:CONSUME_MATERIAL]->(m2)
SET c2.cantidad = 1

MERGE (e2)-[c3:CONSUME_MATERIAL]->(m3)
SET c3.cantidad = 2
"""


CYPHER_CONSULTAR_RUTA = """
MATCH (hr:HojaRuta {id: 'HR-PC-001'})-[:TIENE_ETAPA]->(e:EtapaRuta)-[:SE_EJECUTA_EN]->(ct:CentroTrabajo)
RETURN hr.nombre AS ruta, e.orden AS orden, e.nombre AS etapa,
       e.tiempo_ejecucion_min AS minutos, ct.nombre AS centro
ORDER BY e.orden
"""


def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            session.run(CYPHER_CREAR_GRAFO_RUTAS)
            print("Grafo de Rutas cargado correctamente en Neo4j.")

            resultados = session.run(CYPHER_CONSULTAR_RUTA)
            for fila in resultados:
                print(
                    f"[{fila['orden']}] {fila['etapa']} | "
                    f"{fila['minutos']} min | Centro: {fila['centro']}"
                )
    finally:
        driver.close()


if __name__ == "__main__":
    main()
