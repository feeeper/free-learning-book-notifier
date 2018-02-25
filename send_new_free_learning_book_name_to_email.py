import smtplib
import requests
import argparse
from bs4 import BeautifulSoup
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class BookMessage:
    def __init__(self, title, link, summary, what_learn):
        self.title = title
        self.link = link
        self.summary = summary
        self.what_learn = what_learn

    def __str__(self):
        template = """
Title: {}
Link: {}
Summary: {}
What Learn:
{}
"""
        return template.format(self.title, self.link, self.summary, '\n'.join(['- ' + x for x in self.what_learn]))

    def as_html(self):
        template = """
<h2>
    <a href='{}'>{}</a>
</h2>
<p>{}</p>
<p>
    <ol>
    {}
    </ol>
</p>
<p>
<a href="https://www.packtpub.com/packt/offers/free-learning">Grab the book</a>
</p>
"""
        return template.format(self.link, self.title, self.summary, '\n'.join(['<li>' + x + '</li>' for x in self.what_learn]))


def main():
    parser = argparse.ArgumentParser(description='Send email with new book title to email')
    parser.add_argument('-smtp_host', help='SMTP Host address')
    parser.add_argument('-smtp_port', help='SMTP Host port', default=25)
    parser.add_argument('-smtp_login', help='SMTP Login')
    parser.add_argument('-smtp_pwd', help='SMTP Password')
    parser.add_argument('-from_email', help='From email')
    parser.add_argument('-to_email', help='To email')
    args = parser.parse_args()

    free_learning_link = 'https://www.packtpub.com/packt/offers/free-learning'
    html = requests.get(free_learning_link, headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'})
    soup = BeautifulSoup(str(html.content), 'html.parser')
    book_link = 'https://www.packtpub.com' + soup.find('div', { 'class': 'dotd-main-book-image' }).find('a')['href']

    book_page = requests.get(book_link, headers={'USER-AGENT': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'})
    book_soup = BeautifulSoup(str(book_page.content), 'html.parser')
    book_title = book_soup.find('h1', {'itemprop':'name'}).text
    book_summary = book_soup.find('div', {'class': 'book-top-block-info-one-liner cf'}).get_text(strip=True).replace('\\n', '').replace('\\t', '')
    book_what_learn = book_soup.find('div', {'class': 'book-info-will-learn-text'}).find_all('li')

    book_msg = BookMessage(book_title, book_link, book_summary, [x.get_text(strip=True) for x in book_what_learn])

    msg = MIMEMultipart('alternative')
    msg.attach(MIMEText(book_msg.as_html(), 'html'))
    msg['Subject'] = 'New Book at Free Learning: {}'.format(book_msg.title)
    msg['From'] = args.from_email
    msg['To'] = args.to_email

    smtp = {
    'host': args.smtp_host,
    'port': args.smtp_port,
    'login': args.smtp_login,
    'password': args.smtp_pwd
    }

    s = smtplib.SMTP_SSL(smtp['host'], smtp['port'])
    s.login(smtp['login'], smtp['password'])
    s.send_message(msg)
    s.quit()

main()
