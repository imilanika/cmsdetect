from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

import re
import whois

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        response = requests.get("http://" + url)
        print("http://" + url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string
            # Step : Get the meta description of the webpage
            meta_description = ""
            for meta in soup.find_all("meta"):
                if "name" in meta.attrs and meta.attrs["name"].lower() == "description":
                    meta_description = meta.attrs["content"]


            # Step : Get the meta keywords of the webpage
            meta_keywords = ""
            for meta in soup.find_all("meta"):
                if "name" in meta.attrs and meta.attrs["name"].lower() == "keywords":
                    meta_keywords = meta.attrs["content"]
            # Step : Get the images on the webpage
            images = []
            for img in soup.find_all("img"):
                if "src" in img.attrs:
                    images.append(img.attrs["src"])

            text = soup.get_text()
            with open('check_list.txt', 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Create a dictionary of CMS names and short codes
            cms_dict = {}
            for line in lines:
                cms_name, short_code = line.strip().split('=')
                cms_dict[cms_name.lower()] = short_code.upper()
                # Print the dictionary of CMS names and short codes
            found_cms = ""
            for cms_name, short_code in cms_dict.items():
                if cms_name in text.lower():
                    if found_cms:
                        found_cms += ", "
                    found_cms += f"{cms_name.title()} ({short_code})"
            if found_cms:
                found_cms = "Detected DATA : " + found_cms
            else:
                found_cms = "No detected Additional DATA"
            meta_generator = soup.find("meta", {"name": "generator"})
            cms=""
            if meta_generator:
                cms = meta_generator["content"]          

            address_div = soup.find('div', class_='contact-info').find('p')
            address = address_div.text.strip()
            google_maps_ref = f"https://www.google.com/maps/place/{address.replace(' ', '+')}"
            # Extract telephone number
            telephone_a = soup.find('div', class_='contact-info').find('a', href=re.compile(r'tel:'))
            telephone = telephone_a.text.strip() if telephone_a else None
            telephone_ref = f"tel:{telephone}" if telephone else ''
            # Extract email
            email_a = soup.find('div', class_='contact-info').find('a', href=re.compile(r'mailto:'))
            email = email_a.text.strip() if email_a else None
            email_ref = f"mailto:{email}" if email else ''
            # Build contact info string
            contact_info = ""
            if address:
                contact_info += f"Address: <a href='{google_maps_ref}'>{address}</a><br>"
            if telephone:
                contact_info += f"Telephone: <a href='{telephone_ref}'>{telephone}</a><br>"
            if email:
                contact_info += f"Email: <a href='{email_ref}'>{email}</a><br>"


            # Find all the anchor tags
            links = soup.find_all('a')
            # Extract the URLs from the href attributes
            urls = []
            for link in links:
                url = link.get('href')
                if url:
                    urls.append(url)
            print(urls)
            # Define a dictionary of social media platforms to check for
            social_media_dict = {
                "facebook": "Facebook",
                "instagram": "Instagram",
                "twitter": "Twitter",
                "youtube": "YouTube",
                "linkedin": "LinkedIn",
                "pinterest": "Pinterest",
                "linkedin": "Linkedn",
                "xing": "Xing",
                
            }
            # Check for the presence of each social media platform in the text
            found_social_media = []
            found_social_medianames = []
            for platform, name in social_media_dict.items():
                print("Check",platform)
                print("Check",name)
                if platform in text.lower():
                    found_social_media.append(name)
                    found_social_medianames.append(platform)
                elif name in text.lower():
                    found_social_media.append(name)
                    found_social_medianames.append(platform)
            # Print the list of social media platforms found in the text
            found_soc=""
            print(found_social_medianames)
            if found_social_medianames:
                print("The following social media platforms were found in the text:")
                for platform in found_social_medianames:
                    print("PLAT", platform)
                    for url in urls:
                         if platform.lower() in url.lower():
                            found_soc += f"<a href='{url}'>{platform}</a><br>"

            # create a new Chrome browser instance
            #browser = webdriver.Chrome()
            # navigate to the website
            #browser.get(url)
            # take a screenshot and save it to a file
            #browser.save_screenshot('templates/screenshot.png')
            # close the browser
            #browser.quit()
                        
            return render_template('result.html', cms=cms,
                                   found_cms=found_cms,title=title,
                                   meta_description=meta_description,
                                   meta_keywords=meta_keywords,
                                   images=images, found_soc=found_soc,
                                   contact_info=contact_info)
        else:
            return render_template('result.html', error='Failed to retrieve website content.')
    else:
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
