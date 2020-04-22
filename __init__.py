#!venv/bin/python3

from selenium import webdriver
import time
import requests
import random
import re
import progressbar
from os import path
from bs4 import BeautifulSoup
from datetime import datetime

options = webdriver.firefox.options.Options()
options.headless = True
driver = webdriver.Firefox(options=options)

logPath = './respondents.log'

banList = []
if path.exists('./ban_list.txt'):
    f = open('./ban_list.txt')
    for line in f.readlines():
        banList.append(line.lower())
    f.close()

professionsList = []
if path.exists('./professions_list.txt'):
    f = open('./professions_list.txt')
    for line in f.readlines():
        banList.append(line.lower())
    f.close()

weightsList = {}
if path.exists('./weights_list.txt'):
    f = open('./weights_list.txt')
    for line in f.readlines():
        question = line.split(':')[0]
        if question[-1:] == ' ':
            question = question[:-1]
        weights = line.split(':')[1].split()
        weightsList[question] = weights
    f.close()


def log(header, data=None):
    with open(logPath, 'a') as f:
        f.write(datetime.now().strftime('[%X] ') + header + '\n')
        if data:
            for key, value in data.items():
                f.write(f'           {key}: {value}\n')
        f.write('\n')


def button_by_text(text):  # получение кнопки по тексту на ней

    try:
        button = driver.find_element_by_xpath(
            f'//*[contains(text(), "{text}")]')
        button.click()
        return True
    except Exception:
        return False


def get_profession():  # получение случайной профессии в РФ, где 1 и 2 диапазон - профессии рабочих, 2 и 3 - должности служащих

    global banList

    coin = (1, 2, 3, 4)
    coin = random.choices(coin, [0.1, 0.1, 0.4, 0.4], k=1)[0]

    while True:

        if coin == 1:
            code = random.randint(10003, 19975)
        elif coin == 2:
            code = random.randint(30018, 33270)
        elif coin == 3:
            code = random.randint(20001, 27933)
        else:
            code = random.randint(40064, 47110)

        page = requests.get(f'http://okpdtr.ru/?s={code}').text
        soup = BeautifulSoup(page, features='html.parser')
        try:
            profession = soup.findAll("div", {"class": "my_col2"})[1]
            profession = re.sub(r'\([^()]*\)', '', profession.get_text())

            if not banList:
                return profession
            if not_in_ban_list(profession):
                return profession

        except:
            pass


def not_in_ban_list(word):

    global banList

    wordLowReg = word.lower()  # проверка на наличие слов из бан-листа
    for badWord in banList:
        if badWord in wordLowReg:
            return False
    return True


def profile_maker():

    global driver

    profile = {}

    forms_list = driver.find_elements_by_class_name(
        'freebirdFormviewerViewItemsItemItem')  # получение форм со страницы
    for form in forms_list:

        header = form.find_element_by_class_name(
            'freebirdFormviewerViewItemsItemItemHeader').text  # получение заголовка формы

        if header[-1:] == '*':
            header = header[:-2]

        if header == 'Укажите Ваш пол':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.7, 0.3], k=1)[0]
            button.click()

            profile['Пол'] = button.text

        elif header == 'Укажите Ваш возраст (полных лет)':
            age = random.randint(18, 56)
            field = form.find_elements_by_class_name('quantumWizTextinputPaperinputInput')[
                0]  # получение полей для ввода с формы
            field.click()
            field.send_keys(age)

            profile['Возраст'] = age

        elif header == 'Укажите Ваше образование (возможно несколько вариантов)':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение чекбоксов с формы
            coin = random.randint(0, 4)
            buttons_list[coin].click()

            profile['Образование'] = buttons_list[coin].text

        elif header == 'Выберите из списка основную сферу деятельности организации, в которой Вы сейчас работаете':
            form.find_elements_by_class_name(
                'quantumWizMenuPaperselectOption')[0].click()
            coin = random.randint(3, 24)
            time.sleep(0.5)
            variant = form.find_element_by_xpath(
                f'/html/body/div/div[2]/form/div/div/div[2]/div[5]/div/div[2]/div[2]/div[{coin}]')  # перебор элементов выпадающего списка

            profile['Сфера'] = variant.text

            variant.click()
            time.sleep(1.5)

        elif header == 'Укажите Ваш стаж работы (полных лет) в указанной организации':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение кнопок-радио с формы
            coin = random.randint(0, len(buttons_list) - 1)
            buttons_list[coin].click()

            profile['Стаж работы'] = buttons_list[coin].text

        elif header == 'Укажите тип Вашей должности':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение кнопок-радио с формы
            coin = random.randint(0, len(buttons_list) - 1)
            buttons_list[coin].click()

            profile['Тип должности'] = buttons_list[coin].text

        elif header == 'Укажите название Вашей должности':
            field = form.find_elements_by_class_name('quantumWizTextinputPapertextareaInput')[
                0]  # получение полей для ввода с формы
            field.click()
            profession = get_profession()
            field.send_keys(profession)

            profile['Должность'] = profession

        elif header == 'Укажите Ваш стаж работы в текущей должности (полных лет)':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение кнопок-радио с формы

            if profile['Стаж работы'] == 'Меньше 1 года':
                max_variant = 0
            elif profile['Стаж работы'] == 'От 1 года до 3 лет':
                max_variant = 1
            elif profile['Стаж работы'] == 'от 3 до 5 лет':
                max_variant = 2
            else:
                max_variant = 3
            coin = random.randint(0, max_variant)
            buttons_list[coin].click()

            profile['Стаж в текущей должности'] = buttons_list[coin].text

    log('Новорожденный', profile)


def another_profile_maker():

    global driver

    forms_list = driver.find_elements_by_class_name(
        'freebirdFormviewerViewItemsItemItem')  # получение форм со страницы

    for form in forms_list:

        header = form.find_element_by_class_name(
            'freebirdFormviewerViewItemsItemItemHeader').text  # получение заголовка формы

        if header[-1:] == '*':
            header = header[:-2]

        if header == 'Оцените свою удовлетворенность работой в команде группы разработчиков':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(
                buttons_list, [0, 0, 0.05, 0.07, 0.88], k=1)[0]
            button.click()

        elif header == 'Оцените свою готовность продолжать работу в своей команде':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(
                buttons_list, [0, 0, 0.01, 0.15, 0.84], k=1)[0]
            button.click()

        elif header == 'Укажите ваш стаж работы в IT-сфере':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledLabelWrapper')  # получение кнопок-радио с формы
            button = random.choices(
                buttons_list, [0.1, 0.49, 0.36, 0.05], k=1)[0]
            button.click()

            seniority = button.text

        elif header == 'Укажите занимаемую должность':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.72, 0.28], k=1)[0]
            button.click()

        elif header == 'В каком формате вы обычно работаете?':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.67, 0.31, 0.02], k=1)[0]
            button.click()

        elif header == 'Какой практикой (фреймворком) вы пользуетесь. Укажите 1-2 варианта':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение чекбоксов с формы

            coin = random.randint(1, 2)

            for i in range(coin):
                button = random.choices(
                    buttons_list, [0.4, 0.3, 0.1, 0.1, 0.1], k=1)[0]
            button.click()

        elif header == 'Укажите ваш возраст':
            ageRange_1 = (19, 24)
            ageRange_2 = (25, 28)
            ageRange_3 = (29, 44)

            if seniority == 'меньше 1 года':
                age = random.randint(ageRange_1[0], ageRange_1[1])
            elif seniority == 'от 1 года до 5 лет':
                pool = random.choices(
                    [ageRange_2, ageRange_3], [0.9, 0.1], k=1)[0]
                age = random.randint(pool[0], pool[1])
            elif seniority == 'от 5 лет до 10 лет':
                pool = random.choices(
                    [ageRange_2, ageRange_3], [0.7, 0.3], k=1)[0]
                age = random.randint(pool[0], pool[1])
            else:
                age = random.randint(ageRange_3[0], ageRange_3[1])

            field = form.find_elements_by_class_name('quantumWizTextinputPaperinputInput')[
                0]  # получение полей для ввода с формы
            field.click()
            field.send_keys(age)

        elif header == 'Укажите ваш пол':
            buttons_list = form.find_elements_by_class_name(
                'docssharedWizToggleLabeledContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.63, 0.37], k=1)[0]
            button.click()

        elif header == 'Укажите регион, в котором проживаете на данный момент':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.4, 0.3, 0.2, 0.1], k=1)[0]
            button.click()


def smart_buildozer():

    global driver

    forms_list = driver.find_elements_by_class_name(
        'freebirdFormviewerViewItemsItemItem')  # получение форм со страницы
    for form in forms_list:
        header = form.find_element_by_class_name(
            'freebirdFormviewerViewItemsItemItemHeader').text  # получение заголовка формы
        if header[-1:] == '*':
            header = header[:-2]

        buttons_list = form.find_elements_by_class_name(
            'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
        button = random.choices(buttons_list, weightsList[header], k=1)[0]
        button.click()


def bulldozer():

    global driver

    forms_list = driver.find_elements_by_class_name(
        'freebirdFormviewerViewItemsItemItem')  # получение форм со страницы
    for form in forms_list:
        header = form.find_element_by_class_name(
            'freebirdFormviewerViewItemsItemItemHeader').text  # получение заголовка формы
        if header[-1:] == '*':
            header = header[:-2]

        buttons_list = form.find_elements_by_class_name(
            'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
        buttons_list[random.randint(0, len(buttons_list) - 1)].click()


def main():

    global driver

    url = 'https://docs.google.com/forms/d/1f716YOLUrKhtjTlR4hYiEWkgwjqylR5fCPxWsHQKJqY'
    # url = int(input('Введите ссылку на форму: '))
    respondents = int(input(datetime.now().strftime(
        '[%X] ') + 'Введите желаемое число респондентов: '))

    print(datetime.now().strftime('[%X] ') + 'Начало')

    log('Новый опрос')

    with progressbar.ProgressBar(max_value=respondents) as bar:
        for i in range(respondents):
            bar.update(i)

            driver.get(url)

            button_by_text('Далее')
            profile_maker()

            while True:
                if button_by_text('Далее'):
                    bulldozer()
                else:
                    button_by_text('Отправить')
                    break

            log('Опрошен')

    driver.close()

    print(datetime.now().strftime('[%X] ') + 'Завершено')


def another_main():

    global driver

    url = 'https://docs.google.com/forms/d/e/1FAIpQLSeyfRwOKKsj7w7btlsH6qKhm6VtL0oprjUakUCkN8SPi_su4w/viewform'

    respondents = int(input(datetime.now().strftime(
        '[%X] ') + 'Введите желаемое число респондентов: '))

    with progressbar.ProgressBar(max_value=respondents) as bar:
        for i in range(respondents):
            bar.update(i)

            driver.get(url)

            button_by_text('Далее')
            another_profile_maker()
            button_by_text('Отправить')


if __name__ == '__main__':

    try:
        another_main()
    except:
        driver.close()

