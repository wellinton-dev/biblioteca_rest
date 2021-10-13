import json

from sqlalchemy import func
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from models import Obras, Autores
import os

app = Flask(__name__)
api = Api(app)


class CadastraObra(Resource):

    def post(self, dadosjson=None):
        print(dadosjson)
        try:
            if dadosjson is None:
                dados = json.loads(request.data)
            else:
                dados = dadosjson
            obra = Obras()

            if 'titulo' in dados:
                obra.titulo = dados['titulo']
            if 'editora' in dados:
                obra.editora = dados['editora']
            if 'foto' in dados:
                obra.foto = dados['foto']
            obra.save()
            list_autor = []
            if 'autores' in dados:
                for autor in dados['autores']:
                    add_autor = Autores(autor=autor, obra_id=obra.id)
                    list_autor.append(autor)
                    add_autor.save()
            response = {
                'id': obra.id,
                'titulo': obra.titulo,
                'editora': obra.editora,
                'foto': obra.foto,
                'autores': list_autor

            }
        except json.JSONDecodeError:
            response = {
                'status': 'Error',
                'mensagem': 'Insira um Json válido!'
            }
        return response


# Inserção de multiplos arquivos! Criado somente form-data.
class UploadObra(Resource):

    def post(self):
        if request.headers['Content-Type'].split(';')[0] == 'multipart/form-data':
            arquivos_lista = request.files.listvalues()
            print(arquivos_lista)
            diretorio = os.getcwd()
            cont_arq = 0
            cont_reg = 0
            for arquivos in arquivos_lista:

                for arquivo in arquivos:

                    cont_arq = cont_arq + 1
                    arquivo_saida = f'{diretorio}\\temp{cont_arq}_{arquivo.filename}'
                    arquivo.save(f'{arquivo_saida}')
                    with open(arquivo_saida, 'r') as file:
                        ler = file.readlines()
                        for dados in ler:
                            try:
                                cont_reg = cont_reg + 1
                                dados_json = json.loads(dados)
                                CadastraObra.post(self, dadosjson=dados_json)

                            except json.JSONDecodeError:
                                response = {
                                    'status': 'Error',
                                    'menssagem': f'O arquivo {arquivo.filename} contém Json inválido'
                                }
                                return response
                    file.close()
                    os.remove(arquivo_saida)
            response = {
                'status': 'Sucesso',
                'mensagem': f'{cont_arq} arquivo(s) lidos e {cont_reg} registros inseridos!'
            }
        else:
            response = {
                'status': 'Error',
                'mensagem': 'Para inserção de múltiplos arquivos use o Content-Type multipart/form-data'
            }
        return response


# Lista todas as Obras!
class ListarObra(Resource):

    def get(self):
        obra = Obras.query.all()
        response = [{'id': i.id,
                     'titulo': i.titulo,
                     'editora': i.editora,
                     'foto': i.foto, 'autores': [i.autor for i in i.autores]} for i in obra]
        return response


# Faz o download geral das obras ou por data.Ex: 2021-10-13
class FileObra(Resource):

    def get(self, date_create=None):
        if date_create is None:
            obra = Obras.query.all()
            dados = [{'id': i.id,
                      'titulo': i.titulo,
                      'editora': i.editora,
                      'date_create': str(i.date_create),
                      'foto': i.foto, 'autores': [i.autor for i in i.autores]} for i in obra]
            with open('temp.csv', 'w+') as file:
                for dados_json in dados:
                    files_json = json.dumps(dados_json)
                    file.write(files_json + '\n')
                file.seek(0)
                arquivo = file.read()
                file.close()
                os.remove('temp.csv')
            response = make_response(arquivo)
            response.headers['Content-Type'] = 'text/json'
            response.headers['Content-Disposition'] = 'attachment; filename=obras.csv'
        else:
            obra = Obras.query.filter(func.DATE(Obras.date_create) == date_create).all()

            # Verifica se retornou alguma data existente no banco de dados.

            if len(obra) == 0:
                response = {
                    'status': 'Error',
                    'mensagem': 'Data não encontrada. Verifique se digitou a da correta.Ex:2021-10-10'
                }
                return response
            dados = [{'id': i.id,
                      'titulo': i.titulo,
                      'editora': i.editora,
                      'date_create': str(i.date_create),
                      'foto': i.foto, 'autores': [i.autor for i in i.autores]} for i in obra]
            with open('temp_data.csv', 'w+') as file:
                for dados_json in dados:
                    files_json = json.dumps(dados_json)
                    file.write(files_json + '\n')
                file.seek(0)
                arquivo = file.read()
                file.close()
                os.remove('temp_data.csv')
            response = make_response(arquivo)
            response.headers['Content-Type'] = 'text/json'
            response.headers['Content-Disposition'] = f'attachment; filename={date_create}.csv'

        return response


class ObrasId(Resource):
    # Atualiza Obra e Autor.
    def put(self, id):
        try:
            obra = Obras.query.filter_by(id=id).first()
            dados = json.loads(request.data)

            # Verifica se o dado existe na requisição, se existir atualiza!
            if 'titulo' in dados:
                obra.titulo = dados['titulo']
            if 'editora' in dados:
                obra.editora = dados['editora']
            if 'foto' in dados:
                obra.foto = dados['foto']
            obra.update()

            # Atualiza os autores.
            if 'autores' in dados:
                updt_autor = Autores.query.filter_by(obra_id=id).all()
                dados = dados['autores']
                print(dados)
                cont_autor = len(updt_autor)
                cont_dados = len(dados)
                if cont_autor == cont_dados:
                    for i in range(cont_autor):
                        autor = Autores.query.filter_by(id=updt_autor[i].id).first()
                        autor.autor = dados[i]
                        autor.save()
                elif cont_dados > cont_autor:
                    for i in range(cont_dados):
                        try:
                            autor = Autores.query.filter_by(id=updt_autor[i].id).first()
                            autor.autor = dados[i]
                            autor.save()
                        except IndexError:
                            autor = Autores(autor=dados[i], obra_id=id)
                            autor.save()
                elif cont_dados < cont_autor:
                    for i in range(cont_autor):
                        try:
                            autor = Autores.query.filter_by(id=updt_autor[i].id).first()
                            autor.autor = dados[i]
                            autor.save()
                        except IndexError:
                            autor.delete()
            autor_atualizdo = Autores.query.filter_by(obra_id=3).all()
            autores = [i.autor for i in autor_atualizdo]
            response = {
                'id': obra.id,
                'titulo': obra.titulo,
                'editora': obra.editora,
                'foto': obra.foto,
                'date_create': str(obra.date_create),
                'autores': autores
            }
        except AttributeError:
            response = {
                'status': 'Error',
                'mensagem': 'O ID informado não existe'
            }
        return response

    # Deleta uma obra em cascata com o autor!
    def delete(self, id):
        try:
            obra = Obras.query.filter_by(id=id).first()
            obra.delete()
            response = {
                'status': 'Sucesso',
                'mensagem': f'ID : {id} Deletado com sucesso!'
            }
        except AttributeError:
            response = {
                'status': 'Error',
                'mensagem': 'O ID informado não existe'
            }
        return response


# Configuração das rotas

api.add_resource(CadastraObra, '/obras')
api.add_resource(UploadObra, '/upload-obras')
api.add_resource(ListarObra, '/obras/')
api.add_resource(FileObra, '/file-obras/<date_create>', '/file-obras/')
api.add_resource(ObrasId, '/obras/<int:id>')

if __name__ == '__main__':
    app.run(debug=True)
