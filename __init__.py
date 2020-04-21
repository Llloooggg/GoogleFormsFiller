from selenium import webdriver


url = intput('Введите ссылку на форму: ')

driver = webdriver.Firefox()
driver.get(url)

def button_by_text(text): # получение кнопки по тексту на ней
	try:
		button = driver.find_element_by_xpath(f'//*[contains(text(), "{text}")]')
		button.click()
		return True
	except Exception:
		return False


button_by_text('Далее')

forms_list = driver.find_elements_by_class_name('freebirdFormviewerViewItemsItemItem') # получение форм со страницы
for form in forms_list:
	header = form.find_element_by_class_name('freebirdFormviewerViewItemsItemItemHeader').text # получение заголовка формы
	if header[-1:] == '*':
		header = header[:-2]
	buttons_list = form.find_elements_by_class_name('appsMaterialWizToggleRadiogroupRadioButtonContainer') # получение кнопок-радио с формы
	buttons_list[4].click()

button_by_text('Далее')
button_by_text('Отправить')

# driver.close()
