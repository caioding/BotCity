# Importe das bibliotecas utilizadas
from botcity.maestro import *
from botcity.web import Browser, By, WebBot

BotMaestroSDK.RAISE_NOT_CONNECTED = False

def main():
    # Instanciando o SDK do Orquestrador
    maestro = BotMaestroSDK.from_sys_args()
    execution = maestro.get_execution()

    # Cria alerta de inicio da tarefa
    maestro.alert(
        task_id=execution.task_id,
        title="Iniciando",
        message="Iniciando o cadastro de candidatos no OrangeHRM",
        alert_type=AlertType.INFO
    )

    # Instancia do bot
    bot = WebBot()

    # Configura o modo headless para False
    bot.headless = False

    # Define o navegador a ser utilizado
    bot.browser = Browser.FIREFOX

    # Define o caminho do webdriver
    bot.driver_path = bot.get_resource_abspath("geckodriver.exe")

    # Contador de itens processados
    total_itens = 0
    itens_sucesso = 0
    itens_falhos = 0

    try:
        # Acessa o site OrangeHRM
        bot.browse("https://opensource-demo.orangehrmlive.com/web/index.php/auth/login")
        bot.maximize_window()

        # Obtendo credenciais armazenadas no Orquestrador
        username = maestro.get_credential(label="login_orangehrm", key="username")
        password = maestro.get_credential(label="login_orangehrm", key="password")

        # Função que faz o login
        login(bot, username, password)

        # Navegar até a página de cadastro de candidatos
        element_recruitment = "li.oxd-main-menu-item-wrapper:nth-child(5) > a:nth-child(1)"
        element_add = "button.oxd-button--secondary:nth-child(1)"

        bot.find_element(element_recruitment, By.CSS_SELECTOR).click()
        bot.find_element(element_add, By.CSS_SELECTOR).click()

        # Obtendo a referência do Datapool
        datapool = maestro.get_datapool(label="candidatos_orange")

        # Enquanto houverem itens para serem processados
        while datapool.has_next():
            # Retorna o proximo item disponivel do Datapool
            item = datapool.next(task_id=execution.task_id)

            if item is None:
                # Se o item for nulo, encerra o loop
                break

            # Contador total
            total_itens += 1

            # Faz o cadastro do item (candidato) na plataforma OrangeHRM
            candidato_cadastrado = cadastro(bot, item)

            if candidato_cadastrado:
                # Reporta para o Datapool que o item foi processado com sucesso
                item.report_done()

                # Soma ao contador de itens processados
                itens_sucesso += 1

                # Registrando uma entrada de log com o status do cadastro do candidato
                maestro.new_log_entry(
                    activity_label="controle_cadastro",
                    values = {
                        "nome": item.get_value("full_name"),
                        "status": "Sucesso"
                    } 
                )
            else:
                # Reporta para o Datapool que ocorreu uma falha no processamento do item
                item.report_error()

                # Soma ao contador de itens com falha
                itens_falhos += 1

                # Registrando uma entrada de log com o status do cadastro do candidato
                maestro.new_log_entry(
                    activity_label="controle_cadastro",
                    values = {
                        "nome": item.get_value("full_name"),
                        "status": "Falha - dados incompletos"
                    } 
                )

        if itens_falhos > 0:
            # Define o status de finalização da tarefa
            message = 'Alguns candidatos não foram cadastrados, veja o log.'
            status = AutomationTaskFinishStatus.PARTIALLY_COMPLETED
        else:
            # Define o status de finalização da tarefa
            message = 'Candidatos cadastrados com sucesso.'
            status = AutomationTaskFinishStatus.SUCCESS

    except Exception as e:
        # Reportando erro para o Orquestrador
        maestro.error(
            task_id=execution.task_id,
            exception=e,
            screenshot="captura.png"
        )
        # Define o status de finalização da tarefa
        message = 'Erro ao cadastrar candidatos. ' + str(e)
        status = AutomationTaskFinishStatus.FAILED

    finally:
        # Encerra o navegador e finaliza a execução
        bot.wait(3000)
        bot.stop_browser()

        # Finalizando a tarefa e reportando os itens processados
        maestro.finish_task(
            task_id=execution.task_id,
            status=status,
            message=message,
            total_items=total_itens,
            processed_items=itens_sucesso,
            failed_items=itens_falhos
        )


def login(bot: WebBot, username, password):
    element_user = "div.oxd-form-row:nth-child(2) > div:nth-child(1) > div:nth-child(2) > input:nth-child(1)"
    element_password = "div.oxd-form-row:nth-child(3) > div:nth-child(1) > div:nth-child(2) > input:nth-child(1)"
    element_button = ".oxd-button"

    bot.wait(2000)
    bot.find_element(element_user, By.CSS_SELECTOR).send_keys(username)
    bot.find_element(element_password, By.CSS_SELECTOR).send_keys(password)
    bot.wait(1000)
    bot.find_element(element_button, By.CSS_SELECTOR).click()


def cadastro(bot: WebBot, candidato):
    try:
        element_first_name = ".orangehrm-firstname"
        element_middle_name = ".orangehrm-middlename"
        element_last_name = ".orangehrm-lastname"
        element_vacancy = "i.bi-caret-down-fill:nth-child(1)"
        element_options = "div.oxd-select-option > span:nth-child(1)"
        element_email = "div.oxd-form-row:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > input:nth-child(1)"
        element_contact = "div.oxd-form-row:nth-child(3) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > input:nth-child(1)"
        element_keywords = "div.oxd-form-row:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > input:nth-child(1)"
        element_save = "button.oxd-button:nth-child(3)"
        element_recruitment = "li.oxd-main-menu-item-wrapper:nth-child(5)"
        element_add = "button.oxd-button--secondary:nth-child(1)"
        element_field_required = '//span[@class="oxd-text oxd-text--span oxd-input-field-error-message oxd-input-group__message"]'

        # Preenche as informações do candidato
        primeiro_nome = candidato['full_name'].split(" ")[0]
        nome_meio = candidato['full_name'].split(" ")[1]
        ultimo_nome = candidato['full_name'].split(" ")[2:]

        if ultimo_nome:
            bot.find_element(element_first_name, By.CSS_SELECTOR).send_keys(primeiro_nome)
            bot.wait(1000)

            bot.find_element(element_middle_name, By.CSS_SELECTOR).send_keys(nome_meio)
            bot.wait(1000)

            bot.find_element(element_last_name, By.CSS_SELECTOR).send_keys(ultimo_nome[-1])
            bot.wait(1000)
        else:
            bot.find_element(element_first_name, By.CSS_SELECTOR).send_keys(primeiro_nome)
            bot.wait(1000)
            bot.find_element(element_last_name, By.CSS_SELECTOR).send_keys(ultimo_nome[-1])
            bot.wait(1000)

        bot.find_element(element_vacancy, By.CSS_SELECTOR).click()
        bot.wait(1000)

        options = bot.find_elements(element_options, By.CSS_SELECTOR)
        for option in options:
            if option.text == candidato['vacancy']:
                option.click()
                bot.wait(1000)
                break

        bot.find_element(element_email, By.CSS_SELECTOR).send_keys(candidato['email'])
        bot.wait(1000)
        bot.find_element(element_contact, By.CSS_SELECTOR).send_keys(candidato['contact_number'])
        bot.wait(1000)
        bot.find_element(element_keywords, By.CSS_SELECTOR).send_keys(candidato['keywords'])
        bot.wait(1000)

        # Salvar
        bot.find_element(element_save, By.CSS_SELECTOR).click()
        bot.wait(1000)

        # Validando se algum campo obrigatório não foi preenchido
        candidato_cadastrado = True
        required_fields_error = bot.find_elements(element_field_required, By.XPATH)
        if required_fields_error:
            candidato_cadastrado = False

        # Voltar página
        bot.find_element(element_recruitment, By.CSS_SELECTOR).click()
        bot.find_element(element_add, By.CSS_SELECTOR).click()
        bot.wait(1000)
    except:
        candidato_cadastrado = False

    return candidato_cadastrado


if __name__ == '__main__':
    main()
