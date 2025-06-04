import os
import re
from svn.remote import RemoteClient
from svn.local import LocalClient
from .spinner import Spinner
from .redmine_service import RedmineService
import time
import threading


class SvnService:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def checkout(self, repo_url, path):
        print(f"📥 Fazendo checkout de: {repo_url}")
        try:
            spinner = Spinner("🔄 Realizando checkout")
            spinner.start()
            RemoteClient(repo_url, username=self.user, password=self.password).checkout(path)
            spinner.stop()
            print(f"✅ Checkout concluído em: {path}")
        except Exception as e:
            spinner.stop()
            print(f"❌ Erro ao fazer checkout: {e}")

    def checar_alteracoes(self, path):
        print(f"🔍 Checando alterações em {path}...")

        if not os.path.exists(os.path.join(path, ".svn")):
            print("❌ Diretório não é um repositório SVN válido. Está faltando o checkout?")
            return

        try:
            client = LocalClient(path)
            status = client.status()

            alterações = [
                entry for entry in status
                if entry.text_status in ["modified", "added", "deleted"]
            ]

            if not alterações:
                print("✅ Nenhuma alteração detectada.")
            else:
                print("⚠️ Alterações locais detectadas:")
                for entry in alterações:
                    print(f"📄 {entry.name} - {entry.text_status}")

                ver_diff = input("🔍 Deseja ver o diff? (s/N): ").strip().lower()
                if ver_diff == 's':
                    print("📄 Diff resumido:")
                    resumo = client.diff_summarize()
                    print(resumo)

        except Exception as e:
            print(f"❌ Erro ao verificar alterações: {e}")


    def listar_arquivos(self, path_local: str, filtro: str = ""):
        """
        Lista arquivos dentro da pasta alvo e imprime o trecho entre '_OS' e a extensão.
        """
        subpasta_alvo = os.path.join(
            path_local, "Branches", "Documentacao", "Arquivos_Diversos", "Documentos_Apoio"
        )

        print(f"📂 Buscando arquivos em: {subpasta_alvo}")
        if not os.path.exists(subpasta_alvo):
            print("❌ Subpasta não encontrada. Verifique se o checkout foi feito corretamente.")
            return

        encontrados = []
        for root, _, files in os.walk(subpasta_alvo):
            for file in files:
                if filtro.lower() in file.lower():
                    caminho_relativo = os.path.relpath(os.path.join(root, file), subpasta_alvo)
                    encontrados.append(caminho_relativo)

        if not encontrados:
            print("⚠️ Nenhum arquivo encontrado com esse filtro.")
        else:
            print(f"🧾 {len(encontrados)} arquivo(s) encontrado(s):")
            for f in encontrados:
                match = re.search(r'_PT_(.*?)\.[^.]+$', f)
                if match:
                    trecho = match.group(1)
                    if '_' not in trecho:
                        # print(trecho)
                        redmineService = RedmineService()
                        redmineService.buscar_issue_por_id(int(trecho))
                        