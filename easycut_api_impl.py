# -*- coding: utf-8 -*-
"""
Rotas e helpers da API EasyCut (agendamentos, serviços, horários, favoritos, avaliações).
Mantido em módulo separado para não inflar demais o app.py; é registrado em app.register_extended_api().
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request

FetchHoursFn = Callable[[Any, int], Dict[str, Any]]


def _json_safe(v: Any) -> Any:
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, timedelta):
        total = int(v.total_seconds())
        h, m = total // 3600, (total % 3600) // 60
        return f"{h:02d}:{m:02d}"
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    return v


def _as_hhmm(val: Any) -> str:
    if val is None:
        return "00:00"
    if isinstance(val, timedelta):
        total = int(val.total_seconds()) % 86400
        h, m = total // 3600, (total % 3600) // 60
        return f"{h:02d}:{m:02d}"
    s = str(val)
    return s[:5] if len(s) >= 5 else s


def _time_to_minutes(hhmm: str) -> int:
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def _minutes_to_time(m: int) -> str:
    m = max(0, m) % (24 * 60)
    return f"{m // 60:02d}:{m % 60:02d}"


def _weekday_key(d: date) -> str:
    keys = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return keys[d.weekday()]


def db_status_to_api(s: Optional[str]) -> str:
    if not s:
        return "pending"
    x = str(s).lower().strip()
    m = {
        "pendente": "pending",
        "confirmado": "confirmed",
        "cancelado": "cancelled",
        "concluido": "completed",
        "pending": "pending",
        "confirmed": "confirmed",
        "cancelled": "cancelled",
        "completed": "completed",
    }
    return m.get(x, "pending")


def api_status_to_db(s: str) -> str:
    x = (s or "").lower().strip()
    m = {
        "pending": "pendente",
        "confirmed": "confirmado",
        "cancelled": "cancelado",
        "completed": "concluido",
        "pendente": "pendente",
        "confirmado": "confirmado",
        "cancelado": "cancelado",
        "concluido": "concluido",
    }
    return m.get(x, "pendente")


def servico_db_status_to_api(status: Optional[str]) -> str:
    if not status:
        return "active"
    x = str(status).lower()
    if x in ("ativo", "active"):
        return "active"
    return "inactive"


def servico_api_status_to_db(status: Optional[str]) -> str:
    x = (status or "active").lower()
    if x in ("active", "ativo"):
        return "ativo"
    return "inativo"


def format_barbearia_address(row: Dict[str, Any]) -> str:
    parts = [
        row.get("logradouro"),
        row.get("numero"),
        row.get("bairro"),
        row.get("cidade"),
        row.get("estado"),
    ]
    return ", ".join(str(p) for p in parts if p)


def serialize_barbearia_for_template(
    cursor: Any, row: Dict[str, Any], barbearia_id: int, fetch_barbearia_opening_hours: FetchHoursFn
) -> Dict[str, Any]:
    """Monta o JSON esperado pelas páginas (nome, endereço, photos, etc.) mantendo campos crus do banco."""
    out: Dict[str, Any] = {k: _json_safe(v) for k, v in row.items()}
    out["name"] = row.get("nome_barbearia") or ""
    out["address"] = format_barbearia_address(row)
    out["phone"] = row.get("whatsapp") or row.get("telefone_fixo") or ""
    out["description"] = row.get("descricao") or ""
    out["opening_hours"] = fetch_barbearia_opening_hours(cursor, barbearia_id)

    cursor.execute(
        "SELECT nome_servico FROM servicos WHERE barbearia_id = %s AND status = 'ativo' ORDER BY nome_servico",
        (barbearia_id,),
    )
    out["services"] = []
    for r in cursor.fetchall():
        if isinstance(r, dict):
            out["services"].append(r.get("nome_servico"))
        else:
            out["services"].append(r[0])

    photos: List[str] = []
    if row.get("foto_perfil"):
        photos.append(str(row["foto_perfil"]))
    cursor.execute(
        "SELECT foto FROM barbearia_fotos WHERE barbearia_id = %s ORDER BY id LIMIT 20",
        (barbearia_id,),
    )
    for r in cursor.fetchall():
        foto = r.get("foto") if isinstance(r, dict) else r[0]
        if foto and str(foto) not in photos:
            photos.append(str(foto))
    out["photos"] = photos

    cursor.execute(
        "SELECT AVG(avaliacao_nota) AS media_nota FROM agendamentos WHERE barbearia_id = %s AND avaliacao_nota IS NOT NULL",
        (barbearia_id,),
    )
    avg_row = cursor.fetchone()
    media = None
    if isinstance(avg_row, dict):
        media = avg_row.get("media_nota")
    elif avg_row:
        media = avg_row[0]
    out["rating"] = float(media) if media is not None else 5.0
    out["price_level"] = 2
    return out


def register_extended_api(app: Flask) -> None:
    """Registra rotas adicionais no app Flask."""

    def _db():
        import app as app_module

        return app_module.get_db_connection()

    @app.route("/api/barbearias/<int:barbearia_id>/servicos", methods=["GET"])
    def list_servicos_barbearia(barbearia_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT id, nome_servico AS nome_servico, preco, duracao_minutos, categoria, descricao, status
               FROM servicos WHERE barbearia_id = %s ORDER BY id""",
            (barbearia_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        servicos = []
        for r in rows:
            servicos.append(
                {
                    "id": r["id"],
                    "name": r["nome_servico"],
                    "price": float(r["preco"] or 0),
                    "duration": int(r["duracao_minutos"] or 30),
                    "category": r.get("categoria") or "",
                    "description": r.get("descricao") or "",
                    "status": servico_db_status_to_api(r.get("status")),
                }
            )
        return jsonify({"success": True, "servicos": servicos})

    @app.route("/api/barbearias/<int:barbearia_id>/servicos", methods=["POST"])
    def create_servico_barbearia(barbearia_id: int):
        data = request.get_json() or {}
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        cur.execute("SELECT id FROM barbearias WHERE id = %s", (barbearia_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Barbearia não encontrada."}), 404
        try:
            st = servico_api_status_to_db(data.get("status"))
            cur.execute(
                """INSERT INTO servicos (barbearia_id, nome_servico, preco, duracao_minutos, categoria, descricao, status)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (
                    barbearia_id,
                    data.get("name"),
                    data.get("price"),
                    data.get("duration"),
                    data.get("category"),
                    data.get("description") or "",
                    st,
                ),
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.close()
            conn.close()
            return jsonify({"success": True, "id": new_id})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/api/barbearias/<int:barbearia_id>/servicos/<int:servico_id>", methods=["PUT"])
    def update_servico_barbearia(barbearia_id: int, servico_id: int):
        data = request.get_json() or {}
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT id FROM servicos WHERE id = %s AND barbearia_id = %s",
            (servico_id, barbearia_id),
        )
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Serviço não encontrado."}), 404
        fields = []
        params: List[Any] = []
        if "name" in data:
            fields.append("nome_servico = %s")
            params.append(data["name"])
        if "price" in data:
            fields.append("preco = %s")
            params.append(data["price"])
        if "duration" in data:
            fields.append("duracao_minutos = %s")
            params.append(data["duration"])
        if "category" in data:
            fields.append("categoria = %s")
            params.append(data["category"])
        if "description" in data:
            fields.append("descricao = %s")
            params.append(data["description"])
        if "status" in data:
            fields.append("status = %s")
            params.append(servico_api_status_to_db(data["status"]))
        if not fields:
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Nada para atualizar."})
        params.extend([servico_id, barbearia_id])
        try:
            cur.execute(
                f"UPDATE servicos SET {', '.join(fields)} WHERE id = %s AND barbearia_id = %s",
                tuple(params),
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/api/barbearias/<int:barbearia_id>/servicos/<int:servico_id>", methods=["DELETE"])
    def delete_servico_barbearia(barbearia_id: int, servico_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM servicos WHERE id = %s AND barbearia_id = %s",
            (servico_id, barbearia_id),
        )
        conn.commit()
        deleted = cur.rowcount
        cur.close()
        conn.close()
        if not deleted:
            return jsonify({"success": False, "message": "Serviço não encontrado."}), 404
        return jsonify({"success": True})

    @app.route("/api/barbearias/<int:barbearia_id>/horarios", methods=["GET"])
    def get_horarios_barbearia(barbearia_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT dia_semana, status FROM horarios_status WHERE barbearia_id = %s", (barbearia_id,))
        status_map = {r["dia_semana"]: r["status"] for r in cur.fetchall()}
        cur.execute(
            "SELECT id, dia_semana, inicio, fim FROM horarios_slots WHERE barbearia_id = %s ORDER BY dia_semana, inicio",
            (barbearia_id,),
        )
        slots_rows = cur.fetchall()
        cur.close()
        conn.close()
        schedule: Dict[str, Any] = {}
        for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
            st = status_map.get(day, "closed")
            schedule[day] = {"status": st if st in ("open", "closed") else "closed", "slots": []}
        for r in slots_rows:
            day = r["dia_semana"]
            if day not in schedule:
                continue
            schedule[day]["slots"].append(
                {"id": r["id"], "start": _as_hhmm(r["inicio"]), "end": _as_hhmm(r["fim"])}
            )
        for day in schedule:
            if schedule[day]["slots"] and schedule[day]["status"] != "open":
                schedule[day]["status"] = "open"
        return jsonify({"success": True, "schedule": schedule})

    @app.route("/api/barbearias/<int:barbearia_id>/horarios", methods=["POST"])
    def post_horarios_barbearia(barbearia_id: int):
        data = request.get_json() or {}
        schedule = data.get("schedule") or {}
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        cur.execute("SELECT id FROM barbearias WHERE id = %s", (barbearia_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Barbearia não encontrada."}), 404
        try:
            cur.execute("DELETE FROM horarios_slots WHERE barbearia_id = %s", (barbearia_id,))
            cur.execute("DELETE FROM horarios_status WHERE barbearia_id = %s", (barbearia_id,))
            for day, block in schedule.items():
                if day not in (
                    "monday",
                    "tuesday",
                    "wednesday",
                    "thursday",
                    "friday",
                    "saturday",
                    "sunday",
                ):
                    continue
                st = block.get("status", "closed")
                cur.execute(
                    "INSERT INTO horarios_status (barbearia_id, dia_semana, status) VALUES (%s,%s,%s)",
                    (barbearia_id, day, st if st in ("open", "closed") else "closed"),
                )
                if st == "open":
                    for slot in block.get("slots") or []:
                        start = slot.get("start")
                        end = slot.get("end")
                        if not start or not end:
                            continue
                        cur.execute(
                            """INSERT INTO horarios_slots (barbearia_id, dia_semana, inicio, fim)
                               VALUES (%s,%s,%s,%s)""",
                            (barbearia_id, day, start, end),
                        )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    def _appointment_duration_minutes(cursor: Any, servico_id: int) -> int:
        cursor.execute(
            "SELECT duracao_minutos FROM servicos WHERE id = %s",
            (servico_id,),
        )
        r = cursor.fetchone()
        if not r:
            return 30
        if isinstance(r, dict):
            v = r.get("duracao_minutos")
        else:
            v = r[0]
        return int(v) if v is not None else 30

    def _intervals_overlap(a0: int, a1: int, b0: int, b1: int) -> bool:
        return a0 < b1 and b0 < a1

    @app.route("/api/barbearias/<int:barbearia_id>/availability", methods=["GET"])
    def get_availability(barbearia_id: int):
        date_str = request.args.get("date")
        duration = int(request.args.get("duration") or 30)
        if not date_str:
            return jsonify({"success": False, "message": "Parâmetro date é obrigatório."}), 400
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "message": "Data inválida."}), 400

        # Configurações de antecedência (2 horas)
        MIN_LEAD_TIME_MINUTES = 120
        # Ajuste para Horário de Brasília (UTC-3) para servidores em nuvem (Render/Railway)
        now_utc = datetime.utcnow()
        now_br = now_utc - timedelta(hours=3)
        today_br = now_br.date()
        now_minutes = now_br.hour * 60 + now_br.minute

        if d < today_br:
            return jsonify({"success": False, "message": "Não é possível agendar para datas passadas."}), 400

        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)

        # 1. Busca a capacidade real da barbearia (quantidade de barbeiros configurada)
        cur.execute("SELECT quantidade_barbeiros FROM barbearias WHERE id = %s", (barbearia_id,))
        b_info = cur.fetchone()
        capacity = int(b_info["quantidade_barbeiros"]) if b_info and b_info.get("quantidade_barbeiros") else 1

        day_key = _weekday_key(d)
        cur.execute(
            "SELECT status FROM horarios_status WHERE barbearia_id = %s AND dia_semana = %s",
            (barbearia_id, day_key),
        )
        st = cur.fetchone()
        if st and st.get("status") == "closed":
            cur.close()
            conn.close()
            return jsonify({"success": True, "slots": [], "message": "Fechado neste dia"})

        cur.execute(
            "SELECT inicio, fim FROM horarios_slots WHERE barbearia_id = %s AND dia_semana = %s ORDER BY inicio",
            (barbearia_id, day_key),
        )
        ranges = cur.fetchall()
        if not ranges:
            cur.close()
            conn.close()
            return jsonify({"success": True, "slots": [], "message": "Sem horários configurados"})

        # 2. Busca agendamentos com JOIN para obter a duração, essencial para calcular sobreposições
        cur.execute(
            """SELECT a.horario_inicio, s.duracao_minutos, a.status
               FROM agendamentos a
               JOIN servicos s ON a.servico_id = s.id
               WHERE a.barbearia_id = %s AND a.data_agendamento = %s
               AND LOWER(a.status) NOT IN ('cancelado','cancelled')""",
            (barbearia_id, date_str),
        )
        busy_rows = cur.fetchall()
        busy: List[Tuple[int, int]] = []
        for br in busy_rows:
            hm = _as_hhmm(br["horario_inicio"])
            t0 = _time_to_minutes(hm)
            dur = int(br["duracao_minutos"] or 30)
            busy.append((t0, t0 + dur))

        print(f"[DEBUG] Disponibilidade | Barbearia: {barbearia_id} | Data: {date_str} | "
              f"Capacidade: {capacity} barbeiros | Agendamentos existentes: {len(busy)}")

        slots_out: List[str] = []
        step = 30
        for rng in ranges:
            o0 = _time_to_minutes(_as_hhmm(rng["inicio"]))
            o1 = _time_to_minutes(_as_hhmm(rng["fim"]))
            t = o0
            while t + duration <= o1:
                # Bloqueio de antecedência mínima se o agendamento for para hoje
                if d == today_br and t < (now_minutes + MIN_LEAD_TIME_MINUTES):
                    t += step
                    continue

                # 3. Lógica de Capacidade Múltipla:
                # Conta quantos agendamentos concorrentes existem no intervalo [t, t + duration]
                overlapping_count = sum(1 for b0, b1 in busy if _intervals_overlap(t, t + duration, b0, b1))
                
                # O horário está disponível se o total de ocupações for menor que o número de barbeiros
                if overlapping_count < capacity:
                    slots_out.append(_minutes_to_time(t))
                else:
                    # Log para monitorar bloqueios por excesso de agendamentos
                    # print(f"[DEBUG] Slot {_minutes_to_time(t)} BLOQUEADO: {overlapping_count} ocupados para {capacity} barbeiros")
                    pass

                t += step

        cur.close()
        conn.close()
        return jsonify({"success": True, "slots": slots_out})

    @app.route("/api/agendamentos", methods=["POST"])
    def create_agendamento():
        data = request.get_json() or {}
        required = ("cliente_id", "barbearia_id", "servico_id", "data_agendamento", "horario_inicio")
        if not all(data.get(k) for k in required):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Preencha cliente, barbearia, serviço, data e horário",
                    }
                ),
                400,
            )
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        try:
            cur.execute(
                """INSERT INTO agendamentos
                   (cliente_id, barbearia_id, servico_id, data_agendamento, horario_inicio, status, valor_total, observacoes)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (
                    int(data["cliente_id"]),
                    int(data["barbearia_id"]),
                    int(data["servico_id"]),
                    data["data_agendamento"],
                    data["horario_inicio"],
                    "pendente",
                    data.get("valor_total"),
                    data.get("observacoes"),
                ),
            )
            conn.commit()
            new_id = cur.lastrowid
            cur.close()
            conn.close()
            return jsonify(
                {
                    "success": True,
                    "id": new_id,
                    "message": "Agendamento realizado com sucesso",
                }
            )
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 500

    @app.route("/api/agendamentos/<int:agendamento_id>", methods=["PUT"])
    def update_agendamento(agendamento_id: int):
        data = request.get_json() or {}
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM agendamentos WHERE id = %s", (agendamento_id,))
        row = cur.fetchone()
        if not row:
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": "Agendamento não encontrado."}), 404

        updates = []
        params: List[Any] = []
        if "status" in data:
            updates.append("status = %s")
            params.append(api_status_to_db(str(data["status"])))
        if "date" in data:
            updates.append("data_agendamento = %s")
            params.append(data["date"])
        if "time" in data:
            updates.append("horario_inicio = %s")
            params.append(data["time"])
        if "notes" in data:
            updates.append("observacoes = %s")
            params.append(data["notes"])
        if "price" in data:
            updates.append("valor_total = %s")
            params.append(data["price"])

        if not updates:
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Nada para atualizar."})

        if "date" in data or "time" in data or "notes" in data:
            name_parts = (data.get("notes") or "").split(",")
            first = name_parts[0].strip() if name_parts else ""
            if first:
                cur.execute(
                    """SELECT id FROM servicos WHERE barbearia_id = %s AND LOWER(TRIM(nome_servico)) = LOWER(TRIM(%s)) LIMIT 1""",
                    (row["barbearia_id"], first),
                )
                svc = cur.fetchone()
                if svc:
                    updates.append("servico_id = %s")
                    params.append(int(svc["id"]))

        params.append(agendamento_id)
        try:
            cur.execute(
                f"UPDATE agendamentos SET {', '.join(updates)} WHERE id = %s",
                tuple(params),
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Agendamento atualizado."})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/api/agendamentos/<int:agendamento_id>/avaliacao", methods=["POST"])
    def post_avaliacao(agendamento_id: int):
        data = request.get_json() or {}
        rating = data.get("rating")
        comment = data.get("comment") or ""
        if rating is None:
            return jsonify({"success": False, "message": "Avaliação obrigatória."}), 400
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE agendamentos SET avaliacao_nota = %s, avaliacao_comentario = %s WHERE id = %s",
                (rating, comment, agendamento_id),
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/api/agendamentos/<int:agendamento_id>/resposta", methods=["POST"])
    def post_resposta_avaliacao(agendamento_id: int):
        data = request.get_json() or {}
        texto = (data.get("resposta") or "").strip()
        if not texto:
            return jsonify({"success": False, "message": "Resposta vazia."}), 400
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        try:
            cur.execute(
                """UPDATE agendamentos SET resposta_barbearia = %s, data_resposta = NOW() WHERE id = %s""",
                (texto, agendamento_id),
            )
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"success": True})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            return jsonify({"success": False, "message": str(e)}), 400

    def _serialize_review_row(r: Dict[str, Any], for_barber: bool) -> Dict[str, Any]:
        nome = r.get("nome_cliente") or "Cliente"
        initials = (nome[0] or "?").upper()
        has_resp = bool(r.get("resposta_barbearia"))
        base = {
            "id": r["id"],
            "clientName": nome,
            "clientInitial": initials,
            "service": r.get("nome_servico") or "",
            "text": r.get("avaliacao_comentario") or "",
            "rating": int(float(r["avaliacao_nota"])) if r.get("avaliacao_nota") is not None else 0,
            "date": str(r.get("data_agendamento") or "")[:10],
            "hasResponse": has_resp,
            "response": r.get("resposta_barbearia"),
            "responseDate": r.get("data_resposta"),
        }
        if not for_barber:
            return {
                "clientName": base["clientName"],
                "rating": base["rating"],
                "text": base["text"],
                "hasResponse": base["hasResponse"],
                "response": base["response"],
                "responseDate": base["responseDate"],
            }
        return base

    @app.route("/api/barbearias/<int:barbearia_id>/avaliacoes", methods=["GET"])
    def list_avaliacoes(barbearia_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT a.id, a.data_agendamento, a.avaliacao_nota, a.avaliacao_comentario,
                      a.resposta_barbearia, a.data_resposta, c.nome_completo AS nome_cliente,
                      s.nome_servico
               FROM agendamentos a
               JOIN clientes c ON c.id = a.cliente_id
               JOIN servicos s ON s.id = a.servico_id
               WHERE a.barbearia_id = %s AND a.avaliacao_nota IS NOT NULL
               ORDER BY a.data_agendamento DESC, a.id DESC""",
            (barbearia_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        # Formato completo (id, clientInitial, etc.) para dashboard da barbearia e compatível com a página pública
        reviews = [_serialize_review_row(dict(r), True) for r in rows]
        return jsonify({"success": True, "reviews": reviews})

    @app.route("/api/clientes/<int:cliente_id>/agendamentos", methods=["GET"])
    def list_agendamentos_cliente(cliente_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT a.id, a.barbearia_id, a.data_agendamento, a.horario_inicio, a.status,
                      a.valor_total, a.observacoes, a.avaliacao_nota, a.criado_em,
                      b.nome_barbearia AS nome_barbearia, s.nome_servico, s.duracao_minutos
               FROM agendamentos a
               JOIN barbearias b ON b.id = a.barbearia_id
               JOIN servicos s ON s.id = a.servico_id
               WHERE a.cliente_id = %s
               ORDER BY a.data_agendamento DESC, a.horario_inicio DESC""",
            (cliente_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r["id"],
                    "barbearia_id": r["barbearia_id"],
                    "barbearia": r.get("nome_barbearia") or "",
                    "service": r.get("nome_servico") or "",
                    "date": str(r.get("data_agendamento") or "")[:10],
                    "time": _as_hhmm(r.get("horario_inicio")),
                    "status": db_status_to_api(r.get("status")),
                    "price": float(r["valor_total"] or 0),
                    "duration": int(r.get("duracao_minutos") or 30),
                    "notes": r.get("observacoes") or "",
                    "rating": float(r["avaliacao_nota"]) if r.get("avaliacao_nota") is not None else None,
                    "created_at": r.get("criado_em"),
                }
            )
        return jsonify({"success": True, "agendamentos": out})

    @app.route("/api/barbearias/<int:barbearia_id>/agendamentos", methods=["GET"])
    def list_agendamentos_barbearia(barbearia_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT a.id, a.data_agendamento, a.horario_inicio, a.status, a.valor_total, a.observacoes,
                      c.nome_completo AS nome_cliente, c.telefone AS telefone_cliente
               FROM agendamentos a
               JOIN clientes c ON c.id = a.cliente_id
               WHERE a.barbearia_id = %s
               ORDER BY a.data_agendamento DESC, a.horario_inicio DESC""",
            (barbearia_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        out = []
        for r in rows:
            obs = r.get("observacoes") or ""
            services = [s.strip() for s in obs.split(",") if s.strip()] or ["Serviço"]
            out.append(
                {
                    "id": r["id"],
                    "clientName": r.get("nome_cliente") or "",
                    "clientPhone": r.get("telefone_cliente") or "",
                    "date": str(r.get("data_agendamento") or "")[:10],
                    "time": _as_hhmm(r.get("horario_inicio")),
                    "services": services,
                    "totalPrice": float(r["valor_total"] or 0),
                    "status": db_status_to_api(r.get("status")),
                    "notes": obs,
                    "createdBy": "cliente",
                }
            )
        return jsonify({"success": True, "agendamentos": out})

    @app.route("/api/clientes/<int:cliente_id>/favoritos", methods=["GET"])
    def list_favoritos(cliente_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT b.id, b.nome_barbearia, b.whatsapp, b.cidade, b.estado, b.logradouro, b.numero, b.bairro,
                      (SELECT AVG(a.avaliacao_nota) FROM agendamentos a WHERE a.barbearia_id = b.id AND a.avaliacao_nota IS NOT NULL) AS avg_rating,
                      (SELECT COUNT(*) FROM agendamentos a2 WHERE a2.barbearia_id = b.id AND a2.avaliacao_nota IS NOT NULL) AS review_count
               FROM cliente_favoritos f
               JOIN barbearias b ON b.id = f.barbearia_id
               WHERE f.cliente_id = %s
               ORDER BY b.nome_barbearia""",
            (cliente_id,),
        )
        rows = cur.fetchall()
        favoritos = []
        for r in rows:
            bid = int(r["id"])
            cur.execute(
                "SELECT nome_servico FROM servicos WHERE barbearia_id = %s AND status = 'ativo' LIMIT 12",
                (bid,),
            )
            svc_names = []
            for x in cur.fetchall():
                if isinstance(x, dict):
                    svc_names.append(x.get("nome_servico"))
                else:
                    svc_names.append(x[0])
            rating = float(r["avg_rating"]) if r.get("avg_rating") is not None else 4.5
            favoritos.append(
                {
                    "id": str(bid),
                    "name": r.get("nome_barbearia") or "",
                    "address": format_barbearia_address(r),
                    "rating": round(rating, 1),
                    "totalReviews": int(r.get("review_count") or 0),
                    "distance": "N/A",
                    "phone": r.get("whatsapp") or "",
                    "hours": "Ver perfil",
                    "priceRange": "—",
                    "services": svc_names,
                }
            )
        cur.close()
        conn.close()
        return jsonify({"success": True, "favoritos": favoritos})

    @app.route("/api/clientes/<int:cliente_id>/favoritos", methods=["POST"])
    def add_favorito(cliente_id: int):
        data = request.get_json() or {}
        bid = data.get("barbearia_id")
        if bid is None:
            return jsonify({"success": False, "message": "barbearia_id obrigatório."}), 400
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT IGNORE INTO cliente_favoritos (cliente_id, barbearia_id) VALUES (%s,%s)",
                (cliente_id, int(bid)),
            )
            conn.commit()
            if cur.rowcount == 0:
                cur.close()
                conn.close()
                return jsonify({"success": True, "message": "Já estava nos favoritos."}), 200
            cur.close()
            conn.close()
            return jsonify({"success": True, "message": "Adicionado aos favoritos."})
        except Exception as e:
            conn.rollback()
            cur.close()
            conn.close()
            if "Duplicate" in str(e) or "1062" in str(e):
                return jsonify({"success": True, "message": "Já favoritado."}), 200
            return jsonify({"success": False, "message": str(e)}), 400

    @app.route("/api/clientes/<int:cliente_id>/favoritos/<int:barbearia_id>", methods=["DELETE"])
    def remove_favorito(cliente_id: int, barbearia_id: int):
        conn = _db()
        if not conn:
            return jsonify({"success": False, "message": "Erro DB"}), 500
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM cliente_favoritos WHERE cliente_id = %s AND barbearia_id = %s",
            (cliente_id, barbearia_id),
        )
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True, "message": "Removido dos favoritos."})
