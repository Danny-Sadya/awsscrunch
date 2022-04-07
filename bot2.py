import time
from datetime import datetime
import os
import pandas
from random import randint
import json
import csv

from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait


class ScrunchScraper:
    def __init__(self, dargs):
        self.columns = ['Name', 'Biography', 'Email', 'Phone', 'Interests',
                        'Instagram', 'Instagram Followers', 'Instagram Views', 'YouTube', 'YouTube Followers',
                        'YouTube Views',
                        'Twitter', 'Twitter Followers', 'Twitter Views', 'Facebook', 'Facebook Followers',
                        'Facebook Views',
                        'TikTok', 'TikTok Followers', 'TikTok Views', 'Average Engagement', 'Average Engagement Rate',
                        'Topics', 'Estimated Costs Per Post', 'Audience Topics', 'Audience Hashtags', 'Audience Mentions',
                        'Global Regions', 'Countries', 'States', 'Regions', 'Cities/Towns/Suburbs', 'Audiene analysis']
        self.csv_file_name = None

        # self.shift = shift

        options = ChromeOptions()
#        service = Service('/usr/local/bin/chromedriver')
        options.add_argument('--start-maximized')
        options.add_argument('--no-first-run')
        options.add_argument('--no-sandbox')
        # options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.set_page_load_timeout(20)
        self.args = dargs
        print(self.args)

    def run(self):
        results = []
        try:
            # self.setup_csv()
            self.authenticate()
            time.sleep(5)
            card_number = 0
            for gender_arg in self.args['gender']:
                for engagement_rate_arg in self.args['engagement_rate']:
                    topic_arg = self.args['topic']
                    print(topic_arg, gender_arg, engagement_rate_arg)
                    try:
                        page_num = 0
                        self.driver.get(f'https://app.scrunch.com/discover?engagement_rate={engagement_rate_arg}&topic={topic_arg}&gender={gender_arg}&from={page_num * 25}&size=25')
                        while "Popular Topics" not in self.driver.page_source:
                            try:
                                self.driver.get(
                                    f'https://app.scrunch.com/discover?topic={topic_arg}&gender={gender_arg}&engagement_rate={engagement_rate_arg}from={page_num * 25}&size=25')
                                print(f'Thread: {self.args["shift"]}, reload count: {page_num}')
                                time.sleep(10)
                                cards = self.get_cards()
                                if len(cards) < 5:
                                    break
                                j = 1
                                button_shift = 0
                                for _ in cards:
                                    card_number += 1
                                    print(f'Thread: {self.args["shift"]}, card number: {card_number}')
                                    try:
                                        time.sleep(2)
                                        email = self.get_email(button_shift)
                                        # self.add_card_to_viewed(button_shift)
                                        bio = self.get_bio(j)
                                        self.open_card(button_shift)
                                        soup = BeautifulSoup(self.driver.page_source, 'lxml')
                                        name = self.get_name(soup)
                                        links, followers = self.get_followers(soup)
                                        average_engagement, average_engagement_rate = self.get_engagements(soup)
                                        views = self.get_views(soup)
                                        costs = self.get_estimated_cost_per_post(soup)
                                        topics = self.get_topics(soup)
                                        global_regions, countries, states, regions, cities = self.get_audience_locations(soup)
                                        analysis = self.get_audience_analysis(soup)
                                        audience_topics, audience_hashtags, audience_mentions = self.get_audience_interests(soup)
                                        self.close_card()

                                        # input('Check smth')
                                        results.append({'name': name, 'bio': bio, 'email': email, 'topics': topics, 'followers': followers, 'links': links,
                                                        'average_engagement': average_engagement, 'average_engagement_rate': average_engagement_rate,
                                                        'views': views, 'estimated_cost_per_post': costs, 'audience_global_regions': global_regions,
                                                        'audience_countries': countries, 'audience_states': states, 'audience_regions': regions,
                                                        'audience_cities': cities, 'audience_analysis': analysis, 'audience_topics': audience_topics,
                                                        'audience_hashtags': audience_hashtags, 'audience_mentions': audience_mentions})
                                    except Exception as ex:
                                        print(ex)
                                    finally:
                                        button_shift += 1
                                        j += 2
                            except:
                                page_num += 1
                    except Exception as ex:
                        print(f'Global error in thread {self.args["shift"]}: {ex}' )
                #with open('demo1.json', 'w') as f:
                #    json.dump(results, f, indent=4)
            keys = results[0].keys()
            with open(f'Result{self.args["shift"]}.csv', 'w', newline='', encoding='utf-8') as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)

        except Exception as ex:
            print(f'Error in running {ex}')
        finally:
            self.driver.close()
            self.driver.quit()
            return

    def add_card_to_viewed(self, i):
        # block = self.driver.find_elements(By.XPATH, '//div[@class="jss157"]')[i]
        self.driver.execute_script(f"document.getElementsByClassName('MuiTableRow-root')[{i+1}].getElementsByClassName('MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeSmall')[0].click()")
        # button = self.driver.find_elements(By.XPATH, '//tr[@class="MuiTableRow-root"]')[i].find_elements(By.XPATH, "//button[@class='MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeSmall']")[0]
        # while True:
        #     try:
        #         button.click()
        #         time.sleep(1)
        #     except:
        #         break
        WebDriverWait(self.driver, 5).until(
            EC.text_to_be_present_in_element((By.TAG_NAME, 'body'), 'viewed')
        )
        button = self.driver.find_elements(By.XPATH, '//input[@type="checkbox"]')[-1]
        button.click()
        time.sleep(0.2)
        # self.driver.find_element(By.XPATH, "//div[@style='z-index: -1; position: fixed; inset: 0px; background-color: transparent; -webkit-tap-highlight-color: transparent;']").click()
        self.driver.execute_script("return document.getElementsByClassName('MuiPopover-root')[1].remove();")

    def get_email(self, i):
        # block = self.driver.find_elements(By.XPATH, '//div[@class="jss157"]')[i]
        # button = card.find_elements(By.XPATH, "//button[@class='MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeSmall']")[1]
        # button.click()
        self.driver.execute_script(
            f"document.getElementsByClassName('MuiTableRow-root')[{i + 1}].getElementsByClassName('MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeSmall')[1].click()")
        time.sleep(0.2)
        email_button = self.driver.find_element(By.XPATH, '//div[@class="MuiPaper-root MuiPopover-paper MuiPaper-elevation8 MuiPaper-rounded"]')
        email = email_button.text
        self.driver.find_element(By.XPATH, "//div[@style='z-index: -1; position: fixed; inset: 0px; background-color: transparent; -webkit-tap-highlight-color: transparent;']").click()

        return email

    def get_bio(self, i):
        bio = self.driver.find_elements(By.XPATH, "//p[@class='MuiTypography-root MuiTypography-body2']")[i // 2].text
        return bio

    def open_card(self, i):
        # card.click()
        while True:
            try:
                self.driver.execute_script(f"document.getElementsByClassName('MuiTableRow-root')[{i + 1}].childNodes[3].click()")
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//h5[@class="MuiTypography-root MuiTypography-h5"]'))
                )
                break
            except:
                pass

    def close_card(self):
        button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@class='MuiButtonBase-root MuiIconButton-root']"))
        )
        button[-1].click()
        # self.driver.execute_script("return document.getElementsByClassName('ReactModal__Overlay ReactModal__Overlay--after-open slide-pane__overlay ')[0].remove()")

        # self.driver.find_elements(By.XPATH, "//button[@class='MuiButtonBase-root MuiIconButton-root']")[14].click()
        # opened_card = self.get_element('//div[@class="ReactModalPortal"]', element_number=-1)
        # soup = BeautifulSoup(self.driver.page_source, 'lxml')


    def get_cards(self):
        container = self.get_element('//tbody[@class="MuiTableBody-root"]')
        cards = container.find_elements(By.XPATH, '//tr[@class="MuiTableRow-root"]')
        # card.find_elements(By.XPATH, "//button[@class='MuiButtonBase-root MuiIconButton-root MuiIconButton-sizeSmall']")[1].click()
        return cards

    def authenticate(self):
        try:
            self.driver.get('https://app.scrunch.com/auth/login')
        except:
            pass
        self.paste_text(xpath='//input[@class="MuiInputBase-input MuiInput-input"]', value='klaar081@gmail.com')
        self.paste_text(xpath='//input[@class="MuiInputBase-input MuiInput-input MuiInputBase-inputAdornedEnd"]',
                        value='Mangust1!')
        self.click_button(xpath="//button[@type='submit']")

    def get_element(self, xpath, element_number=0):
        element = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)),
            message=f'Unable to find element with XPATH {xpath}'
        )[element_number]
        return element

    def get_elements(self, xpath):
        return WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)),
            message=f'Unable to find elements with XPATH {xpath}'
        )

    def find_element_by_text_and_click_on_it(self, xpath, text):
        elements = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)),
            message=f"Unable to find element with TEXT '{text}' and XPATH '{xpath}'"
        )
        for element in elements:
            if text in element.text:
                element.click()
                break
            print(f'Unable to find element with TEXT {text}')

    def click_button(self, xpath, element_number=0):
        button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)),
            message=f'Unable to find element with XPATH {xpath}'
        )[element_number]
        button.click()
        return button

    def paste_text(self, xpath, value, element_number=0):
        button = WebDriverWait(self.driver, 15).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath)),
            message=f"Unable to find element with XPATH {xpath}"
        )[element_number]
        button.click()
        button.send_keys(value)

    @staticmethod
    def get_name(soup):
        name = soup.find('h5', class_='MuiTypography-root MuiTypography-h5').text
        return name

    @staticmethod
    def get_followers(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        followers_num_delta = 14
        social_box = soup.find_all('div', class_=f'jss{main_jss_num + followers_num_delta}')
        links = {
            'instagram': '',
            'youtube': '',
            'twitter': '',
            'facebook': '',
            'tiktok': '',
        }
        followers = {
            'instagram': '',
            'youtube': '',
            'twitter': '',
            'facebook': '',
            'tiktok': '',
        }
        for x in social_box:
            social_followers = x.find('p', class_='MuiTypography-root MuiTypography-body1').text
            social_link = x.find('a').get('href')
            if 'instagram' in social_followers:
                links['instagram'] = social_link
                followers['instagram'] = social_followers.split('\xa0')[0]
            elif 'youtube' in social_followers:
                links['youtube'] = social_link
                followers['youtube'] = social_followers.split('\xa0')[0]
            elif 'twitter' in social_followers:
                links['twitter'] = social_link
                followers['twitter'] = social_followers.split('\xa0')[0]
            elif 'facebook' in social_followers:
                links['facebook'] = social_link
                followers['facebook'] = social_followers.split('\xa0')[0]
            elif 'tiktok' in social_followers:
                links['tiktok'] = social_link
                followers['tiktok'] = social_followers.split('\xa0')[0]
        return links, followers

    @staticmethod
    def get_engagements(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        engagement_num_delta = 11
        engagement_box = soup.find_all('div', class_=f'jss{main_jss_num + engagement_num_delta}')[-1]
        average_engagement = engagement_box.find('h5').text.strip('average engagement').strip()
        average_engagement_rate = engagement_box.find('span').text.strip('Avg. Engagement Rate')
        return average_engagement, average_engagement_rate

    @staticmethod
    def get_views(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        views = {
            'instagram': '',
            'youtube': '',
            'twitter': '',
            'facebook': '',
            'tiktok': '',
        }
        instagram_icon = "M7.8 2h8.4C19.4 2 22 4.6 22 7.8v8.4a5.8 5.8 0 0 1-5.8 5.8H7.8C4.6 22 2 19.4 2 16.2V7.8A5.8 5.8 0 0 1 7.8 2m-.2 2A3.6 3.6 0 0 0 4 7.6v8.8C4 18.39 5.61 20 7.6 20h8.8a3.6 3.6 0 0 0 3.6-3.6V7.6C20 5.61 18.39 4 16.4 4H7.6m9.65 1.5a1.25 1.25 0 0 1 1.25 1.25A1.25 1.25 0 0 1 17.25 8 1.25 1.25 0 0 1 16 6.75a1.25 1.25 0 0 1 1.25-1.25M12 7a5 5 0 0 1 5 5 5 5 0 0 1-5 5 5 5 0 0 1-5-5 5 5 0 0 1 5-5m0 2a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z"
        youtube_icon = "M10 15l5.19-3L10 9v6m11.56-7.83c.13.47.22 1.1.28 1.9.07.8.1 1.49.1 2.09L22 12c0 2.19-.16 3.8-.44 4.83-.25.9-.83 1.48-1.73 1.73-.47.13-1.33.22-2.65.28-1.3.07-2.49.1-3.59.1L12 19c-4.19 0-6.8-.16-7.83-.44-.9-.25-1.48-.83-1.73-1.73-.13-.47-.22-1.1-.28-1.9-.07-.8-.1-1.49-.1-2.09L2 12c0-2.19.16-3.8.44-4.83.25-.9.83-1.48 1.73-1.73.47-.13 1.33-.22 2.65-.28 1.3-.07 2.49-.1 3.59-.1L12 5c4.19 0 6.8.16 7.83.44.9.25 1.48.83 1.73 1.73z"
        twitter_icon = "M22.46 6c-.77.35-1.6.58-2.46.69.88-.53 1.56-1.37 1.88-2.38-.83.5-1.75.85-2.72 1.05C18.37 4.5 17.26 4 16 4c-2.35 0-4.27 1.92-4.27 4.29 0 .34.04.67.11.98C8.28 9.09 5.11 7.38 3 4.79c-.37.63-.58 1.37-.58 2.15 0 1.49.75 2.81 1.91 3.56-.71 0-1.37-.2-1.95-.5v.03c0 2.08 1.48 3.82 3.44 4.21a4.22 4.22 0 0 1-1.93.07 4.28 4.28 0 0 0 4 2.98 8.521 8.521 0 0 1-5.33 1.84c-.34 0-.68-.02-1.02-.06C3.44 20.29 5.7 21 8.12 21 16 21 20.33 14.46 20.33 8.79c0-.19 0-.37-.01-.56.84-.6 1.56-1.36 2.14-2.23z"
        facebook_icon = "M5 3h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2m13 2h-2.5A3.5 3.5 0 0 0 12 8.5V11h-2v3h2v7h3v-7h3v-3h-3V9a1 1 0 0 1 1-1h2V5z"
        tiktok_icon = "M 21.142857,0 H 2.857143 C 1.281714,0 0,1.281714 0,2.857143 V 21.142857 C 0,22.718286 1.281714,24 2.857143,24 H 21.142857 C 22.718286,24 24,22.718286 24,21.142857 V 2.857143 C 24,1.281714 22.718286,0 21.142857,0 Z m -2.282286,10.470286 c -0.129714,0.012 -0.261142,0.02 -0.394285,0.02 -1.498857,0 -2.816,-0.770857 -3.582286,-1.936 0,3.056571 0,6.534285 0,6.592571 0,2.690857 -2.181714,4.872572 -4.872571,4.872572 -2.690858,0 -4.872572,-2.181715 -4.872572,-4.872572 0,-2.690857 2.181714,-4.872571 4.872572,-4.872571 0.101714,0 0.201142,0.0091 0.301142,0.01543 v 2.401143 c -0.1,-0.012 -0.198285,-0.03029 -0.301142,-0.03029 -1.373715,0 -2.486858,1.113143 -2.486858,2.486858 0,1.373714 1.113143,2.486857 2.486858,2.486857 1.373714,0 2.586857,-1.082286 2.586857,-2.456 0,-0.05429 0.024,-11.196572 0.024,-11.196572 h 2.294857 c 0.216,2.052 1.872571,3.671429 3.943428,3.82 z"
        views_box_num_delta = 17
        views_box = soup.find('div', class_=f'jss{main_jss_num + views_box_num_delta}')
        for views_card in views_box.find_all('div'):
            if views_card.find('path').get('d') == instagram_icon:
                views['instagram'] = views_card.text
            elif views_card.find('path').get('d') == youtube_icon:
                views['youtube'] = views_card.text
            elif views_card.find('path').get('d') == twitter_icon:
                views['twitter'] = views_card.text
            elif views_card.find('path').get('d') == facebook_icon:
                views['facebook'] = views_card.text
            elif views_card.find('path').get('d') == tiktok_icon:
                views['tiktok'] = views_card.text
        return views

    @staticmethod
    def get_estimated_cost_per_post(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        costs = {
            'instagram': '',
            'youtube': '',
            'twitter': '',
            'facebook': '',
            'tiktok': '',
        }
        estimated_cost_box_num_delta = -6
        estimated_cost_box = soup.find('div', class_=f'jss{main_jss_num + estimated_cost_box_num_delta}')
        for x in estimated_cost_box.find_all('div', class_='MuiChip-root MuiChip-sizeSmall'):
            cost = x.find('span').text
            if 'instagram' in cost:
                costs['instagram'] = cost.split(' ')[0]
            elif 'youtube' in cost:
                costs['youtube'] = cost.split(' ')[0]
            elif 'twitter' in cost:
                costs['twitter'] = cost.split(' ')[0]
            elif 'facebook' in cost:
                costs['facebook'] = cost.split(' ')[0]
            elif 'tiktok' in cost:
                costs['tiktok'] = cost.split(' ')[0]
        return costs

    @staticmethod
    def get_topics(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        topic_box_num_delta = -6
        topics_box = soup.find_all('div', class_=f'jss{main_jss_num + topic_box_num_delta}')[-1]
        topics = ''
        for x in topics_box.find_all('span'):
            topics += x.text + '; '
        return topics

    @staticmethod
    def get_audience_locations(soup):
        box = soup.find('p', string='Audience locations')
        num = int(box.parent.findNextSiblings()[1].get('class')[0].strip('jss'))
        audience_locations = soup.find_all('div', class_=f'jss{num + 1}')
        # print(audience_locations)
        global_regions_box, countries_box, states_box, regions_box, cities_box = audience_locations
        global_regions, countries, states, regions, cities = [], [], [], [], []
        audience_locations_num_delta = 55
        for x in global_regions_box.find_all('div', class_=f'jss{num + 3}')[1:]:
            region = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[0].text
            percent = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[1].text
            global_regions.append(region + ' ' + percent)
        for x in countries_box.find_all('div', class_=f'jss{num + 3}')[1:]:
            region = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[0].text
            percent = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[1].text
            countries.append(region + ' ' + percent)
        for x in states_box.find_all('div', class_=f'jss{num + 3}')[1:]:
            region = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[0].text
            percent = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[1].text
            states.append(region + ' ' + percent)
        for x in regions_box.find_all('div', class_=f'jss{num + 3}')[1:]:
            region = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[0].text
            percent = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[1].text
            regions.append(region + ' ' + percent)
        for x in cities_box.find_all('div', class_=f'jss{num + 3}')[1:]:
            region = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[0].text
            percent = x.find_all('p', class_='MuiTypography-root MuiTypography-body2')[1].text
            cities.append(region + ' ' + percent)
        return global_regions, countries, states, regions, cities

    @staticmethod
    def get_audience_analysis(soup):
        box = soup.find('p', string='Audience analysis')
        num = int(box.parent.findNextSiblings()[0].get('class')[0].strip('jss'))
        analysis = \
        soup.find('div', class_=f'jss{num + 1}').find_all('p', class_='MuiTypography-root MuiTypography-body2')[
            -1].text.strip()
        return analysis

    @staticmethod
    def get_audience_interests(soup):
        main_jss_num = int(
            soup.find('h5', class_='MuiTypography-root MuiTypography-h5').findParent().get('class')[0].strip('jss'))

        audience_interests_num_delta = 62
        audience_interests = soup.find_all('div', class_=f'jss{main_jss_num + audience_interests_num_delta}')
        themes = audience_interests[0].find_all('div', class_="MuiChip-root")
        audience_topics = ''
        for t in themes:
            audience_topics += t.text + '; '
        themes = audience_interests[1].find_all('div', class_="MuiChip-root")
        audience_hashtags = ''
        for t in themes:
            audience_hashtags += t.text + '; '
        themes = audience_interests[2].find_all('div', class_="MuiChip-root")
        audience_mentions = ''
        for t in themes:
            audience_mentions += t.text + '; '

        return audience_topics, audience_hashtags, audience_mentions


if __name__ == "__main__":
    scraper = ScrunchScraper(args=0)
    results = scraper.run()
