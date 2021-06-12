# -*- encoding: utf-8 -*-
import action

infos = {
    "phone": "",
    "password": "",
    "sc_key": "",
    "tg_bot_key": "",
    "bark_key": "",
    "wecom_key": "",
    "push_plus_key": "",
}


def main_handler(event, context):
    action.task_pool(infos)


if __name__ == "__main__":
    main_handler("", "")
