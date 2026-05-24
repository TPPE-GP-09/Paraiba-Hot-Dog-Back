from datetime import time
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.permissoes.model import Permissao, TipoPermissao
from src.permissoes.schema import PermissaoUpdate
from src.permissoes import repository as permissoes_repository
from src.unidades.model import Endereco, Unidade
from src.unidades.schema import EnderecoCreate, EnderecoUpdate, UnidadeCreate, UnidadeUpdate
from src.unidades import repository as unidades_repository
from src.usuarios.model import FuncaoUsuario, Usuario
from src.usuarios.schema import UsuarioCreate, UsuarioUpdate
from src.usuarios import repository as usuarios_repository


class FakeQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *_args):
        return self

    def order_by(self, *_args):
        return self

    def all(self):
        return self.items


class FakeIntegrityOrig:
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def integrity_error(message: str) -> IntegrityError:
    return IntegrityError("statement", "params", FakeIntegrityOrig(message))


def permissao(permissao_id=1, nome=TipoPermissao.dashboard):
    item = Permissao(id=permissao_id, nome=nome)
    item.usuarios = []
    return item


def usuario(usuario_id=1):
    item = Usuario(
        id=usuario_id,
        keycloak_id="kc-1",
        nome="Usuario Teste",
        email="usuario@example.com",
        funcao=FuncaoUsuario.caixa,
        unidade_id=1,
    )
    item.permissoes = []
    return item


def unidade(unidade_id=1, endereco=None):
    return Unidade(
        id=unidade_id,
        nome="Centro",
        imagem=None,
        abertura=time(11, 0),
        fechamento=time(23, 0),
        descricao="Unidade central",
        endereco=endereco,
        endereco_id=getattr(endereco, "id", None),
    )


def test_resolver_permissoes_retorna_todas():
    db = Mock()
    itens = [permissao(1), permissao(2, TipoPermissao.cozinha)]
    db.query.return_value = FakeQuery(itens)

    resultado = usuarios_repository._resolver_permissoes(db, [1, 2])

    assert resultado == itens


def test_resolver_permissoes_lanca_404_quando_falta_id():
    db = Mock()
    db.query.return_value = FakeQuery([permissao(1)])

    with pytest.raises(HTTPException) as exc:
        usuarios_repository._resolver_permissoes(db, [1, 2])

    assert exc.value.status_code == 404
    assert exc.value.detail == "Uma ou mais permissoes nao encontradas"


def test_validar_unidade_ignora_none_e_rejeita_inexistente():
    db = Mock()

    usuarios_repository._validar_unidade(db, None)
    db.get.assert_not_called()

    db.get.return_value = None
    with pytest.raises(HTTPException) as exc:
        usuarios_repository._validar_unidade(db, 99)

    assert exc.value.status_code == 404


@pytest.mark.parametrize(
    "mensagem,status_code,detail",
    [
        ("duplicate key email", 409, "Email ja cadastrado"),
        ("violates fk_usuarios_unidade_id", 404, "Unidade nao encontrada"),
        ("outro erro", 409, "Violacao de integridade"),
    ],
)
def test_tratar_integridade_mapeia_erros(mensagem, status_code, detail):
    exc = usuarios_repository._tratar_integridade(integrity_error(mensagem))

    assert exc.status_code == status_code
    assert exc.detail == detail


def test_create_usuario_cria_no_keycloak_e_no_banco(monkeypatch):
    db = Mock()
    db.query.return_value = FakeQuery([permissao()])
    db.get.return_value = unidade()
    monkeypatch.setattr(usuarios_repository, "create_keycloak_user", Mock(return_value=("kc-1", True)))

    data = UsuarioCreate(
        nome="Usuario Teste",
        email="usuario@example.com",
        senha="12345678",
        funcao=FuncaoUsuario.caixa,
        unidade_id=1,
        permissao_ids=[1],
    )

    criado = usuarios_repository.create_usuario(db, data)

    assert criado.keycloak_id == "kc-1"
    assert criado.permissoes[0].id == 1
    db.add.assert_called_once_with(criado)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(criado)


def test_create_usuario_remove_keycloak_quando_commit_falha(monkeypatch):
    db = Mock()
    db.query.return_value = FakeQuery([])
    db.get.return_value = None
    db.commit.side_effect = integrity_error("duplicate email")
    delete_mock = Mock()
    monkeypatch.setattr(usuarios_repository, "create_keycloak_user", Mock(return_value=("kc-1", True)))
    monkeypatch.setattr(usuarios_repository, "delete_keycloak_user", delete_mock)

    data = UsuarioCreate(
        nome="Usuario Teste",
        email="usuario@example.com",
        senha="12345678",
        unidade_id=None,
        permissao_ids=[],
    )

    with pytest.raises(HTTPException) as exc:
        usuarios_repository.create_usuario(db, data)

    assert exc.value.status_code == 409
    db.rollback.assert_called_once()
    delete_mock.assert_called_once_with("kc-1")


def test_list_get_update_delete_usuario(monkeypatch):
    item = usuario()
    db = Mock()
    db.query.return_value = FakeQuery([item])
    db.get.return_value = item
    db.query.return_value.all = Mock(return_value=[item])
    update_mock = Mock()
    delete_mock = Mock()
    monkeypatch.setattr(usuarios_repository, "update_keycloak_user", update_mock)
    monkeypatch.setattr(usuarios_repository, "delete_keycloak_user", delete_mock)

    assert usuarios_repository.list_usuarios(db, "usuario@example.com", "Usuario") == [item]
    assert usuarios_repository.get_usuario(db, 1) == item

    atualizado = usuarios_repository.update_usuario(
        db,
        1,
        UsuarioUpdate(nome="Novo Nome", senha="nova", funcao=FuncaoUsuario.administrador),
    )
    assert atualizado.nome == "Novo Nome"
    update_mock.assert_called_once_with(
        "kc-1",
        nome="Novo Nome",
        email=None,
        senha="nova",
        nome_role="administrador",
    )

    usuarios_repository.delete_usuario(db, 1)
    db.delete.assert_called_once_with(item)
    delete_mock.assert_called_once_with("kc-1")


def test_update_usuario_valida_unidade_permissoes_e_integridade(monkeypatch):
    item = usuario()
    db = Mock()
    db.get.return_value = item
    db.query.return_value = FakeQuery([permissao()])
    db.commit.side_effect = integrity_error("duplicate email")
    monkeypatch.setattr(usuarios_repository, "update_keycloak_user", Mock())

    with pytest.raises(HTTPException) as exc:
        usuarios_repository.update_usuario(
            db,
            1,
            UsuarioUpdate(email="novo@example.com", unidade_id=1, permissao_ids=[1]),
        )

    assert exc.value.status_code == 409
    db.rollback.assert_called_once()
    assert item.permissoes[0].id == 1


def test_get_usuario_nao_encontrado():
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        usuarios_repository.get_usuario(db, 99)

    assert exc.value.status_code == 404


def test_permissoes_repository_fluxo_feliz():
    db = Mock()
    item = permissao()
    user = usuario()
    db.query.return_value.all.return_value = [item]
    db.get.side_effect = [item, item, item, user, item, user, item]

    assert permissoes_repository.listar_permissoes(db) == [item]
    assert permissoes_repository.obter_permissao(db, 1) == item
    assert permissoes_repository.criar_permissao(db, TipoPermissao.cozinha).nome == TipoPermissao.cozinha
    assert permissoes_repository.atualizar_permissao(
        db,
        1,
        PermissaoUpdate(nome=TipoPermissao.configuracoes),
    ).nome == TipoPermissao.configuracoes
    assert permissoes_repository.conceder_permissao(db, 1, 1) == item
    assert item in user.permissoes

    permissoes_repository.revogar_permissao(db, 1, 1)
    assert item not in user.permissoes

    permissoes_repository.excluir_permissao(db, 1)
    db.delete.assert_called_with(item)


def test_permissoes_repository_erros():
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        permissoes_repository.obter_permissao(db, 1)
    assert exc.value.status_code == 404

    db.commit.side_effect = integrity_error("duplicado")
    with pytest.raises(HTTPException) as exc:
        permissoes_repository.criar_permissao(db, TipoPermissao.dashboard)
    assert exc.value.status_code == 409

    db.commit.side_effect = integrity_error("duplicado")
    db.get.return_value = permissao()
    with pytest.raises(HTTPException) as exc:
        permissoes_repository.atualizar_permissao(
            db,
            1,
            PermissaoUpdate(nome=TipoPermissao.dashboard),
        )
    assert exc.value.status_code == 409


def test_conceder_e_revogar_permissao_com_erros():
    item = permissao()
    user = usuario()
    user.permissoes = [item]
    db = Mock()

    db.get.side_effect = [item, None]
    with pytest.raises(HTTPException) as exc:
        permissoes_repository.conceder_permissao(db, 1, 99)
    assert exc.value.status_code == 404

    db.get.side_effect = [item, user]
    with pytest.raises(HTTPException) as exc:
        permissoes_repository.conceder_permissao(db, 1, 1)
    assert exc.value.status_code == 409

    user.permissoes = []
    db.get.side_effect = [item, user]
    with pytest.raises(HTTPException) as exc:
        permissoes_repository.revogar_permissao(db, 1, 1)
    assert exc.value.status_code == 404


def test_unidades_repository_fluxos_de_criacao_atualizacao_e_exclusao():
    db = Mock()
    endereco = Endereco(
        id=1,
        cep="58000000",
        logradouro="Rua A",
        numero="10",
        complemento=None,
        bairro="Centro",
        cidade="Joao Pessoa",
        estado="PB",
    )
    item = unidade(endereco=endereco)
    db.query.return_value.all.return_value = [item]
    db.get.return_value = item

    assert unidades_repository.listar_unidades(db) == [item]
    assert unidades_repository.obter_unidade(db, 1) == item

    criado = unidades_repository.criar_unidade(
        db,
        UnidadeCreate(
            nome="Nova Unidade",
            imagem=None,
            abertura=time(10, 0),
            fechamento=time(22, 0),
            descricao=None,
            endereco=EnderecoCreate(
                cep="58000001",
                logradouro="Rua B",
                numero=None,
                complemento=None,
                bairro="Bairro",
                cidade="Joao Pessoa",
                estado="PB",
            ),
        ),
    )
    assert criado.nome == "Nova Unidade"
    assert db.add.call_count >= 2

    atualizado = unidades_repository.atualizar_unidade(
        db,
        1,
        UnidadeUpdate(nome="Centro Atualizado", endereco=EnderecoUpdate(cidade="Cabedelo")),
    )
    assert atualizado.nome == "Centro Atualizado"
    assert atualizado.endereco.cidade == "Cabedelo"

    unidades_repository.excluir_unidade(db, 1)
    db.delete.assert_called_with(item)


def test_atualizar_unidade_cria_endereco_quando_nao_existe():
    item = unidade(endereco=None)
    db = Mock()
    db.get.return_value = item

    atualizado = unidades_repository.atualizar_unidade(
        db,
        1,
        UnidadeUpdate(endereco=EnderecoUpdate(cidade="Joao Pessoa", estado="PB")),
    )

    assert atualizado.endereco_id is None
    db.add.assert_called_once()


def test_obter_unidade_nao_encontrada():
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        unidades_repository.obter_unidade(db, 99)

    assert exc.value.status_code == 404
