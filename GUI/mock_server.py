# mock_server.py
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/submit_evaluation', methods=['POST'])
def mock_submit_evaluation():
    """ Devuelve EXACTAMENTE lo que recibe para corroborar el formato """
    try:
        data = request.get_json()

        print("\n=== DATOS RECIBIDOS EN EL SERVIDOR ===")
        print(f"Código (primeros 100 chars): {data.get('code', 'N/A')[:100]}...")
        print(f"Usuario: {data.get('user_name', 'N/A')}")

        problem_details = data.get('problem_details', {})
        print(f"Título del problema: {problem_details.get('title', 'N/A')}")
        print(f"Dificultad: {problem_details.get('difficulty', 'N/A')}")

        # Mostrar ejemplos si existen
        examples = problem_details.get('examples', [])
        print(f"Número de ejemplos: {len(examples)}")
        for i, example in enumerate(examples, 1):
            print(f"  Ejemplo {i}:")
            print(f"    Input: {example.get('input_raw', 'N/A')}")
            print(f"    Output esperado: {example.get('output_raw', 'N/A')}")

        print("=====================================\n")

        # DEVOLVER EXACTAMENTE LO RECIBIDO (más un campo extra para confirmación)
        response_data = {
            "status": "debug_mode",
            "message": "Esto es exactamente lo que recibí del cliente:",
            "received_data": data,  # ← ESTO ES LO IMPORTANTE
            "confirmation": "El servidor recibió todos los datos correctamente"
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({
            "status": "server_error",
            "message": f"Error interno en el mock: {e}"
        }), 500


if __name__ == '__main__':
    print("MOCK SERVER EN MODO DEBUG INICIADO.")
    print("Mostrará y devolverá exactamente lo recibido.")
    print("Esperando en http://127.0.0.1:5000/submit_evaluation")
    app.run(host='127.0.0.1', port=5000, debug=False)