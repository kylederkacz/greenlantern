from greenlantern.filters import strip_html


class TestFilters:

    def setUp(self):
        pass

    def test_strip_html(self):

        test1 = "<html>content</html>"
        res1 = strip_html(test1)
        assert res1 == "content"

        test2 = "<html><body><p>content2</p></body></html>"
        res2 = strip_html(test2)
        assert res2 == "content2"
