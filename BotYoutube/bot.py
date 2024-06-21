"""
WARNING:

Please make sure you install the bot with `pip install -e .` in order to get all the dependencies
on your Python environment.

Also, if you are using PyCharm or another IDE, make sure that you use the SAME Python interpreter
as your IDE.

If you get an error like:
```
ModuleNotFoundError: No module named 'botcity'
```

This means that you are likely using a different Python interpreter than the one used to install the bot.
To fix this, you can either:
- Use the same interpreter as your IDE and install your bot with `pip install --upgrade -r requirements.txt`
- Use the same interpreter as the one used to install the bot (`pip install --upgrade -r requirements.txt`)

Please refer to the documentation for more information at https://documentation.botcity.dev/
"""


# Import for the Web Bot
from botcity.web import WebBot, Browser, By

# Import for integration with BotCity Maestro SDK
from botcity.maestro import *

from datetime import datetime

# Disable errors if we are not connected to Maestro
BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main():
    try:
        maestro = BotMaestroSDK.from_sys_args()
        execution = maestro.get_execution()

        username = maestro.get_credential(label="login_db", key="username")
        password = maestro.get_credential(label="login_db", key="password")

        bot = WebBot()

        # Configurando para rodar em modo headless
        bot.headless = False

        # Setando Firefox
        bot.browser = Browser.FIREFOX

        # Setando caminho do WebDriver
        bot.driver_path = r"resources\geckodriver.exe"

        maestro.alert(
            task_id=execution.task_id,
            title="BotYoutube - Inicio",
            message="Estamos iniciando o processo",
            alert_type=AlertType.INFO
        )

        canal = execution.parameters.get("canal", "pythonbrasiloficial")
        bot.browse(f"https://www.youtube.com/@{canal}")

        # Buscando elemento da página
        elemento_inscritos = bot.find_element("subscriber-count", By.ID)

        # Coletando o conteúdo de texto do elemento
        inscritos = elemento_inscritos.text

        # Printando os dados coletados
        print(f"Inscritos => {inscritos}")

        status = AutomationTaskFinishStatus.SUCCESS
        message = "Tarefa BotYoutube finalizada com sucesso"

        # Forcando uma exception para registrarmos um erro
        # x = 0/0

    except Exception as ex:
        # Salvando captura de tela do erro
        bot.save_screenshot("erro.png")

        # Salvando uma captura de tela
        bot.save_screenshot("captura.png")

        # Enviando para a plataforma com o nome "Captura Canal..."
        maestro.post_artifact(
            task_id=execution.task_id,
            artifact_name=f"Captura Canal {canal}.png",
            filepath="captura.png"
        )
    
        maestro.new_log_entry(
            activity_label="EstatisticasYoutube",
            values = {
                "data_hora": datetime.now().strftime("%Y-%m-%d_%H-%M"),
                "canal": canal,
                "inscritos": inscritos
            }
        )

        # Dicionario de tags adicionais
        tags = {"canal": canal}

        # Registrando o erro
        maestro.error(
            task_id=execution.task_id,
            exception=ex,
            screenshot="erro.png",
            tags=tags
        )

        status = AutomationTaskFinishStatus.FAILED
        message = "Tarefa BotYoutube finalizada com falha"

    finally:
        bot.wait(2000)
        bot.stop_browser()

        # Finalizando a tarefa
        maestro.finish_task(
            task_id=execution.task_id,
            status=status,
            message=message
        )

    # maestro.finish_task(
    #     task_id=execution.task_id,
    #     status=AutomationTaskFinishStatus.SUCCESS,
    #     message="Task Finished with Success.",
    #     total_items=100, # Total number of items processed
    #     processed_items=90, # Number of items processed successfully
    #     failed_items=10 # Number of items processed with failure
    # )

def not_found(label):
    print(f"Element not found: {label}")


if __name__ == '__main__':
    main()
