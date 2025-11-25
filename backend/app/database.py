import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid


class JSONDatabase:
    """
    Classe para simular uma base de dados usando ficheiros JSON locais.
    Os dados são armazenados na pasta 'data'.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        # Garante que o diretório 'data' existe
        os.makedirs(data_dir, exist_ok=True)
        
        self.files = {
            "users": os.path.join(data_dir, "users.json"),
            "appointments": os.path.join(data_dir, "appointments.json"),
            "professionals": os.path.join(data_dir, "professionals.json")
        }
        
        self._initialize_files()
        self._create_default_professionals()
    
    def _initialize_files(self):
        """Garante que todos os ficheiros JSON existem e estão vazios ([])."""
        for file_path in self.files.values():
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    def _create_default_professionals(self):
        """Cria alguns profissionais por defeito se a lista estiver vazia."""
        professionals_data = self._read_file("professionals")
        
        if not professionals_data:
            default_professionals = [
                {
                    "id": str(uuid.uuid4()),
                    "nome": "Maria Silva",
                    "tipo_servico": "cabelo",
                    "especialidades": ["corte feminino", "coloração", "mechas"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "nome": "João Santos",
                    "tipo_servico": "cabelo",
                    "especialidades": ["corte masculino", "barba", "coloração"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "nome": "Carla Mendes",
                    "tipo_servico": "unha",
                    "especialidades": ["manicure", "pedicure", "nail art"]
                }
            ]
            self._write_file("professionals", default_professionals)
    
    def _read_file(self, file_key: str) -> List[Dict]:
        """Lê os dados de um ficheiro JSON."""
        try:
            with open(self.files[file_key], 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _write_file(self, file_key: str, data: List[Dict]):
        """Escreve os dados para um ficheiro JSON."""
        with open(self.files[file_key], 'w', encoding='utf-8') as f:
            # default=str é importante para serializar objetos como datetime ou UUID, caso sejam usados
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    # === Métodos de Utilizador ===
    
    def create_user(self, user_data: Dict) -> Dict:
        """Cria um novo utilizador, atribui um UUID e guarda na BD."""
        users = self._read_file("users")
        user_data["id"] = str(uuid.uuid4())
        user_data["created_at"] = datetime.now().isoformat()
        users.append(user_data)
        self._write_file("users", users)
        return user_data
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Procura um utilizador pelo email."""
        users = self._read_file("users")
        return next((u for u in users if u.get("email") == email), None)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Procura um utilizador pelo ID (UUID string)."""
        users = self._read_file("users")
        return next((u for u in users if u.get("id") == user_id), None)
        
    def update_user_photo(self, user_id: str, photo_url: str) -> Optional[Dict]:
        """Atualiza a foto de perfil de um utilizador e retorna o objeto atualizado."""
        users = self._read_file("users")
        updated_user = None
        
        for i, user in enumerate(users):
            if user.get("id") == user_id:
                user["foto_perfil"] = photo_url
                # Pode adicionar um campo de data de atualização
                user["updated_at"] = datetime.now().isoformat()
                updated_user = user
                users[i] = user # Atualiza a lista
                break
                
        self._write_file("users", users)
        return updated_user
    
    # === Métodos de Agendamento ===
    
    def create_appointment(self, appointment_data: Dict) -> Dict:
        """Cria um novo agendamento."""
        appointments = self._read_file("appointments")
        appointment_data["id"] = str(uuid.uuid4())
        appointment_data["created_at"] = datetime.now().isoformat()
        appointment_data["status"] = "agendado"
        appointments.append(appointment_data)
        self._write_file("appointments", appointments)
        return appointment_data
    
    def get_appointments_by_datetime(self, data_hora: str, profissional_id: str) -> List[Dict]:
        """Obtém agendamentos pela data/hora e profissional."""
        appointments = self._read_file("appointments")
        return [a for a in appointments 
                if a.get("data_hora") == data_hora 
                and a.get("profissional_id") == profissional_id
                and a.get("status") == "agendado"]
    
    def get_user_appointments(self, user_id: str) -> List[Dict]:
        """Obtém agendamentos de um utilizador específico."""
        appointments = self._read_file("appointments")
        return [a for a in appointments if a.get("usuario_id") == user_id]
    
    # === Métodos de Profissionais ===
    
    def get_all_professionals(self) -> List[Dict]:
        """Obtém todos os profissionais."""
        return self._read_file("professionals")
    
    def get_professionals_by_type(self, tipo_servico: str) -> List[Dict]:
        """Obtém profissionais por tipo de serviço."""
        professionals = self._read_file("professionals")
        return [p for p in professionals if p.get("tipo_servico") == tipo_servico]

# Inicialização da instância da base de dados JSON
db = JSONDatabase()