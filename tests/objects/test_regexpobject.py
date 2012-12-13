from ..base import BaseRuPyPyTest


class TestRegexpObject(BaseRuPyPyTest):
    def test_source(self, space):
        w_res = space.execute("return /abc/.source")
        assert space.str_w(w_res) == "abc"

    def test_compile_regexps(self, space):
        space.execute("""
        /^/
        /(a|b)/
        /(ab|ac)/
        /(ms|min)/
        /$/
        /[^f]/
        /[a]+/
        /\\(/
        /[()#:]/
        /[^()#:]/
        /([^)]+)?/
        /cy|m/
        /[\\-]/
        /(?!a)/
        /(?=a)/
        /a{1}/
        /a{2,3}/
        /foo(?#comment)bar/
        /abc/i
        /(?<=\d)/
        /(?<foo>.*)/
        /A++/
        /.*?/
        /\\z/
        /[a-z]/
        /\\d+/
        /([a-z])|b/
        /[a-zA-z]|[a-z]/
        /(?<foo>a)\\g<foo>/
        /[^a-z]/
        /[a-z&&[^a-c]]/
        /[a&&[^b]]+/
        /\\G/
        """)

    def test_match_operator(self, space):
        w_res = space.execute("""
        idx = /(l)(l)(o)(a)(b)(c)(h)(e)(l)/ =~ 'helloabchello'
        return idx, $1, $2, $3, $4, $5, $6, $7, $8, $9, $&, $+, $`, $'
        """)
        assert self.unwrap(space, w_res) == [2, "l", "l", "o", "a", "b", "c", "h", "e", "l", "lloabchel", "l", "he", "lo"]

    def test_match_method(self, space):
        w_res = space.execute("return /bc/.match('abc').begin(0)")
        assert space.int_w(w_res) == 1

    def test_new_regexp(self, space):
        w_res = space.execute("return Regexp.new('..abc..') == Regexp.compile('..abc..')")
        assert w_res is space.w_true
        w_res = space.execute("return Regexp.new(/abc/).source")
        assert space.str_w(w_res) == "abc"

    def test_size(self, space):
        w_res = space.execute("""
        /(a)(b)(c)/ =~ "hey hey, abc, hey hey"
        return $~.size
        """)
        assert space.int_w(w_res) == 4

    def test_set_match_data_wrong_type(self, space):
        with self.raises(space, "TypeError"):
            space.execute("$~ = 12")
        space.execute("$~ = nil")

    def test_atomic_grouping(self, space):
        w_res = space.execute('return /"(?>.*)"/ =~ (\'"Quote"\')')
        assert w_res is space.w_nil

        w_res = space.execute('return /"(?>[A-Za-z]*)"/ =~ \'"Quote"\'')
        assert space.int_w(w_res) == 0

    def test_set_intersection(self, space):
        w_res = space.execute("return /[a-z&&[^a-c]]+/ =~ 'abcdef'")
        assert space.int_w(w_res) == 3

    def test_to_a(self, space):
        w_res = space.execute("""
        m = /(a)(b)(c)/.match('defabcdef')
        return m.to_a
        """)
        assert self.unwrap(space, w_res) == ["abc", "a", "b", "c"]

    def test_branch(self, space):
        w_res = space.execute("return /a|b/ =~ 'a'")
        assert space.int_w(w_res) == 0

    def test_dot(self, space):
        w_res = space.execute("return /./ =~ '\\n'")
        assert w_res is space.w_nil

        w_res = space.execute("return /./m =~ '\\n'")
        assert space.int_w(w_res) == 0
