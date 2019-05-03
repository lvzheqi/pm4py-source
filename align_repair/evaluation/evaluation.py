from align_repair.evaluation.random_dataset import dataset_generation, alignment_generation
from align_repair.evaluation.config import REPAIR_RESULTS, ALIGN_FILE_NAME, ALIGN_MTS, MPT_LEVEL, EAP_ALIGNS


if __name__ == "__main__":
    dataset_generation.create_tree()
    dataset_generation.create_log()

    alignment_generation.compute_alignment(0, ALIGN_FILE_NAME)
    for i in range(1, len(MPT_LEVEL) + 1):
        alignment_generation.compute_alignment(i, ALIGN_MTS[i - 1])
        alignment_generation.compute_repair_result(ALIGN_MTS[i-1], EAP_ALIGNS[i-1], REPAIR_RESULTS[i - 1])

        from align_repair.evaluation.execl_operation.object_read import read_repair_result_from_file
        print(read_repair_result_from_file(ALIGN_MTS[i - 1], REPAIR_RESULTS[i - 1]))
