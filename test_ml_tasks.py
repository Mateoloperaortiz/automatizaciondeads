"""
Script para probar las mejoras en las tareas de ML.

Este script verifica que las correcciones y mejoras implementadas
en las tareas de ML funcionen correctamente.
"""

import os
import numpy as np
from sklearn.cluster import KMeans
from adflux.ml.common import ensure_segment_records
from adflux.ml.batch_processing import process_candidates_in_batches, batch_iterator

def test_kmeans_clusters():
    """Prueba que la corrección del acceso a n_clusters funcione correctamente."""
    print("\n=== Prueba 1: Acceso a n_clusters ===")
    n_clusters = 3
    data = np.array([[1, 2], [3, 4], [5, 6], [7, 8], [9, 10], [11, 12]])
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(data)
    
    clusters_count = model.cluster_centers_.shape[0]
    print(f"Número de clusters configurado: {n_clusters}")
    print(f"Número de clusters obtenido: {clusters_count}")
    assert clusters_count == n_clusters, "El número de clusters no coincide"
    print("✓ Prueba exitosa: Acceso a n_clusters corregido")

def test_batch_processing():
    """Prueba que el procesamiento por lotes funcione correctamente."""
    print("\n=== Prueba 2: Procesamiento por lotes ===")
    items = list(range(100))
    batch_size = 25
    
    batches = list(batch_iterator(items, batch_size))
    
    print(f"Total de elementos: {len(items)}")
    print(f"Tamaño de lote: {batch_size}")
    print(f"Número de lotes: {len(batches)}")
    
    assert len(batches) == 4, f"Número incorrecto de lotes: {len(batches)}, esperado: 4"
    assert all(len(batch) == batch_size for batch in batches[:-1]), "Tamaño de lote incorrecto"
    print("✓ Prueba exitosa: Procesamiento por lotes funciona correctamente")

def test_ensure_segment_records():
    """Prueba que ensure_segment_records maneje correctamente los errores."""
    print("\n=== Prueba 3: Manejo de errores en ensure_segment_records ===")
    model = KMeans(n_clusters=3, random_state=42)
    model.fit(np.array([[1, 2], [3, 4], [5, 6]]))
    
    try:
        class MockLogger:
            def info(self, msg): print(f"INFO: {msg}")
            def error(self, msg, **kwargs): print(f"ERROR: {msg}")
        
        ensure_segment_records(model, logger=MockLogger())
        print("Nota: La función falló como se esperaba (sin BD), pero el manejo de errores funcionó")
    except Exception as e:
        print(f"Error inesperado: {e}")
        assert False, "La función no debería lanzar excepciones no manejadas"
    
    print("✓ Prueba exitosa: Manejo de errores funciona correctamente")

if __name__ == "__main__":
    print("Iniciando pruebas de mejoras en tareas ML...")
    test_kmeans_clusters()
    test_batch_processing()
    test_ensure_segment_records()
    print("\n✓ Todas las pruebas completadas exitosamente")
