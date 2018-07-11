from flask import render_template

from . import news_blu


# 新闻详情展示
@news_blu.route('/<int:news_id>')
def new_details(news_id):
    
    return render_template("news/detail.html")
