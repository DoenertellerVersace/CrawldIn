import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys


options = webdriver.ChromeOptions()

options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_experimental_option(
    'prefs', {
        'download.default_directory': '/tmp',
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    }
)

driver = webdriver.Chrome(options=options)
driver.get("https://www.linkedin.com/login/de?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
assert "Login" in driver.title
driver.set_window_size(1800, 1000)
driver.implicitly_wait(10)
compLinks = {}
companies = {}
print('\n')

# session_login = input("Bitte LinkedIn-E-Mail zur Anmeldung eingeben:\n")
# session_passwd = input("Bitte LinkedIn-Passwort zur Anmeldung eingeben:\n")
session_search = input("Bitte Unternehmen mit Komma getrennt eingeben:\n")
# print('\n')

loginField = driver.find_element_by_xpath("//input[@name='session_key']")
passwdField = driver.find_element_by_xpath("//input[@name='session_password']")


compList = session_search.split(",")


loginField.send_keys("jakob.hadulla@gmail.com")
passwdField.send_keys("TestPasswort0912")

submit = driver.find_element_by_xpath("//button[@type='submit']")
submit.click()
print("\n")

for company in compList:
    try:
        search = driver.find_element_by_xpath(
            "//input[@class='search-global-typeahead__input always-show-placeholder']"
        )
        search.clear()
        search.send_keys(company)
        print(f"Suche nach Unternehmen mit Namen '{company}'...")
        search.send_keys(Keys.ENTER)
    except ElementNotInteractableException:
        print('Suchfeld reagiert nicht! WHYYYYY')
    except NoSuchElementException:
        print('Suchfeld nicht gefunden!')


    try:
        result = driver.find_element_by_xpath("//a[@class='app-aware-link']")
        resLink = result.get_attribute("href")
        if "company" in resLink:
            compLinks[company] = resLink
            print(f"'{company}' gefunden: {resLink[33:-1]}\n")
        else:
            altResults = driver.find_elements_by_xpath("//a[@class='app-aware-link']")
            for res in altResults:
                altResLink = res.get_attribute("href")
                if "company" in altResLink:
                    compLinks[company] = altResLink
                    print(f"'{company}' gefunden: {altResLink[33:-1]}\n")
                    break
            # print(f"Für '{company}' wurde nichts gefunden.\n")
            # driver.get_screenshot_as_file(f"../pics/fail-{company}.png")
    except NoSuchElementException as e:
        print(f"Für '{company}' wurde nichts gefunden.\n")
        driver.get_screenshot_as_file(f"../pics/fail-{company}.png")

print(compLinks)




print("\n\n")

print(f"Mitarbeiter von {len(compLinks)} Unternehmen werden gezählt:\n")


for company in compLinks:
    if compLinks[company]:
        print(f"{compLinks[company][33:-1]}...")
        driver.get(compLinks[company])
        peopleText = ""
        try:
            peopleText = driver.find_element_by_xpath(
                "//span[@class='org-top-card-secondary-content__see-all t-normal t-black--light link-without-visited-state link-without-hover-state']").text
        except NoSuchElementException as e:
            print(e)


        driver.get(f"{compLinks[company]}about/")
        compSize = False
        try:
            compSize = driver.find_element_by_xpath(
            "//dd[@class='org-about-company-module__company-size-definition-text t-14 t-black--light mb1 fl']").text
        except NoSuchElementException:
            print("keine Information zu finden")

        companies[company] = compSize

    else:
        companies[company] = False

    # time.sleep(2)

nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# for company in companies:
#     if companies[company]:
#         new = []
#         for char in companies[company][0]:
#             if char in nums:
#                 new.append(char)
#         newText = "".join(new)
#         compNumberOfPeople = int(newText)
#         companies[company][0] = compNumberOfPeople

print(companies)

# time.sleep(2)

driver.close()

