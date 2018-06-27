import requests
from bs4 import BeautifulSoup
from csv import DictWriter
import _pickle as cPickle

def get_response(location, distance, page_number):
    url_string = "https://en.infoengine.cymru/search?keywords=&location={}&lat=&lng=&distance={}&type=services&page={}".format(location,distance, page_number)
    try:
        r = requests.get(url_string)
    except:
        return 0
    return r

def get_soup(response):
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
    except:
        print('could not parse html')
    return soup

def get_detail_page_urls(soup):
    list_of_urls = []
    try:
        list_of_elements = soup.find_all(class_="link")
    except:
        print('could not find elements')
    for el in list_of_elements:
        if 'https://en.infoengine.cymru/services' in el['href']:            
            list_of_urls.append(el['href'])
    return list_of_urls

def clean_string(string):
    return string.strip('\n').replace('\n','').rstrip().lstrip()

def get_organisation_name(list_of_urls):
    try:
        string = [i.text for i in list_of_urls if 'https://en.infoengine.cymru/organisations/' in i['href']][0]
        string = clean_string(string)
    except:
        return ""
    return string

def process_address(soup_input):
    output_list = []
    for line in soup_input:
        output_list.append(clean_string(line.text))
    return ",".join(output_list)

def process_categories(list_of_categories):
    category_list = []
    for category in list_of_categories:
        category_list.append(clean_string(category.text))
    return  ",".join(category_list)

def process_email(soup):
    email = ""
    try:
        email = soup.select_one("a[href*=mailto]")['href'].replace('mailto:','')
    except:
        pass
    return email

def process_website(contact_line):
    website = ""
    try:
        website = [j.find_all('a') for j in [i for i in contact_line if 'Website' in i.text]][0][0]['href']
    except:
        pass
    return website

def process_phone(soup):
    phone = ""
    try:
        phone = clean_string(soup.find_all('span', {'class' : 'icon-phone'})[0].nextSibling)
    except:
        pass
    return phone

def process_facebook(soup):
    facebook = ""
    try:
        facebook = soup.find_all('span', {'class' : 'icon-facebook'})[0].nextSibling.nextSibling['href']
    except:
        pass
    return facebook

def process_facilities(soup):
    list_of_facilities = []
    try:
        soup_list = soup.find_all('li',{'class':'facility'})
        for el in soup_list:
            list_of_facilities.append(clean_string(el.find('span').nextSibling))
    except:
        pass
    return ",".join(list_of_facilities)

def process_access_options(soup):
    list_of_access_options = []
    try:
        for el in soup.find_all('span', {'class' : 'icon-tick'}):
            list_of_access_options.append(clean_string(el.nextSibling))
    except:
        pass
    return ",".join(list_of_access_options)

def process_opening_times(soup):
    opening_times = ''
    try:
        opening_times =  '\''+ [i for i in soup.find_all('h3',{'class':'heading'}) if i.text == 'Opening times'][0].nextSibling.nextSibling.text
    except:
        pass
    return opening_times

def process_accreditation(soup):
    accreditation = ''
    try:
        accreditation = soup.find('div',{'class':'accreditation'}).find('h5',{'class':'sub-heading'}).text
    except:
        pass
    return accreditation

def process_url(url):
    temp_dict = {}
    try:
        r = requests.get(url)
        soup = get_soup(r)
        temp_dict['service_name'] = soup.select('h1')[0].text
        temp_dict['organisation_name'] = get_organisation_name(soup.find_all(class_="link"))
        temp_dict['description'] = clean_string(soup.select('p.description')[0].text)
        temp_dict['address'] = process_address(soup.find_all(class_="address-line"))
        temp_dict['categories'] = process_categories(soup.find_all(class_="category-link"))
        temp_dict['email'] = process_email(soup)
        temp_dict['website'] = process_website(soup.find_all(class_="contact-line"))
        temp_dict['facebook'] = process_facebook(soup)
        temp_dict['phone'] = process_phone(soup)
        temp_dict['facilities'] = process_facilities(soup)
        temp_dict['access_options'] = process_access_options(soup)
        temp_dict['opening_times'] = process_opening_times(soup)
        temp_dict['accreditation'] = process_accreditation(soup)
    except:
        pass
    return temp_dict

def save_pkl_data(data):
    with open('raw_data.p', 'wb') as fp:
        cPickle.dump(data, fp)
    print('Data saved successfully')

def save_csv(data):
    keys = data[0].keys()
    with open('infoengine.csv', 'w', encoding="utf-8") as output_file:
        dict_writer = DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
    print('Data saved to csv successfully')
    
if __name__ == "__main__":
    results = []
    location = "neath"
    distance = 20
    for page_number in range(1,90):
        print('processing page {}'.format(page_number))
        response = get_response(location, distance, page_number)
        soup = get_soup(response)
        list_of_urls = get_detail_page_urls(soup)
        for url in list_of_urls:
            results.append(process_url(url))
    save_pkl_data(results)
    save_csv(results)
