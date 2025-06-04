import typer
from .services.svn_service import SvnService
from .services.redmine_service import RedmineService
from dotenv import load_dotenv
import os

app = typer.Typer()
load_dotenv()

SVN_USER = os.getenv("SVN_USER")
SVN_PASS = os.getenv("SVN_PASS")
REPO_LOCAL_PATH = os.getenv("REPO_LOCAL_PATH")

@app.command("repositorios")
def checkout(path: str = typer.Option(None, help="Caminho local do repositório SVN (opcional)")):
    """
    Verifica alterações locais no repositório.
    Faz checkout se necessário.
    """
    url_repo = None

    if path is None:
        repos_file = os.path.join("data", "repositorios.txt")
        if not os.path.exists(repos_file):
            print("❌ Arquivo 'repositorios.txt' não encontrado em ./data/")
            raise typer.Exit(code=1)

        with open(repos_file, "r", encoding="utf-8") as f:
            repos = [linha.strip() for linha in f if linha.strip()]

        if not repos:
            print("❌ Nenhum repositório listado em 'repositorios.txt'.")
            raise typer.Exit(code=1)

        print("📁 Repositórios disponíveis:")
        for i, url in enumerate(repos, 1):
            print(f"{i}) {url}")

        escolha = typer.prompt("Escolha um número")
        try:
            idx = int(escolha) - 1
            if idx < 0 or idx >= len(repos):
                raise ValueError()
            url_repo = repos[idx]  # <- URL real do repositório SVN
            nome_repo = url_repo.rstrip("/").split("/")[-1]  # <- Apenas o nome final
        except ValueError:
            print("❌ Escolha inválida.")
            raise typer.Exit(code=1)

        if not REPO_LOCAL_PATH:
            print("❌ Variável REPO_LOCAL_PATH não definida no .env")
            raise typer.Exit(code=1)

        path = os.path.join(REPO_LOCAL_PATH, nome_repo)

    print(f"🔍 Verificando alterações em: {path}")
    service = SvnService(SVN_USER, SVN_PASS)

    if not os.path.exists(path):
        if not url_repo:
            print("❌ Para repositórios não clonados, o caminho deve vir de uma URL do repositorios.txt")
            raise typer.Exit(code=1)
        print("📥 Repositório ainda não clonado. Fazendo checkout...")
        service.checkout(url_repo, path)

    service.checar_alteracoes(path)
    
@app.command('tarefas')
def tarefas():
    """
    Lista tarefas abertas do Redmine.
    """
    redmine = RedmineService()
    issues = redmine.buscar_issues()
    redmine.mostrar_issues(issues)

if __name__ == "__main__":
    app()

@app.command('arquivos')
def arquivos(filtro: str = typer.Option("", help="Filtro por nome de arquivo")):
    """
    Lista os arquivos de um repositório SVN local escolhido a partir do menu de repositórios.
    """
    repos_file = os.path.join("data", "repositorios.txt")
    if not os.path.exists(repos_file):
        print("❌ Arquivo 'repositorios.txt' não encontrado.")
        raise typer.Exit(code=1)

    with open(repos_file, "r", encoding="utf-8") as f:
        repos = [linha.strip() for linha in f if linha.strip()]

    if not repos:
        print("❌ Nenhum repositório listado.")
        raise typer.Exit(code=1)

    print("📁 Repositórios disponíveis:")
    for i, url in enumerate(repos, 1):
        print(f"{i}) {url}")

    escolha = typer.prompt("Escolha um número")
    try:
        idx = int(escolha) - 1
        if idx < 0 or idx >= len(repos):
            raise ValueError()
        url_repo = repos[idx]
        nome_repo = url_repo.rstrip("/").split("/")[-1]
    except ValueError:
        print("❌ Escolha inválida.")
        raise typer.Exit(code=1)

    base_path = os.getenv("REPO_LOCAL_PATH")
    if not base_path:
        print("❌ REPO_LOCAL_PATH não definido no .env")
        raise typer.Exit(code=1)

    full_path = os.path.join(base_path, nome_repo)

    service = SvnService(SVN_USER, SVN_PASS)
    service.listar_arquivos(full_path, filtro)