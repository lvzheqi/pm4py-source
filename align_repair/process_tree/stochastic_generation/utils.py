def get_cur_label(no_number):
    """
    Return a unique label for the current node

    Parameters
    -----------
    no_number
        The number of the node, each leaf-node has a unique number

    Returns
    ------------
    Label
        Unique label of current node
    """
    # return 'label_' + str(no_number)
    return chr(no_number + 96)
