from flet import *
from flet import Column as Diabo
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import bcrypt

# Configuração do SQLAlchemy
DATABASE_URL = "sqlite:///dk_card.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criando uma classe base para modelos
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

# Definição da classe Usuario antes de criar as tabelas
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    senha_hash = Column(String)

    def verificar_senha(self, senha):
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha_hash.encode('utf-8'))

    def formatar_dados(self):
        return [
            Text(f"Nome: {self.nome}", size=15, color=Colors.WHITE),
            Text(f"E-mail: {self.email}", size=15, color=Colors.WHITE),
        ]

class Cartao(ModeloBase):
    __tablename__ = "cartoes"
    nome = Column(String, index=True)
    cpf = Column(String, index=True)
    numero = Column(String, index=True)
    data_vencimento = Column(String)
    cvc = Column(String)

    def formatar_dados(self):
        return [
            Text(f"Nome: {self.nome}", size=15, color=Colors.WHITE),
            Text(f"CPF: {self.cpf}", size=15, color=Colors.WHITE),
            Text(f"Número: {self.numero}", size=15, color=Colors.WHITE),
            Text(f"Vencimento: {self.data_vencimento}", size=15, color=Colors.WHITE),
            Text(f"CVC: {self.cvc}", size=15, color=Colors.WHITE),
        ]

# Após definir todos os modelos, criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

class TransacaoBase:
    def descricao(self):
        pass

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

class AppControlador:
    def __init__(self):
        self.db = SessionLocal()
        self.cartao_principal = None
        self.usuario_atual = None

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

    def obter_cartao_principal(self):
        if not self.cartao_principal:
            self.cartao_principal = self.db.query(Cartao).first()
        return self.cartao_principal

    def registrar_usuario(self, nome, email, senha):
        try:
            senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash.decode('utf-8'))
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
            print(f"Usuário {email} registrado com sucesso")
            return usuario
        except Exception as ex:
            print(f"Erro ao registrar usuário: {ex}")
            self.db.rollback()
            raise

    def autenticar_usuario(self, email, senha):
        try:
            usuario = self.db.query(Usuario).filter(Usuario.email == email).first()
            if usuario and usuario.verificar_senha(senha):
                self.usuario_atual = usuario
                print(f"Usuário {email} autenticado com sucesso")
                return True
            else:
                print("Falha na autenticação: E-mail ou senha incorretos")
                return False
        except Exception as ex:
            print(f"Erro ao autenticar usuário: {ex}")
            raise

    def obter_usuario_atual(self):
        return self.usuario_atual

    def fechar_conexao(self):
        self.db.close()

def main(page: Page):
    controlador = AppControlador()
    page.title = "DK - Card's"
    page.window.height = 600
    page.window.width = 300
    page.theme_mode = "Dark"

    # Função para ir para a tela inicial
    def ir_para_inicio():
        login.visible = False
        cadastro.visible = False
        inicio.visible = True
        cartoes_view.visible = False
        novo.visible = False
        botao_menu.visible = True
        atualizar_cartao_principal()
        page.update()

    # Função para criar tela de login
    def criar_tela_login():
        email_field = TextField(label="E-mail", width=280)
        senha_field = TextField(label="Senha", width=280, password=True, can_reveal_password=True)

        def on_login_click(e):
            print("Botão de login clicado")
            email = email_field.value
            senha = senha_field.value
            if controlador.autenticar_usuario(email, senha):
                page.snack_bar = SnackBar(Text("Login bem-sucedido!"), bgcolor=Colors.GREEN)
                page.snack_bar.open = True
                ir_para_inicio()
            else:
                page.snack_bar = SnackBar(Text("E-mail ou senha incorretos."), bgcolor=Colors.RED)
                page.snack_bar.open = True
            page.update()

        def ir_para_cadastro(e):
            login.visible = False
            cadastro.visible = True
            botao_menu.visible = False
            page.update()

        login = Diabo(
            controls=[
                Image(src="logo.png",width=135, height=135, fit=ImageFit.CONTAIN),
                Text("Login", size=30),
                email_field,
                senha_field,
                ElevatedButton("Entrar", on_click=on_login_click),
                TextButton("Não tem uma conta? Cadastre-se", on_click=ir_para_cadastro)
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            alignment=MainAxisAlignment.CENTER,
        )
        return login

    # Função para criar tela de cadastro
    def criar_tela_cadastro():
        nome_field = TextField(label="Nome Completo", width=280)
        email_field = TextField(label="E-mail", width=280)
        senha_field = TextField(label="Senha", width=280, password=True, can_reveal_password=True)
        confirmar_senha_field = TextField(label="Confirmar Senha", width=280, password=True, can_reveal_password=True)

        def on_cadastrar_click(e):
            print("Botão de cadastro clicado")
            nome = nome_field.value
            email = email_field.value
            senha = senha_field.value
            confirmar_senha = confirmar_senha_field.value

            if senha != confirmar_senha:
                page.snack_bar = SnackBar(Text("As senhas não coincidem."), bgcolor=Colors.RED)
                page.snack_bar.open = True
                page.update()
                return

            try:
                controlador.registrar_usuario(nome, email, senha)
                page.snack_bar = SnackBar(Text("Cadastro realizado com sucesso!"), bgcolor=Colors.GREEN)
                page.snack_bar.open = True
                ir_para_login(None)
            except Exception as ex:
                page.snack_bar = SnackBar(Text(f"Erro ao cadastrar: {ex}"), bgcolor=Colors.RED)
                page.snack_bar.open = True
            page.update()

        def ir_para_login(e):
            cadastro.visible = False
            login.visible = True
            botao_menu.visible = False
            page.update()

        cadastro = Diabo(
            controls=[
                Text("Cadastro", size=30),
                nome_field,
                email_field,
                senha_field,
                confirmar_senha_field,
                ElevatedButton("Cadastrar", on_click=on_cadastrar_click),
                TextButton("Já tem uma conta? Faça login", on_click=ir_para_login)
            ],
            horizontal_alignment=CrossAxisAlignment.CENTER,
            alignment=MainAxisAlignment.CENTER,
            visible=False
        )
        return cadastro

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
        visible=False
    )

    # Formulário para adicionar novo cartão
    nome_field = TextField(label="Nome Completo", width=280)
    cpf_field = TextField(label="CPF do Titular", width=280)
    numero_field = TextField(label="Número do Cartão", width=280)
    vencimento_field = TextField(label="Data Vencimento", width=135)
    cvc_field = TextField(label="CVC", width=135)

    def on_avancar_click(e):
        print("Botão de adicionar cartão clicado")
        nome = nome_field.value
        cpf = cpf_field.value
        numero = numero_field.value
        vencimento = vencimento_field.value
        cvc = cvc_field.value

        controlador.adicionar_cartao(nome, cpf, numero, vencimento, cvc)

        # Limpar campos
        nome_field.value = ""
        cpf_field.value = ""
        numero_field.value = ""
        vencimento_field.value = ""
        cvc_field.value = ""
        page.update()

        novo.visible = False
        cartoes_view.visible = True
        atualizar_lista_cartoes()
        page.update()

    novo = Diabo(
        controls=[
            Image(src="logo.png",width=135, height=135, fit=ImageFit.CONTAIN),
            Text("Insira os dados para adicionar cartão", size=20),
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
                content=Text("Seus cartões aqui", size=30, color=Colors.BLUE_600, weight="bold"),
                alignment=alignment.center,
                padding=padding.symmetric(horizontal=10, vertical=5),
                margin=padding.symmetric(vertical=10)
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
                content=Text("Seus cartões aqui", size=30, color=Colors.BLUE_600, weight="bold"),
                alignment=alignment.center,
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

    # Função para atualizar o cartão principal
    def atualizar_cartao_principal():
        cartao_principal = controlador.obter_cartao_principal()

        cartao_principal_container.controls.clear()
        transacoes_container.controls.clear()

        if cartao_principal:
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

    # Função menu
    def menu(key):
        if not controlador.obter_usuario_atual():
            login.visible = True
            cadastro.visible = False
            inicio.visible = False
            cartoes_view.visible = False
            novo.visible = False
            page.update()
            return

        if key == "Inicio":
            ir_para_inicio()
        elif key == "Cartões":
            inicio.visible = False
            cartoes_view.visible = True
            novo.visible = False
            atualizar_lista_cartoes()
            page.update()
        elif key == "Novo":
            inicio.visible = False
            cartoes_view.visible = False
            novo.visible = True
            page.update()

    # Criar as telas de login e cadastro
    login = criar_tela_login()
    cadastro = criar_tela_cadastro()

    # Menu inferior
    botao_menu = BottomAppBar(
        content=Row(
            controls=[
                IconButton(icon=icons.HOME, on_click=lambda _: menu("Inicio")),
                IconButton(icon=icons.ADD_BOX, on_click=lambda _: menu("Novo")),
                IconButton(icon=icons.VIEW_LIST, on_click=lambda _: menu("Cartões"))
            ],
            alignment=MainAxisAlignment.CENTER
        ), 
        visible= False
    )

    # Adicionar os componentes à página
    page.add(login, cadastro, inicio, cartoes_view, novo)
    page.add(botao_menu)

    # Função para checar autenticação
    def checar_autenticacao():
        if controlador.obter_usuario_atual():
            ir_para_inicio()
        else:
            login.visible = True
            cadastro.visible = False
            inicio.visible = False
            cartoes_view.visible = False
            novo.visible = False
            botao_menu.visible = False
            page.update()

    # Checar autenticação ao iniciar
    checar_autenticacao()

    # Fechar a sessão ao fechar a aplicação
    def on_close(e):
        controlador.fechar_conexao()

    page.on_close = on_close
    page.update()

# Iniciar a aplicação
app(target=main)
