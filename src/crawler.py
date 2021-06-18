

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys


def crawl(session_key: str, session_password: str, data: dict):

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
    driver.implicitly_wait(5)
    companies = {}
    failedTemp = []
    print('\n')

    loginField = driver.find_element_by_xpath("//input[@name='session_key']")
    passwdField = driver.find_element_by_xpath("//input[@name='session_password']")

    loginField.send_keys(session_key)
    passwdField.send_keys(session_password)

    submit = driver.find_element_by_xpath("//button[@type='submit']")
    submit.click()

    for comp in data:
        compID, company = comp
        companies[compID] = {'name': company}
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
                companies[compID]["link"] = resLink
                print(f"'{company}' gefunden: {resLink[33:-1]}")
            else:
                altResults = driver.find_elements_by_xpath("//a[@class='app-aware-link']")
                for res in altResults:
                    altResLink = res.get_attribute("href")
                    if "company" in altResLink:
                        companies[compID]["link"] = altResLink
                        print(f"'{company}' gefunden: {altResLink[33:-1]}\n")
                        break
        except NoSuchElementException as e:
            print(f"Für '{company}' wurde nichts gefunden.\n")
            driver.get_screenshot_as_file(f"../pics/fail-{company}.png")

    print(f"Daten von {len(companies)} Unternehmen werden gesammelt:\n")
    nums = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    ### Schleife, bei der die Liste der gerade erarbeiteten Links der Unternehmen/Organisationen durchgegangen wird
    assert isinstance(companies, dict)
    for compID in companies:
        company = companies[compID]['name']
        print(f"{company}...")
        if 'link' in companies[compID]:
            driver.get(companies[compID]['link'])
        else:
            failedTemp.append((compID, company))
            continue

        # hier wird nach der Zahl (in Textform!) der auf LinkdIn befindlichen Beschäftigten des gerade aufgerufenen
        # Unternehmens gesucht.
        try:
            empOnLIText = driver.find_element_by_xpath(
                "//span[@class='org-top-card-secondary-content__see-all t-normal t-black--light "
                "link-without-visited-state link-without-hover-state'] "
            ).text

            ### danach wird die im Text vorliegende Zahl isoliert
            empOnLI = []
            for char in empOnLIText:
                if char in nums:
                    empOnLI.append(char)
            empOnLI = "".join(empOnLI)

            ### und zum eintrag des Unternehmens hinzugefügt
            companies[compID]['empOnLI'] = empOnLI

        except NoSuchElementException:
            pass

        # jetzt die Zahl der Follower (Textform). wir suchen nach den html-tags, die in frage kommen, gespeichert in
        # der Liste temp:
        try:
            temp = driver.find_elements_by_xpath(
                "//div[@class='org-top-card-summary-info-list__info-item']"
            )
            followerText = ""

            ### prüfen, in welchem das wort "Follower" vorkommt
            for tag in temp:
                if "Follower" in tag.text:
                    followerText = tag.text
                    break

            ### und wenn wir eines gefunden haben, isolieren wir die zahl
            if followerText != "":
                followers = []
                for char in followerText:
                    if char in nums:
                        followers.append(char)
                followers = "".join(followers)

                ### und fügen es zum eintrag hinzu.
                companies[compID]['followers'] = followers

        except NoSuchElementException:
            pass

        ### jetzt wechseln wir auf die /about-Seite der company
        driver.get(f"{companies[compID]['link']}about/")

        ### suchen nach der ggf. angegebenen Company Size
        try:
            compSize = driver.find_element_by_xpath(
                "//dd[@class='org-about-company-module__company-size-definition-text t-14 t-black--light mb1 fl']").text

            ### und fügen sie zum Eintrag hinzu.
            companies[compID]['compSize'] = compSize

        except NoSuchElementException:
            pass

    driver.close()

    return companies, failedTemp

