from typing import List, Tuple, Dict, Union

import src.fastq_tools as fastq_tools
import src.dna_rna_tools as dna_rna_tools


def filter_fastq_seqs(
        seqs: Dict[str, Tuple[str]],
        gc_bounds: Union[float, Tuple[float]] = (0, 100),
        length_bounds: Union[int, Tuple[int]] = (0, 2 ** 32),
        quality_threshold: int = 0
) -> Dict[str, Tuple[str]]:
    """
    Filters provided sequences with specified parameters.

    Args:
    - seqs (Dict[str, Tuple[str]]): a dictionary with FASTQ-file contents
    - gc_bounds (Union[float, Tuple[float]]): GC-content boundaries (from 0 to 100)
        within which filtered sequences must be included
    - length_bounds (Union[int, Tuple[int]]): length boundaries
        within which filtered sequences must be included
    - quality_threshold (int): reading quality value according to table phred+33,
        below which filtering will not be performed

    Return:
    - Dict[str, Tuple[str]]: a dictionary with filtered sequences
    """

    if isinstance(gc_bounds, (int, float)):  # проверка инпута и указание границ
        gc_bounds = (0, gc_bounds)
    if isinstance(length_bounds, int):
        length_bounds = (0, length_bounds)
    if gc_bounds[1] > 100 or \
            (gc_bounds[0] > gc_bounds[1]) or \
            (length_bounds[0] > length_bounds[1]) or \
            not (0 <= quality_threshold <= 40):  # проверка указания границ
        raise ValueError('The bounds are indicated incorrectly!')
    seqs_gc_and_len_in_bounds = fastq_tools.is_gc_and_length_in_bounds(seqs, gc_bounds, length_bounds)
    quality_in_bounds = fastq_tools.is_quality_in_bounds(seqs, quality_threshold)

    filtered_fastq_seqs = {}
    for key in seqs:
        if (seqs_gc_and_len_in_bounds[key][0] and
                seqs_gc_and_len_in_bounds[key][1] and
                quality_in_bounds[key]) is True:
            filtered_fastq_seqs[key] = seqs[key]
    return filtered_fastq_seqs


def run_dna_rna_tools(*args: str) -> Union[str, List[str]]:
    """
    Accepts sequences and action to be done with them.

    Args:
    The last argument is the action performed on the sequences that are the other arguments

    Return:
    - Union[str, List[str]]: sequence / sequences after action
    """

    *seqs, function = args
    functions = {
        'transcribe': dna_rna_tools.transcribe,
        'reverse': dna_rna_tools.reverse,
        'complement': dna_rna_tools.complement,
        'reverse_complement': dna_rna_tools.reverse_complement
    }
    result_list = []
    show_warning_message = False
    for seq in seqs:
        if (set(seq) <= set('AUTGCautgc')) is False or 'T' in seq.upper() and 'U' in seq.upper():
            result_list.append(None)
            show_warning_message = True
        else:
            res = functions[function](seq)
            result_list.append(res)

    if show_warning_message:
        print('Some of your sequences have unreadable data!')

    if len(result_list) == 1:
        return result_list[0]
    else:
        return result_list
    