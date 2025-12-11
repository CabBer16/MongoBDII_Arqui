from concurrent import futures
import grpc
import ecommerce_pb2
import ecommerce_pb2_grpc
from pymongo import MongoClient
from bson.objectid import ObjectId

# Conexión a MongoDB
client = MongoClient('mongodb://root:root@mongodb:27017')
db = client.LPFM
collection = db.usuarios

class UsuarioService(ecommerce_pb2_grpc.UsuarioServiceServicer):

    def CrearUsuario(self, request, context):
        nuevo_usuario = {
            "nombre_completo": request.nombre_completo,
            "email": request.email,
            "password_hash": request.password_hash,
            "direcciones": []
        }
        res = collection.insert_one(nuevo_usuario)
        return ecommerce_pb2.UsuarioResponse(id=str(res.inserted_id), nombre_completo=request.nombre_completo, email=request.email)

    def ObtenerUsuario(self, request, context):
        usuario = collection.find_one({"_id": ObjectId(request.id)})
        if usuario:
            return ecommerce_pb2.UsuarioResponse(id=str(usuario["_id"]), nombre_completo=usuario.get("nombre_completo"), email=usuario.get("email"))
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return ecommerce_pb2.UsuarioResponse()

    def ListarUsuarios(self, request, context):
        usuarios = []
        for u in collection.find():
            usuarios.append(ecommerce_pb2.UsuarioResponse(id=str(u["_id"]), nombre_completo=u.get("nombre_completo", ""), email=u.get("email", "")))
        return ecommerce_pb2.ListaUsuariosResponse(usuarios=usuarios)

    def ActualizarUsuario(self, request, context):
        filtro = {"_id": ObjectId(request.id)}
        nuevos_datos = {"$set": {"nombre_completo": request.nombre_completo, "email": request.email}}
        result = collection.update_one(filtro, nuevos_datos)
        if result.matched_count > 0:
            return ecommerce_pb2.UsuarioResponse(id=request.id, nombre_completo=request.nombre_completo, email=request.email)
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return ecommerce_pb2.UsuarioResponse()

    def EliminarUsuario(self, request, context):
        result = collection.delete_one({"_id": ObjectId(request.id)})
        if result.deleted_count > 0:
            return ecommerce_pb2.DeleteResponse(mensaje="Usuario eliminado")
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return ecommerce_pb2.DeleteResponse(mensaje="No encontrado")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ecommerce_pb2_grpc.add_UsuarioServiceServicer_to_server(UsuarioService(), server)
    server.add_insecure_port('[::]:50051')
    print("Servidor gRPC corriendo en el puerto 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()