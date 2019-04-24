import unittest

if __name__ == "__main__":
    from ar_tests.pt_compare_test import PTCompareTest
    from ar_tests.pt_stochastic_generation_test import PTGenerationTest
    from ar_tests.align_repair_test import AlignRepairTest
    from ar_tests.scope_expand_test import ScopeExpandTest

    ptCompareTest = PTCompareTest()
    ptGenerationTest = PTGenerationTest()
    alignRepairTest = AlignRepairTest()
    scopeExpandTest = ScopeExpandTest()

    unittest.main()
