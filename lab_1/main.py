from flask import Flask, jsonify, request
import proximo_feriado
import random

app = Flask(__name__)
peliculas = [
    {'id': 1, 'titulo': 'Indiana Jones', 'genero': 'Acción'},
    {'id': 2, 'titulo': 'Star Wars', 'genero': 'Acción'},
    {'id': 3, 'titulo': 'Interstellar', 'genero': 'Ciencia ficción'},
    {'id': 4, 'titulo': 'Jurassic Park', 'genero': 'Aventura'},
    {'id': 5, 'titulo': 'The Avengers', 'genero': 'Acción'},
    {'id': 6, 'titulo': 'Back to the Future', 'genero': 'Ciencia ficción'},
    {'id': 7, 'titulo': 'The Lord of the Rings', 'genero': 'Fantasía'},
    {'id': 8, 'titulo': 'The Dark Knight', 'genero': 'Acción'},
    {'id': 9, 'titulo': 'Inception', 'genero': 'Ciencia ficción'},
    {'id': 10, 'titulo': 'The Shawshank Redemption', 'genero': 'Drama'},
    {'id': 11, 'titulo': 'Pulp Fiction', 'genero': 'Crimen'},
    {'id': 12, 'titulo': 'Fight Club', 'genero': 'Drama'}
]


def obtener_peliculas():
    return jsonify(peliculas)


def obtener_pelicula(id):
    # Lógica para buscar la película por su ID y devolver sus detalles
    for pelicula in peliculas :
        if pelicula['id']==id:
            pelicula_encontrada = {
                'id' : pelicula['id'],
                'titulo': pelicula['titulo'],
                'genero': pelicula['genero']
            }
    if pelicula_encontrada:
        return jsonify(pelicula_encontrada)
    else:
        return jsonify({'mensaje': 'No se encontro el id de la pelicula'}), 404


def agregar_pelicula():
    nueva_pelicula = {
        'id': obtener_nuevo_id(),
        'titulo': request.json['titulo'],
        'genero': request.json['genero']
    }
    peliculas.append(nueva_pelicula)
    print(peliculas)
    return jsonify(nueva_pelicula), 201


def actualizar_pelicula(id):
    # Lógica para buscar la película por su ID y actualizar sus detalles
    encontro_id = False
    for pelicula in peliculas:
        if pelicula['id']==id:
            encontro_id = True
            pelicula['titulo'] = request.json['titulo']
            pelicula['genero'] = request.json['genero']
            break
    if encontro_id:
        return jsonify(pelicula)
    else:
        return jsonify({'mensaje': 'No se encontro el id de la pelicula'}), 404

def eliminar_pelicula(id):
    # Lógica para buscar la película por su ID y eliminarla
    encontro_id = False
    for pelicula in peliculas:
        if pelicula['id']==id:
            encontro_id = True
            peliculas.remove(pelicula)
    if encontro_id:
        return jsonify({'mensaje': 'Película eliminada correctamente'})
    else:
        return jsonify({'mensaje': 'No se encontro el id de la pelicula'}), 404



def obtener_nuevo_id():
    if len(peliculas) > 0:
        ultimo_id = peliculas[-1]['id']
        return ultimo_id + 1
    else:
        return 1


def peliculas_por_genero(genero):
    peliculas_genero = []
    for pelicula in peliculas:
        if pelicula['genero']==genero:
            peliculas_genero.append(pelicula)
    if len(peliculas_genero)==0:
        return jsonify({'mensaje': 'No se encontraron peliculas con ese genero'})
    else:
        return jsonify(peliculas_genero)

def buscar_peliculas_con_string(palabra):
    peliculas_con_palabra = []
    for pelicula in peliculas:
        if palabra in pelicula['titulo']:
            peliculas_con_palabra.append(pelicula)
    if len(peliculas_con_palabra)==0:
        return jsonify({'mensaje': 'No se encontraron peliculas que contengan ese string'})
    else:
        return jsonify(peliculas_con_palabra)

def pelicula_aleatoria():
    pelicula_aleatoria = random.choice(peliculas)
    return jsonify(pelicula_aleatoria)

def pelicula_aleatoria_segun_genero(genero):
    peliculas_segun_genero = []
    for pelicula in peliculas:
        if pelicula['genero']==genero:
            peliculas_segun_genero.append(pelicula)
    peli = random.choice(peliculas_segun_genero)
    return jsonify(peli)


    

def feriado():
    prox_feriado = proximo_feriado.NextHoliday()
    prox_feriado.fetch_holidays()
    return prox_feriado.holiday



def pelicula_feriado(genero):

    peliculas_segun_genero = []
    for pelicula in peliculas:
        if pelicula['genero']==genero:
            peliculas_segun_genero.append(pelicula)
    pelicula_genero = random.choice(peliculas_segun_genero)
    prox_feriado = feriado()

    response = {
        'id' : pelicula_genero['id'],
        'titulo': pelicula_genero['titulo'],
        'genero' : pelicula_genero['genero'],
        'fecha': f"{prox_feriado['dia']}/{prox_feriado['mes']}",
        'motivo': prox_feriado['motivo']
    }

    return jsonify(response)





app.add_url_rule('/peliculas', 'obtener_peliculas', obtener_peliculas, methods=['GET'])
app.add_url_rule('/peliculas/<int:id>', 'obtener_pelicula', obtener_pelicula, methods=['GET'])
app.add_url_rule('/peliculas', 'agregar_pelicula', agregar_pelicula, methods=['POST'])
app.add_url_rule('/peliculas/<int:id>', 'actualizar_pelicula', actualizar_pelicula, methods=['PUT'])
app.add_url_rule('/peliculas/<int:id>', 'eliminar_pelicula', eliminar_pelicula, methods=['DELETE'])
app.add_url_rule('/peliculas/<string:palabra>', 'buscar_peliculas_con_string', buscar_peliculas_con_string, methods=['GET'])
app.add_url_rule('/peliculas/gen/<string:genero>', 'obtener_peliculas_por_genero', peliculas_por_genero, methods=['GET'])
app.add_url_rule('/peliculas/aleatoria', 'pelicula_aleatoria', pelicula_aleatoria, methods=['GET'])
app.add_url_rule('/peliculas/aleatoria/<string:genero>', 'pelicula_aleatoria_segun_genero', pelicula_aleatoria_segun_genero, methods=['GET'])
app.add_url_rule('/peliculas/feriado/<string:genero>', 'pelicula_feriado', pelicula_feriado, methods=['GET'])


if __name__ == '__main__':
    app.run()









    