import discord
import os
import json
from datetime import datetime

from utils import convert_role_to_name


class Vouch:
    file_path = None
    loaded_vouches = None
    backup_data = None
    vouch_keys = ["vouch", "description", "attributed_by", "date"]

    @staticmethod
    def load_vouches():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        Vouch.file_path = os.path.join(script_dir, "vouches.json")
        with open(Vouch.file_path, 'r') as file:
            Vouch.file = file
            Vouch.loaded_vouches = json.load(file)

    @staticmethod
    def get_user_vouches(user_id: int):
        user_id_str = str(user_id)
        if user_id_str not in Vouch.loaded_vouches:
            return {}

        return Vouch.loaded_vouches[str(user_id)]

    @staticmethod
    def get_description(user_id: int, vouch_id: str):
        if not Vouch._check_keys(user_id, vouch_id):
            return None

        return Vouch.loaded_vouches[str(user_id)][vouch_id]["description"]

    @staticmethod
    def get_attributed_by(user_id: int, vouch_id: str):
        if not Vouch._check_keys(user_id, vouch_id):
            return None

        return int(Vouch.loaded_vouches[str(user_id)][vouch_id]["attributed_by"])

    @staticmethod
    def get_date(user_id: int, vouch_id: str):
        if not Vouch._check_keys(user_id, vouch_id):
            return None

        return Vouch.loaded_vouches[str(user_id)][vouch_id]["date"]

    @staticmethod
    def get_vouch(user_id: int, vouch_id: str):
        if not Vouch._check_keys(user_id, vouch_id):
            return None

        return Vouch.loaded_vouches[str(user_id)][vouch_id]["vouch"]

    @staticmethod
    def user_has_vouches(user_id: int):
        if str(user_id) in Vouch.loaded_vouches:
            return True

        return False

    @staticmethod
    def add_vouch(user: discord.User, description: str, attributed_by_user_id: int):
        user_vouches = Vouch.loaded_vouches.get(str(user.id))

        if not user_vouches:
            last_key = 0
        else:
            last_key = int(list(user_vouches.keys())[-1])

        vouch = Vouch.get_vouch_name(user)
        if not vouch:
            print("Error: _get_vouch_name returned None")
            return

        Vouch._add_vouch_keys(user.id, last_key + 1, vouch, description, attributed_by_user_id)

    @staticmethod
    def delete_vouch(user_id: int, vouch_id: str):
        user_vouches = Vouch.loaded_vouches.get(str(user_id))
        if not user_vouches:
            return None

        Vouch._delete_vouch_key(user_vouches, user_id, vouch_id)

        return True

    @staticmethod
    def get_vouch_name(user):
        role_name = convert_role_to_name(user)
        if role_name == "Divisao 1":
            return "Divisao 1A"
        elif role_name == "Divisao 2":
            return "Divisao 1"
        elif role_name == "Divisao 3":
            return "Divisao 2"
        elif role_name == "Casual":
            return "Divisao 3"
        else:
            return None

    @staticmethod
    def _check_keys(user_id: int, vouch_id: str):
        user_id_str = str(user_id)

        if user_id_str not in Vouch.loaded_vouches:
            return False

        if vouch_id not in Vouch.loaded_vouches[user_id_str]:
            return False

        return True

    @staticmethod
    def _add_vouch_keys(user_id: int, vouch_id: int, vouch: str, description: str, attributed_by: int):
        try:
            Vouch._save_backup()

            with open(Vouch.file_path, 'w') as file:
                user_id_str = str(user_id)
                if user_id_str not in Vouch.loaded_vouches:
                    Vouch.loaded_vouches[user_id_str] = {}

                Vouch.loaded_vouches[user_id_str][str(vouch_id)] = {
                    Vouch.vouch_keys[0]: vouch,
                    Vouch.vouch_keys[1]: description,
                    Vouch.vouch_keys[2]: str(attributed_by),
                    Vouch.vouch_keys[3]: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
    def _delete_vouch_key(user_vouches, user_id: int, vouch_id: str):
        try:
            Vouch._save_backup()

            with open(Vouch.file_path, 'w') as file:
                del user_vouches[vouch_id]
                if len(user_vouches.keys()) == 0:
                    del Vouch.loaded_vouches[str(user_id)]

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

            Vouch.loaded_vouches = Vouch.backup_data
        except Exception as e:
            print(f"Erro ao fazer backup dos vouches: {e}")
