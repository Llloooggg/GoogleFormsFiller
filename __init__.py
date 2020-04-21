from selenium import webdriver
import time
import requests
import random
import re
import progressbar
from bs4 import BeautifulSoup
from datetime import datetime


def button_by_text(text):  # получение кнопки по тексту на ней

    try:
        button = driver.find_element_by_xpath(
            f'//*[contains(text(), "{text}")]')
        button.click()
        return True
    except Exception:
        return False


def get_profession():  # получение случайной профессии в РФ, где 1 и 2 диапазон - профессии рабочих, 2 и 3 - должности служащих

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
            return profession
        except:
            pass


def profile_maker():

    global areas_of_activity

    forms_list = driver.find_elements_by_class_name(
        'freebirdFormviewerViewItemsItemItem')  # получение форм со страницы
    for form in forms_list:

        header = form.find_element_by_class_name(
            'freebirdFormviewerViewItemsItemItemHeader').text  # получение заголовка формы

        if header[-1:] == '*':
            header = header[:-2]

        if header == 'Укажите Ваш пол':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            button = random.choices(buttons_list, [0.7, 0.3], k=1)[0]
            button.click()

        elif header == 'Укажите Ваш возраст (полных лет)':
            age = random.randint(18, 56)
            field = form.find_elements_by_class_name('quantumWizTextinputPaperinputInput')[
                0]  # получение полей для ввода с формы
            field.click()
            field.send_keys(age)

        elif header == 'Укажите Ваше образование (возможно несколько вариантов)':
            buttons_list = form.find_elements_by_class_name(
                'quantumWizTogglePapercheckboxEl')  # получение чекбоксов с формы
            buttons_list[random.randint(0, 4)].click()

        elif header == 'Выберите из списка основную сферу деятельности организации, в которой Вы сейчас работаете':
            form.find_elements_by_class_name(
                'quantumWizMenuPaperselectOption')[0].click()
            coin = random.randint(3, 24)
            variants_list = form.find_element_by_xpath(
                f'//*[@id="mG61Hd"]/div/div/div[2]/div[5]/div/div[2]/div[2]/div[{coin}]')  # перебор элементов выпадающего списка
            variants_list.click()
            time.sleep(3)

        elif header == 'Укажите Ваш стаж работы (полных лет) в указанной организации':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            buttons_list[random.randint(0, len(buttons_list) - 1)].click()

        elif header == 'Укажите тип Вашей должности':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            buttons_list[random.randint(0, len(buttons_list) - 1)].click()

        elif header == 'Укажите название Вашей должности':
            field = form.find_elements_by_class_name('quantumWizTextinputPapertextareaInput')[
                0]  # получение полей для ввода с формы
            field.click()
            field.send_keys(get_profession())

        elif header == 'Укажите Ваш стаж работы в текущей должности (полных лет)':
            buttons_list = form.find_elements_by_class_name(
                'appsMaterialWizToggleRadiogroupRadioButtonContainer')  # получение кнопок-радио с формы
            buttons_list[random.randint(0, len(buttons_list) - 1)].click()


def bulldozer():

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


if __name__ == '__main__':

    url = 'https://docs.google.com/forms/d/1f716YOLUrKhtjTlR4hYiEWkgwjqylR5fCPxWsHQKJqY'
    resnondents = int(input('Введите желаемое число респондентов: '))

    driver = webdriver.Firefox()

    with progressbar.ProgressBar(max_value=resnondents) as bar:
        for i in range(resnondents):

            bar.update(i)

            driver.get(url)

            button_by_text('Далее')

            profile_maker()

            while True:

            	if button_by_text('Далее'):
	            	bulldozer()
	           	else:
	            	button_by_text('Отправить')

    driver.close()
