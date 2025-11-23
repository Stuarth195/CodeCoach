# update_problems.py
from pymongo import MongoClient


def update_problems_with_function_types():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["codecoach_db"]
    problems = db["problems"]

    # Actualizar problemas existentes
    problems.update_many(
        {"title": "Número Palíndromo"},
        {"$set": {
            "function_type": "int",
            "function_name": "esNumeroPalindromo"
        }}
    )

    problems.update_many(
        {"title": "Cadena Palíndromo"},
        {"$set": {
            "function_type": "string",
            "function_name": "esPalindromo"
        }}
    )

    problems.update_many(
        {"title": "Two Sum"},
        {"$set": {
            "function_type": "array",
            "function_name": "twoSum"
        }}
    )

    print("✅ Problemas actualizados con function_type")


if __name__ == "__main__":
    update_problems_with_function_types()


