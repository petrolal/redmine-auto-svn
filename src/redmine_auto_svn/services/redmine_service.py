from re import I
import os
from redminelib import Redmine
from dotenv import load_dotenv

load_dotenv()

class RedmineService:
    def __init__(self):
        self.url = os.getenv("REDMINE_URL")
        self.usuario = os.getenv("REDMINE_USER")
        self.senha = os.getenv("REDMINE_PASS")

        if not self.url or not self.usuario or not self.senha:
            raise ValueError("❌ Variáveis REDMINE_URL, REDMINE_USER e REDMINE_PASS precisam estar no .env")

        self.redmine = Redmine(self.url, username=self.usuario, password=self.senha, include=['children'])

    def buscar_issues(self, projeto_id=None, atribuida_para=None, status_id="open"):
        """
        Retorna uma lista de issues com base nos filtros.
        - projeto_id: slug ou ID do projeto
        - atribuida_para: ID do usuário (opcional)
        - status_id: 'open', 'closed' ou 'all' (padrão: 'open')
        """
        try:
            filtros = {"status_id": status_id}
            if projeto_id:
                filtros["project_id"] = projeto_id
            if atribuida_para:
                filtros["assigned_to_id"] = atribuida_para                        

            return self.redmine.issue.filter(**filtros)

        except Exception as e:
            print(f"❌ Erro ao buscar issues: {e}")
            return []

    def mostrar_issues(self, issues):
        """
        Exibe as issues formatadas no terminal.
        """
        if not issues:
            print("✅ Nenhuma issue encontrada com os critérios especificados.")
            return

        print(f"Usuário: {self.usuario} \nSenha: {self.senha}")
        print(f"📋 {len(issues)} issue(s) encontrada(s):")        
        for issue in issues:
                for filho in issue.children:
                    if filho.tracker.name.lower() == "plano de trabalho":
                        subtarefa = self.redmine.issue.get(filho.id, include=["custom_fields"])
                        situacao = next((f.value for f in subtarefa.custom_fields if f.name.lower() == "situação da subtarefa"), "N/D")
                                            
                        print(f"#[{issue.id}] refs #{subtarefa.id} - {situacao}")                
                    
    
    def buscar_issue_por_id(self, issue_id: int):
        """
        Busca uma issue no Redmine pelo ID e exibe informações básicas + subtarefas com 'plano de trabalho' no título.
        """
        try:
            issue = self.redmine.issue.get(issue_id, include=["children"])
            if hasattr(issue, "children") and issue.children:
                encontrou = False
                for sub in issue.children:
                    sub_detalhada = self.redmine.issue.get(sub.id)
                    if "plano de trabalho" in sub_detalhada.tracker.name.lower():
                        encontrou = True
                        print(f"[RED #{issue.id}] refs #{sub_detalhada.id} - {sub_detalhada.tracker.name}")
            else:
                print("\n✅ Nenhuma subtarefa encontrada.")

            return issue

        except Exception as e:
            print(f"❌ Erro ao buscar issue #{issue_id}: {e}")
            return None