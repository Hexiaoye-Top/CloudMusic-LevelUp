# -*- encoding: utf-8 -*-
import action

infos = {
    "phone": "",
    "password": "",
    # "sc_key": ["XXXX"],
    # "tg_bot_key": ["XXXX", "XXXXX"],
    # "bark_key": ["XXXX"],
    # "wecom_key": ["XXXX", "XXXX", "XXXX"],
    # "push_plus_key": ["XXXX"],
}


def main_handler(event, context):
    action.task_pool(infos)


if __name__ == "__main__":
    main_handler("", "")
