# Import Splinter and BeautifulSoup
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import datetime as dt

# Set up an executable path
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)

# -- Connect to Mongo and establish communication between our code and the database -- #
# 1. Initialize the browser.
# 2. Create a data dictionary.
# 3. End the WebDriver and return the scraped data.

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "hemispheres": hemisphere(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


# -- News Title and Paragraph -- #

def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


# -- Featured Images -- #

def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# -- Mars Facts -- #

def mars_facts():
    
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


# -- Hemisphere Data -- 

def hemisphere(browser):

    # Visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # Write code to retrieve the image urls and titles for each hemisphere.
    html = browser.html
    mars_hemi_soup = soup(html, 'html.parser')

    try:
        items = mars_hemi_soup.find_all('div', class_='item')
    
        for item in items:
            
            # Create an empty dictionary
            hemispheres = {}
            
            # Find link to each hemiphere
            hemi_url = item.find('a', class_='itemLink product-item')['href']
            browser.visit(url+hemi_url)
            
            # Parse each hemiphere
            html = browser.html
            hemi_soup = soup(html, 'html.parser')
            
            # Find the title
            title = hemi_soup.find('h2', class_='title').get_text()
            # Find the image urls
            img_download = hemi_soup.find('div', class_='downloads')
            img_url = img_download.find('a')['href']
            
            # Save the hemisphere image title and the image URL to the 'hemisphere' dictionary
            hemispheres = { 
                    'title': title, 
                    'img_url': url+img_url}
            
            # Append the 'hemispheres' dictionary to the 'hemisphere_image_urls' list
            hemisphere_image_urls.append(hemispheres)
            
            # Navigate back to the beginning to get the next hemisphere
            browser.back()

    except AttributeError:
        return None, None

    return hemisphere_image_urls


# Tell Flask that the script is complete and ready for action
if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())


