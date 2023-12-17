from elasticsearch_dsl import Document, Keyword, Text, Integer, Boolean, Date


class BlogEs(Document):
    name = Keyword()
    tag_line=Text(fields={"keyword":Keyword()},analyzer="ik_max_word")
    char_count=Integer()
    is_published = Boolean()
    pub_datetime = Date()
    blog_id = Integer()
    id = Integer()

    class Index:
        name = "blog"
        using = "private"
