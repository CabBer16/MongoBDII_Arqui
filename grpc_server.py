from concurrent import futures
import grpc
import ecommerce_pb2
import ecommerce_pb2_grpc
from pymongo import MongoClient
from bson.objectid import ObjectId

# Configuración de MongoDB (igual que en tu app.py)
client = MongoClient('mongodb://root:root@mongodb:27017')
db = client.LPFM
collection = db.usuarios  # Usamos la colección 'usuarios' definida en init-mongo.js

class UsuarioService(ecommerce_pb2_grpc.UsuarioServiceServicer):

    # --- CREATE ---
    def CrearUsuario(self, request, context):
        nuevo_usuario = {
            "nombre_completo": request.nombre_completo,
            "email": request.email,
            "password_hash": request.password_hash,
            "direcciones": [] # Inicializamos vacío por simplicidad
        }
        resultado = collection.insert_one(nuevo_usuario)
        new_id = str(resultado.inserted_id)
        
        return ecommerce_pb2.UsuarioResponse(
            id=new_id,
            nombre_completo=request.nombre_completo,
            email=request.email
        )

    # --- READ (Uno) ---
    def ObtenerUsuario(self, request, context):
        usuario = collection.find_one({"_id": ObjectId(request.id)})
        if usuario:
            return ecommerce_pb2.UsuarioResponse(
                id=str(usuario["_id"]),
                nombre_completo=usuario.get("nombre_completo", ""),
                email=usuario.get("email", "")
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuario no encontrado')
            return ecommerce_pb2.UsuarioResponse()

    # --- UPDATE ---
    def ActualizarUsuario(self, request, context):
        filtro = {"_id": ObjectId(request.id)}
        nuevos_datos = {"$set": {}}
        
        if request.nombre_completo:
            nuevos_datos["$set"]["nombre_completo"] = request.nombre_completo
        if request.email:
            nuevos_datos["$set"]["email"] = request.email

        resultado = collection.update_one(filtro, nuevos_datos)

        if resultado.matched_count > 0:
            # Retornamos los datos actualizados (buscamos de nuevo para confirmar)
            usuario = collection.find_one(filtro)
            return ecommerce_pb2.UsuarioResponse(
                id=str(usuario["_id"]),
                nombre_completo=usuario["nombre_completo"],
                email=usuario["email"]
            )
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuario no encontrado para actualizar')
            return ecommerce_pb2.UsuarioResponse()

    # --- DELETE ---
    def EliminarUsuario(self, request, context):
        resultado = collection.delete_one({"_id": ObjectId(request.id)})
        if resultado.deleted_count > 0:
            return ecommerce_pb2.DeleteResponse(mensaje="Usuario eliminado correctamente")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Usuario no encontrado')
            return ecommerce_pb2.DeleteResponse()
            
    # --- LIST (READ Todos) ---
    def ListarUsuarios(self, request, context):
        usuarios_db = collection.find()
        lista_respuesta = []
        for u in usuarios_db:
            lista_respuesta.append(ecommerce_pb2.UsuarioResponse(
                id=str(u["_id"]),
                nombre_completo=u.get("nombre_completo", ""),
                email=u.get("email", "")
            ))
        return ecommerce_pb2.ListaUsuariosResponse(usuarios=lista_respuesta)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ecommerce_pb2_grpc.add_UsuarioServiceServicer_to_server(UsuarioService(), server)
    
    # Escuchar en el puerto 50051 (Estándar para gRPC)
    print("Iniciando servidor gRPC en puerto 50051...")
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()