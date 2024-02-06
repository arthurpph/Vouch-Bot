import os
import json


class Config:
    loaded_config = None

    @staticmethod
    def load_config():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'config.json')

        with open(file_path, 'r') as f:
            Config.loaded_config = json.load(f)

    @staticmethod
    def get_casual_role_id():
        return int(Config.loaded_config["casualRoleId"])

    @staticmethod
    def get_div_roles_id():
        return [int(Config.loaded_config["div1RoleId"]),
                int(Config.loaded_config["div2RoleId"]),
                int(Config.loaded_config["div3RoleId"])]

    @staticmethod
    def get_div_council_roles_id():
        return [int(Config.loaded_config["div1CouncilRoleId"]),
                int(Config.loaded_config["div2CouncilRoleId"]),
                int(Config.loaded_config["div3CouncilRoleId"])]

    @staticmethod
    def get_staff_roles_id():
        return list(map(int, Config.loaded_config["staffRoles"]))

    @staticmethod
    def get_div_role_id(div: int):
        return int(Config.loaded_config[f"div{div}RoleId"])

    @staticmethod
    def get_div_council_role_id(div: int):
        return int(Config.loaded_config[f"div{div}CouncilRoleId"])

    @staticmethod
    def get_promotions_channel_id():
        return int(Config.loaded_config["promotionsChannelId"])

    @staticmethod
    def get_council_duels_role_id():
        return int(Config.loaded_config["councilDuelsRoleId"])

    @staticmethod
    def get_div_purge_forum_id(div: int):
        return int(Config.loaded_config[f"div{div}PurgeForumId"])
