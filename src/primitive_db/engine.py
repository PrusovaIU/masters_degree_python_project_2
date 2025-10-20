import prompt


def welcome() -> None:
    to_exit = False
    while not to_exit:
        print(
            "Первая попытка запустить проект!\n\n"
            "***\n"
            "<command> exit - выйти из программы\n"
            "<command> help - справочная информация"
        )
        command = prompt.string("Введите команду: ")
        if command == "exit":
            to_exit = True
