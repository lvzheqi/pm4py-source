from align_repair.evaluation.random_dataset import dataset_generation, alignment_generation
from align_repair.evaluation.config import REPAIR_RESULTS, ALIGN_FILE_NAME, ALIGN_MTS, MPT_LEVEL, EAP_ALIGNS, OP2_REPAIR_RESULTS


if __name__ == "__main__":
    dataset_generation.create_tree()
    dataset_generation.create_log()

    print("create pt and log")
    alignment_generation.compute_alignment(0, ALIGN_FILE_NAME)
    for i in range(1, len(MPT_LEVEL) + 1):
        alignment_generation.compute_alignment(i, ALIGN_MTS[i - 1])

    print("create align")
    for i in range(1, len(MPT_LEVEL) + 1):
        alignment_generation.compute_repair_result(i, ALIGN_MTS[i-1], EAP_ALIGNS[i-1], REPAIR_RESULTS[i - 1])

        from align_repair.evaluation.execl_operation.object_read import read_repair_result_from_file
        print(read_repair_result_from_file(ALIGN_MTS[i - 1], REPAIR_RESULTS[i - 1]))

    for i in range(1, len(MPT_LEVEL) + 1):
        alignment_generation.compute_repair_result_option2(REPAIR_RESULTS[i-1], i, ALIGN_MTS[i-1],
                                                           OP2_REPAIR_RESULTS[i - 1])
