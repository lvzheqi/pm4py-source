import unittest

if __name__ == "__main__":
    from ra_tests.pt_manipulate_test import PTUtilsTest
    from ra_tests.pt_stochastic_generation_test import PTGenerationTest
    from ra_tests.lock_align_repair_test import LockAlignRepairTest
    from ra_tests.lock_scope_expand_test import LockScopeExpandTest
    from ra_tests.pt_align_lock import AlignLockTest

    ptUtilsTest = PTUtilsTest()
    ptGenerationTest = PTGenerationTest()
    alignRepairTest = LockAlignRepairTest()
    scopeExpandTest = LockScopeExpandTest()
    alignLockTest = AlignLockTest()

    unittest.main()
