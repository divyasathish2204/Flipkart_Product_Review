from flask import Flask,render_template,request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import pandas
import logging
logging.basicConfig(filename='scraper.log',level=logging.INFO)
application = Flask(__name__)
app = application
@app.route('/',methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')
@app.route('/review',methods=['POST','GET'])
@cross_origin()
def index():
    if request.method == 'POST':
        try:
            search_string = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + search_string
            uClient = uReq(flipkart_url)
            flipkart_page = uClient.read()
            uClient.close()
            flipkart_html=BeautifulSoup(flipkart_page,"html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0 :3]
            box = bigboxes[0]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            product_response = requests.get(product_link)
            product_response.encoding='utf-8'
            product_html = BeautifulSoup(product_response.text,"html.parser")
            print(product_html)
            commentboxes = product_html.find_all('div', {'class': "_16PBlm"})
            filename = search_string + ".csv"
            file = open(filename,"w")
            headers = "Product,Customer_name,Rating,Comment_heading,Comment\n"
            file.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                except Exception as e:
                    logging.info(e)
                    name = 'No_name'
                try:
                     rating = commentbox.div.div.div.div.text
                except Exception as e:
                    logging.info(e)
                    rating = "no rating"
                try:
                    commentHead = commentbox.div.div.div.p.text
                except Exception as e:
                    logging.info(e)
                    commentHead = 'No Comment Heading'
                
                try:
                    commenttag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    customer_Comment = commenttag[0].div.text
                except Exception as e:
                    logging.info(e)
                    print("Exception while creating dictionary: ",e)
                my_dict = {"Product": search_string, "Customer_name": name, "Rating": rating, "Comment_heading": commentHead,
                          "Comment": customer_Comment}
                reviews.append(my_dict)
                df_reviews = pandas.DataFrame(reviews)
                df_reviews.to_csv('flipkart.csv',index=False)
            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return "something is wrong"
    else:
        return render_template("index.html")
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8000,debug=True)


        
        


















            
























