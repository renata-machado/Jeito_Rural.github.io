from datetime import date
from fastapi import APIRouter, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.endereco_model import Endereco
from models.usuario_model import Usuario
from repositories.usuario_repo import UsuarioRepo
from util.auth import NOME_COOKIE_AUTH, criar_token, obter_hash_senha
from util.cookies import adicionar_cookie_auth
from util.mensagens import adicionar_mensagem_erro

router = APIRouter()

templates = Jinja2Templates(directory="templates")

@router.get("/")
async def get_root(request: Request):
    usuario = request.state.usuario if hasattr(request.state, "usuario") else None
    if not usuario:
        return RedirectResponse("/entrar", status_code=status.HTTP_303_SEE_OTHER)
    if usuario.perfil == 1:
        return RedirectResponse("/cliente", status_code=status.HTTP_303_SEE_OTHER)
    if usuario.perfil == 2:
        return RedirectResponse("/vendedor", status_code=status.HTTP_303_SEE_OTHER)
    
@router.get("/entrar")
async def get_entrar(request: Request):
    return templates.TemplateResponse("pages/entrar.html", {"request": request})

@router.post("/post_entrar")
async def post_entrar(email: str = Form(...), senha: str = Form(...)):
    usuario = UsuarioRepo.checar_credenciais(email, senha)
    if usuario:
        # Assumindo que o retorno de checar_credenciais é uma tupla (id, nome, email, perfil, telefone)
        token = criar_token(usuario[1], usuario[2], usuario[3], usuario[4])  # Gerar o token JWT
        response = RedirectResponse(url=f"/", status_code=status.HTTP_303_SEE_OTHER)
        adicionar_cookie_auth(response, token)  # Adicionar o cookie com o token

        # Redirecionar o usuário com base no perfil
        if usuario[2] == 1:  # Perfil de cliente
            response = RedirectResponse(url="/cliente", status_code=status.HTTP_303_SEE_OTHER)
        elif usuario[2] == 2:  # Perfil de vendedor
            response = RedirectResponse(url="/vendedor", status_code=status.HTTP_303_SEE_OTHER)

        return response
    else:
        response = RedirectResponse("/entrar", status.HTTP_303_SEE_OTHER)
        adicionar_mensagem_erro(response, "Credenciais inválidas! Cheque os valores digitados e tente novamente.")
        return response
        # raise HTTPException(status_code=401, detail="Usuário ou senha inválidos.")
    
@router.get("/cadastrar")
async def get_cadastrar(request: Request):
    estadobr=[{"value": "am", "label": "Amazonas"},
    {"value": "ac", "label":"Acre"},
    {"value": "ro","label": "Rondônia"},
    {"value": "rr","label": "Roraima"},
    {"value": "ap","label": "Amapá"},
    {"value": "pa","label": "Pará"},
    {"value": "to","label": "Tocantins"},
    {"value": "ma","label": "Maranhão"},
    {"value": "pi","label": "Piauí"},
    {"value": "ce","label": "Ceará"},
    {"value": "rn","label": "Rio Grande do Norte"},
    {"value": "pb","label": "Paraíba"},
    {"value": "pe","label": "Pernambuco"},
    {"value": "al","label": "Alagoas"},
    {"value": "se","label": "Sergipe"},
    {"value": "ba","label": "Bahia"},
    {"value": "mt","label": "Mato Grosso"},
    {"value": "ms","label": "Mato Grosso do Sul"},
    {"value": "go","label": "Goiás"},
    {"value": "df","label": "Distrito Federal"},
    {"value": "mg","label": "Minas Gerais"},
    {"value": "es","label": "Espírito Santo"},
    {"value": "rj","label": "Rio de Janeiro"},
    {"value": "sp","label": "São Paulo"},
    {"value": "pr","label": "Paraná"},
    {"value": "sc","label": "Santa Catarina"},
    {"value": "rs","label": "Rio Grande do Sul"}]

    listperfil=[
        {"value": "1", "label": "Cliente"},
        {"value": "2", "label": "Produtor"},
    ]
    return templates.TemplateResponse("pages/cadastrar.html", {"request": request, "estadobr":estadobr, "listperfil": listperfil})

@router.post("/post_cadastrar")
async def post_cadastrar(
    nome: str = Form(...),
    sobrenome: str = Form(...),
    email: str = Form(...),
    telefone: str = Form(...),
    senha: str = Form(...),
    confsenha: str = Form(...),
    perfil: int = Form(...),
    cep: str = Form(...),
    numero: str = Form(...),
    complemento: str = Form(),
    endereco: str = Form(...),
    cidade: str = Form(...),
    uf: str = Form(...)
    ):
    if senha != confsenha:
        print ("senha não confere", senha, " ", confsenha)
        return RedirectResponse("/cadastrar", status_code=status.HTTP_303_SEE_OTHER)
    senha_hash = obter_hash_senha(senha)
    usuario = Usuario(
        nome=nome,
        sobrenome=sobrenome,
        email=email,
        telefone=telefone,
        senha=senha_hash,
        perfil=perfil)
    usuario_id= (UsuarioRepo.inserir(usuario)).id
    print(usuario_id)

    endereco = Endereco(
        id_usuario=usuario_id,
        endereco_cep= cep,
        endereco_numero = numero,
        endereco_complemento=complemento,
        endereco_endereco=endereco,
        endereco_cidade = cidade,
        endereco_uf=uf  )

    UsuarioRepo.inserir_endereco(endereco)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)



@router.get("/sobreNos")
async def get_sobreNos(request: Request):
    return templates.TemplateResponse("pages/sobreNos.html", {"request": request})


@router.get("/ajuda")
async def get_ajuda(request: Request):
    return templates.TemplateResponse("pages/ajuda.html", {"request": request})


@router.get("/ajudaLogado")
async def get_ajudaLogado(request: Request):
    return templates.TemplateResponse("pages/ajudaLogado.html", {"request": request})

@router.get("/perfilVendedor")
async def get_ajudaLogado(request: Request):
    return templates.TemplateResponse("pages/vendedor/tela_perfil_vendedor.html", {"request": request})