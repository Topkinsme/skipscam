from flask import Flask,render_template,request
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
from sklearn.linear_model import LogisticRegression

id_data=pd.read_csv('train.csv')
id_data.drop(['profile pic','description length','external URL'],axis=1,inplace=True)
X_train=id_data[['nums/length username','fullname words','nums/length fullname','name==username','private','#posts','#followers','#follows']]
y_train=id_data['fake']


lr=LogisticRegression()
lr.fit(X_train,y_train)
app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def main():
    if request.method=='POST':
        name=request.form.get('username')
        if name=="":
            return render_template('/index.html')
        url=f"https://www.instagram.com/{name}/"
        page=requests.get(url)
        soup=BeautifulSoup(page.content,'html.parser')
        text=soup.prettify()
        loc=text.find('See Instagram photos and videos')
        text=text[loc-50:loc+100]
        followers=text[text.find("\"")+1:text.find("Followers")-1].replace(",","")
        if 'M' in followers:
            followers=followers.replace("M","")
            followers=int(followers)*1000000
        elif 'K' in followers:
            followers=followers.replace("K","")
            followers=int(followers)*1000
        following=text[text.find(", ")+2:text.find("Following")-1].replace(",","")
        if 'M' in following:
            following=following.replace("M","")
            following=int(following)*1000000
        elif 'K' in following:
            following=following.replace("K","")
            following=int(following)*1000
        posts=text[text.find("g, ")+3:text.find("Posts")-1].replace(",","")
        username=name
        realname=text[text.find("videos from ")+12:text.find("(@")-1]
        if realname=="" and following=="":
          return render_template('/result.html',result="Error! Account not found!",searchres="")
        elif realname=="":
            realname=" "
        temp1=0
        temp2=0
        for l in username:
            if l.isdigit():
                temp1+=1
        for l in realname:
            if l.isdigit():
                temp2+=1
        numbers=[temp1/len(username),realname.count(" ")+1,temp2/len(realname),int(realname==username),int(followers==0),int(posts),int(followers),int(following)]
        data=[f"Followers - {followers}",f"Following - {following}",f"Posts - {posts}",f"Username - {username}",f"Real Name - {realname}",str(numbers)]
        predict=lr.predict([numbers])
        print(predict[0])
        if predict[0]==0:
            op="This is likely not a malicious user."
        else:
            op="This is likely a MALICIOUS USER!"
        return render_template('/result.html',result=op,link=url,searchres=username)
    else:
        return render_template('/index.html')

if __name__=="__main__":
  app.run(debug=True)