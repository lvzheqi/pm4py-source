import unittest

if __name__ == "__main__":
    from ar_tests.pt_manipulate_test import PTUtilsTest
    from ar_tests.pt_stochastic_generation_test import PTGenerationTest
    from ar_tests.align_repair_test import AlignRepairTest
    from ar_tests.scope_expand_test import ScopeExpandTest
    from ar_tests.pt_align_lock import AlignLockTest

    ptUtilsTest = PTUtilsTest()
    ptGenerationTest = PTGenerationTest()
    alignRepairTest = AlignRepairTest()
    scopeExpandTest = ScopeExpandTest()
    alignLockTest = AlignLockTest()

    unittest.main()
