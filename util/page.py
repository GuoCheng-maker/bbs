import urllib.parse

class Pagination(object):
    """
    自定义分页组件
    """
    def __init__(self, current_page, all_count, base_url,params, per_page_num=8, pager_count=11, ):
        """
        封装分页相关数据
        :param current_page: 当前页
        :param all_count:    数据库中的数据总条数
        :param per_page_num: 每页显示的数据条数
        :param base_url:     分页中显示的URL前缀
        :param pager_count:  最多显示的页码个数
        """
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1

        if current_page < 1:
            current_page = 1

        self.current_page = current_page
        self.all_count = all_count
        self.per_page_num = per_page_num
        self.base_url = base_url

        # 总页码
        all_pager, tmp = divmod(all_count, per_page_num)
        if tmp:
            all_pager += 1
        self.all_pager = all_pager

        self.pager_count = pager_count  # 最多显示页码数
        self.pager_count_half = int((pager_count - 1) / 2)

        import copy
        params = copy.deepcopy(params)
        params._mutable = True
        self.params = params  # self.params : {"page":77,"title":"python","nid":1}


    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_num


    @property
    def end(self):
        return self.current_page * self.per_page_num


    def page_html(self):
        # 如果总页码 < 11个：
        if self.all_pager <= self.pager_count:
            pager_start = 1
            pager_end = self.all_pager + 1
        # 总页码  > 11
        else:
            # 当前页如果<=页面上最多显示(11-1)/2个页码
            if self.current_page <= self.pager_count_half:
                pager_start = 1
                pager_end = self.pager_count + 1

            # 当前页大于5
            else:
                # 页码翻到最后
                if (self.current_page + self.pager_count_half) > self.all_pager:
                    pager_start = self.all_pager - self.pager_count + 1
                    pager_end = self.all_pager + 1

                else:
                    pager_start = self.current_page - self.pager_count_half
                    pager_end = self.current_page + self.pager_count_half + 1

        page_html_list = []
        self.params["page"] = 1
        first_page = '<li><a href="%s?%s">首页</a></li>' % (self.base_url, urllib.parse.urlencode(self.params),)
        page_html_list.append(first_page)

        if self.current_page <= 1:
            prev_page = '<li class="disabled"><a href="#">上一页</a></li>'
        else:
            self.params["page"] = self.current_page - 1
            prev_page = '<li><a href="%s?%s">上一页</a></li>' % (self.base_url,urllib.parse.urlencode(self.params),)

        page_html_list.append(prev_page)

        for i in range(pager_start, pager_end):
            #  self.params  : {"page":77,"title":"python","nid":1}

            self.params["page"] = i  # {"page":72,"title":"python","nid":1}
            if i == self.current_page:
                temp = '<li class="active"><a href="%s?%s">%s</a></li>' % (self.base_url, urllib.parse.urlencode(self.params), i,)
            else:
                temp = '<li><a href="%s?%s">%s</a></li>' % (self.base_url, urllib.parse.urlencode(self.params), i,)
            page_html_list.append(temp)

        if self.current_page >= self.all_pager:
            next_page = '<li class="disabled"><a href="#">下一页</a></li>'
        else:
            self.params["page"] = self.current_page + 1
            next_page = '<li><a href="%s?%s">下一页</a></li>' % (self.base_url, urllib.parse.urlencode(self.params),)
        page_html_list.append(next_page)

        self.params["page"] = self.all_pager
        last_page = '<li><a href="%s?%s">尾页</a></li>' % (self.base_url, urllib.parse.urlencode(self.params),)
        page_html_list.append(last_page)

        return ''.join(page_html_list)

