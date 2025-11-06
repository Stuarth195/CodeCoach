    # mock_server.py prueab de envio
    from flask import Flask, request, jsonify

    app = Flask(__name__)


    @app.route('/submit_evaluation', methods=['POST'])
    def mock_submit_evaluation():
        """ Recibe y verifica el paquete de datos, luego simula un resultado. """
        try:
            data = request.get_json()

            # Extracción y verificación del paquete (Tu código está funcionando si ves esto)
            code_snippet = data.get('code', 'N/A')[:50]  # Primeros 50 caracteres del código
            problem_title = data.get('problem_details', {}).get('title', 'Problema Desconocido')

            print("\n--- ¡PAQUETE RECIBIDO DE LA GUI! ---")
            print(f"Código Enviado (Snippet): {code_snippet}...")
            print(f"Detalles del Problema: {problem_title}")
            print("------------------------------------")

            # Simula una respuesta de error para ver el color rojo en la GUI
            return jsonify({
                "status": "runtime_error",
                "message": "La evaluación falló en el caso de prueba 5/10.",
                "error": "Error de segmentación: Desbordamiento de búfer en la línea 42.",
                "output": "Resultado de la ejecución de la prueba #1: OK.\nResultado de la prueba #5: Fallo."
            }), 200  # Estado HTTP 200: El servidor recibió y procesó la petición.

        except Exception as e:
            return jsonify({"status": "server_error", "message": f"Error interno en el mock: {e}"}), 500


    if __name__ == '__main__':
        print("MOCK SERVER INICIADO. Esperando en http://127.0.0.1:5000/submit_evaluation")
        app.run(host='127.0.0.1', port=5000, debug=False)