"""Limpa o banco e popula dados iniciais reais para desenvolvimento."""

from datetime import date, time
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.blog.model import Blog, TipoNoticiaPromocao
from src.clientes.model import Cliente
from src.database import Base, SessionLocal
from src.pedidos.model import ItemPedido, ItemPedidoAdicional, Pedido
from src.permissoes.model import Permissao, TipoPermissao
from src.produtos.model import (
    Categoria,
    Produto,
    ProdutoAdicional,
    ProdutoVariacao,
    Subcategoria,
    TipoVariacao,
)
from src.unidades.model import Endereco, Unidade
from src.usuarios.model import FuncaoUsuario, Usuario


def limpar_banco(db: Session) -> None:
    """Remove todos os dados das tabelas mapeadas antes de aplicar os seeds."""
    if db.bind.dialect.name == "postgresql":
        tabelas = ", ".join(table.name for table in Base.metadata.sorted_tables)
        db.execute(text(f"TRUNCATE TABLE {tabelas} RESTART IDENTITY CASCADE"))
        return

    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())


def criar_permissoes(db: Session) -> list[Permissao]:
    """Cadastra as permissoes padrao da aplicacao."""
    permissoes = [Permissao(nome=nome) for nome in TipoPermissao]
    db.add_all(permissoes)
    db.flush()
    return permissoes


def criar_unidades(db: Session) -> list[Unidade]:
    """Cadastra as unidades reais de Aguas Claras."""
    dados_unidades = [
        {
            "nome": "Unidade Aguas Claras (Avenida Jequitiba)",
            "abertura": time(18, 0),
            "fechamento": time(23, 0),
            "descricao": "Unidade da Avenida Jequitiba em Aguas Claras.",
            "endereco": {
                "cep": "70297400",
                "logradouro": "Av. Jequitiba Praca Tangara",
                "numero": None,
                "complemento": None,
                "bairro": "Aguas Claras",
                "cidade": "Brasilia",
                "estado": "DF",
            },
        },
        {
            "nome": "Unidade Aguas Claras (Avenida das Araucarias)",
            "abertura": time(17, 0),
            "fechamento": time(23, 0),
            "descricao": "Unidade da Avenida das Araucarias em Aguas Claras.",
            "endereco": {
                "cep": "70297400",
                "logradouro": "Av. das Araucarias",
                "numero": "1395",
                "complemento": None,
                "bairro": "Aguas Claras",
                "cidade": "Brasilia",
                "estado": "DF",
            },
        },
    ]

    unidades = []
    for dados in dados_unidades:
        endereco = Endereco(**dados.pop("endereco"))
        unidade = Unidade(**dados, imagem=None, endereco=endereco)
        db.add(unidade)
        unidades.append(unidade)

    db.flush()
    return unidades


def criar_blog(db: Session) -> None:
    """Cadastra as noticias e promocoes informadas."""
    posts = [
        Blog(
            titulo="NOVA UNIDADE ABRE NA SAMAMBAIA",
            imagem_url=None,
            descricao=(
                "Estamos expandindo! Nossa terceira unidade chega na Samambaia "
                "com cardapio especial e horario estendido"
            ),
            tipo=TipoNoticiaPromocao.noticia,
            data=date(2026, 5, 24),
        ),
        Blog(
            titulo="COMBO ESPECIAL: HOT DOG + BATATA + REFRI POR R$ 25",
            imagem_url=None,
            descricao=(
                "Aproveite nossa promocao especial! Combo completo com desconto "
                "ate o final do mes"
            ),
            tipo=TipoNoticiaPromocao.promocao,
            data=date(2026, 5, 24),
        ),
    ]
    db.add_all(posts)


def criar_cliente(db: Session) -> Cliente:
    """Cadastra um cliente inicial para testes manuais."""
    cliente = Cliente(
        nome="Daniel Ferreira",
        telefone="61999990001",
        email="daniel.ferreira@example.com",
        pontos_fidelidade=12,
        ativo=True,
    )
    db.add(cliente)
    db.flush()
    return cliente


def criar_usuario(db: Session, unidade: Unidade, permissoes: list[Permissao]) -> Usuario:
    """Cadastra um usuario administrador local para testes manuais."""
    usuario = Usuario(
        nome="Administrador Paraiba Hot Dog",
        email="admin.paraiba@example.com",
        senha=None,
        funcao=FuncaoUsuario.administrador,
        unidade_id=unidade.id,
        keycloak_id=None,
    )
    usuario.permissoes = permissoes
    db.add(usuario)
    db.flush()
    return usuario


def criar_categoria_com_subcategoria(db: Session, categoria_nome: str, subcategoria_nome: str) -> Subcategoria:
    """Cria uma categoria com uma subcategoria associada."""
    categoria = Categoria(nome=categoria_nome)
    subcategoria = Subcategoria(nome=subcategoria_nome, categoria=categoria)
    db.add(categoria)
    db.flush()
    return subcategoria


def criar_produto(
    db: Session,
    *,
    subcategoria: Subcategoria,
    unidades: list[Unidade],
    nome: str,
    descricao: str,
    variacoes: list[tuple[str, TipoVariacao, str]],
    adicionais: list[tuple[str, str]] | None = None,
    pontos: int = 1,
) -> Produto:
    """Cria produto com variacoes de preco e adicionais opcionais."""
    produto = Produto(
        nome=nome,
        descricao=descricao,
        imagem_url=None,
        ativo=True,
        pontos_fidelidade_por_unidade=pontos,
        disponivel_todas_unidades=True,
        subcategoria_id=subcategoria.id,
    )
    produto.unidades = unidades
    db.add(produto)
    db.flush()

    for variacao_nome, tipo, preco in variacoes:
        db.add(
            ProdutoVariacao(
                produto_id=produto.id,
                nome=variacao_nome,
                tipo=tipo,
                preco=Decimal(preco),
                ativo=True,
            )
        )

    for adicional_nome, preco in adicionais or []:
        db.add(
            ProdutoAdicional(
                produto_id=produto.id,
                nome=adicional_nome,
                preco=Decimal(preco),
            )
        )

    return produto


def adicionais_hot_dog() -> list[tuple[str, str]]:
    """Retorna adicionais padrao dos hot dogs."""
    return [
        ("Carne", "5.00"),
        ("Queijo", "5.00"),
        ("Bacon", "5.00"),
        ("Ovo de Codorna", "2.00"),
        ("Milho", "2.00"),
        ("Vinagrete", "2.00"),
        ("Parmesao", "2.00"),
        ("Maionese Extra - Alho Ervas", "3.00"),
        ("Maionese Extra - Tradicional", "3.00"),
        ("Maionese Extra - Apimentada", "3.00"),
        ("Maionese Extra - Bacon", "3.00"),
    ]


def adicionais_smashdog() -> list[tuple[str, str]]:
    """Retorna adicionais padrao dos smashdogs."""
    return [
        ("Carne", "7.00"),
        ("Bacon", "5.00"),
        ("Queijo", "4.00"),
        ("Salada", "4.00"),
        ("Pickles", "4.00"),
        ("Salsicha", "3.00"),
    ]


def seed_hot_dogs(db: Session, unidades: list[Unidade]) -> None:
    """Cadastra o cardapio Paraiba Hot Dog."""
    subcategoria = criar_categoria_com_subcategoria(db, "Paraiba Hot Dog", "Lanches")
    produtos = [
        (
            "TRADICIONAL",
            "Pao de hot-dog, maionese, salsicha perdigao, queijo mucarela, molho de tomate caseiro, milho e batata palha.",
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "17.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "20.00"),
                ("Combo Simples", TipoVariacao.combo, "27.00"),
                ("Combo Duplo", TipoVariacao.combo, "30.00"),
            ],
        ),
        (
            "ARRETADO",
            "Pao de hot-dog, maionese, salsicha perdigao, queijo mucarela, molho de tomate caseiro, carne moida temperada, milho, vinagrete, batata palha e parmesao.",
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "21.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "24.00"),
                ("Combo Simples", TipoVariacao.combo, "31.00"),
                ("Combo Duplo", TipoVariacao.combo, "34.00"),
            ],
        ),
        (
            "PARAIBANO",
            "Pao de hot-dog, maionese, salsicha perdigao, carne moida temperada, milho, vinagrete, parmesao e ovo de codorna.",
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "21.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "24.00"),
                ("Combo Simples", TipoVariacao.combo, "31.00"),
                ("Combo Duplo", TipoVariacao.combo, "34.00"),
            ],
        ),
        (
            "BIXIN",
            "Pao de hot-dog, maionese, salsicha perdigao, molho de tomate caseiro e batata palha.",
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "11.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "14.00"),
                ("Combo Simples", TipoVariacao.combo, "21.00"),
                ("Combo Duplo", TipoVariacao.combo, "24.00"),
            ],
        ),
        (
            "VEGETARIANO",
            "Pao de hot-dog, maionese, queijo mucarela, molho de tomate caseiro, milho, vinagrete, batata palha, parmesao e ovo de codorna.",
            [
                ("Simples", TipoVariacao.normal, "20.00"),
                ("Combo", TipoVariacao.combo, "30.00"),
            ],
        ),
    ]

    for nome, descricao, variacoes in produtos:
        criar_produto(
            db,
            subcategoria=subcategoria,
            unidades=unidades,
            nome=nome,
            descricao=descricao,
            variacoes=variacoes,
            adicionais=adicionais_hot_dog(),
        )


def seed_acompanhamentos(db: Session, unidades: list[Unidade]) -> None:
    """Cadastra acompanhamentos usados nos combos."""
    subcategoria = criar_categoria_com_subcategoria(db, "Acompanhamentos", "Extras")
    acompanhamentos = [
        ("Batata Chips", "8.00"),
        ("Batata Chips G", "14.00"),
        ("Brownie Tradicional", "8.00"),
        ("Brownie Recheado", "10.00"),
    ]
    for nome, preco in acompanhamentos:
        criar_produto(
            db,
            subcategoria=subcategoria,
            unidades=unidades,
            nome=nome,
            descricao="Acompanhamento para pedido ou combo.",
            variacoes=[("Unico", TipoVariacao.normal, preco)],
            pontos=0,
        )


def seed_smashdogs(db: Session, unidades: list[Unidade]) -> None:
    """Cadastra o cardapio Paraiba Smashdog."""
    subcategoria = criar_categoria_com_subcategoria(db, "Paraiba Smashdog", "Hamburgueres")
    produtos = [
        (
            "FACHEIRO",
            "Pao brioche, blend artesanal 120g, mucarela e maionese.",
            [
                ("1 Carne", TipoVariacao.normal, "29.00"),
                ("2 Carnes", TipoVariacao.normal, "36.00"),
                ("3 Carnes", TipoVariacao.normal, "43.00"),
                ("Combo 1 Carne", TipoVariacao.combo, "32.00"),
                ("Combo 2 Carnes", TipoVariacao.combo, "39.00"),
                ("Combo 3 Carnes", TipoVariacao.combo, "46.00"),
                ("Combo 4 Carnes", TipoVariacao.combo, "53.00"),
            ],
        ),
        (
            "MANDACARU",
            "Pao brioche, blend artesanal 120g, mucarela, alface, tomate, cebola roxa e maionese.",
            [
                ("1 Carne", TipoVariacao.normal, "26.00"),
                ("2 Carnes", TipoVariacao.normal, "33.00"),
                ("3 Carnes", TipoVariacao.normal, "40.00"),
                ("4 Carnes", TipoVariacao.normal, "47.00"),
                ("Combo 1 Carne", TipoVariacao.combo, "36.00"),
                ("Combo 2 Carnes", TipoVariacao.combo, "43.00"),
                ("Combo 3 Carnes", TipoVariacao.combo, "50.00"),
                ("Combo 4 Carnes", TipoVariacao.combo, "57.00"),
            ],
        ),
        (
            "XIQUE-XIQUE",
            "Pao australiano, blend artesanal 120g, mucarela, bacon e maionese.",
            [
                ("1 Carne", TipoVariacao.normal, "27.00"),
                ("2 Carnes", TipoVariacao.normal, "34.00"),
                ("3 Carnes", TipoVariacao.normal, "41.00"),
                ("4 Carnes", TipoVariacao.normal, "48.00"),
                ("Combo 1 Carne", TipoVariacao.combo, "37.00"),
                ("Combo 2 Carnes", TipoVariacao.combo, "44.00"),
                ("Combo 3 Carnes", TipoVariacao.combo, "51.00"),
                ("Combo 4 Carnes", TipoVariacao.combo, "58.00"),
            ],
        ),
    ]

    for nome, descricao, variacoes in produtos:
        criar_produto(
            db,
            subcategoria=subcategoria,
            unidades=unidades,
            nome=nome,
            descricao=descricao,
            variacoes=variacoes,
            adicionais=adicionais_smashdog(),
        )


def run() -> None:
    """Executa limpeza e carga inicial em uma transacao unica."""
    db = SessionLocal()
    try:
        limpar_banco(db)
        permissoes = criar_permissoes(db)
        unidades = criar_unidades(db)
        criar_blog(db)
        criar_cliente(db)
        criar_usuario(db, unidades[0], permissoes)
        seed_hot_dogs(db, unidades)
        seed_acompanhamentos(db, unidades)
        seed_smashdogs(db, unidades)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Banco limpo e seeds aplicados com sucesso.")
