# migrate_problem_formats.py
from pymongo import MongoClient
import re


def migrate_problems():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["codecoach_db"]
    problems = db["problems"]

    # Problemas booleanos - convertir salidas a "1"/"0"
    bool_problems = ["Número Palíndromo", "Es Primo", "Cadena Palíndromo"]

    for problem_title in bool_problems:
        problem = problems.find_one({"title": problem_title})
        if not problem:
            continue

        print(f"🔄 Migrando problema booleano: {problem_title}")

        # Actualizar ejemplos
        examples = problem.get('examples', [])
        for example in examples:
            output_raw = example.get('output_raw', '')
            # Convertir true/false a 1/0
            if output_raw.lower() == 'true':
                example['output_raw'] = '1'
            elif output_raw.lower() == 'false':
                example['output_raw'] = '0'

        # Actualizar en base de datos
        problems.update_one(
            {"title": problem_title},
            {"$set": {
                "examples": examples,
                "function_type": "bool"
            }}
        )
        print(f"✅ {problem_title} migrado a booleano")

    # Problemas de arrays - normalizar formato
    array_problems = ["Two Sum", "Rotar Array", "Suma de Arrays"]

    for problem_title in array_problems:
        problem = problems.find_one({"title": problem_title})
        if not problem:
            continue

        print(f"🔄 Migrando problema de array: {problem_title}")

        examples = problem.get('examples', [])
        for example in examples:
            # Normalizar formato de arrays [1,2,3]
            input_raw = example.get('input_raw', '')
            output_raw = example.get('output_raw', '')

            # Remover espacios extra en arrays
            example['input_raw'] = re.sub(r'\s*,\s*', ',', input_raw)
            example['output_raw'] = re.sub(r'\s*,\s*', ',', output_raw)

        problems.update_one(
            {"title": problem_title},
            {"$set": {
                "examples": examples,
                "function_type": "array"
            }}
        )
        print(f"✅ {problem_title} migrado a array")

    print("🎉 Migración completada!")


if __name__ == "__main__":
    migrate_problems()