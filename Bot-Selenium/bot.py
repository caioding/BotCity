from botcity.maestro import *

from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service

BotMaestroSDK.RAISE_NOT_CONNECTED = False


def main():
    # Instancia do Orquestrador
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    try:
        # Seta o caminho do WebDriver do Firefox
        service = Service(executable_path=r"geckodriver.exe")

        # Cria uma instância do Navegador
        bot = webdriver.Firefox(service=service)

        # Acessa página Practice Test Automation
        bot.get("https://practicetestautomation.com/practice-test-login/")

        username = maestro.get_credential(label="login_automatico", key="username")
        password = maestro.get_credential(label="login_automatico", key="password")

        # Busca pelo elemento input de nome de usuário
        input_username = bot.find_element(By.ID, "username")
        # Ação de digitar
        input_username.send_keys(username)

        # Busca pelo elemento input de senha
        input_password = bot.find_element(By.ID, "password")
        # Ação de digitar
        input_password.send_keys(password)

        # Busca pelo elemento botão submit
        input_button = bot.find_element(By.ID, "submit")
        # Ação de clicar
        input_button.click()

        # Aguarda 3 segundos para garantir que carregou a página com resultado
        sleep(3)

        # Busca pela confirmação de login
        logged = bot.find_element(By.CSS_SELECTOR, ".post-title")
        # Imprime o texto da confirmação
        print(logged.text)        

        # Busca pelo elemento botão log out
        logout = bot.find_element(By.CSS_SELECTOR, ".wp-block-button__link")
        # Ação de clicar
        logout.click()

        # Busca pelo titulo login para garantir que fez o logout
        bot.find_element(By.CSS_SELECTOR, "#login > h2:nth-child(1)")

        # Define status e mensagem de finalização da tarefa com sucesso
        finish_status = AutomationTaskFinishStatus.SUCCESS
        finish_message = "Tarefa bot-selenium finalizada com sucesso"

    except Exception as ex:
        # Busca pelo elemento de mensagem de erro
        error_alert = bot.find_element(By.ID, "error")
        # print(error_alert.text) remove
        # print(ex) remove

        # Grava uma captura de tela
        bot.save_screenshot("captura.png")

        # Define quais informações extras 
        # serão carregadas no BotCity Maestro
        tags = {
            "username": username,
            "password": password,
            "error": error_alert.text
            }

        # Registrando o erro
        maestro.error(
            task_id=execution.task_id,
            exception=ex,
            tags=tags,
            screenshot="captura.png"
        )

        # Define status de finalização da tarefa com falha
        finish_status = AutomationTaskFinishStatus.FAILED
        finish_message = f"Tarefa bot-selenium finalizada com falha: {error_alert.text}"

    finally:
        # Finaliza fechando o navegador
        bot.quit()

        # Finaliza tarefa com o BotMaestro
        maestro.finish_task(
            task_id=execution.task_id,
            status=finish_status,
            message=finish_message
        )

        # Imprime mensagem de finalização
        print("Finally")

if __name__ == "__main__":
    main()