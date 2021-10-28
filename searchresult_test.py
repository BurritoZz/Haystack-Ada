import unittest
from searchresult import SearchResult
import libadalang as lal


class TestSearchResult(unittest.TestCase):
    def test_expr_rule(self):
        # standard put statement
        dosort1 = SearchResult("dosort.adb", "Put(Arr(I).X)", rule=lal.GrammarRule.expr_rule)
        self.assertEqual(dosort1.found, True)
        self.assertEqual(str(dosort1.locations), "[<SlocRange 34:10-34:23>]")

    def test_for_loop(self):
        # for loop
        dosort2 = SearchResult("dosort.adb", "for I     in Arr'Range loop\n\n"
                                             "Put(\"(\") ;\n"
                                             "Put(Arr(I).X);\n"
                                             "Put(\",\");\n"
                                             "Put(Arr(I).Y);  \n"
                                             "Put(\")\");\n\n\n"
                                             "end loop;\",",
                               rule=lal.GrammarRule.loop_stmt_rule)
        self.assertEqual(dosort2.found, True)
        self.assertEqual(str(dosort2.locations), "[<SlocRange 32:7-38:16>]")

    def test_empty(self):
        # empty search term
        dosort3 = SearchResult("dosort.adb", "",
                               rule=lal.GrammarRule.compilation_rule)
        self.assertEqual(dosort3.found, False)
        self.assertEqual(str(dosort3.locations), "[]")

    def test_invalid_file(self):
        # invalid filename
        with self.assertRaises(ValueError):
            SearchResult("", "", rule=lal.GrammarRule.compilation_rule)

    def test_exception_file(self):
        # exception rule
        stack1 = SearchResult("g_stack_user.adb", "when Data_Error =>\n"
                                                  "Put_Line(\"Okay, that'll be your first string.\");\n",
                              rule=lal.GrammarRule.exception_handler_rule)
        self.assertEqual(stack1.found, True)

    def test_if(self):
        # if statement
        obj1 = SearchResult("obj1.adb", "if LC.Count > L\n"
                                        "then LC.Count := L;\n"
                                        "end if;",
                            rule=lal.GrammarRule.if_stmt_rule)
        self.assertEqual(obj1.found, True)
        self.assertEqual(str(obj1.locations), "[<SlocRange 38:7-38:50>]")

    # Test of Case (in)sensitive stuff:
    def test_expr(self):
        hello1 = SearchResult("hello.adb", "put(arr(ii).x)", rule=lal.GrammarRule.expr_rule)
        self.assertEqual(hello1.found, True)
        self.assertEqual(str(hello1.locations), "[<SlocRange 6:4-6:18>]")

    def test_expr_multiple(self):
        hello2 = SearchResult("hello.adb", "put(arr(i).x)", rule=lal.GrammarRule.expr_rule)
        self.assertEqual(hello2.found, True)
        self.assertEqual(str(hello2.locations), "[<SlocRange 7:4-7:17>, <SlocRange 8:4-8:17>, <SlocRange 10:7-10:20>, <SlocRange 11:7-11:20>, <SlocRange 12:7-12:20>]")

    def test_if_stmt(self):
        hello3 = SearchResult("hello.adb", "IF THE_MONTH > The_Time then\n"
                                            "The_Month := THE_TIME;\n"
                                            "end IF;", rule=lal.GrammarRule.if_stmt_rule)
        self.assertEqual(hello3.found, True)
        self.assertEqual(str(hello3.locations), "[<SlocRange 16:4-18:11>]")

    #TODO : Real for loop

    
