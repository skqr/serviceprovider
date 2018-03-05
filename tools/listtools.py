import logging

from typing import List

logger = logging.getLogger()


def flatten_list(list_of_lists: List[List]):
    try:
        0 < len(list_of_lists) and list_of_lists[0][0]

    except KeyError:
        logger.info('flatten_list() called on a non-multidimensional list.')
        return list_of_lists

    composite_list = []

    # Deliberately not using a comprehension
    for single_list in list_of_lists:
        composite_list += single_list

    return composite_list
