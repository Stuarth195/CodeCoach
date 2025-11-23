# fix_palindrome_type.py
from pymongo import MongoClient


def fix_palindrome_problem():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["codecoach_db"]
    problems = db["problems"]

    # Actualizar el problema de palíndromo
    problem = problems.find_one({"title": "numero_palindromo"})
    if problem:
        print("🔧 Actualizando problema 'Número Palíndromo'")

        # Cambiar a "int" porque la función recibe int y retorna bool
        problems.update_one(
            {"title": "Número Palíndromo"},
            {"$set": {
                "function_type": "bool",  # Mantenemos bool porque retorna bool
                "function_param_type": "int"  # Nuevo campo para el tipo de parámetro
            }}
        )
        print("✅ Problema actualizado: function_type='bool', function_param_type='int'")

        # Verificar los ejemplos
        examples = problem.get('examples', [])
        print("📋 Ejemplos actuales:")
        for i, example in enumerate(examples, 1):
            print(f"   {i}. Input: {example.get('input_raw')} -> Expected: {example.get('output_raw')}")
    else:
        print("❌ Problema 'Número Palíndromo' no encontrado")


if __name__ == "__main__":
    fix_palindrome_problem()