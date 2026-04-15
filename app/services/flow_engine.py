from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Step(StrEnum):
    """Estados da máquina de estados do chatbot."""

    WELCOME = "WELCOME"
    AUTH_USERNAME = "AUTH_USERNAME"
    AUTH_PASSWORD = "AUTH_PASSWORD"
    MAIN_MENU = "MAIN_MENU"
    CREATE_TICKET_TITLE = "CREATE_TICKET_TITLE"
    CREATE_TICKET_DESC = "CREATE_TICKET_DESC"
    LIST_TICKETS = "LIST_TICKETS"
    TICKET_STATUS = "TICKET_STATUS"


@dataclass
class FlowResult:
    """Resultado do processamento de uma mensagem pelo motor de fluxo."""

    response_text: str
    next_step: Step
    session_updates: dict = field(default_factory=dict)


class FlowEngine:
    """
    Motor de fluxo do chatbot baseado em máquina de estados.

    Puro — não faz I/O diretamente. Recebe dependências por injeção.
    """

    def __init__(self, glpi_client, session_manager) -> None:
        self._glpi = glpi_client
        self._session = session_manager

    async def process(self, message: str, session: dict) -> FlowResult:
        """
        Processa uma mensagem recebida com base no estado atual da sessão.
        """
        step = Step(session.get("step", Step.WELCOME))

        if step == Step.WELCOME:
            return FlowResult(
                response_text="Olá! Bem-vindo ao Assistente GLPI. Por favor, informe seu login:",
                next_step=Step.AUTH_USERNAME,
            )

        if step == Step.AUTH_USERNAME:
            return FlowResult(
                response_text="Agora, por favor, informe sua senha:",
                next_step=Step.AUTH_PASSWORD,
                session_updates={"login": message},
            )

        if step == Step.AUTH_PASSWORD:
            login = session.get("login")
            try:
                # Tenta autenticar no GLPI
                token = await self._glpi.init_session_with_credentials(login, message)
                return FlowResult(
                    response_text=(
                        "Autenticado com sucesso! O que deseja fazer?\n"
                        "1. Abrir novo chamado\n"
                        "2. Listar meus chamados\n"
                        "3. Ver status de um chamado"
                    ),
                    next_step=Step.MAIN_MENU,
                    session_updates={"glpi_session_token": token, "authenticated": True},
                )
            except Exception:
                return FlowResult(
                    response_text="Falha na autenticação. Por favor, verifique seu login e tente novamente:",
                    next_step=Step.AUTH_USERNAME,
                    session_updates={"authenticated": False},
                )

        if step == Step.MAIN_MENU:
            if message == "1":
                return FlowResult(
                    response_text="Qual o título do chamado?",
                    next_step=Step.CREATE_TICKET_TITLE,
                )
            elif message == "2":
                try:
                    tickets = await self._glpi.search_tickets()
                    if not tickets:
                        return FlowResult(
                            response_text="Você não possui chamados abertos no momento.",
                            next_step=Step.MAIN_MENU,
                        )
                    
                    text = "📋 Seus últimos chamados:\n\n"
                    for t in tickets[:5]:  # Mostrar os 5 primeiros
                        # O GLPI Search API retorna os campos pelos IDs dos cabeçalhos.
                        # No scaffolding, o mock retorna {"id": X, "name": Y}.
                        t_id = t.get("id") or t.get("1")
                        t_name = t.get("name") or t.get("2")
                        text += f"• #{t_id}: {t_name}\n"
                    
                    text += "\nO que deseja fazer agora? (1, 2 ou 3)"
                    return FlowResult(response_text=text, next_step=Step.MAIN_MENU)
                except Exception:
                    return FlowResult(
                        response_text="Erro ao buscar chamados. Tente novamente mais tarde.",
                        next_step=Step.MAIN_MENU,
                    )
            elif message == "3":
                return FlowResult(
                    response_text="Por favor, informe o número do chamado:",
                    next_step=Step.TICKET_STATUS,
                )
            else:
                return FlowResult(
                    response_text="Opção inválida. Escolha 1, 2 ou 3.",
                    next_step=Step.MAIN_MENU,
                )

        if step == Step.CREATE_TICKET_TITLE:
            return FlowResult(
                response_text="Por favor, informe a descrição do problema:",
                next_step=Step.CREATE_TICKET_DESC,
                session_updates={"ticket_title": message},
            )

        if step == Step.CREATE_TICKET_DESC:
            title = session.get("ticket_title")
            try:
                result = await self._glpi.create_ticket(title, message)
                ticket_id = result.get("id")
                return FlowResult(
                    response_text=f"✅ Chamado #{ticket_id} criado com sucesso!",
                    next_step=Step.MAIN_MENU,
                )
            except Exception:
                return FlowResult(
                    response_text="❌ Erro ao criar chamado. Tente novamente mais tarde.",
                    next_step=Step.MAIN_MENU,
                )

        if step == Step.TICKET_STATUS:
            if not message.isdigit():
                return FlowResult(
                    response_text="Número de chamado inválido. Por favor, digite apenas números:",
                    next_step=Step.TICKET_STATUS,
                )
            try:
                ticket = await self._glpi.get_ticket(int(message))
                # Simplificação do mapeamento de status
                status_map = {1: "Novo", 2: "Em atendimento", 5: "Solucionado", 6: "Fechado"}
                status = status_map.get(ticket.get("status"), "Em andamento")
                
                response = (
                    f"🎫 Chamado #{ticket['id']}\n"
                    f"Assunto: {ticket['name']}\n"
                    f"Status: {status}\n"
                    f"Data: {ticket.get('date')}\n"
                )
                return FlowResult(response_text=response, next_step=Step.MAIN_MENU)
            except Exception:
                return FlowResult(
                    response_text="Chamado não encontrado ou erro na busca.",
                    next_step=Step.MAIN_MENU,
                )

        # Fallback
        return FlowResult(response_text="Desculpe, não entendi.", next_step=Step.WELCOME)
