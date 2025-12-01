"""
DATABASE.PY - SISTEMA DE DATABASE JSON
=======================================
Gerencia todas as operações de dados
"""

import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class JSONDatabase:
    """Sistema de database usando JSON"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.files = {
            "users": os.path.join(data_dir, "users.json"),
            "appointments": os.path.join(data_dir, "appointments.json"),
            "professionals": os.path.join(data_dir, "professionals.json"),
            "settings": os.path.join(data_dir, "settings.json"),
            "medical_history": os.path.join(data_dir, "medical_history.json"),
            "strand_tests": os.path.join(data_dir, "strand_tests.json"),
            "attendance_records": os.path.join(data_dir, "attendance_records.json"),
            "consultations": os.path.join(data_dir, "consultations.json"),
            "system_config": os.path.join(data_dir, "system_config.json")
        }
        
        self._initialize_files()
        self._create_defaults()
    
    def _initialize_files(self):
        """Inicializa todos os arquivos JSON"""
        for key, file_path in self.files.items():
            if not os.path.exists(file_path):
                if key in ["settings", "system_config"]:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({}, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=2)
    
    def _create_defaults(self):
        """Cria dados padrão"""
        self._create_default_professionals()
        self._create_default_settings()
    
    def _create_default_professionals(self):
        """Cria profissionais padrão"""
        professionals_data = self._read_file("professionals")
        
        if not professionals_data:
            default_professionals = [
                {
                    "id": "1",
                    "nome": "Maria Silva",
                    "tipo_servico": "cabelo",
                    "especialidades": ["corte feminino", "coloração", "mechas", "luzes", "hidratação"],
                    "is_active": True
                },
                {
                    "id": "2",
                    "nome": "João Santos",
                    "tipo_servico": "cabelo",
                    "especialidades": ["corte masculino", "barba", "coloração", "retoque raiz"],
                    "is_active": True
                },
                {
                    "id": "3",
                    "nome": "Ana Costa",
                    "tipo_servico": "cabelo",
                    "especialidades": ["corte feminino", "penteados", "tratamentos", "hidratação profunda"],
                    "is_active": True
                },
                {
                    "id": "4",
                    "nome": "Carla Mendes",
                    "tipo_servico": "unha",
                    "especialidades": ["manicure", "pedicure", "nail art", "unhas gel"],
                    "is_active": True
                },
                {
                    "id": "5",
                    "nome": "Paula Oliveira",
                    "tipo_servico": "unha",
                    "especialidades": ["manicure", "unhas de gel", "decoração", "alongamento"],
                    "is_active": True
                }
            ]
            self._write_file("professionals", default_professionals)
    
    def _create_default_settings(self):
        """Cria settings padrão"""
        settings_data = self._read_settings_file()
        
        if not settings_data:
            default_settings = {
                "salon_name": "Salão IA",
                "logo_url": "/static/images/default_logo.png",
                "logo_filename": None,
                "colors": {
                    "primary": "#6366f1",
                    "secondary": "#8b5cf6",
                    "accent": "#ec4899",
                    "background": "#ffffff",
                    "text": "#1f2937"
                },
                "updated_at": datetime.now().isoformat(),
                "updated_by": None
            }
            self._write_settings_file(default_settings)
    
    # ===== MÉTODOS AUXILIARES =====
    
    def _read_file(self, file_key: str) -> List[Dict]:
        """Lê arquivo JSON (lista)"""
        try:
            with open(self.files[file_key], 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_file(self, file_key: str, data: List[Dict]):
        """Escreve arquivo JSON (lista)"""
        with open(self.files[file_key], 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _read_settings_file(self) -> Dict:
        """Lê settings"""
        try:
            with open(self.files["settings"], 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_settings_file(self, data: Dict):
        """Escreve settings"""
        with open(self.files["settings"], 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    # ===== DOCUMENT OPERATIONS (para system_config) =====
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict]:
        """Obtém documento de uma coleção"""
        try:
            file_path = self.files.get(collection, os.path.join(self.data_dir, f"{collection}.json"))
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data.get(doc_id) or data
                    return None
            return None
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def update_document(self, collection: str, doc_id: str, data: Dict):
        """Atualiza documento em uma coleção"""
        file_path = self.files.get(collection, os.path.join(self.data_dir, f"{collection}.json"))
        
        try:
            existing = {}
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing = {}
        
        if isinstance(existing, dict):
            existing[doc_id] = data
        else:
            existing = {doc_id: data}
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2, default=str)
    
    # ===== SETTINGS =====
    
    def get_settings(self) -> Dict:
        """Obtém settings"""
        settings = self._read_settings_file()
        if not settings:
            self._create_default_settings()
            settings = self._read_settings_file()
        return settings
    
    def update_settings(self, settings_data: Dict, admin_id: Optional[str] = None) -> Dict:
        """Atualiza settings"""
        current_settings = self.get_settings()
        
        for key, value in settings_data.items():
            if value is not None:
                current_settings[key] = value
        
        current_settings["updated_at"] = datetime.now().isoformat()
        if admin_id:
            current_settings["updated_by"] = admin_id
        
        self._write_settings_file(current_settings)
        return current_settings
    
    # ===== USERS =====
    
    def create_user(self, user_data: Dict) -> Dict:
        """Cria usuário"""
        users = self._read_file("users")
        user_data["id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.now().isoformat()
        user_data["is_active"] = True
        if "role" not in user_data:
            user_data["role"] = "cliente"
        users.append(user_data)
        self._write_file("users", users)
        return user_data
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Busca usuário por email"""
        users = self._read_file("users")
        return next((u for u in users if u.get("email") == email), None)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Busca usuário por ID"""
        users = self._read_file("users")
        return next((u for u in users if u.get("id") == user_id), None)
    
    def get_all_users(self) -> List[Dict]:
        """Lista todos os usuários"""
        return self._read_file("users")
    
    def update_user(self, user_id: str, update_data: Dict) -> Optional[Dict]:
        """Atualiza usuário"""
        users = self._read_file("users")
        updated_user = None
        
        for i, user in enumerate(users):
            if user.get("id") == user_id:
                for key, value in update_data.items():
                    if value is not None:
                        user[key] = value
                user["updated_at"] = datetime.now().isoformat()
                updated_user = user
                users[i] = user
                break
        
        if updated_user:
            self._write_file("users", users)
        return updated_user
    
    def update_user_photo(self, user_id: str, photo_path: str) -> Optional[Dict]:
        """Atualiza foto do usuário"""
        return self.update_user(user_id, {"foto_perfil": photo_path})
    
    # ===== PROFESSIONALS =====
    
    def get_all_professionals(self) -> List[Dict]:
        """Lista todos profissionais"""
        return self._read_file("professionals")
    
    def get_professionals_by_type(self, tipo_servico: str) -> List[Dict]:
        """Filtra profissionais por tipo"""
        professionals = self._read_file("professionals")
        return [p for p in professionals if p.get("tipo_servico") == tipo_servico and p.get("is_active", True)]
    
    def get_professional_by_id(self, professional_id: str) -> Optional[Dict]:
        """Busca profissional por ID"""
        professionals = self._read_file("professionals")
        return next((p for p in professionals if p.get("id") == professional_id), None)
    
    # ===== APPOINTMENTS =====
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        """Cria agendamento"""
        appointments = self._read_file("appointments")
        appointment_data["id"] = str(uuid.uuid4())
        appointment_data["created_at"] = datetime.now().isoformat()
        if "status" not in appointment_data:
            appointment_data["status"] = "pendente"
        appointments.append(appointment_data)
        self._write_file("appointments", appointments)
        return appointment_data
    
    def get_appointment_by_id(self, appointment_id: str) -> Optional[Dict]:
        """Busca agendamento por ID"""
        appointments = self._read_file("appointments")
        return next((a for a in appointments if a.get("id") == appointment_id), None)
    
    def get_appointments_by_datetime(self, data_hora: str, profissional_id: str) -> List[Dict]:
        """Busca agendamentos por data/hora e profissional"""
        appointments = self._read_file("appointments")
        return [a for a in appointments 
                if a.get("data_hora") == data_hora 
                and a.get("profissional_id") == profissional_id
                and a.get("status") not in ["cancelado", "concluido"]]
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Lista agendamentos do usuário"""
        appointments = self._read_file("appointments")
        return [a for a in appointments if a.get("cliente_id") == user_id]
    
    def get_all_appointments(self) -> List[Dict]:
        """Lista todos agendamentos"""
        return self._read_file("appointments")
    
    def get_professional_appointments(self, profissional_id: str, data: Optional[str] = None) -> List[Dict]:
        """Lista agendamentos do profissional"""
        appointments = self._read_file("appointments")
        result = [a for a in appointments if a.get("profissional_id") == profissional_id]
        
        if data:
            result = [a for a in result if a.get("data_hora", "").startswith(data)]
        
        return result
    
    def get_appointments_by_professional(self, profissional_id: str) -> List[Dict]:
        """Lista agendamentos do profissional (alias)"""
        return self.get_professional_appointments(profissional_id)
    
    def update_appointment(self, appointment_id: str, update_data: Dict) -> Optional[Dict]:
        """Atualiza agendamento"""
        appointments = self._read_file("appointments")
        updated_appointment = None
        
        for i, apt in enumerate(appointments):
            if apt.get("id") == appointment_id:
                for key, value in update_data.items():
                    apt[key] = value
                apt["updated_at"] = datetime.now().isoformat()
                updated_appointment = apt
                appointments[i] = apt
                break
        
        if updated_appointment:
            self._write_file("appointments", appointments)
        return updated_appointment
    
    def update_appointment_status(self, appointment_id: str, status: str, profissional_id: Optional[str] = None) -> Optional[Dict]:
        """Atualiza status do agendamento"""
        appointments = self._read_file("appointments")
        updated_appointment = None
        
        for i, apt in enumerate(appointments):
            if apt.get("id") == appointment_id:
                apt["status"] = status
                apt["updated_at"] = datetime.now().isoformat()
                
                if status == "confirmado":
                    apt["confirmed_at"] = datetime.now().isoformat()
                    if profissional_id:
                        apt["confirmed_by"] = profissional_id
                elif status == "concluido":
                    apt["completed_at"] = datetime.now().isoformat()
                
                updated_appointment = apt
                appointments[i] = apt
                break
        
        if updated_appointment:
            self._write_file("appointments", appointments)
        return updated_appointment
    
    # ===== MEDICAL HISTORY =====
    
    def create_medical_history(self, history_data: Dict) -> Dict:
        """Cria histórico médico"""
        histories = self._read_file("medical_history")
        history_data["id"] = str(uuid.uuid4())
        history_data["created_at"] = datetime.now().isoformat()
        history_data["data_atualizacao"] = datetime.now().isoformat()
        histories.append(history_data)
        self._write_file("medical_history", histories)
        return history_data
    
    def get_medical_history_by_client(self, cliente_id: str) -> Optional[Dict]:
        """Busca histórico médico do cliente"""
        histories = self._read_file("medical_history")
        return next((h for h in histories if h.get("cliente_id") == cliente_id), None)
    
    def update_medical_history(self, cliente_id: str, history_data: Dict) -> Optional[Dict]:
        """Atualiza histórico médico"""
        histories = self._read_file("medical_history")
        updated_history = None
        
        for i, history in enumerate(histories):
            if history.get("cliente_id") == cliente_id:
                for key, value in history_data.items():
                    if value is not None:
                        history[key] = value
                history["data_atualizacao"] = datetime.now().isoformat()
                updated_history = history
                histories[i] = history
                break
        
        if updated_history:
            self._write_file("medical_history", histories)
        return updated_history
    
    # ===== STRAND TESTS =====
    
    def create_strand_test(self, test_data: Dict) -> Dict:
        """Cria teste de mecha"""
        tests = self._read_file("strand_tests")
        test_data["id"] = str(uuid.uuid4())
        test_data["created_at"] = datetime.now().isoformat()
        tests.append(test_data)
        self._write_file("strand_tests", tests)
        return test_data
    
    def get_strand_tests_by_client(self, cliente_id: str) -> List[Dict]:
        """Lista testes de mecha do cliente"""
        tests = self._read_file("strand_tests")
        return [t for t in tests if t.get("cliente_id") == cliente_id]
    
    # ===== ATTENDANCE RECORDS =====
    
    def create_attendance_record(self, record_data: Dict) -> Dict:
        """Cria ficha de atendimento"""
        records = self._read_file("attendance_records")
        record_data["id"] = str(uuid.uuid4())
        record_data["created_at"] = datetime.now().isoformat()
        records.append(record_data)
        self._write_file("attendance_records", records)
        return record_data
    
    def get_attendance_records_by_client(self, cliente_id: str) -> List[Dict]:
        """Lista fichas de atendimento do cliente"""
        records = self._read_file("attendance_records")
        return [r for r in records if r.get("cliente_id") == cliente_id]
    
    def get_attendance_record_by_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Busca ficha por agendamento"""
        records = self._read_file("attendance_records")
        return next((r for r in records if r.get("appointment_id") == appointment_id), None)
    
    def update_attendance_record(self, record_id: str, update_data: Dict) -> Optional[Dict]:
        """Atualiza ficha de atendimento"""
        records = self._read_file("attendance_records")
        updated_record = None
        
        for i, record in enumerate(records):
            if record.get("id") == record_id:
                for key, value in update_data.items():
                    if value is not None:
                        record[key] = value
                record["updated_at"] = datetime.now().isoformat()
                updated_record = record
                records[i] = record
                break
        
        if updated_record:
            self._write_file("attendance_records", records)
        return updated_record
    
    # ===== CONSULTATIONS =====
    
    def create_consultation(self, consultation_data: Dict) -> Dict:
        """Cria consulta"""
        consultations = self._read_file("consultations")
        consultation_data["id"] = str(uuid.uuid4())
        consultation_data["created_at"] = datetime.now().isoformat()
        consultations.append(consultation_data)
        self._write_file("consultations", consultations)
        return consultation_data
    
    def get_consultations_by_client(self, cliente_id: str) -> List[Dict]:
        """Lista consultas do cliente"""
        consultations = self._read_file("consultations")
        return [c for c in consultations if c.get("cliente_id") == cliente_id]


# Instância global
db = JSONDatabase()
