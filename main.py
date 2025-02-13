from flet import *
from flet import Column as Diabo
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuração do SQLAlchemy
DATABASE_URL = "sqlite:///cartoes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criando uma classe base abstrata para modelos
Base = declarative_base()

class ModeloBase(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)

    def save(self, db: Session):
        db.add(self)
        db.commit()
        db.refresh(self)

    def delete(self, db: Session):
        db.delete(self)
        db.commit()

# Classe Cartao que herda de ModeloBase
class Cartao(ModeloBase):
    __tablename__ = "cartoes"

    nome = Column(String, index=True)
    cpf = Column(String, index=True)
    numero = Column(String, index=True)
    data_vencimento = Column(String)
    cvc = Column(String)

    # Método para formatar os dados do cartão
    def formatar_dados(self):
        return [
            Text(f"Nome: {self.nome}", size=15, color=Colors.WHITE),
            Text(f"CPF: {self.cpf}", size=15, color=Colors.WHITE),
            Text(f"Número: {self.numero}", size=15, color=Colors.WHITE),
            Text(f"Vencimento: {self.data_vencimento}", size=15, color=Colors.WHITE),
            Text(f"CVC: {self.cvc}", size=15, color=Colors.WHITE),
        ]

# Classe abstrata para Transação
class TransacaoBase:
    def descricao(self):
        pass

# Subclasses de TransacaoBase
class Compra(TransacaoBase):
    def __init__(self, descricao, valor):
        self.descricao_transacao = descricao
        self.valor = valor

    def descricao(self):
        return f"Compra: {self.descricao_transacao} - R$ {self.valor:.2f}"

class Pagamento(TransacaoBase):
    def __init__(self, descricao, valor):
        self.descricao_transacao = descricao
        self.valor = valor

    def descricao(self):
        return f"Pagamento: {self.descricao_transacao} - R$ {self.valor:.2f}"

Base.metadata.create_all(bind=engine)

# Controladora da aplicação
class AppControlador:
    def __init__(self):
        self.db = SessionLocal()
        self.cartao_principal = None

    def adicionar_cartao(self, nome, cpf, numero, data_vencimento, cvc):
        cartao = Cartao(
            nome=nome,
            cpf=cpf,
            numero=numero,
            data_vencimento=data_vencimento,
            cvc=cvc
        )
        cartao.save(self.db)
        return cartao

    def listar_cartoes(self):
        return self.db.query(Cartao).all()

    def buscar_cartao(self, cartao_id):
        return self.db.query(Cartao).filter(Cartao.id == cartao_id).first()

    def obter_cartao_principal(self):
        if not self.cartao_principal:
            self.cartao_principal = self.db.query(Cartao).first()
        return self.cartao_principal

    def fechar_conexao(self):
        self.db.close()

# Função principal do Flet
def main(page: Page):
    # Instanciar o controlador da aplicação
    controlador = AppControlador()

    # Configurações da página
    page.title = "DK - Card's"
    page.window.height = 600
    page.window.width = 300
    page.theme_mode = "Dark"

    def menu(key):
        if key == "Inicio":
            atualizar_cartao_principal()
            inicio.visible = True
            cartoes_view.visible = False
            novo.visible = False
        elif key == "Cartões":
            inicio.visible = False
            cartoes_view.visible = True
            novo.visible = False
            atualizar_lista_cartoes()
        elif key == "Novo":
            inicio.visible = False
            cartoes_view.visible = False
            novo.visible = True
        page.update()

    def atualizar_cartao_principal():
        cartao_principal = controlador.obter_cartao_principal()

        cartao_principal_container.controls.clear()
        transacoes_container.controls.clear()

        if cartao_principal:
            # Usando encapsulamento para formatar os dados do cartão
            dados_cartao = cartao_principal.formatar_dados()
            cartao_principal_container.controls.append(
                Container(
                    content=Diabo(
                        controls=dados_cartao,
                        alignment=MainAxisAlignment.START,
                        horizontal_alignment=CrossAxisAlignment.START,
                    ),
                    bgcolor=Colors.BLUE_700,
                    border_radius=10,
                    padding=10,
                    margin=5,
                    alignment=alignment.center
                )
            )

            # Lista de transações fictícias usando polimorfismo
            transacoes = [
                Compra("Supermercado", 150.00),
                Pagamento("Fatura Cartão", 300.00),
                Compra("Recarga Celular", 50.00),
                Compra("Compra Online", 200.00),
            ]

            transacoes_container.controls.append(
                Text("Transações Recentes", size=20, color=Colors.BLUE_600, weight="bold")
            )

            for transacao in transacoes:
                descricao_transacao = transacao.descricao()
                transacoes_container.controls.append(
                    Text(descricao_transacao, size=15, color=Colors.WHITE)
                )
        else:
            cartao_principal_container.controls.append(
                Text("Nenhum cartão encontrado.", size=15, color=Colors.RED)
            )
        page.update()

    # Definição dos containers
    cartao_principal_container = Diabo(controls=[], visible=True)
    transacoes_container = Diabo(controls=[], visible=True)

    inicio = Diabo(
        controls=[
            Container(
                content=Text("Bem-vindo a DK - Cards", size=20, color=Colors.BLUE_600, weight="bold"),
                alignment=alignment.center,
                padding=padding.symmetric(horizontal=10, vertical=5),
                margin=padding.symmetric(vertical=10)
            ),
            cartao_principal_container,
            transacoes_container,
        ],
        visible=True
    )

    # Formulário para adicionar novo cartão
    nome_field = TextField(label="Nome Completo", width=280)
    cpf_field = TextField(label="CPF do Titular", width=280)
    numero_field = TextField(label="Número do Cartão", width=280)
    vencimento_field = TextField(label="Data Vencimento", width=135)
    cvc_field = TextField(label="CVC", width=135)

    def on_avancar_click(e):
        # Recuperar dados do formulário
        nome = nome_field.value
        cpf = cpf_field.value
        numero = numero_field.value
        vencimento = vencimento_field.value
        cvc = cvc_field.value

        # Adicionar ao banco de dados usando o controlador
        controlador.adicionar_cartao(nome, cpf, numero, vencimento, cvc)

        # Limpar campos do formulário
        nome_field.value = ""
        cpf_field.value = ""
        numero_field.value = ""
        vencimento_field.value = ""
        cvc_field.value = ""
        page.update()

        # Atualizar exibição
        novo.visible = False
        cartoes_view.visible = True
        atualizar_lista_cartoes()
        page.update()

    novo = Diabo(
        controls=[
            Text("Insira os dados para adicionar cartão", size=20, color=Colors.BLUE_600, weight="bold"),
            nome_field,
            cpf_field,
            numero_field,
            Row(
                [vencimento_field, cvc_field],
                alignment=MainAxisAlignment.CENTER
            ),
            ElevatedButton("Avançar", on_click=on_avancar_click)
        ],
        horizontal_alignment=CrossAxisAlignment.CENTER,
        alignment=MainAxisAlignment.CENTER,
        visible=False
    )

    # Lista de cartões
    cartoes_view = ListView(
        controls=[
            Container(
                content=Text("Meus Cartões", size=20, color=Colors.BLUE_600, weight="bold")
            )
        ],
        visible=False,
        expand=True,
    )

    def atualizar_lista_cartoes():
        cartoes = controlador.listar_cartoes()

        cartoes_view.controls.clear()
        cartoes_view.controls.append(
            Container(
                content=Text("Meus cartões", size=30, color=Colors.BLUE_600, weight="bold"),
                padding=padding.symmetric(horizontal=10, vertical=5),
                margin=padding.symmetric(vertical=10)
            )
        )
        for cartao in cartoes:
            dados_cartao = cartao.formatar_dados()
            cartoes_view.controls.append(
                Container(
                    content=Diabo(
                        controls=dados_cartao,
                        alignment=MainAxisAlignment.START,
                        horizontal_alignment=CrossAxisAlignment.START,
                    ),
                    bgcolor=Colors.BLUE_700,
                    border_radius=10,
                    padding=10,
                    margin=5,
                    alignment=alignment.center
                )
            )
        cartoes_view.update()

    # Menu inferior
    botao_menu = BottomAppBar(
        content=Row(
            controls=[
                IconButton(icon=icons.HOME, on_click=lambda _: menu("Inicio")),
                IconButton(icon=icons.ADD_BOX, on_click=lambda _: menu("Novo")),
                IconButton(icon=icons.VIEW_LIST, on_click=lambda _: menu("Cartões"))
            ],
            alignment=MainAxisAlignment.CENTER
        )
    )

    # Adicionar elementos à página
    page.add(inicio, cartoes_view, novo)
    page.add(botao_menu)

    # Atualizar cartão principal ao iniciar
    atualizar_cartao_principal()

    # Fechar a sessão ao fechar a aplicação
    def on_close(e):
        controlador.fechar_conexao()

    page.on_close = on_close
    page.update()

# Iniciar a aplicação
app(target=main)
