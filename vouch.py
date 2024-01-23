import os
import json
from datetime import datetime


class Vouch:
    file_path = None
    loaded_vouches = None
    backup_data = None
    vouch_keys = ["name", "description", "attributed_by", "date"]

    @staticmethod
    def load_vouches():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        Vouch.file_path = os.path.join(script_dir, "vouches.json")
        with open(Vouch.file_path, 'r') as file:
            Vouch.file = file
            Vouch.loaded_vouches = json.load(file)

    @staticmethod
    def get_user_vouches(user_id: int):
        return Vouch.loaded_vouches[str(user_id)]

    @staticmethod
    def add_vouch(user_id: int, name: str, description: str, attributed_by_user_id: int):
        user_vouches = Vouch.loaded_vouches.get(str(user_id))

        if not user_vouches:
            last_key = 0
        else:
            last_key = int(list(user_vouches.keys())[-1])

        Vouch._add_vouch_keys(user_id, last_key + 1, name, description, attributed_by_user_id)

    @staticmethod
    def _add_vouch_keys(user_id: int, vouch_id: int, name: str, description: str, attributed_by: int):
        try:
            Vouch._save_backup()

            with open(Vouch.file_path, 'w') as file:
                user_id_str = str(user_id)
                if user_id_str not in Vouch.loaded_vouches:
                    Vouch.loaded_vouches[user_id_str] = {}

                Vouch.loaded_vouches[user_id_str][str(vouch_id)] = {
                    Vouch.vouch_keys[0]: name,
                    Vouch.vouch_keys[1]: description,
                    Vouch.vouch_keys[2]: str(attributed_by),
                    Vouch.vouch_keys[3]: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }

                file.truncate(0)
                file.seek(0)
                json.dump(Vouch.loaded_vouches, file, indent=3)
        except FileNotFoundError as e:
            print("O arquivo não foi encontrado")
        except PermissionError as e:
            print("Sem permissões suficientes para acessar/modificar o arquivo")
            Vouch._do_backup()
        except json.JSONDecodeError as e:
            print("Erro ao decodificar o conteúdo JSON do arquivo")
            Vouch._do_backup()
        except Exception as e:
            print(f"Ocorreu uma exceção não tratada: {e}")
            Vouch._do_backup()

    @staticmethod
    def _save_backup():
        try:
            with open(Vouch.file_path, 'r') as file:
                Vouch.backup_data = json.load(file)
        except FileNotFoundError as e:
            print("O arquivo não foi encontrado enquanto salvando o backup")
        except json.JSONDecodeError as e:
            print("Erro ao decodificar o conteúdo JSON do arquivo enquanto salvando o backup")
        except Exception as e:
            print(f"Ocorreu uma exceção não tratada: {e}")

    @staticmethod
    def _do_backup():
        try:
            with open(Vouch.file_path, 'w') as file:
                json.dump(Vouch.backup_data, file, indent=3)
        except Exception as e:
            print(f"Erro ao fazer backup: {e}")

