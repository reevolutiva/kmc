# /Users/giorgio/Documents/kmc/kmc/test_direct_import.py
import sys
print(f"Python Executable: {sys.executable}")
print(f"Python Version: {sys.version}")
print(f"sys.path: {sys.path}")

try:
    print("Intentando importar SupabaseVectorStore desde llama_index.vector_stores.supabase...")
    from llama_index.vector_stores.supabase import SupabaseVectorStore # MODIFICADO AQUÍ
    print("Importación de SupabaseVectorStore EXITOSA!")
    print(f"SupabaseVectorStore: {SupabaseVectorStore}")

    # Verificar el módulo llama_index base
    import llama_index
    print(f"--- Detalles del módulo llama_index importado ---")
    print(f"llama_index.__file__: {getattr(llama_index, '__file__', 'No tiene __file__')}")
    print(f"llama_index.__path__: {getattr(llama_index, '__path__', 'No tiene __path__')}")
    print(f"llama_index.__version__: {getattr(llama_index, '__version__', 'No tiene __version__')}")
    print(f"dir(llama_index): {dir(llama_index)}")
    print(f"-------------------------------------------------")

    # Intentar acceder a llama_index.core
    if hasattr(llama_index, 'core'):
        print("llama_index.core existe.")
        print(f"dir(llama_index.core): {dir(llama_index.core)}")
        if hasattr(llama_index.core, 'vector_stores'):
            print("llama_index.core.vector_stores existe.")
            print(f"dir(llama_index.core.vector_stores): {dir(llama_index.core.vector_stores)}")
            if hasattr(llama_index.core.vector_stores, 'supabase'):
                 print("llama_index.core.vector_stores.supabase existe.")
                 print(f"Contenido de supabase: {dir(llama_index.core.vector_stores.supabase)}")
            else:
                print("FALLO: llama_index.core.vector_stores.supabase NO existe.")
        else:
            print("FALLO: llama_index.core.vector_stores NO existe.")
    else:
        print("FALLO: llama_index.core NO existe.")


except ImportError as e:
    print(f"Error en la importación directa: {e}")
    import traceback
    traceback.print_exc()

except Exception as e:
    print(f"Otro error durante la prueba de importación directa: {e}")
    import traceback
    traceback.print_exc()