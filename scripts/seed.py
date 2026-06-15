"""Limpa o banco e popula dados iniciais reais para desenvolvimento."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from src.blog.model import Blog, TipoNoticiaPromocao
from src.clientes.model import Cliente
from src.database import Base, SessionLocal
from src.pedidos.model import (
    FormaPagamento,
    ItemPedido,
    ItemPedidoAdicional,
    Pedido,
    StatusItemPedido,
    StatusPedido,
)
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


def criar_clientes(db: Session) -> list[Cliente]:
    """Cadastra clientes iniciais para testes manuais e pedidos fake."""
    dados_clientes = [
        ("Daniel Ferreira", "61999990001", "daniel.ferreira@example.com", 12),
        ("Mariana Alves", "61999990002", "mariana.alves@example.com", 6),
        ("Pedro Lima", "61999990003", "pedro.lima@example.com", 3),
        ("Ana Beatriz", "61999990004", "ana.beatriz@example.com", 9),
    ]
    clientes = [
        Cliente(
            nome=nome,
            telefone=telefone,
            email=email,
            pontos_fidelidade=pontos,
            ativo=True,
        )
        for nome, telefone, email, pontos in dados_clientes
    ]
    db.add_all(clientes)
    db.flush()
    return clientes


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


# pylint: disable=too-many-arguments
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
            (
                "Pao de hot-dog, maionese, salsicha perdigao, queijo mucarela, "
                "molho de tomate caseiro, milho e batata palha."
            ),
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "17.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "20.00"),
                ("Combo Simples", TipoVariacao.combo, "27.00"),
                ("Combo Duplo", TipoVariacao.combo, "30.00"),
            ],
        ),
        (
            "ARRETADO",
            (
                "Pao de hot-dog, maionese, salsicha perdigao, queijo mucarela, "
                "molho de tomate caseiro, carne moida temperada, milho, "
                "vinagrete, batata palha e parmesao."
            ),
            [
                ("Simples - 1 Salsicha", TipoVariacao.normal, "21.00"),
                ("Duplo - 2 Salsichas", TipoVariacao.normal, "24.00"),
                ("Combo Simples", TipoVariacao.combo, "31.00"),
                ("Combo Duplo", TipoVariacao.combo, "34.00"),
            ],
        ),
        (
            "PARAIBANO",
            (
                "Pao de hot-dog, maionese, salsicha perdigao, carne moida "
                "temperada, milho, vinagrete, parmesao e ovo de codorna."
            ),
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
            (
                "Pao de hot-dog, maionese, queijo mucarela, molho de tomate "
                "caseiro, milho, vinagrete, batata palha, parmesao e ovo de codorna."
            ),
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


def _momento_pedido(dias_atras: int, hora: int, minuto: int) -> datetime:
    """Monta uma data fechada para pedidos fake do BI."""
    hoje = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
    return hoje - timedelta(days=dias_atras)


def _adicionais_do_item(produto: Produto, limite: int) -> list[ItemPedidoAdicional]:
    """Seleciona alguns adicionais do produto para variar o ticket dos pedidos fake."""
    adicionais = []
    for adicional in produto.adicionais[:limite]:
        adicionais.append(
            ItemPedidoAdicional(
                adicional_id=adicional.id,
                nome=adicional.nome,
                preco=adicional.preco,
            )
        )
    return adicionais


def _criar_item_pedido(
    variacao: ProdutoVariacao,
    quantidade: int,
    adicionais_limite: int,
) -> ItemPedido:
    """Cria um item de pedido pago com snapshot de produto, variacao e adicionais."""
    produto = variacao.produto
    item = ItemPedido(
        produto_variacao_id=variacao.id,
        produto_id=produto.id,
        produto_nome=produto.nome,
        produto_variacao_nome=variacao.nome,
        quantidade=quantidade,
        preco_unitario=variacao.preco,
        status=StatusItemPedido.entregue,
        lote=1,
    )
    item.adicionais = _adicionais_do_item(produto, adicionais_limite)
    return item


def _total_item(item: ItemPedido) -> Decimal:
    adicionais = sum((adicional.preco for adicional in item.adicionais), Decimal("0"))
    return Decimal(item.quantidade) * (item.preco_unitario + adicionais)


def _criar_pedido_fake(
    db: Session,
    *,
    unidade: Unidade,
    cliente: Cliente | None,
    momento: datetime,
    itens: list[ItemPedido],
    forma_pagamento: FormaPagamento,
    desconto: Decimal = Decimal("0.00"),
) -> Pedido:
    """Cria um pedido pago para popular indicadores do BI."""
    subtotal = sum((_total_item(item) for item in itens), Decimal("0.00"))
    pedido = Pedido(
        unidade_id=unidade.id,
        cliente_id=cliente.id if cliente else None,
        nome_comanda=cliente.nome if cliente else "Cliente Balcao",
        status=StatusPedido.pago,
        subtotal=subtotal,
        desconto_fidelidade=min(desconto, subtotal),
        total=max(subtotal - desconto, Decimal("0.00")),
        forma_pagamento=forma_pagamento,
        pontos_fidelidade_utilizados=12 if desconto else 0,
        pontos_fidelidade_creditados=True,
        created_at=momento,
        fechado_em=momento + timedelta(minutes=18),
    )
    pedido.itens = itens
    db.add(pedido)
    return pedido


def seed_pedidos_bi(db: Session, unidades: list[Unidade], clientes: list[Cliente]) -> None:
    """Cadastra pedidos pagos fake para demonstrar a tela de BI."""
    db.flush()
    variacoes = db.query(ProdutoVariacao).order_by(ProdutoVariacao.id.asc()).all()
    if len(variacoes) < 8:
        return

    pedidos = [
        (
            4,
            18,
            10,
            0,
            0,
            FormaPagamento.pix,
            Decimal("0.00"),
            [(0, 2, 1), (5, 1, 0)],
        ),
        (
            4,
            19,
            35,
            0,
            1,
            FormaPagamento.credito,
            Decimal("0.00"),
            [(1, 1, 2), (6, 2, 0)],
        ),
        (3, 20, 5, 1, 2, FormaPagamento.debito, Decimal("0.00"), [(2, 2, 1)]),
        (
            3,
            21,
            15,
            1,
            None,
            FormaPagamento.pix,
            Decimal("0.00"),
            [(10, 1, 1), (7, 1, 0)],
        ),
        (2, 18, 45, 0, 3, FormaPagamento.dinheiro, Decimal("17.00"), [(3, 2, 2)]),
        (
            2,
            19,
            20,
            1,
            0,
            FormaPagamento.credito,
            Decimal("0.00"),
            [(4, 1, 1), (8, 2, 0)],
        ),
        (1, 20, 50, 0, 1, FormaPagamento.pix, Decimal("0.00"), [(11, 2, 1)]),
        (
            1,
            21,
            25,
            1,
            2,
            FormaPagamento.debito,
            Decimal("0.00"),
            [(12, 1, 2), (9, 1, 0)],
        ),
        (
            18,
            18,
            15,
            0,
            0,
            FormaPagamento.pix,
            Decimal("0.00"),
            [(0, 1, 0), (5, 1, 0)],
        ),
        (18, 19, 40, 1, 1, FormaPagamento.credito, Decimal("0.00"), [(1, 1, 1)]),
        (
            17,
            20,
            30,
            0,
            2,
            FormaPagamento.debito,
            Decimal("0.00"),
            [(2, 1, 1), (6, 1, 0)],
        ),
        (16, 21, 5, 1, None, FormaPagamento.dinheiro, Decimal("0.00"), [(10, 1, 0)]),
        (36, 18, 20, 0, 0, FormaPagamento.pix, Decimal("0.00"), [(0, 1, 0)]),
        (35, 19, 10, 1, 1, FormaPagamento.credito, Decimal("0.00"), [(1, 1, 0)]),
        (34, 20, 45, 0, 2, FormaPagamento.debito, Decimal("0.00"), [(5, 1, 0)]),
        (33, 21, 30, 1, 3, FormaPagamento.pix, Decimal("0.00"), [(10, 1, 1)]),
    ]

    for dias, hora, minuto, unidade_idx, cliente_idx, pagamento, desconto, itens_dados in pedidos:
        itens = [
            _criar_item_pedido(
                variacoes[variacao_idx % len(variacoes)],
                quantidade,
                adicionais_limite,
            )
            for variacao_idx, quantidade, adicionais_limite in itens_dados
        ]
        _criar_pedido_fake(
            db,
            unidade=unidades[unidade_idx],
            cliente=clientes[cliente_idx] if cliente_idx is not None else None,
            momento=_momento_pedido(dias, hora, minuto),
            itens=itens,
            forma_pagamento=pagamento,
            desconto=desconto,
        )


def run() -> None:
    """Executa limpeza e carga inicial em uma transacao unica."""
    db = SessionLocal()
    try:
        limpar_banco(db)
        permissoes = criar_permissoes(db)
        unidades = criar_unidades(db)
        criar_blog(db)
        clientes = criar_clientes(db)
        criar_usuario(db, unidades[0], permissoes)
        seed_hot_dogs(db, unidades)
        seed_acompanhamentos(db, unidades)
        seed_smashdogs(db, unidades)
        seed_pedidos_bi(db, unidades, clientes)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
    print("Banco limpo e seeds aplicados com sucesso.")
