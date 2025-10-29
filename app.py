from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.objectid import ObjectId # Importante para buscar por _id si fuera necesario
import json

app = Flask(__name__)

# Conexión al contenedor de MongoDB
# 'mongodb' es el nombre del servicio en docker-compose.yml
client = MongoClient('mongodb://root:root@mongodb:27017')
db = client.LPFM
mycollection = db.UsuariosDB

@app.route('/')
def home():
    return "Welcome to the Flask MongoDB API!"

# --- LEER (READ) ---
# Esto ya lo tenías
@app.route('/items', methods=['GET'])
def get_items():
    items = []
    # Iteramos para convertir el ObjectId a string y que sea serializable en JSON
    for item in mycollection.find():
        item['_id'] = str(item['_id'])
        items.append(item)
    return jsonify(items)

# --- AGREGAR (CREATE) ---
# Esto ya lo tenías
@app.route('/items', methods=['POST'])
def add_item():
    data = request.get_json()
    if data and 'name' in data and 'email' in data:
        mycollection.insert_one(data)
        return jsonify({"message": "Item added successfully"}), 201
    return jsonify({"message": "Invalid data: 'name' and 'email' are required"}), 400

# --- ACTUALIZAR (UPDATE) ---
# Ruta nueva: Actualiza el nombre de un usuario buscando por email
@app.route('/items', methods=['PUT'])
def update_item():
    data = request.get_json()
    if data and 'email' in data and 'newName' in data:
        query = { "email": data['email'] }
        new_values = { "$set": { "name": data['newName'] } }
        
        result = mycollection.update_one(query, new_values)
        
        if result.matched_count > 0:
            return jsonify({"message": "Item updated successfully"}), 200
        else:
            return jsonify({"message": "Item not found"}), 404
    return jsonify({"message": "Invalid data: 'email' and 'newName' are required"}), 400

# --- ELIMINAR (DELETE) ---
# Ruta nueva: Elimina un usuario buscando por email
@app.route('/items', methods=['DELETE'])
def delete_item():
    data = request.get_json()
    if data and 'email' in data:
        query = { "email": data['email'] }
        result = mycollection.delete_one(query)
        
        if result.deleted_count > 0:
            return jsonify({"message": "Item deleted successfully"}), 200
        else:
            return jsonify({"message": "Item not found"}), 404
    return jsonify({"message": "Invalid data: 'email' is required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)