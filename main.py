from flet import *

def main(page: Page):
    page.title = "DK - Card's"
    page.window.height = 600
    page.window.width = 300
    page.theme_mode = "Dark"
    def menu(key):
        if key == "Inicio":
            page.controls[0].visible = True
            page.controls[1].visible = False
            page.controls[2].visible = False
        elif key == "Cartões":
            page.controls[0].visible = False
            page.controls[1].visible = True
            page.controls[2].visible = False
        elif key == "Novo":
            page.controls[0].visible = False
            page.controls[1].visible = False
            page.controls[2].visible = True
        page.update()

    inicio = Column(controls=[
        Text("Bem vindo à carteira DK - Card's", size=30)
    ], visible=True)
    
    cartoes = Column(controls=[
        Text("Seus cartões aqui", size=30)
    ], visible=False)
    
    novo = Column(controls=[
        Text("Insira os dados para adicionar cartão", size=20),
        TextField(label="Nome Completo", width=280),
        TextField(label="CPF do Títular", width=280),
        TextField(label="Número do Cartão", width=280),
        Row(
            [
                TextField(label="Data Vencimento", width=135), 
                TextField(label="CVC", width=135)
            ], 
            alignment=MainAxisAlignment.CENTER
        ),
        ElevatedButton("Avançar")
    ],
    horizontal_alignment=CrossAxisAlignment.CENTER,
    alignment=MainAxisAlignment.CENTER,
    visible=False)
    
    page.add(inicio, cartoes, novo)

    botao_menu = BottomAppBar(content=Row(
        controls=[
            IconButton(icon=icons.HOME, on_click=lambda _: menu("Inicio")),
            IconButton(icon=icons.ADD_BOX, on_click=lambda _: menu("Novo")),
            IconButton(icon=icons.VIEW_LIST, on_click=lambda _: menu("Cartões"))
        ],
        alignment=MainAxisAlignment.CENTER
    ))
    
    page.add(botao_menu)
    page.update()  

app(target=main)
