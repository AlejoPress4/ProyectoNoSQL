"""
Sistema RAG de Productos Tecnológicos con MongoDB Atlas
Aplicación principal con menú interactivo
"""

import sys
import os

# Agregar el directorio raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import verify_connection
from scripts import (
    create_all_collections,
    create_all_indexes,
    load_all_data,
    verify_all_data
)


def print_header():
    """Imprime el encabezado de la aplicación."""
    print("\n" + "="*70)
    print(" " * 10 + "SISTEMA RAG DE PRODUCTOS TECNOLÓGICOS")
    print(" " * 15 + "MongoDB Atlas + Embeddings Vectoriales")
    print("="*70 + "\n")


def print_menu():
    """Imprime el menú principal."""
    print("\n" + "-"*70)
    print("MENÚ PRINCIPAL")
    print("-"*70)
    print("  [1] Crear colecciones con validación de esquema")
    print("  [2] Crear índices")
    print("  [3] Cargar datos completos (categorías → productos → usuarios → imágenes)")
    print("  [4] Verificar datos cargados")
    print("  [5] Ejecutar setup completo (1 → 2 → 3)")
    print("  [6] Verificar conexión a MongoDB")
    print("  [0] Salir")
    print("-"*70)


def option_1_create_collections():
    """Opción 1: Crear colecciones."""
    print("\n" + "🔨 Creando colecciones...")
    try:
        success = create_all_collections()
        if success:
            print("\n✅ Colecciones creadas exitosamente")
            input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Error al crear colecciones")
            input("\nPresiona Enter para continuar...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        input("\nPresiona Enter para continuar...")


def option_2_create_indexes():
    """Opción 2: Crear índices."""
    print("\n" + "🔨 Creando índices...")
    try:
        success = create_all_indexes()
        if success:
            print("\n✅ Índices creados exitosamente")
            input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Error al crear índices")
            input("\nPresiona Enter para continuar...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        input("\nPresiona Enter para continuar...")


def option_3_load_data():
    """Opción 3: Cargar datos."""
    print("\n" + "🔨 Cargando datos...")
    print("\n⚠️  ADVERTENCIA: Este proceso puede tomar varios minutos")
    print("    Se generarán embeddings para todos los productos y reseñas")
    
    confirm = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    
    if confirm == 's' or confirm == 'si' or confirm == 'sí':
        try:
            success = load_all_data()
            if success:
                print("\n✅ Datos cargados exitosamente")
                input("\nPresiona Enter para continuar...")
            else:
                print("\n❌ Error al cargar datos")
                input("\nPresiona Enter para continuar...")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            input("\nPresiona Enter para continuar...")
    else:
        print("\n❌ Operación cancelada")
        input("\nPresiona Enter para continuar...")


def option_4_verify_data():
    """Opción 4: Verificar datos."""
    print("\n" + "🔍 Verificando datos...")
    try:
        success = verify_all_data()
        if success:
            print("\n✅ Verificación completada")
            input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Error en la verificación")
            input("\nPresiona Enter para continuar...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        input("\nPresiona Enter para continuar...")


def option_5_full_setup():
    """Opción 5: Setup completo."""
    print("\n" + "🚀 SETUP COMPLETO DEL SISTEMA")
    print("\nEste proceso ejecutará:")
    print("  1. Crear colecciones con validación")
    print("  2. Crear índices")
    print("  3. Cargar todos los datos con embeddings")
    
    print("\n⚠️  ADVERTENCIA: Este proceso puede tomar 10-15 minutos")
    print("    y eliminará todos los datos existentes en las colecciones")
    
    confirm = input("\n¿Deseas continuar? (s/n): ").strip().lower()
    
    if confirm == 's' or confirm == 'si' or confirm == 'sí':
        try:
            print("\n" + "="*70)
            print("INICIANDO SETUP COMPLETO")
            print("="*70)
            
            # Paso 1: Crear colecciones
            print("\n🔹 PASO 1/3: Creando colecciones...")
            success_1 = create_all_collections()
            
            if not success_1:
                print("\n❌ Error en Paso 1. Setup cancelado.")
                input("\nPresiona Enter para continuar...")
                return
            
            # Paso 2: Crear índices
            print("\n🔹 PASO 2/3: Creando índices...")
            success_2 = create_all_indexes()
            
            if not success_2:
                print("\n❌ Error en Paso 2. Setup cancelado.")
                input("\nPresiona Enter para continuar...")
                return
            
            # Paso 3: Cargar datos
            print("\n🔹 PASO 3/3: Cargando datos con embeddings...")
            success_3 = load_all_data()
            
            if not success_3:
                print("\n❌ Error en Paso 3. Setup cancelado.")
                input("\nPresiona Enter para continuar...")
                return
            
            # Todo exitoso
            print("\n" + "="*70)
            print("✅ SETUP COMPLETO EXITOSO")
            print("="*70)
            print("\n🎉 El sistema está listo para usar")
            print("\nPuedes usar la opción [4] para verificar los datos cargados")
            input("\nPresiona Enter para continuar...")
            
        except Exception as e:
            print(f"\n❌ Error durante el setup: {str(e)}")
            input("\nPresiona Enter para continuar...")
    else:
        print("\n❌ Operación cancelada")
        input("\nPresiona Enter para continuar...")


def option_6_verify_connection():
    """Opción 6: Verificar conexión."""
    print("\n" + "🔍 Verificando conexión a MongoDB Atlas...")
    try:
        success = verify_connection()
        if success:
            print("\n✅ Conexión exitosa")
            input("\nPresiona Enter para continuar...")
        else:
            print("\n❌ Error de conexión")
            print("\nAsegúrate de:")
            print("  1. Tener configurado correctamente el archivo .env")
            print("  2. Tener acceso a internet")
            print("  3. Que tu IP esté autorizada en MongoDB Atlas")
            input("\nPresiona Enter para continuar...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nAsegúrate de:")
        print("  1. Tener configurado correctamente el archivo .env")
        print("  2. Tener acceso a internet")
        print("  3. Que tu IP esté autorizada en MongoDB Atlas")
        input("\nPresiona Enter para continuar...")


def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def main():
    """Función principal de la aplicación."""
    while True:
        try:
            clear_screen()
            print_header()
            print_menu()
            
            opcion = input("\nSelecciona una opción: ").strip()
            
            if opcion == '1':
                option_1_create_collections()
            elif opcion == '2':
                option_2_create_indexes()
            elif opcion == '3':
                option_3_load_data()
            elif opcion == '4':
                option_4_verify_data()
            elif opcion == '5':
                option_5_full_setup()
            elif opcion == '6':
                option_6_verify_connection()
            elif opcion == '0':
                print("\n👋 ¡Hasta luego!")
                print("="*70 + "\n")
                sys.exit(0)
            else:
                print("\n❌ Opción inválida. Por favor selecciona una opción del menú.")
                input("\nPresiona Enter para continuar...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Programa interrumpido por el usuario")
            print("="*70 + "\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ Error inesperado: {str(e)}")
            import traceback
            traceback.print_exc()
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()
