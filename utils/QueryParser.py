try:
    set
except NameError:
    from sets import Set as set

#
# Class for parsing expressions in a simple query language.
#
# Grammar:  CLAUSE -> ( CMD ARGS )
#           ARGS ->   ARG ARGS | e
#           ARG ->    CLAUSE | STRING
#           STRING -> ".*" | '.*'
#           CMD ->    [A-Z]+
#
# Usage:    myparser = QueryParser(mytrie)
#           result = myparser.parse(query)
#
class QueryParser(object):

    __slots__ = '__trie'

    def __init__(self, trie):

        self.__trie = trie


    def parse(self, query):

        query, result = self.__parse_CLAUSE(query)
        if (query.strip()): raise SyntaxError("trailing garbage: %s" % (query))

        return result


    def __parse_CLAUSE(self, query):

        query = query.lstrip()
        token = query[0]
        query = query[1:]
        if (token != "("): raise SyntaxError("'(' expected.")

        # read command
        query = query.lstrip()
        pos = query.find(" ")
        cmd = query[:pos]
        query = query[pos:]

        if (cmd == "AND"):
            query, r1 = self.__parse_ARG(query)
            query, r2 = self.__parse_ARG(query)
            result = set(r1)
            result.intersection_update(r2)
            result = list(result)

        elif (cmd == "OR"):
            query, r1 = self.__parse_ARG(query)
            query, r2 = self.__parse_ARG(query)
            result = set(r1)
            result.union_update(r2)
            result = list(result)

        elif (cmd == "MATCH"):
            query, r1 = self.__parse_ARG(query)
            query, r2 = self.__parse_ARG(query)
            result = self.__trie.retrieve([r1] + list(r2))

        # read paren
        query = query.lstrip()
        token = query[0]
        if (token != ")"): raise SyntaxError("')' expected. " + query)
        query = query[1:]

        return (query, result)


    def __parse_ARG(self, query):

        query = query.lstrip()
        token = query[0]

        if (token == "("):
            query, result = self.__parse_CLAUSE(query)

        elif (token in ["\"", "'"]):
            query, result = self.__parse_STRING(query)

        else:
            raise SyntaxError("'(' or '\"' expected.")

        return (query, result)


    def __parse_STRING(self, query):

        delimiter = query[0]
        value = ""
        cnt = 1
        c = query[cnt]
        while (c != delimiter):
            value += c
            cnt += 1
            c = query[cnt]
        #end while

        query = query[cnt + 1:]
        return (query, value)
