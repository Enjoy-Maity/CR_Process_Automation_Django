import traceback
from typing import List, Tuple, AnyStr, Any


def batch_maker(total_cr_list: List[str]):
    batch_size = 10
    batches = [
        total_cr_list[i : i + batch_size]
        for i in range(0, len(total_cr_list), batch_size)
    ]
    return batches


def batch_maker_based_on_len(length: int):
    batch_size = 3
    list_ = list(range(0, length))
    
    batches = [
        list_[i:i+batch_size]
        for i in range(0, length, batch_size)
    ]
    return batches


def main_method(input, logs, *args) -> Tuple[bool, List[List[AnyStr]] | None, List[AnyStr]]:
    flag = False
    result = None
    try:
        if isinstance(input, (list, tuple)):
            result = batch_maker(input)
        
        if isinstance(input, int):
            result = batch_maker_based_on_len(input)
        
        if result:
            flag = True

    except Exception:
        logs.append(
            (
                f"{e.__class__.__name__}",
                f"{traceback.format_exc()}",
                f"{e}",
            )
        )
        raise

    return flag, result, logs
    