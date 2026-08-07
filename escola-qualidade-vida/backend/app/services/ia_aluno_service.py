import json
import os
import re
import unicodedata
import urllib.request
from datetime import date, datetime, timedelta

from app.models.aluno import Aluno, only_digits
from app.models.curso import Curso
from app.models.ocorrencia import Ocorrencia
from app.models.turma import Turma


DISCLAIMER = (
    "Sugestões de apoio escolar. Não substituem avaliação profissional, "
    "psicológica, médica, pedagógica ou decisão institucional."
)

RISK_DETAILS = {
    "alto": {
        "prioridade": "Alta prioridade",
        "explicacao": "Precisa de acompanhamento próximo e registro de devolutiva.",
        "prazo": "Em até 2 dias letivos",
    },
    "medio": {
        "prioridade": "Prioridade moderada",
        "explicacao": "Pede monitoramento na semana para evitar recorrência.",
        "prazo": "Na próxima semana",
    },
    "baixo": {
        "prioridade": "Acompanhamento de rotina",
        "explicacao": "Sem sinais fortes de urgência nos dados analisados.",
        "prazo": "Acompanhamento de rotina",
    },
}

HIGH_IMPACT_TYPES = {
    Ocorrencia.TIPO_APOIO_PSICOLOGICO,
    Ocorrencia.TIPO_PROBLEMA_SAUDE,
    Ocorrencia.TIPO_ATENDIMENTO_PAIS,
}

FOLLOW_UP_TYPES = {
    Ocorrencia.TIPO_ATRASO,
    Ocorrencia.TIPO_SAIDA_ANTECIPADA,
    Ocorrencia.TIPO_APOIO_EDUCACIONAL,
    Ocorrencia.TIPO_ATENDIMENTO_EMPRESAS,
}

SECURITY_ALERT_CATEGORIES = {
    "violencia": {
        "label": "Violência, ameaça ou agressão",
        "terms": [
            "violencia",
            "agressao",
            "agressoes",
            "agredir",
            "agrediu",
            "agredido",
            "agredida",
            "briga",
            "ameaca",
            "ameacas",
            "ameacar",
            "ameacou",
            "intimidacao",
            "arma",
            "armas",
            "armado",
            "armada",
            "faca",
            "lesao",
            "abuso",
            "assedio",
        ],
    },
    "drogas": {
        "label": "Uso, porte ou tráfico de drogas",
        "terms": [
            "droga",
            "drogas",
            "entorpecente",
            "entorpecentes",
            "narcotico",
            "narcoticos",
            "maconha",
            "cocaina",
            "crack",
            "trafico",
            "porte de droga",
            "uso de droga",
        ],
    },
    "medicamentos_controlados": {
        "label": "Uso indevido de medicamentos controlados",
        "terms": [
            "remedio controlado",
            "remedios controlados",
            "medicamento controlado",
            "medicamentos controlados",
            "medicacao controlada",
            "medicacoes controladas",
            "uso de remedio controlado",
            "uso de remedios controlados",
            "uso de medicamento controlado",
            "uso de medicamentos controlados",
            "remedio tarja preta",
            "medicamento tarja preta",
            "tarja preta",
            "receita controlada",
            "comprimido controlado",
            "comprimidos controlados",
            "ansiolitico",
            "ansioliticos",
            "clonazepam",
            "rivotril",
            "diazepam",
            "alprazolam",
        ],
    },
    "crime": {
        "label": "Possível ação criminosa",
        "terms": [
            "crime",
            "criminal",
            "furto",
            "furtou",
            "roubo",
            "roubou",
            "roubar",
            "assalto",
            "vandalismo",
            "depredacao",
            "porte ilegal",
            "boletim de ocorrencia",
        ],
    },
}

SECURITY_ALERT_ACTIONS = [
    "Acionar imediatamente a coordenação e a equipe de qualidade de vida.",
    "Verificar o protocolo institucional para situações de segurança.",
    "Preservar os registros da ocorrência e registrar as providências tomadas.",
    "Envolver responsáveis e autoridades competentes quando houver risco imediato ou exigência legal.",
]

EMOTIONAL_ALERT_CATEGORIES = {
    "suicidio": {
        "level": "critico",
        "label": "Risco de autoagressão ou suicídio",
        "terms": [
            "suicidio",
            "suicida",
            "autoagressao",
            "automutilacao",
            "autoexterminio",
            "tirar a propria vida",
            "tirou a propria vida",
            "se matar",
            "quer se matar",
            "quer morrer",
            "vontade de morrer",
            "nao quero viver",
            "nao aguenta mais viver",
            "sem motivo para viver",
            "sem razao para viver",
            "planejou morrer",
            "plano para morrer",
            "cortar os pulsos",
            "despedida",
        ],
    },
    "depressao": {
        "level": "atencao",
        "label": "Possíveis sinais de depressão ou sofrimento emocional",
        "terms": [
            "depressao",
            "depressivo",
            "depressiva",
            "tristeza profunda",
            "triste constante",
            "choro frequente",
            "chorando muito",
            "desanimo",
            "apatia",
            "isolamento",
            "isolado",
            "isolada",
            "sem vontade",
            "sem energia",
            "sem esperanca",
            "desesperanca",
            "sentimento de vazio",
            "vazio",
            "inutil",
            "culpa excessiva",
            "baixa autoestima",
            "perda de interesse",
            "alteracao de sono",
            "insonia",
            "dorme demais",
            "falta de apetite",
            "ansiedade intensa",
        ],
    },
}

EMOTIONAL_ALERT_ACTIONS_CRITICAL = [
    "Acionar imediatamente a coordenação e a equipe de qualidade de vida.",
    "Não deixar o aluno sem acompanhamento até a avaliação da equipe responsável.",
    "Seguir o protocolo institucional de risco à vida e registrar as providências.",
    "Envolver responsáveis e serviço especializado conforme o protocolo da instituição.",
]

EMOTIONAL_ALERT_ACTIONS_ATTENTION = [
    "Agendar acolhimento individual com escuta cuidadosa e sem julgamento.",
    "Encaminhar para a equipe de qualidade de vida ou profissional habilitado.",
    "Observar mudanças recentes de comportamento, frequência, sono, apetite ou isolamento.",
    "Registrar devolutiva e combinar acompanhamento próximo.",
]


def detectar_alertas_ocorrencia(tipo, descricao, data_ocorrencia=None):
    occurrence = [{
        "tipo": tipo or "",
        "descricao": descricao or "",
        "data_ocorrencia": data_ocorrencia,
    }]
    security_alert = _security_alert_from_occurrence_data(occurrence)
    emotional_alert = _emotional_alert_from_occurrence_data(occurrence)

    has_security = security_alert["ativo"]
    has_emotional = emotional_alert["ativo"]
    has_alert = has_security or has_emotional
    emotional_is_critical = emotional_alert.get("nivel") == "critico"
    level = "critico" if has_security or emotional_is_critical else "atencao" if has_alert else ""

    if has_security and has_emotional:
        alert_type = "multiplo"
    elif emotional_is_critical:
        alert_type = "risco_vida"
    elif has_emotional:
        alert_type = "saude_emocional"
    elif has_security:
        alert_type = "seguranca"
    else:
        alert_type = ""

    reasons = _unique([
        *security_alert.get("motivos", []),
        *emotional_alert.get("motivos", []),
    ])

    return {
        "ativo": has_alert,
        "tipo": alert_type,
        "nivel": level,
        "motivos": reasons,
        "seguranca": security_alert,
        "saude_emocional": emotional_alert,
        "campos_obrigatorios": (
            ["acao_tomada", "acompanhamento", "data_acompanhamento"]
            if has_alert
            else []
        ),
    }


def analisar_alunos(limit=30, aluno_id=None, cpf=None):
    alunos = _load_students(limit=limit, aluno_id=aluno_id, cpf=cpf)
    contexts = [_build_student_context(aluno) for aluno in alunos]
    security_alerts = {
        context["aluno_id"]: _security_alert_for_context(context)
        for context in contexts
    }
    emotional_alerts = {
        context["aluno_id"]: _emotional_alert_for_context(context)
        for context in contexts
    }

    local_analysis = [_heuristic_analysis(context) for context in contexts]
    ai_analysis = _try_openai_analysis(contexts) if contexts else None
    if ai_analysis:
        ai_analysis = _restore_context_identity(ai_analysis, contexts)

    analyses = [
        _apply_emotional_alert(
            _apply_security_alert(analysis, security_alerts.get(analysis.get("aluno_id"))),
            emotional_alerts.get(analysis.get("aluno_id")),
        )
        for analysis in (ai_analysis or local_analysis)
    ]
    analyses = sorted(
        analyses,
        key=lambda item: (_risk_weight(item.get("risco")), item.get("pontuacao", 0)),
        reverse=True,
    )
    source = "openai" if ai_analysis else "heuristica"

    return {
        "modo": source,
        "gerado_em": datetime.utcnow().isoformat() + "Z",
        "total_analisado": len(analyses),
        "resumo_geral": _overall_summary(analyses),
        "disclaimer": DISCLAIMER,
        "analises": analyses,
    }


def _load_students(limit=30, aluno_id=None, cpf=None):
    query = Aluno.query.order_by(Aluno.id.desc())
    if aluno_id is not None:
        query = query.filter(Aluno.id == aluno_id)
    if cpf:
        query = query.filter(Aluno.cpf == only_digits(cpf))

    try:
        limit = int(limit or 30)
    except (TypeError, ValueError):
        limit = 30
    limit = max(1, min(limit, 100))

    return query.limit(limit).all()


def _build_student_context(aluno):
    ocorrencias = (
        Ocorrencia.query
        .filter(Ocorrencia.aluno_id == aluno.id)
        .order_by(Ocorrencia.data_ocorrencia.desc().nullslast(), Ocorrencia.data.desc())
        .all()
    )

    curso = Curso.query.get(aluno.curso_id) if aluno.curso_id else None
    turma = Turma.query.get(aluno.turma_id) if aluno.turma_id else None

    tipos = {}
    for ocorrencia in ocorrencias:
        tipos[ocorrencia.tipo] = tipos.get(ocorrencia.tipo, 0) + 1

    ultima_data = None
    if ocorrencias:
        ultima = ocorrencias[0]
        ultima_data = ultima.data_ocorrencia or (ultima.data.date() if ultima.data else None)

    security_alert = _security_alert_from_occurrences(ocorrencias)
    emotional_alert = _emotional_alert_from_occurrences(ocorrencias)

    return {
        "aluno_id": aluno.id,
        "nome": _student_name(aluno),
        "idade": aluno.idade,
        "curso": curso.nome if curso else (aluno.curso or "Sem curso"),
        "turma": turma.nome if turma else (aluno.turma or "Sem turma"),
        "turma_status": "finalizada" if turma and turma.data_fim else "ativa" if turma else "sem_turma",
        "escola_integrada": aluno.escola_integrada,
        "pessoa_com_deficiencia": bool(aluno.pessoa_com_deficiencia),
        "total_ocorrencias": len(ocorrencias),
        "tipos_ocorrencia": tipos,
        "ultima_ocorrencia": ultima_data.isoformat() if ultima_data else None,
        "ocorrencias_recentes_30d": _count_recent(ocorrencias, days=30),
        "alerta_seguranca_detectado": security_alert,
        "alerta_saude_emocional_detectado": emotional_alert,
        "ocorrencias": [
            {
                "tipo": ocorrencia.tipo,
                "descricao": (ocorrencia.descricao or "")[:360],
                "data_ocorrencia": ocorrencia.data_ocorrencia.isoformat() if ocorrencia.data_ocorrencia else None,
            }
            for ocorrencia in ocorrencias[:8]
        ],
    }


def _student_name(aluno):
    return (
        getattr(aluno, "nome_social", None)
        or getattr(aluno, "nome_completo", None)
        or f"{getattr(aluno, 'nome', '')} {getattr(aluno, 'sobrenome', '')}".strip()
        or f"Aluno {aluno.id}"
    )


def _count_recent(ocorrencias, days=30):
    since = date.today() - timedelta(days=days)
    count = 0
    for ocorrencia in ocorrencias:
        event_date = ocorrencia.data_ocorrencia or (ocorrencia.data.date() if ocorrencia.data else None)
        if event_date and event_date >= since:
            count += 1
    return count


def _security_alert_from_occurrences(occurrences):
    occurrence_data = [
        {
            "tipo": occurrence.tipo,
            "descricao": occurrence.descricao,
            "data_ocorrencia": (
                occurrence.data_ocorrencia.isoformat()
                if occurrence.data_ocorrencia
                else None
            ),
        }
        for occurrence in occurrences
    ]
    return _security_alert_from_occurrence_data(occurrence_data)


def _security_alert_for_context(context):
    detected_alert = context.get("alerta_seguranca_detectado")
    if detected_alert:
        return detected_alert

    return _security_alert_from_occurrence_data(context["ocorrencias"])


def _security_alert_from_occurrence_data(occurrences):
    matched_labels = []
    related_occurrences = []

    for occurrence in occurrences:
        searchable_text = _normalize_text(
            f"{occurrence.get('tipo', '')} {occurrence.get('descricao', '')}"
        )
        occurrence_matched = False

        for category in SECURITY_ALERT_CATEGORIES.values():
            if any(_contains_security_term(searchable_text, term) for term in category["terms"]):
                if category["label"] not in matched_labels:
                    matched_labels.append(category["label"])
                occurrence_matched = True

        if occurrence_matched:
            related_occurrences.append({
                "tipo": occurrence.get("tipo") or "Ocorrência",
                "data": _format_date(occurrence.get("data_ocorrencia")),
            })

    if not matched_labels:
        return _empty_security_alert()

    return {
        "ativo": True,
        "titulo": "Alerta de segurança",
        "mensagem": (
            "Há ocorrência com possível violência, uso de drogas, medicamento controlado ou ação criminosa. "
            "Trate como prioridade imediata e siga o protocolo institucional."
        ),
        "motivos": matched_labels,
        "orientacoes": SECURITY_ALERT_ACTIONS,
        "ocorrencias_relacionadas": related_occurrences[:4],
    }


def _apply_security_alert(analysis, security_alert):
    alert = security_alert or _empty_security_alert()
    result = dict(analysis)
    result["alerta_seguranca"] = alert

    if not alert["ativo"]:
        return result

    result["risco"] = "alto"
    result["prioridade"] = "Alerta de segurança"
    result["pontuacao"] = max(int(result.get("pontuacao") or 0), 90)
    result["leitura_rapida"] = "Existe uma ocorrência sensível. Priorize este caso agora."
    result["motivo_principal"] = alert["mensagem"]
    result["proximo_passo"] = SECURITY_ALERT_ACTIONS[0]
    result["prazo_sugerido"] = "Imediato, no mesmo dia letivo"
    result["responsavel_sugerido"] = "Coordenação / equipe de qualidade de vida"
    result["fatores"] = _unique([
        alert["mensagem"],
        *alert["motivos"],
        *result.get("fatores", []),
    ])[:8]
    result["acoes_sugeridas"] = _unique([
        *SECURITY_ALERT_ACTIONS,
        *result.get("acoes_sugeridas", []),
    ])[:8]
    return result


def _empty_security_alert():
    return {
        "ativo": False,
        "titulo": "",
        "mensagem": "",
        "motivos": [],
        "orientacoes": [],
        "ocorrencias_relacionadas": [],
    }


def _emotional_alert_from_occurrences(occurrences):
    occurrence_data = [
        {
            "tipo": occurrence.tipo,
            "descricao": occurrence.descricao,
            "data_ocorrencia": (
                occurrence.data_ocorrencia.isoformat()
                if occurrence.data_ocorrencia
                else None
            ),
        }
        for occurrence in occurrences
    ]
    return _emotional_alert_from_occurrence_data(occurrence_data)


def _emotional_alert_for_context(context):
    detected_alert = context.get("alerta_saude_emocional_detectado")
    if detected_alert:
        return detected_alert

    return _emotional_alert_from_occurrence_data(context["ocorrencias"])


def _emotional_alert_from_occurrence_data(occurrences):
    matched_labels = []
    related_occurrences = []
    highest_level = None

    for occurrence in occurrences:
        searchable_text = _normalize_text(
            f"{occurrence.get('tipo', '')} {occurrence.get('descricao', '')}"
        )
        occurrence_matched = False

        for category in EMOTIONAL_ALERT_CATEGORIES.values():
            if any(_contains_security_term(searchable_text, term) for term in category["terms"]):
                if category["label"] not in matched_labels:
                    matched_labels.append(category["label"])
                highest_level = _highest_emotional_level(highest_level, category["level"])
                occurrence_matched = True

        if occurrence_matched:
            related_occurrences.append({
                "tipo": occurrence.get("tipo") or "Ocorrência",
                "data": _format_date(occurrence.get("data_ocorrencia")),
            })

    if not matched_labels:
        return _empty_emotional_alert()

    is_critical = highest_level == "critico"
    return {
        "ativo": True,
        "nivel": highest_level,
        "titulo": "Alerta de risco à vida" if is_critical else "Alerta de saúde emocional",
        "mensagem": (
            "Há ocorrência com possível risco de autoagressão ou suicídio. "
            "Trate como prioridade imediata e siga o protocolo institucional."
            if is_critical
            else "Há possíveis sinais de depressão ou sofrimento emocional. "
            "O sistema não diagnostica; ele indica necessidade de acolhimento e avaliação profissional."
        ),
        "motivos": matched_labels,
        "orientacoes": (
            EMOTIONAL_ALERT_ACTIONS_CRITICAL
            if is_critical
            else EMOTIONAL_ALERT_ACTIONS_ATTENTION
        ),
        "ocorrencias_relacionadas": related_occurrences[:4],
    }


def _apply_emotional_alert(analysis, emotional_alert):
    alert = emotional_alert or _empty_emotional_alert()
    result = dict(analysis)
    result["alerta_saude_emocional"] = alert

    if not alert["ativo"]:
        return result

    if alert["nivel"] == "critico":
        result["risco"] = "alto"
        result["prioridade"] = "Alerta de risco à vida"
        result["pontuacao"] = max(int(result.get("pontuacao") or 0), 95)
        result["leitura_rapida"] = "Existe possível risco de autoagressão ou suicídio. Priorize agora."
        result["proximo_passo"] = EMOTIONAL_ALERT_ACTIONS_CRITICAL[0]
        result["prazo_sugerido"] = "Imediato, no mesmo dia letivo"
        result["responsavel_sugerido"] = "Coordenação / equipe de qualidade de vida"
    else:
        current_score = int(result.get("pontuacao") or 0)
        if _risk_weight(result.get("risco")) < _risk_weight("medio"):
            result["risco"] = "medio"
            result["prioridade"] = "Alerta de saúde emocional"
        result["pontuacao"] = max(current_score, 55)
        result["leitura_rapida"] = "Há possíveis sinais de sofrimento emocional. Acompanhe de perto."
        result["proximo_passo"] = EMOTIONAL_ALERT_ACTIONS_ATTENTION[0]
        if result.get("prazo_sugerido") == RISK_DETAILS["baixo"]["prazo"]:
            result["prazo_sugerido"] = "Na próxima semana"
        if result.get("responsavel_sugerido") == "Acompanhamento de rotina":
            result["responsavel_sugerido"] = "Equipe de qualidade de vida"

    result["motivo_principal"] = alert["mensagem"]
    result["fatores"] = _unique([
        alert["mensagem"],
        *alert["motivos"],
        *result.get("fatores", []),
    ])[:8]
    result["acoes_sugeridas"] = _unique([
        *alert["orientacoes"],
        *result.get("acoes_sugeridas", []),
    ])[:8]
    return result


def _empty_emotional_alert():
    return {
        "ativo": False,
        "nivel": "",
        "titulo": "",
        "mensagem": "",
        "motivos": [],
        "orientacoes": [],
        "ocorrencias_relacionadas": [],
    }


def _highest_emotional_level(current, candidate):
    weights = {"atencao": 1, "critico": 2}
    return candidate if weights.get(candidate, 0) > weights.get(current, 0) else current


def _contains_security_term(text, term):
    normalized_term = _normalize_text(term)
    if not normalized_term:
        return False

    if " " in normalized_term:
        return normalized_term in text

    return re.search(rf"\b{re.escape(normalized_term)}\b", text) is not None


def _normalize_text(value):
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return normalized.lower()


def _heuristic_analysis(context):
    score = 0
    factors = []
    actions = []

    total = context["total_ocorrencias"]
    recent = context["ocorrencias_recentes_30d"]
    types = context["tipos_ocorrencia"]

    if total >= 5:
        score += 35
        factors.append(
            f"Histórico com {total} ocorrências. A repetição indica necessidade de olhar o caso com mais cuidado."
        )
    elif total >= 2:
        score += 18
        factors.append(f"Histórico com {total} ocorrências registradas.")

    if recent >= 3:
        score += 30
        factors.append(f"{recent} ocorrências nos últimos 30 dias. Isso sugere uma situação ainda ativa.")
    elif recent >= 1:
        score += 10
        factors.append(f"{recent} ocorrência(s) recente(s) nos últimos 30 dias.")

    high_types = [tipo for tipo in types if tipo in HIGH_IMPACT_TYPES]
    if high_types:
        score += 22
        factors.append(
            "Há registro(s) que pedem acolhimento ou encaminhamento cuidadoso: "
            + ", ".join(high_types)
            + "."
        )

    follow_up_types = [tipo for tipo in types if tipo in FOLLOW_UP_TYPES]
    if follow_up_types:
        score += 12
        factors.append(
            "Há sinais ligados à rotina, frequência ou aprendizagem: "
            + ", ".join(follow_up_types)
            + "."
        )

    if context["pessoa_com_deficiencia"]:
        score += 8
        factors.append("Aluno PCD: verificar se o plano de apoio e acessibilidade está atualizado.")

    if context["idade"] is not None and context["idade"] < 18:
        score += 6
        factors.append("Aluno menor de idade: envolver responsável quando o caso pedir alinhamento familiar.")

    if score >= 65:
        risk = "alto"
    elif score >= 35:
        risk = "medio"
    else:
        risk = "baixo"

    deadline = RISK_DETAILS[risk]["prazo"]

    if total == 0:
        factors.append("Sem ocorrências registradas.")
        actions.extend([
            "Manter acompanhamento preventivo e registrar novas observações quando surgirem.",
            "Confirmar se dados cadastrais, curso e turma estão atualizados.",
        ])
    else:
        actions.extend([
            "Revisar o histórico de ocorrências antes do próximo atendimento.",
            "Registrar uma devolutiva objetiva após cada encaminhamento realizado.",
        ])

    if recent >= 2 or risk == "alto":
        actions.append("Agendar conversa individual com o aluno para entender o que está se repetindo.")

    if high_types:
        actions.append("Avaliar encaminhamento para equipe de apoio adequada, sem registrar diagnósticos.")

    if Ocorrencia.TIPO_ATENDIMENTO_PAIS in types or (context["idade"] is not None and context["idade"] < 18 and risk != "baixo"):
        actions.append("Contatar responsável para alinhar acompanhamento e combinados.")

    if Ocorrencia.TIPO_ATENDIMENTO_EMPRESAS in types:
        actions.append("Alinhar com empresa parceira pontos de frequência, horário ou aprendizagem.")

    if Ocorrencia.TIPO_APOIO_EDUCACIONAL in types:
        actions.append("Montar plano curto de estudo com prazos e conteúdos prioritários.")

    unique_actions = _unique(actions)[:6]
    score = min(score, 100)

    return {
        "aluno_id": context["aluno_id"],
        "nome": context["nome"],
        "curso": context["curso"],
        "turma": context["turma"],
        "risco": risk,
        "prioridade": RISK_DETAILS[risk]["prioridade"],
        "pontuacao": score,
        "resumo": _summary_for(context, risk),
        "leitura_rapida": _quick_read(context, risk),
        "motivo_principal": _main_reason(context, risk, factors),
        "proximo_passo": unique_actions[0] if unique_actions else "Manter acompanhamento de rotina.",
        "indicadores": _indicators_for(context),
        "fatores": factors[:6],
        "acoes_sugeridas": unique_actions,
        "prazo_sugerido": deadline,
        "responsavel_sugerido": _responsible_for(risk, high_types),
        "observacao": DISCLAIMER,
    }


def _summary_for(context, risk):
    total = context["total_ocorrencias"]
    explanation = RISK_DETAILS[risk]["explicacao"]
    if total == 0:
        return "Não há ocorrências registradas. A recomendação é manter acompanhamento preventivo."
    return (
        f"{total} ocorrência(s) no histórico. {explanation} "
        f"Última ocorrência: {_format_date(context['ultima_ocorrencia'])}."
    )


def _quick_read(context, risk):
    if context["total_ocorrencias"] == 0:
        return "Caso sem alerta nos registros atuais."

    if risk == "alto":
        return "Priorize este aluno na rotina de acompanhamento."
    if risk == "medio":
        return "Acompanhe nesta semana e observe se há repetição."
    return "Mantenha observação regular e registre novas situações."


def _main_reason(context, risk, factors):
    if factors:
        return factors[0]

    if risk == "baixo":
        return "Os dados atuais não mostram repetição ou urgência."

    return RISK_DETAILS[risk]["explicacao"]


def _indicators_for(context):
    top_types = _top_occurrence_types(context["tipos_ocorrencia"])
    return [
        {"rotulo": "Histórico", "valor": _plural(context["total_ocorrencias"], "ocorrência")},
        {"rotulo": "Últimos 30 dias", "valor": _plural(context["ocorrencias_recentes_30d"], "ocorrência")},
        {"rotulo": "Última ocorrência", "valor": _format_date(context["ultima_ocorrencia"])},
        {"rotulo": "Tipo mais comum", "valor": top_types[0] if top_types else "Sem registros"},
    ]


def _top_occurrence_types(types):
    sorted_types = sorted(types.items(), key=lambda item: item[1], reverse=True)
    return [f"{tipo} ({count})" for tipo, count in sorted_types[:3]]


def _format_date(value):
    if not value:
        return "Não informada"
    try:
        parsed = date.fromisoformat(value)
    except (TypeError, ValueError):
        return str(value)
    return parsed.strftime("%d/%m/%Y")


def _plural(count, singular):
    if count == 1:
        return f"1 {singular}"
    return f"{count} {singular}s"


def _responsible_for(risk, high_types):
    if high_types:
        return "Equipe de qualidade de vida / coordenação"
    if risk == "alto":
        return "Coordenação pedagógica"
    if risk == "medio":
        return "Analista ou coordenação"
    return "Acompanhamento de rotina"


def _overall_summary(analyses):
    counts = {"alto": 0, "medio": 0, "baixo": 0}
    security_alerts = 0
    emotional_alerts = 0
    emotional_critical_alerts = 0
    for analysis in analyses:
        risk = analysis.get("risco", "baixo")
        counts[risk] = counts.get(risk, 0) + 1
        if analysis.get("alerta_seguranca", {}).get("ativo"):
            security_alerts += 1
        emotional_alert = analysis.get("alerta_saude_emocional", {})
        if emotional_alert.get("ativo"):
            emotional_alerts += 1
            if emotional_alert.get("nivel") == "critico":
                emotional_critical_alerts += 1

    total = len(analyses)
    if total == 0:
        message = "Nenhum aluno encontrado para análise."
    elif emotional_critical_alerts:
        message = f"{emotional_critical_alerts} alerta(s) de risco à vida precisam de atenção imediata."
    elif security_alerts:
        message = f"{security_alerts} alerta(s) de segurança precisam de atenção imediata."
    elif emotional_alerts:
        message = f"{emotional_alerts} alerta(s) de saúde emocional pedem acolhimento próximo."
    elif counts["alto"]:
        message = f"{counts['alto']} aluno(s) precisam de prioridade no acompanhamento."
    elif counts["medio"]:
        message = f"{counts['medio']} aluno(s) pedem monitoramento nesta semana."
    else:
        message = "Nenhum alerta prioritário nos alunos analisados."

    return {
        "total": total,
        "alto": counts["alto"],
        "medio": counts["medio"],
        "baixo": counts["baixo"],
        "alertas_seguranca": security_alerts,
        "alertas_saude_emocional": emotional_alerts,
        "alertas_risco_vida": emotional_critical_alerts,
        "mensagem": message,
    }


def _risk_weight(risk):
    return {"alto": 3, "medio": 2, "baixo": 1}.get(risk, 0)


def _unique(items):
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def _try_openai_analysis(contexts):
    if os.environ.get("ENABLE_OPENAI_ANALYSIS") != "1":
        return None

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None

    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    contexts_for_ai = _contexts_for_external_ai(contexts)
    payload = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": (
                    "Você é um assistente de apoio escolar. Analise dados de alunos e sugira ações "
                    "práticas, seguras, não diagnósticas e fáceis de entender por uma equipe escolar. "
                    "Use frases curtas, explique o motivo principal e responda somente JSON válido no schema pedido."
                ),
            },
            {
                "role": "user",
                "content": json.dumps({
                    "disclaimer": DISCLAIMER,
                    "alunos": contexts_for_ai,
                    "schema": (
                        "lista de analises com prioridade, leitura_rapida, motivo_principal, "
                        "indicadores, fatores, acoes_sugeridas, proximo_passo, prazo_sugerido "
                        "e responsavel_sugerido"
                    ),
                }, ensure_ascii=False),
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "analise_alunos",
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "analises": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": False,
                                "properties": {
                                    "aluno_id": {"type": "integer"},
                                    "nome": {"type": "string"},
                                    "curso": {"type": "string"},
                                    "turma": {"type": "string"},
                                    "risco": {"type": "string", "enum": ["baixo", "medio", "alto"]},
                                    "prioridade": {"type": "string"},
                                    "pontuacao": {"type": "integer"},
                                    "resumo": {"type": "string"},
                                    "leitura_rapida": {"type": "string"},
                                    "motivo_principal": {"type": "string"},
                                    "proximo_passo": {"type": "string"},
                                    "indicadores": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "additionalProperties": False,
                                            "properties": {
                                                "rotulo": {"type": "string"},
                                                "valor": {"type": "string"},
                                            },
                                            "required": ["rotulo", "valor"],
                                        },
                                    },
                                    "fatores": {"type": "array", "items": {"type": "string"}},
                                    "acoes_sugeridas": {"type": "array", "items": {"type": "string"}},
                                    "prazo_sugerido": {"type": "string"},
                                    "responsavel_sugerido": {"type": "string"},
                                    "observacao": {"type": "string"},
                                },
                                "required": [
                                    "aluno_id",
                                    "nome",
                                    "curso",
                                    "turma",
                                    "risco",
                                    "prioridade",
                                    "pontuacao",
                                    "resumo",
                                    "leitura_rapida",
                                    "motivo_principal",
                                    "proximo_passo",
                                    "indicadores",
                                    "fatores",
                                    "acoes_sugeridas",
                                    "prazo_sugerido",
                                    "responsavel_sugerido",
                                    "observacao",
                                ],
                            },
                        },
                    },
                    "required": ["analises"],
                },
                "strict": True,
            }
        },
    }

    try:
        response_data = _post_openai_response(api_key, payload)
        parsed = _extract_response_json(response_data)
        analyses = parsed.get("analises")
        if isinstance(analyses, list):
            return analyses
    except Exception:
        return None

    return None


def _contexts_for_external_ai(contexts):
    if os.environ.get("OPENAI_SEND_PERSONAL_DATA") == "1":
        return contexts

    redacted = []
    for context in contexts:
        safe_context = dict(context)
        safe_context["nome"] = f"Aluno {context['aluno_id']}"
        safe_context["ocorrencias"] = [
            {
                "tipo": occurrence.get("tipo"),
                "descricao": "[omitida por privacidade]",
                "data_ocorrencia": occurrence.get("data_ocorrencia"),
            }
            for occurrence in context.get("ocorrencias", [])
        ]
        redacted.append(safe_context)
    return redacted


def _restore_context_identity(analyses, contexts):
    contexts_by_id = {context["aluno_id"]: context for context in contexts}
    restored = []
    for analysis in analyses:
        item = dict(analysis)
        context = contexts_by_id.get(item.get("aluno_id"))
        if context:
            item["nome"] = context["nome"]
            item["curso"] = context["curso"]
            item["turma"] = context["turma"]
        restored.append(item)
    return restored


def _post_openai_response(api_key, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    timeout = int(os.environ.get("OPENAI_TIMEOUT_SECONDS", "20"))
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_response_json(response_data):
    if response_data.get("output_text"):
        return json.loads(response_data["output_text"])

    for item in response_data.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                return json.loads(text)

    raise ValueError("Resposta da IA sem texto JSON.")
