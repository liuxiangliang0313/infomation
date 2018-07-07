from info import redis_store
from . import index_blue
import logging
from  flask import current_app,render_template

@index_blue.route('/',methods=["GET",'POST'])
def hello_world():

    return render_template('news/index.html')
