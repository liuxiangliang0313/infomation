# 公用内容写在此处

# 过滤器，过滤热门新闻颜色
def news_class_filter(index):
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        ""
